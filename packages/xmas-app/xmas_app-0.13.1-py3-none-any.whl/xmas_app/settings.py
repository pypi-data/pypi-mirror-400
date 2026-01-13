import os
from functools import cached_property, lru_cache
from pathlib import Path
from typing import Dict, List, Literal, Optional, TypedDict

from pydantic import HttpUrl
from pydantic_extra_types.semver import _VersionPydanticAnnotation
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)
from semver import Version
from xplan_tools.interface.db import DBRepository

from xmas_app.models.mappings import AssociationTableMapping


class AppSchema(TypedDict):
    type: str
    versions: List[str]


APPSCHEMAS: Dict[str, AppSchema] = {
    "XPlanung": {"type": "xplan", "versions": ["5.4", "6.0", "6.1"]},
    "XTrasse": {"type": "xtrasse", "versions": ["2.0"]},
}


def get_appschema(schema_type: str, version: str):
    try:
        name = next(
            filter(
                lambda key: APPSCHEMAS[key]["type"] == schema_type, APPSCHEMAS.keys()
            )
        )
        if version not in APPSCHEMAS[name]["versions"]:
            raise ValueError(f"Invalid version for Appschema {name}")
    except (StopIteration, ValueError):
        return None
    else:
        return f"{name} {version}"


class Settings(BaseSettings):
    debug: bool = False

    PGUSER: Optional[str] = None
    PGPASSWORD: Optional[str] = None
    PGHOST: Optional[str] = None
    PGPORT: Optional[str] = None
    PGDATABASE: Optional[str] = None
    PGSERVICE: Optional[str] = None

    appschema: Literal["xplan", "xtrasse"]
    appschema_version: Literal["2.0", "5.4", "6.0", "6.1"]
    app_port: int
    db_type: str = "postgres"  # defaulting to postgres
    app_mode: Literal["dev", "prod"] = "prod"
    srid: int = 25832
    codelist_repo: HttpUrl = HttpUrl(
        "https://registry.gdi-de.org/codelist/de.xleitstelle.xplanung"
    )
    qgis_plugin_name: str = "XMAS-Plugin"
    qgis_plugin_min_version: _VersionPydanticAnnotation = Version(major=0, minor=15)
    mappings_toml: str = str(Path(__file__).parent / "resources/mappings.toml")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @cached_property
    def repo(self):
        """Set environment variable, initialize and return repo."""
        os.environ.update(
            self.model_dump(
                include={
                    "PGUSER",
                    "PGHOST",
                    "PGPASSWORD",
                    "PGPORT",
                    "PGDATABASE",
                    "PGSERVICE",
                },
                exclude_none=True,
            )
        )
        return DBRepository(
            "postgresql://",
            srid=self.srid,
            with_views=True,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


class Mappings(BaseSettings):
    association_table: AssociationTableMapping

    model_config = SettingsConfigDict(toml_file=get_settings().mappings_toml)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)


@lru_cache
def get_mappings() -> Mappings:
    return Mappings()
