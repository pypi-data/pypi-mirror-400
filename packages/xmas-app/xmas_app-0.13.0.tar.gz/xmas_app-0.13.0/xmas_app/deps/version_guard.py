from fastapi import Header, HTTPException
from semver import format_version, parse

from xmas_app.settings import get_settings


async def enforce_plugin_version(
    user_agent: str = Header(...),
):
    if (
        not user_agent.startswith(get_settings().qgis_plugin_name)
        or get_settings().app_mode == "dev"
    ):
        return
    try:
        _, plugin_version = user_agent.split("/")
        client_v = parse(plugin_version)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {get_settings().qgis_plugin_name} user-agent header: '{user_agent}'",
        )

    if client_v < get_settings().qgis_plugin_min_version:
        # 426 Upgrade Required is appropriate
        raise HTTPException(
            status_code=426,
            detail=f"Plugin version {get_settings().qgis_plugin_min_version}+ required, got {format_version(**client_v)}",
        )
