import logging

from nicegui.observables import ObservableSet
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased, selectinload
from xplan_tools.interface.db import DBRepository
from xplan_tools.model import model_factory
from xplan_tools.model.base import BaseFeature
from xplan_tools.model.orm import Feature, Refs

from xmas_app.settings import get_mappings, get_settings

logger = logging.getLogger(__name__)


def get_db_feature_ids(
    repo: DBRepository,
    typenames: str | list | None = None,
    featuretype_regex: str | None = None,
    value_prop: str | None = None,
) -> dict:
    """
    Query the database for features matching the provided type(s) or regex, and
    return a mapping from feature IDs to label (from `value_prop`) or a fallback string.

    Args:
        repo (DBRepository): The database repository instance.
        typenames (str | list | None): Single typename or list of typenames to filter on.
        featuretype_regex (str | None): Optional regex to match featuretype.
        value_prop (str | None): The property to use for the label in the result dict.

    Returns:
        dict: Mapping from stringified feature ID to label or fallback.
    """
    logger.info("Entered db.get_db_feature_ids().")
    results = {}
    try:
        with repo.Session() as session:
            stmt = select(Feature)
            if typenames:
                names_list = [typenames] if isinstance(typenames, str) else typenames
                stmt = stmt.where(Feature.featuretype.in_(names_list))
                logger.info(f"Filtering for typenames: {names_list}")
            if featuretype_regex:
                stmt = stmt.where(Feature.featuretype.regexp_match(featuretype_regex))
                logger.info(f"Filtering with regex: {featuretype_regex}")
            try:
                db_result = session.execute(stmt)
                features = db_result.unique().scalars().all()
                logger.info(f"Found {len(features)} feature(s) in DB.")
            except Exception as db_ex:
                logger.error(f"Database query failed: {db_ex}", exc_info=True)
                return {}

            for feature in features:
                label = None
                try:
                    label = (
                        feature.properties.get(value_prop, None) if value_prop else None
                    )
                except Exception as prop_ex:
                    logger.warning(
                        f"Error accessing properties of feature ID {feature.id}: {prop_ex}",
                        exc_info=True,
                    )
                key = str(feature.id)
                value = label if label else f"{feature.featuretype}::{feature.id}"
                results[key] = value

    except Exception as ex:
        logger.error(f"Failed to get feature IDs: {ex}", exc_info=True)
        raise
    return results


def get_db_plans() -> list[dict]:
    """Get plan data from the database.

    Query the database for plan objects.

    Returns:
        list[dict]: List of dicts containing plan data, i.e. name, id, appschema, version, last update.
    """
    results = []
    try:
        with get_settings().repo.Session() as session:
            stmt = select(Feature).where(Feature.featuretype.regexp_match("^.*Plan$"))
            try:
                db_result = session.execute(stmt)
                features = db_result.unique().scalars().all()
                logger.info(f"Found {len(features)} feature(s) in DB.")
            except Exception as db_ex:
                logger.error(f"Database query failed: {db_ex}", exc_info=True)
            for feature in features:
                plan_data = {
                    "id": str(feature.id),
                    "label": feature.properties.get("name", "<Name unbekannt>"),
                    "appschema": {
                        "name": feature.appschema.upper(),
                        "version": feature.version,
                    },
                    "updated": {
                        "date": f"{feature.updated_at.strftime('%m.%d.%Y')}",
                        "time": f"{feature.updated_at.strftime('%H:%M:%S Uhr')}",
                    },
                }
                results.append(plan_data)

    except Exception as ex:
        logger.error(f"Failed to get plan data: {ex}", exc_info=True)
        raise
    return results


def delete_db_association(base_id: str, related_id: str, repo: DBRepository):
    try:
        with repo.Session() as session:
            stmt = text("""
                DELETE FROM public.refs
                WHERE base_id = :base_id AND related_id = :related_id
            """)
            try:
                result = session.execute(
                    stmt, {"base_id": base_id, "related_id": related_id}
                )
                session.commit()
                logger.info(
                    f"Deleted {result.rowcount} record(s) from public.refs with base_id={base_id} and related_id={related_id}"
                )
                return {"deleted_rows": result.rowcount}
            except SQLAlchemyError as db_ex:
                session.rollback()
                logger.error(f"Database delete failed: {db_ex}", exc_info=True)
                return {"error": str(db_ex)}
    except Exception as ex:
        logger.error(f"Failed to delete association: {ex}", exc_info=True)
        raise


