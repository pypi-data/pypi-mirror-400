import logging

from nicegui import app, binding, events, run, ui

from xmas_app.components.buttons import FeatureInteractionButton
from xmas_app.db import get_ref_candidates, get_ref_objects

logger = logging.getLogger("xmas_app")


class AssociationList(ui.button):
    """Class to view and edit associations with multiplicity > 1.

    It initializes a button to use in a feature form that opens a dialog.
    The dialog contains two tabs: one for existing and one for potential feature references.
    The (potential) reference features are retreived from the database and rendered in tables.
    A click on a feature (row) opens a dialog with action buttons to zoom to it etc.
    Active references are handled via the tables selection mechanism: selected features are referenced, deselected features are not.
    """

    refs = binding.BindableProperty()

    def __init__(self, bind_obj: object, bind_key: str) -> None:
        """Initialize the button element.

        Args:
            bind_obj: The binding object to bind the reference list to, i.e. the feature.
            bind_key: The property of the binding object to bind to, i.e. the association attribute.
        """
        super().__init__(icon="link")
        self.props("square unelevated outline")
        self.classes("w-full")
        binding.bind(
            self,
            "refs",
            bind_obj,
            bind_key,
            forward=lambda x: None if not x else x,
            backward=lambda x: [] if not x else x,
        )
        self.rel = bind_key
        self.dialog = ui.dialog().props("full-height")
        self.dialog.on("before-show", self._on_dialog_open)
        self.action_dialog = ui.dialog()
        self.tab_panels: ui.tab_panels | None = None
        self.table_existing: ui.table | None = None
        self.table_candidates: ui.table | None = None
        self.ref_objects: list[dict] | None = None
        self.ref_candidates: list[dict] | None = None
        # create a badge on the button showing the number of active references
        with self:
            ui.badge().props("floating").bind_text_from(
                self,
                "refs",
                backward=lambda refs: str(len(refs)),
            )
        with (
            self.dialog,
            ui.card().style("min-width: 800px; max-width: 90vw;"),
        ):
            with ui.icon("live_help", size="1.2rem").classes("absolute top-1 right-1"):
                ui.tooltip(
                    """
                    Durch Klick auf Features öffnet sich ein Aktionsdialog.
                    Durch Selektion bzw. Deselektion von Features (nur im Editiermodus verfügbar)
                    wird die entsprechende Referenz hinzugefügt bzw. entfernt.
                    """
                ).props("max-width=200px")
            with ui.tabs().classes("w-full pt-2").props("no-caps dense") as tabs:
                ui.tab("existing", "Bestehende Referenzen", "link").classes("w-full")
                ui.tab("candidates", "Mögliche Referenzen", "add_link").classes(
                    "w-full"
                )
            self.tab_panels = ui.tab_panels(
                tabs, on_change=self._on_tab_change
            ).classes("w-full")
            with self.tab_panels:
                with ui.tab_panel("existing"):
                    self.table_existing = self._create_table()
                with ui.tab_panel("candidates"):
                    self.table_candidates = self._create_table()
        self.on_click(self.dialog.open)

    async def _on_dialog_open(self, _: events.GenericEventArguments):
        """Deferred one-time initialization of table content."""
        if not self.tab_panels.value:
            self.tab_panels.set_value("existing")

    async def _on_row_click(self, e: events.GenericEventArguments):
        """Opens a dialog with action buttons for the row/feature."""
        try:
            row = e.args[1]
            feature_id = row["id"]
        except Exception as e:
            logger.exception("error on loading feature data from row: %s", e)
            return ui.notify("Fehler beim Abruf der Feature-Daten", type="negative")
        self.action_dialog.clear()
        with self.action_dialog, ui.card():
            ui.label(f"{row['featuretype']} {feature_id[:8]}").classes("text-bold")
            ui.button(
                text="Vorschau öffnen",
                icon="o_preview",
                on_click=lambda: app.storage.client["form"]._preview_association(
                    feature_id
                ),
            ).props("flat square no-caps align=left").classes("w-full")
            FeatureInteractionButton(
                "highlight_feature", feature_id, row["geometry_type"] != "nogeom"
            )
            FeatureInteractionButton("select_feature", feature_id)
            FeatureInteractionButton(
                "show_attribute_form", feature_id, app.storage.client["form"].feature.id
            )
        self.action_dialog.open()

    async def _on_select(self, _: events.TableSelectionEventArguments):
        """Sets active references to the aggregated selected features from both tables."""
        try:
            self.refs = [
                selected["id"]
                for selected in (
                    self.table_existing.selected + self.table_candidates.selected
                )
            ]
        except Exception as e:
            logger.exception("Error while updating references: %s", e)
            ui.notify("Fehler bei Aktualisierung der Referenzen", type="negative")

    async def _on_tab_change(self, e: events.ValueChangeEventArguments):
        """Deferred loading of DB features and table initialisation via tab change event."""
        match e.value:
            case "existing":
                if self.ref_objects is None:
                    self.table_existing.props("loading")
                    self.ref_objects = await run.io_bound(get_ref_objects, self.refs)
                    self.table_existing.update_rows(self.ref_objects)
                    self.table_existing.selected = self.ref_objects
                    self.table_existing.props(
                        f":selected-rows-label='(numberOfRows) => `${{ numberOfRows }} von {len(self.ref_objects)} Referenzen selektiert`'"
                    )
                    self.table_existing.props(remove="loading")
            case "candidates":
                if self.ref_candidates is None:
                    self.table_candidates.props("loading")
                    self.ref_candidates = await run.io_bound(
                        get_ref_candidates,
                        self.refs,
                        app.storage.client["plan_id"],
                        app.storage.client["form"].model,
                        self.rel,
                    )
                    self.table_candidates.update_rows(self.ref_candidates)
                    self.table_candidates.props(
                        f":selected-rows-label='(numberOfRows) => `${{ numberOfRows }} von {len(self.ref_candidates)} Referenzen selektiert`'"
                    )
                    self.table_candidates.props(remove="loading")

    def _create_table(self) -> ui.table:
        """Creates a table with adequate columns, props and event handlers."""
        columns = [
            {
                "name": "id",
                "label": "Identifikator",
                "field": "id",
                "align": "left",
                "sortable": True,
            },
            {
                "name": "featuretype",
                "label": "Objektart",
                "field": "featuretype",
                "align": "left",
                "sortable": True,
            },
            {
                "name": "updated",
                "label": "letzte Aktualisierung",
                "field": "updated",
                "align": "left",
                "sortable": True,
            },
            {
                "name": "extra_property",
                "label": "Selektionskriterium",
                "field": "extra_property",
                "align": "left",
                "sortable": True,
                "classes": "hidden",
                "headerClasses": "hidden",
            },
        ]
        table = (
            ui.table(
                rows=[],
                columns=columns,
                selection="multiple",
            )
            .props(
                """
                no-data-label='keine passenden Features vorhanden'
                no-results-label='keine passenden Ergebnisse gefunden'
                flat
                square
                dense
                virtual-scroll
            """
            )
            .classes("w-full h-full")
        )
        if form := app.storage.client["form"]:
            # use existing bind method to enable/disable selection
            table.bind_visibility_from(
                form,
                "editable",
                backward=lambda editable, table=table: table.props(
                    f"selection={'none' if not editable else 'multiple'}"
                ),
            )
        table.on("row-click", self._on_row_click)
        table.on_select(self._on_select)
        with table.add_slot("top"):
            search = (
                ui.input("Filter")
                .bind_value(table, "filter")
                .tooltip("über alle Spalten nach Ausdruck filtern")
                .props("clearable square dense")
                .classes("w-64")
            )
            with search.add_slot("prepend"):
                ui.icon("filter_list")
            ui.space()
            ui.checkbox(
                "Selektionskriterium",
                on_change=lambda e, table=table: (
                    table.columns[-1].update(
                        {
                            "classes": "" if e.value else "hidden",
                            "headerClasses": "" if e.value else "hidden",
                        }
                    ),
                    table.update(),
                ),
            ).tooltip(
                "aktiviert eine zusätzliche Spalte mit einem ggf. definierten Selektionskriterium"
            )
        return table
