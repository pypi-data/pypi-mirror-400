import logging
from uuid import UUID

from fastapi import HTTPException
from nicegui import run
from pydantic import ValidationError
from xplan_tools.model import model_factory

from xmas_app.models.crud import InsertPayload, UpdatePayload
from xmas_app.settings import get_settings

logger = logging.getLogger("xmas_app")


async def create(payload: InsertPayload, plan_id: str):
    """Create features in the database.

    Iterates over data items in the payload and validates them with pydantic.

    For non-geometry aka text features, the corresping plan is updated to have
    a reference to the new text feature so that there are no orphans in the db.

    If everything is valid, the features and feature update are saved to the database.
    """
    logger.debug(
        "Processing create payload for plan with ID '%s': %s", plan_id, payload
    )
    features = []
    feature_updates = []
    errors = []
    for item in payload.root:
        try:
            featuretype = model_factory(item.featuretype, item.version, item.appschema)
            geom_field = featuretype.get_geom_field()
            properties = item.properties
            properties.pop("featuretype", None)
            if item.geometry:
                properties[geom_field] = item.geometry
            feature = featuretype.model_validate(properties)
            features.append(feature)
            # if feature has geom_field, i.e. it's not a text feature, continue
            if geom_field:
                continue
            # else add unidirectional reference from corresponding plan to text feature
            try:
                plan = get_settings().repo.get(plan_id)
            except Exception as e:
                logger.exception("failed to load plan: %s", e)
            else:
                for assoc in plan.get_associations():
                    prop_info = plan.get_property_info(assoc)
                    ref = getattr(plan, "assoc", [] if prop_info["list"] else "")
                    if item.featuretype not in prop_info["typename"]:
                        continue
                    feature_uuid = UUID(feature.id)
                    if feature_uuid in ref:
                        continue
                    if isinstance(ref, list):
                        ref.append(feature_uuid)
                    else:
                        ref = feature_uuid
                    setattr(plan, assoc, ref)
                    break
                feature_updates.append(plan)

        except ValidationError as e:
            errors.append(e.errors())
    if errors:
        raise HTTPException(
            status_code=422,
            detail=errors,
        )
    try:
        await run.io_bound(get_settings().repo.save_all, features)
        if feature_updates:
            await run.io_bound(get_settings().repo.update_all, feature_updates)
    except Exception as e:
        logger.exception("Exception occured while saving features to db: %s", e)
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


async def update(payload: UpdatePayload):
    """Update features in the database.

    Iterates over data items in the payload and updates existing features with them.

    The update data is validated with pydantic.

    If everything is valid, the features are saved to the database.
    """
    logger.debug("Processing update payload: %s", payload)
    features = []
    errors = []
    for id, item in payload.root.items():
        feature = await run.io_bound(get_settings().repo.get, str(id))
        update = item.properties
        if item.geometry:
            update[feature.get_geom_field()] = item.geometry
        data = feature.model_dump() | update
        try:
            feature = feature.model_validate(data)
            features.append(feature)
        except ValidationError as e:
            errors.append(e.errors())
    if errors:
        raise HTTPException(
            status_code=422,
            detail=errors,
        )
    try:
        await run.io_bound(get_settings().repo.update_all, features)
    except Exception as e:
        logger.exception("Exception occured while updating features in db: %s", e)
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