def get_nodes(
    id: str, features_set: ObservableSet
) -> tuple[dict, str, str, str] | None:
    def build_node(feature: Feature, path: str) -> dict:
        features_set.add(feature.id)
        node = {
            "id": f"{path}.{feature.featuretype}.{feature.id}",
            "label": f"{feature.featuretype} {str(feature.id)[:8]}",
            "icon": get_icon(feature),
        }
        node["children"] = build_nodes(feature)
        return node

    def build_nodes(feature: Feature) -> list[dict]:
        model = model_factory(feature.featuretype, feature.version, feature.appschema)
        node_dict = {}
        for assoc in model.get_associations():
            prop_info = model.get_property_info(assoc)
            if prop_info["assoc_info"]["source_or_target"] == (
                "target"
                if (feature.featuretype == "FP_Plan" and assoc == "bereich")
                or (feature.featuretype == "FP_Bereich" and assoc == "gehoertZuPlan")
                else "source"
            ):
                continue
            node = {
                "id": f"{feature.featuretype}.{feature.id}.{assoc}",
                "label": assoc,
                "selectable": True,
                "icon": "link",
            }
            node_dict[assoc] = node
        for ref in feature.refs:
            path = ".".join(
                [
                    feature.featuretype,
                    str(feature.id),
                    ref.rel,
                ]
            )
            node = build_node(ref.feature_inv, path)
            node_dict[ref.rel].setdefault("children", []).append(node)

        nodes = []
        for node in node_dict.values():
            if children := node.get("children"):
                node["label"] += f" [{len(children)}]"
            nodes.append(node)
        return nodes

    def get_icon(feature: Feature):
        match feature.geometry_type:
            case "polygon":
                icon = "o_space_dashboard"
            case "line":
                icon = "show_chart"
            case "point":
                icon = "o_location_on"
            case _:
                icon = "o_text_snippet"
        return icon

    with get_settings().repo.Session() as session:
        stmt = (
            select(Feature)
            .options(
                selectinload(Feature.refs)
                .selectinload(Refs.feature_inv)
                .selectinload(Feature.refs)
                .selectinload(Refs.feature_inv)
                .selectinload(Feature.refs)
            )
            .where(Feature.id == id)
        )

        feature = session.execute(stmt).scalar_one_or_none()
        # feature = session.get(Feature, id)
        if not feature or "Plan" not in feature.featuretype:
            return

        features_set.add(feature.id)

        tree_nodes = [
            {
                "id": feature.id,
                "label": feature.properties["name"],
                "selectable": False,
                "children": build_nodes(feature),
            }
        ]

        return (
            tree_nodes,
            feature.featuretype,
            feature.id,
            feature.appschema,
        )


def _feature_to_table_row(feature: Feature) -> dict:
    extra_property = getattr(
        get_mappings().association_table.extra_properties, feature.appschema
    ).get(feature.featuretype)
    extra_property_label = feature.properties.get(extra_property, "N/A")
    return {
        "id": str(feature.id),
        "featuretype": feature.featuretype,
        "geometry_type": feature.geometry_type,
        "updated": f"{feature.updated_at.strftime('%m.%d.%Y')} {feature.updated_at.strftime('%H:%M:%S')}",
        "extra_property": f"{extra_property}={extra_property_label}"
        if extra_property
        else "N/A",
    }


def _rel_inv_is_list(feature: Feature, rel_inv: str | None) -> bool:
    # if there is no inverse relation, return True
    if not rel_inv:
        return True
    model = model_factory(feature.featuretype, feature.version, feature.appschema)
    return model.get_property_info(rel_inv)["list"]


def get_ref_objects(refs: list[str]) -> list[dict]:
    """Returns a list of data objects for existing feature references to use in table rows."""
    with get_settings().repo.Session() as session:
        stmt = select(Feature).where(Feature.id.in_(refs))
        features = session.execute(stmt).scalars().all()

    return [_feature_to_table_row(feature) for feature in features]


def get_ref_candidates(
    refs: list[str], plan_id: str, model: BaseFeature, rel: str
) -> list[dict]:
    """Returns a list of data objects for potential feature references to use in table rows."""
    prop_info = model.get_property_info(rel)
    typename = prop_info["typename"]
    featuretypes = typename if isinstance(typename, list) else [typename]
    rel_inv = model.get_property_info(rel)["assoc_info"]["reverse"]

    with get_settings().repo.Session() as session:
        # collect all plan features while applying WHERE clauses to filter on the DB side
        Plan = aliased(Feature, name="plan")
        DirectFeature = aliased(Feature, name="direct_feature")
        IndirectFeature = aliased(Feature, name="indirect_feature")

        RefPlanDirect = aliased(Refs, name="ref_plan_direct")
        RefDirectIndirect = aliased(Refs, name="ref_direct_indirect")
        direct = (
            select(DirectFeature)
            .select_from(Plan)
            .join(RefPlanDirect, RefPlanDirect.base_id == Plan.id)
            .join(DirectFeature, DirectFeature.id == RefPlanDirect.related_id)
            .where(Plan.id == plan_id)
            .where(DirectFeature.featuretype.in_(featuretypes))
            .where(DirectFeature.id.not_in(refs))
        )

        indirect = (
            select(IndirectFeature)
            .select_from(Plan)
            .join(RefPlanDirect, RefPlanDirect.base_id == Plan.id)
            .join(DirectFeature, DirectFeature.id == RefPlanDirect.related_id)
            .join(RefDirectIndirect, RefDirectIndirect.base_id == DirectFeature.id)
            .join(IndirectFeature, IndirectFeature.id == RefDirectIndirect.related_id)
            .where(Plan.id == plan_id)
            .where(IndirectFeature.featuretype.in_(featuretypes))
            .where(IndirectFeature.id.not_in(refs))
        )
        stmt = direct.union(indirect)

        candidates = (
            session.execute(select(Feature).from_statement(stmt)).scalars().all()
        )
        return [
            _feature_to_table_row(feature)
            for feature in candidates
            if _rel_inv_is_list(feature, rel_inv)
        ]
