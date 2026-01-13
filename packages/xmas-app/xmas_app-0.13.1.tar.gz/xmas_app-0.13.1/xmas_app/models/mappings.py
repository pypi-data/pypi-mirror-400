from pydantic import BaseModel


class ExtraProperties(BaseModel):
    xplan: dict[str, str] = {}
    xtrasse: dict[str, str] = {}


class AssociationTableMapping(BaseModel):
    extra_properties: ExtraProperties
