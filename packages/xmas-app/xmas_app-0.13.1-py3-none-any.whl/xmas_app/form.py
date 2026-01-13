import re
from datetime import date
from functools import partial

import orjson
from nicegui import ElementFilter, app, run, ui
from nicegui.binding import BindableProperty
from pydantic import AnyUrl, ValidationError
from sqlalchemy import select
from xplan_tools.model import model_factory
from xplan_tools.model.base import BaseFeature
from xplan_tools.model.orm import Feature, Refs
from xplan_tools.util.style import add_style_properties_to_feature

from xmas_app.components.association import AssociationList
from xmas_app.components.label import LabelWithDescription
from xmas_app.settings import get_settings
from xmas_app.util.codelist import get_codelist_options


class ModelForm:
    """A dynamic form builder for XPlan features using NiceGUI.

    This class provides methods to render and manage forms for editing and previewing
    XPlan/XTrasse features, including nested data types and associations.
    """

    editable: bool = BindableProperty()

    def __init__(
        self,
        appschema: str,
        version: str,
        parent: ui.element | None = None,
        header: ui.header | None = None,
    ):
        """Initialize the ModelForm.

        Args:
            appschema (str): The application schema name.
            version (str): The schema version.
            parent (ui.element | None): The parent UI element for rendering.
            header (ui.header | None): Optional header UI element.
        """
        self.appschema = appschema
        self.version = version
        self.featuretype = None
        self.sub_models = {}
        self.parent = parent
        self.header = header
        self.rendered = False
        self.editable = False

    async def _filter_properties(self):
        """Filter property rows in the UI based on the selected filter option."""
        self.row_filter.set_value("")
        match self.radio_filter.value:
            case "all":
                ElementFilter(marker="property_row").classes(remove="hidden")
            case "mandatory":
                ElementFilter(marker="property_row").classes(remove="hidden")
                ElementFilter(marker="nullable").classes(add="hidden")
            case "set":
                ElementFilter(marker="property_row").classes(remove="hidden")
                for elem in (
                    ElementFilter(kind=ui.label)
                    .within(marker="property_row")
                    .not_within(marker="sub_form")
                ):
                    if not getattr(self.feature, elem.text, None):
                        ElementFilter(marker=elem.text).not_within(
                            marker="sub_form"
                        ).classes(add="hidden")

    @staticmethod
    def validate_uri(value: str | None):
        if value is None:
            return True
        try:
            _ = AnyUrl(value)
        except ValidationError:
            return False
        else:
            return True

    @staticmethod
    def validate_date(value: str | None):
        if value is None:
            return True
        try:
            date.fromisoformat(value)
        except ValueError:
            return False
        else:
            return True

    async def _preview_association(self, assoc_id: str):
        """Show a dialog previewing the associated object.

        Args:
            assoc_id (str): The ID of the associated object to preview.
        """
        with self.parent:
            with (
                ui.dialog() as dialog,
                ui.card().style("width: auto; max-width: none") as card,
            ):
                try:
                    linked_feature = get_settings().repo.get(assoc_id)
                    await ModelForm(
                        self.appschema,
                        self.version,
                        card,
                    ).render_form(
                        feature_type=linked_feature.get_name(),
                        feature=linked_feature.model_dump(
                            mode="json", context={"datatype": True, "file_uri": True}
                        ),
                        main_form=True,
                        preview=True,
                    )
                except ValidationError:
                    ui.notify(
                        "Fehler beim Anzeigen der Daten",
                        type="negative",
                        position="top",
                    )
        await dialog
        dialog.delete()

    def _propagate_data(self):
        if not self.editable:
            return
        if model_instance := self.model_instance:
            feature_data = {
                "properties": model_instance.model_dump(
                    mode="json",
                    exclude_unset=True,
                    exclude={"id", self.model.get_geom_field()},
                ),
                "featuretype": self.model.get_name(),
                "id": model_instance.id,
            }
        else:
            feature_data = {
                "properties": None,
                "featuretype": None,
                "id": None,
            }
            # self.radio_filter.set_value("mandatory")
        ui.run_javascript(f"""new QWebChannel(qt.webChannelTransport, function (channel) {{
                                    channel.objects.handler.receive_feature({orjson.dumps(feature_data).decode()})
                            }});""")

    def _get_bindable_object(self, model: type[BaseFeature]) -> type:
        """Construct a class with bindable properties from a BaseFeature.

        Takes a BaseFeature class as input and returns a new class with the BaseFeature's attributes as BindableProperties.
        The new bindable class can be instantiated with keyword arguments corresponding to the attributes,
        e.g. with an unpacked dict generated by the model_dump() method.

        Nested models will be assigned to corresponding bindable classes recursively.

        Args:
            model (type[BaseFeature]): The Pydantic BaseFeature to build the bindable class from.

        Returns:
            type: The bindable class with properties corresponding to the model fields.
        """

        def constructor(bindable_object, **kwargs) -> None:
            """The init method of the bindable class.

            Args:
                bindable_object (object): The class instance, i.e. self.
                kwargs: The feature's attributes as keyword arguments.
            """
            for key in model.model_fields.keys():
                value = kwargs.get(key, None)
                prop_info = model.get_property_info(key)
                if prop_info["stereotype"] == "DataType" and value:
                    if isinstance(prop_info["typename"], str):
                        sub_obj = self._get_bindable_object(
                            model_factory(
                                prop_info["typename"], self.version, self.appschema
                            )
                        )
                        value = (
                            [sub_obj(**item) for item in value]
                            if prop_info["list"]
                            else sub_obj(**value)
                        )
                    else:
                        value = (
                            [
                                self._get_bindable_object(
                                    model_factory(
                                        item["datatype"], self.version, self.appschema
                                    )
                                )(**item)
                                for item in value
                            ]
                            if prop_info["list"]
                            else self._get_bindable_object(
                                model_factory(
                                    value["datatype"], self.version, self.appschema
                                )
                            )(**value)
                        )
                setattr(bindable_object, key, value)

        attributes = {"__init__": constructor}
        for field in model.model_fields.keys():
            attributes[field] = BindableProperty(
                on_change=lambda *_: self._propagate_data()
            )
        return type(model.get_name(), (), attributes)

    @property
    def model_instance(self) -> BaseFeature | None:
        """Get the validated model instance from the current feature.

        Returns:
            BaseFeature | None: The validated model instance, or None if validation fails.
        """
        feature = self.feature
        vars(feature).pop("sub_models", None)
        if (geom := vars(self.feature).pop("geometry", None)) and (
            geom_field := self.model.get_geom_field()
        ):
            setattr(feature, geom_field, geom)
        try:
            return self.model.model_validate(feature)
        except ValidationError as e:
            message = f"Fehlerhafte Eingabe: {', '.join(set([str(error['loc'][0]) for error in e.errors()]))}"
            if getattr(self, "current_validation_error", None) != message:
                self.current_validation_error = message
                ui.notify(
                    message,
                    type="negative",
                    position="bottom",
                )

    async def _set_stylesheetId_and_schriftinhalt(self) -> None:
        """Set the stylesheetId and schriftinhalt attributes based on the referenced feature."""
        if not self.editable:
            return
        ref_id = getattr(self.feature, "dientZurDarstellungVon", None)
        if not ref_id or not getattr(self.feature, "art", None):
            return
        obj = self.model_instance
        if not obj:
            return
        new_obj = add_style_properties_to_feature(
            obj, get_settings().repo.get(ref_id[0])
        )
        stylesheet_id = getattr(new_obj, "stylesheetId", None)
        setattr(
            self.feature, "stylesheetId", str(stylesheet_id) if stylesheet_id else None
        )
        if schriftinhalt := getattr(new_obj, "schriftinhalt", None):
            setattr(self.feature, "schriftinhalt", schriftinhalt)

    def _get_association_targets(
        self,
        property: str | list,
        typenames: str | list,
        excluded_ids: list[str] | str = [],
        plan_id: str | None = None,
    ):
        """Get possible association targets for a property.

        Args:
            property (str | list): The property name or list of names.
            typenames (str | list): The type name(s) to filter by.
            excluded_ids (list[str] | str, optional): IDs to exclude. Defaults to [].
            plan_id (str | None, optional): The ID of the associated plan. Defaults to None.

        Returns:
            dict: Mapping of feature IDs to feature type names.
        """
        if plan_id and isinstance(property, str) and property.startswith("gehoertZu"):
            plan = get_settings().repo.get(plan_id)
            if property.endswith("Bereich"):
                bereiche = [
                    get_settings().repo.get(bereich) for bereich in plan.bereich
                ]
                return {
                    bereich.id: f"{bereich.get_name()} {bereich.nummer}"
                    for bereich in bereiche
                }
            else:
                return {plan_id: f"{plan.get_name()} {plan.name}"}
        with get_settings().repo.Session() as session:
            stmt = (
                select(Feature)
                .where(
                    Feature.featuretype.in_(
                        [typenames] if isinstance(typenames, str) else typenames
                    )
                )
                .where(
                    Feature.id.not_in(
                        [excluded_ids]
                        if isinstance(excluded_ids, str)
                        else excluded_ids
                    )
                )
                .where(Feature.id != self.feature.id)
            )
            if plan_id:
                # limit features to the ones belonging to the plan
                stmt = stmt.where(
                    Feature.refs_inv.any(
                        Refs.feature.has(Feature.refs_inv.any(Refs.base_id == plan_id)),
                    )
                )
            result = session.execute(stmt)

            targets = {
                str(feature.id): f"{feature.featuretype} {str(feature.id)[:8]}"
                for feature in result.unique().scalars().all()
            }

        return targets

    def _is_geometry_required(self, typename: str) -> bool:
        """Check if a geometry is required for the given type.

        Args:
            typename (str): The type name.

        Returns:
            bool: True if geometry is required, False otherwise.
        """
        model = model_factory(typename, self.version, self.appschema)
        if geom := model.get_geom_field():
            return not model.get_property_info(geom)["nullable"]
        return False

    def _get_art_options(self) -> None:
        """Populate the 'art' select input with options derived from referenced feature attributes."""

        def derive_art_from_attributes():
            """Derive art options from the referenced feature's attributes.

            Returns:
                dict: Mapping of attribute paths to display values.
            """

            def set_option_value(path, value):
                art[path] = f"{path} ({str(value)})"

            art = {}
            for name, value in ref_feature.model_dump(
                mode="json",
                exclude_none=True,
                exclude={"id", ref_feature.get_geom_field()},
            ).items():
                # TODO refactor recursive parsing
                prop_info = ref_feature.get_property_info(name)
                if prop_info["stereotype"] == "Association":
                    continue
                elif prop_info["list"]:
                    for index, item in enumerate(value, 0):
                        path = f"{name}[{index + 1}]"
                        if prop_info["stereotype"] == "BasicType":
                            set_option_value(path, item)
                        elif prop_info["stereotype"] == "Enumeration":
                            set_option_value(path, prop_info["enum_info"][item]["name"])
                        elif prop_info["stereotype"] == "DataType":
                            sub_model = getattr(ref_feature, name)[index]
                            for sub_name, sub_value in item.items():
                                sub_prop_info = sub_model.get_property_info(sub_name)
                                sub_path = "/".join(
                                    [path, sub_model.get_name(), sub_name]
                                )
                                set_option_value(
                                    sub_path,
                                    sub_prop_info["enum_info"][sub_value]["name"]
                                    if sub_prop_info["stereotype"] == "Enumeration"
                                    else sub_value,
                                )
                elif prop_info["stereotype"] == "DataType":
                    sub_model = model_factory(
                        prop_info["typename"],
                        self.version,
                        self.appschema,
                    )
                    for sub_name, sub_value in value.items():
                        sub_prop_info = sub_model.get_property_info(sub_name)
                        path = "/".join([name, prop_info["typename"], sub_name])
                        set_option_value(
                            path,
                            sub_prop_info["enum_info"][sub_value]["name"]
                            if sub_prop_info["stereotype"] == "Enumeration"
                            else sub_value,
                        )
                else:
                    set_option_value(
                        name,
                        prop_info["enum_info"][value]["name"]
                        if prop_info["stereotype"] == "Enumeration"
                        else value,
                    )
            return art

        if ref := getattr(self.feature, "dientZurDarstellungVon", None):
            ref_feature = get_settings().repo.get(ref[0])
            self.feature.gehoertZuBereich = str(ref_feature.gehoertZuBereich)
            art_options = derive_art_from_attributes()
            self.art_input.set_options(self.art_input.options | art_options)

    # @ui.refreshable_method
    async def _build_sub_form(
        self, key: str, bind_obj: type, prop_info: dict, preview: bool = False
    ) -> None:
        """Construct a nested form for data types.

        Args:
            key (str): The name of the attribute where the data type is the value.
            bind_obj (type): The bindable parent class the sub-form is bound to.
            prop_info (dict): The property info object for the given attribute.
            preview (bool, optional): Whether the form should be rendered in preview mode. Defaults to False.
        """

        async def add_form(type_name: str | None = None):
            """Add a new sub-form instance for the data type.

            Args:
                type_name (str | None): The type name to instantiate, if it's a union type, otherwise the typename is taken from the property info.
            """
            sub_obj = self._get_bindable_object(
                model_factory(
                    type_name or prop_info["typename"], self.version, self.appschema
                )
            )()
            if not getattr(bind_obj, key, None):
                setattr(bind_obj, key, [sub_obj] if prop_info["list"] else sub_obj)
            elif prop_info["list"]:
                getattr(bind_obj, key).append(sub_obj)
            else:
                setattr(bind_obj, key, sub_obj)

            item = await build_item(
                None,
                sub_obj,
                getattr(bind_obj, key).index(sub_obj) if prop_info["list"] else None,
            )
            item.move(item_list)
            # self._build_sub_form.refresh()

        def delete_form(element: ui.element, item: type):
            """Delete a sub-form instance.

            Args:
                index (int | None): The index to delete, if the property is a list.
            """
            if isinstance(getattr(bind_obj, key), list):
                getattr(bind_obj, key).remove(item)
                if not len(getattr(bind_obj, key)):
                    setattr(bind_obj, key, None)
            else:
                setattr(bind_obj, key, None)
            element.delete()
            # self._build_sub_form.refresh()

        async def build_item(
            sub_model: BaseFeature | None,
            item: type,
            index: int | None = None,
        ) -> ui.item:
            """Build a UI item for a sub-form instance.

            This corresponds to an instance of the data type.

            Args:
                sub_model (BaseFeature | None): The sub-model class.
                item (type): The bindable object instance.
                index (int | None): The index in the list, if applicable.
            """
            if not sub_model:
                sub_model = model_factory(
                    item.__class__.__name__,
                    self.version,
                    self.appschema,
                )

            with ui.item().props("dense") as list_item:
                with ui.item_section():
                    if isinstance(prop_info["typename"], list):
                        with ui.item_label():
                            LabelWithDescription(
                                sub_model.get_name(), sub_model.__doc__
                            ).classes("text-bold")
                    await self._build_model_form(
                        sub_model,
                        getattr(bind_obj, key)[index]
                        if prop_info["list"]
                        else getattr(bind_obj, key),
                        preview=preview,
                    )
                if not preview:
                    with ui.item_section().props("side"):
                        delete_button = (
                            ui.button(
                                icon="delete",
                                on_click=partial(delete_form, list_item, item),
                            )
                            .props("flat round")
                            .bind_enabled_from(
                                bind_obj,
                                key,
                                backward=lambda x: len(x) > 1
                                if not prop_info["nullable"] and isinstance(x, list)
                                else x is not None
                                if prop_info["nullable"]
                                else x,
                            )
                        )
                        if not self.editable:
                            delete_button.disable()
            return list_item

        if not prop_info["nullable"] and not getattr(bind_obj, key, None):
            if isinstance(prop_info["typename"], str):
                sub_obj = self._get_bindable_object(
                    model_factory(prop_info["typename"], self.version, self.appschema)
                )()
                setattr(bind_obj, key, [sub_obj] if prop_info["list"] else sub_obj)

        value = getattr(bind_obj, key, None)
        with (
            ui.list()
            .classes("w-full")
            .props("bordered separator dense")
            .mark("sub_form")
        ) as item_list:
            sub_model = None
            if isinstance(prop_info["typename"], str):
                sub_model = model_factory(
                    prop_info["typename"],
                    self.version,
                    self.appschema,
                )
                with ui.item().props("dense"):
                    LabelWithDescription(
                        sub_model.get_name(), sub_model.__doc__
                    ).classes("text-bold")
                ui.separator()
            if value is not None:
                if isinstance(value, list):
                    for index, item in enumerate(value):
                        await build_item(sub_model, item, index)
                else:
                    await build_item(sub_model, value)
            if not preview:
                if prop_info["list"] or (prop_info["nullable"] and not value):
                    with ui.item().classes("justify-center"):
                        if isinstance(prop_info["typename"], str):
                            ui.button(
                                icon="add",
                                on_click=add_form,
                            ).bind_enabled_from(self, "editable").props("flat round")
                        else:
                            with (
                                ui.dropdown_button(
                                    text="Datentyp auswählen",
                                    icon="add",
                                    auto_close=True,
                                )
                                .bind_enabled_from(self, "editable")
                                .props("flat rounded no-caps")
                            ):
                                for type_name in prop_info["typename"]:
                                    ui.item(
                                        type_name,
                                        on_click=lambda x: add_form(
                                            next(x.sender.descendants()).text
                                        ),
                                    )

    async def _build_model_form(
        self,
        model: BaseFeature,
        bind_obj: type,
        main_form: bool = False,
        preview: bool = False,
    ) -> None:
        """Construct a form for a given feature.

        This method is also called recursively for nested data types.

        Args:
            model (BaseFeature): The BaseFeature class.
            bind_obj (type): The bindable class to bind input to.
            main_form (bool, optional): Whether it's the initial/parent form or a sub-form. Defaults to False.
            preview (bool, optional): Whether the form should be rendered in preview mode. Defaults to False.
        """
        if main_form:
            with ui.row(align_items="center") as class_info:
                LabelWithDescription(model.get_name(), model.__doc__).classes("text-h6")
            if not preview:
                with class_info:
                    with ui.row(align_items="center"):
                        row_filter = (
                            ui.input(
                                "Attributnamen und -definition filtern",
                                on_change=lambda x: radio_filter.set_value("all")
                                if x.value
                                else radio_filter.set_value(radio_filter.value),
                            )
                            .classes("on-right")
                            .style("width: 380px;")
                            .props("clearable square filled dense bg-color=white")
                        )
                        self.row_filter = row_filter
                        with row_filter.add_slot("prepend"):
                            ui.icon("o_filter_alt")
                        radio_filter = (
                            ui.radio(
                                {
                                    "all": "Alle Attribute",
                                    "mandatory": "Pflichattribute",
                                    "set": "Belegte Attribute",
                                },
                                value="all",
                                on_change=self._filter_properties,
                            )
                            .props("dense inline dark color=white")
                            .classes("on-right")
                        )
                        self.radio_filter = radio_filter
            class_info.move(self.header if not preview else self.parent, 0)
        with ui.grid(columns="minmax(0, 1fr) minmax(0, 2fr)"):
            for key, field_info in model.model_fields.items():
                if key == model.get_geom_field():
                    continue
                prop_info = model.get_property_info(key)
                if preview and (
                    prop_info["stereotype"] == "Association"
                    or getattr(bind_obj, key, None) is None
                ):
                    continue
                default = None
                if isinstance(
                    field_default := getattr(field_info, "default", None),
                    (float, int, str),
                ):
                    default = field_default
                with ui.row().classes("w-full min-w-0 pr-8") as property_row:
                    if main_form and not preview:
                        property_row.bind_visibility_from(
                            row_filter,
                            "value",
                            backward=lambda filter_value,
                            key=key,
                            docs=field_info.description: re.search(
                                filter_value, key + str(docs), re.I
                            )
                            if filter_value
                            else True,
                        )
                        marker = ["property_row", key]
                        if prop_info["nullable"]:
                            marker.append("nullable")
                        property_row.mark(" ".join(marker))
                    LabelWithDescription(
                        key,
                        "Identifikator des Features."
                        if key == "id"
                        else field_info.description,
                    ).classes("text-bold")
                with (
                    ui.row()
                    .style("min-width: 250px;")
                    .classes("w-full min-w-0") as property_row
                ):
                    if main_form and not preview:
                        property_row.bind_visibility_from(
                            row_filter,
                            "value",
                            backward=lambda filter_value,
                            key=key,
                            docs=field_info.description: re.search(
                                filter_value, key + str(docs), re.I
                            )
                            if filter_value
                            else True,
                        )
                        marker = ["property_row", key]
                        if prop_info["nullable"]:
                            marker.append("nullable")
                        property_row.mark(" ".join(marker))
                    if key == "id":
                        input = (
                            ui.label()
                            .bind_text_from(
                                bind_obj,
                                key,
                            )
                            .classes("w-full")
                        )
                        continue
                    if key == "stylesheetId":
                        input = (
                            ui.label()
                            .bind_text_from(
                                bind_obj,
                                key,
                                backward=lambda x: x.split("/")[-1]
                                if x and "/" in x
                                else "keine passende ID gefunden",
                            )
                            .classes("w-full")
                        )
                        continue
                    match prop_info["stereotype"]:
                        case "BasicType":
                            match prop_info["typename"]:
                                case "CharacterString":
                                    if key == "art":
                                        options = {}
                                        if existing := getattr(bind_obj, key, None):
                                            options.update(
                                                {
                                                    item: f"{item} (?)"
                                                    for item in existing
                                                }
                                            )
                                        input = (
                                            ui.select(
                                                options,
                                                label=prop_info["typename"],
                                                on_change=self._set_stylesheetId_and_schriftinhalt,
                                                multiple=prop_info["list"],
                                                clearable=prop_info["nullable"],
                                                validation=None
                                                if prop_info["nullable"]
                                                else {"Pflichtfeld": lambda x: x},
                                            )
                                            .bind_value(
                                                bind_obj,
                                                key,
                                                forward=lambda x: None if not x else x,
                                            )
                                            .bind_enabled_from(self, "editable")
                                            .props("stack-label square filled dense")
                                            .classes("w-full")
                                            .mark("art")
                                        )
                                        self.art_input = input
                                        self._get_art_options()
                                        input.validate()
                                    elif prop_info["list"]:
                                        ui.label("TODO")
                                    else:
                                        input = (
                                            ui.textarea(
                                                prop_info["typename"],
                                                validation=None
                                                if prop_info["nullable"]
                                                else {"Pflichtfeld": lambda x: x},
                                            )
                                            .bind_value(
                                                bind_obj,
                                                key,
                                                forward=lambda x: None if not x else x,
                                            )
                                            .props(
                                                "stack-label clearable autogrow square filled dense"
                                            )
                                            .classes("w-full q-pa-none q-gutter-none")
                                        )
                                        input.bind_enabled_from(
                                            self,
                                            "editable",
                                            backward=lambda v, input=input: input.props(
                                                **{
                                                    "add"
                                                    if not v
                                                    else "remove": "readonly"
                                                }
                                            ),
                                        )
                                        input.validate()
                                case "Integer":
                                    if prop_info["list"]:
                                        ui.label("TODO")
                                    else:
                                        input = (
                                            ui.number(
                                                prop_info["typename"],
                                                value=default,
                                                precision=0,
                                                format="%d",
                                                validation=None
                                                if prop_info["nullable"]
                                                else {
                                                    "Pflichtfeld": lambda x: x
                                                    is not None
                                                },
                                            )
                                            .bind_value(
                                                bind_obj,
                                                key,
                                                forward=lambda x: int(x)
                                                if x is not None
                                                else None,
                                                # backward=lambda x: x,
                                            )
                                            .props(
                                                "stack-label clearable square filled dense"
                                            )
                                            .classes("w-full q-pa-none q-gutter-none")
                                        )
                                        input.bind_enabled_from(
                                            self,
                                            "editable",
                                            backward=lambda v, input=input: input.props(
                                                **{
                                                    "add"
                                                    if not v
                                                    else "remove": "readonly"
                                                }
                                            ),
                                        )
                                        input.validate()
                                case "Decimal":
                                    if prop_info["list"]:
                                        ui.label("TODO")
                                    else:
                                        input = (
                                            ui.number(
                                                prop_info["typename"],
                                                # value=default,
                                                validation=None
                                                if prop_info["nullable"]
                                                else {
                                                    "Pflichtfeld": lambda x: x
                                                    is not None
                                                },
                                            )
                                            .bind_value(
                                                bind_obj,
                                                key,
                                                # backward=lambda x: None if not x else x,
                                            )
                                            .props(
                                                "stack-label clearable square filled dense"
                                            )
                                            .classes("w-full q-pa-none q-gutter-none")
                                        )
                                        input.bind_enabled_from(
                                            self,
                                            "editable",
                                            backward=lambda v, input=input: input.props(
                                                **{
                                                    "add"
                                                    if not v
                                                    else "remove": "readonly"
                                                }
                                            ),
                                        )
                                        input.validate()
                                case "Boolean":
                                    ui.switch(value=default).props(
                                        "toggle-indeterminate"
                                    ).bind_value(bind_obj, key).bind_enabled_from(
                                        self, "editable"
                                    )
                                case "URI":
                                    if prop_info["list"]:
                                        ui.label("TODO")
                                    else:
                                        input = (
                                            ui.input(
                                                prop_info["typename"],
                                                validation={
                                                    "Keine URI": self.validate_uri
                                                }
                                                if prop_info["nullable"]
                                                else {
                                                    "Pflichtfeld": lambda x: x,
                                                    "Keine URI": self.validate_uri,
                                                },
                                            )
                                            .bind_value(
                                                bind_obj,
                                                key,
                                                forward=lambda x: None if not x else x,
                                            )
                                            .classes("w-full q-pa-none q-gutter-none")
                                            .props("stack-label square filled dense")
                                        )
                                        input.bind_enabled_from(
                                            self,
                                            "editable",
                                            backward=lambda v, input=input: input.props(
                                                **{
                                                    "add"
                                                    if not v
                                                    else "remove": "readonly"
                                                }
                                            ),
                                        )
                                        input.validate()
                                case _:
                                    ui.label("BasicType")
                        case "Enumeration":
                            input = (
                                ui.select(
                                    {
                                        k: f"{v['name']} ({k})"
                                        for k, v in prop_info["enum_info"].items()
                                    },
                                    label=prop_info["typename"],
                                    multiple=prop_info["list"],
                                    clearable=prop_info["nullable"],
                                    validation=None
                                    if prop_info["nullable"]
                                    else {"Pflichtfeld": lambda x: x},
                                )
                                .classes("w-full q-pa-none q-gutter-none")
                                .props("stack-label square filled dense")
                                .bind_value(
                                    bind_obj,
                                    key,
                                    backward=lambda x: None if not x else x,
                                )
                            )
                            input.bind_enabled_from(
                                self,
                                "editable",
                                backward=lambda v, input=input: input.props(
                                    **{"add" if not v else "remove": "readonly"}
                                ),
                            )
                            if prop_info["list"]:
                                input.props("use-chips")
                            input.validate()
                        case "Codelist":
                            input = (
                                ui.select(
                                    await get_codelist_options(
                                        values=getattr(bind_obj, key, []),
                                        codelist=prop_info["typename"],
                                    ),
                                    label=prop_info["typename"],
                                    multiple=prop_info["list"],
                                    clearable=prop_info["nullable"],
                                    with_input=True,
                                    # new_value_mode="add-unique",
                                    # key_generator=lambda value,
                                    # codelist=prop_info[
                                    #     "typename"
                                    # ]: f"urn:{self.appschema}:codelist:{codelist}:{value}",
                                    validation={
                                        "Keine URI": lambda value: self.validate_uri(
                                            value
                                        )
                                        if isinstance(value, str)
                                        else all(
                                            [self.validate_uri(item) for item in value]
                                        )
                                        if value
                                        else True
                                    }
                                    if prop_info["nullable"]
                                    else {
                                        "Pflichtfeld": lambda x: x,
                                        "Keine URI": lambda value: self.validate_uri(
                                            value
                                        )
                                        if isinstance(value, str)
                                        else all(
                                            [self.validate_uri(item) for item in value]
                                        )
                                        if value
                                        else True,
                                    },
                                )
                                .bind_value(
                                    bind_obj,
                                    key,
                                    forward=lambda x: None if not x else x,
                                )
                                .classes("w-full q-pa-none q-gutter-none")
                                .props("stack-label square filled dense")
                            )
                            input.bind_enabled_from(
                                self,
                                "editable",
                                backward=lambda v, input=input: input.props(
                                    **{"add" if not v else "remove": "readonly"}
                                ),
                            )
                            if prop_info["list"]:
                                input.props("use-chips")
                            input.validate()
                            with input.add_slot("after"):
                                ui.button(
                                    icon="o_open_in_new",
                                    on_click=lambda input=input: ui.navigate.to(
                                        input.value
                                    ),
                                ).bind_enabled_from(
                                    input,
                                    "value",
                                    backward=lambda value: "registry.gdi-de.org"
                                    in value
                                    if value
                                    else False,
                                ).props("square unelevated")
                        case "Temporal":
                            match prop_info["typename"]:
                                case "Date":
                                    with (
                                        ui.input(
                                            prop_info["typename"],
                                            validation={
                                                "ungültiges Datum": self.validate_date
                                            }
                                            if prop_info["nullable"]
                                            else {
                                                "Pflichtfeld": lambda x: x,
                                                "ungültiges Datum": self.validate_date,
                                            },
                                        )
                                        .bind_value(
                                            bind_obj,
                                            key,
                                            backward=lambda x: None if not x else x,
                                        )
                                        .classes("w-full q-pa-none q-gutter-none")
                                        .props(
                                            "stack-label square filled dense mask='####-##-##'"
                                        ) as date
                                    ):
                                        with ui.menu().props("no-parent-event") as menu:
                                            ui.date(on_change=menu.close).bind_value(
                                                date
                                            ).bind_enabled_from(self, "editable")
                                        with date.add_slot("append"):
                                            ui.icon("edit_calendar").on(
                                                "click", menu.open
                                            ).classes("cursor-pointer")
                                        date.bind_enabled_from(
                                            self,
                                            "editable",
                                            backward=lambda v, input=date: input.props(
                                                **{
                                                    "add"
                                                    if not v
                                                    else "remove": "readonly"
                                                }
                                            ),
                                        )
                                        date.validate()
                                case "TM_Duration":
                                    input = (
                                        ui.number(
                                            prop_info["typename"],
                                            value=default,
                                            suffix="Tage",
                                            step=1,
                                            precision=0,
                                            format="%d",
                                            validation=None
                                            if prop_info["nullable"]
                                            else {
                                                "Pflichtfeld": lambda x: x is not None
                                            },
                                        )
                                        .bind_value(
                                            bind_obj,
                                            key,
                                            forward=lambda x: x * 86400 if x else None,
                                            backward=lambda x: x / 86400 if x else None,
                                        )
                                        .props(
                                            "stack-label clearable square filled dense"
                                        )
                                        .classes("w-full q-pa-none q-gutter-none")
                                    )
                                    input.bind_enabled_from(
                                        self,
                                        "editable",
                                        backward=lambda v, input=input: input.props(
                                            **{"add" if not v else "remove": "readonly"}
                                        ),
                                    )
                                    input.validate()
                                case _:
                                    ui.label("TODO Temporal")
                        case "DataType":
                            await self._build_sub_form(
                                key, bind_obj, prop_info, preview
                            )
                        case "Association":
                            if prop_info["list"]:
                                AssociationList(bind_obj, key)
                            else:
                                input = (
                                    ui.select(
                                        {},
                                        multiple=prop_info["list"],
                                        clearable=prop_info["nullable"],
                                        validation=None
                                        if prop_info["nullable"]
                                        else {"Pflichtfeld": lambda x: x},
                                    )
                                    .classes("w-full q-pa-none q-gutter-none")
                                    .props("square filled dense")
                                )
                                targets = await run.io_bound(
                                    self._get_association_targets,
                                    key,
                                    prop_info["typename"],
                                    [],
                                    app.storage.client.get("plan_id", None),
                                )
                                if not targets:
                                    input.set_label(
                                        "keine passenden Features vorhanden"
                                    )
                                else:
                                    input.set_options(targets)
                                if parent_id := app.storage.client.get(
                                    "parent_id", None
                                ):
                                    input.set_value(parent_id)
                                elif len((keys := list(targets.keys()))) == 1:
                                    input.set_value(keys[0])
                                input.bind_value(
                                    bind_obj,
                                    key,
                                    backward=lambda x: None if not x else x,
                                )
                                input.bind_enabled_from(
                                    self,
                                    "editable",
                                    backward=lambda v, input=input: input.props(
                                        **{"add" if not v else "remove": "readonly"}
                                    ),
                                )
                                input.validate()
                                with input.add_slot("after"):
                                    ui.button(
                                        icon="o_open_in_new",
                                        on_click=lambda input=input: ui.navigate.to(
                                            f"/feature/{input.value}"
                                        ),
                                    ).bind_enabled_from(input, "value").props(
                                        "square unelevated"
                                    )
                                    ui.button(
                                        icon="o_preview",
                                        on_click=lambda assoc_id=input.value: self._preview_association(
                                            assoc_id
                                        ),
                                    ).bind_enabled_from(input, "value").props(
                                        "square unelevated"
                                    )
                        case "Measure":
                            uom = str(prop_info["uom"])
                            input = (
                                ui.number(
                                    f"{prop_info['typename']} [{prop_info['uom']}]",
                                    suffix=prop_info["uom"],
                                    min=-360.0 if uom == "grad" else None,
                                    max=360.0 if uom == "grad" else None,
                                    validation=None
                                    if prop_info["nullable"]
                                    else {"Pflichtfeld": lambda x: x},
                                )
                                .bind_value(
                                    bind_obj,
                                    key,
                                    forward=lambda x, uom=uom: None
                                    if not x
                                    else {"value": x, "uom": uom},
                                    backward=lambda x: None if not x else x["value"],
                                )
                                .classes("w-full q-pa-none q-gutter-none")
                                .props("stack-label square filled dense")
                            )
                            input.bind_enabled_from(
                                self,
                                "editable",
                                backward=lambda v, input=input: input.props(
                                    **{"add" if not v else "remove": "readonly"}
                                ),
                            )
                            input.validate()
                        case _:
                            ui.label("TODO")
        self.rendered = True

    async def render_form(
        self,
        feature_type: str,
        feature: dict,
        main_form: bool = True,
        preview: bool = False,
    ):
        """Render the form for a given feature.

        Args:
            feature_type (str): The type of the feature.
            feature (dict): The feature data as a dictionary.
            main_form (bool, optional): Whether this is the main form. Defaults to True.
            preview (bool, optional): Whether to render in preview mode. Defaults to False.
        """
        self.parent.clear()
        self.featuretype = feature_type
        self.model = model_factory(feature_type, self.version, self.appschema)
        if main_form:
            if (geom := feature.pop("geometry", None)) and (
                model_geom := self.model.get_geom_field()
            ):
                feature[model_geom] = geom
        self.feature = self._get_bindable_object(self.model)(**feature)
        await self._build_model_form(self.model, self.feature, main_form, preview)
