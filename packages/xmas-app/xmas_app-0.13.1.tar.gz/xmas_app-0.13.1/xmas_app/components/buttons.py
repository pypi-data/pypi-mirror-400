import json
import logging
from typing import Literal, get_args

from nicegui import events, ui

logger = logging.getLogger("xmas_app")


class FeatureInteractionButton(ui.button):
    """Generic Button to interact with QGIS features via QWebchannel."""

    action_types = Literal["highlight_feature", "show_attribute_form", "select_feature"]
    type_map = {
        "highlight_feature": {"text": "Zum Feature springen", "icon": "o_pageview"},
        "show_attribute_form": {
            "text": "Attributformular öffnen",
            "icon": "list_alt",
        },
        "select_feature": {"text": "Feature selektieren", "icon": "select_all"},
    }

    def __init__(
        self,
        action_type: action_types,
        target: str,
        source: str | None = None,
        geom: bool = True,
    ):
        """Button initialization.

        Args:
            type: the specific action to initialize the button for
            target: the ID of the target feature
            source: the ID of the source feature
            geom: whether the feature has a geometry
        Raises:
            ValueError: if the type is unknown
        """
        if action_type not in get_args(self.action_types):
            raise ValueError(f"invalid type: '{action_type}'")
        self.action_type = action_type
        self.source = source
        self.target = target
        super().__init__(**self.type_map[action_type], on_click=self._on_click)
        self.props("flat square no-caps align=left")
        self.classes("w-full")
        if not geom:
            self.disable()
            self.tooltip("Keine Geometrie")

    async def _on_click(self, _: events.ClickEventArguments):
        try:
            logger.debug("Sending %s request to QWebChannel handler", self.action_type)
            data = json.dumps({"source": self.source, "target": self.target})
            ui.run_javascript(f"""new QWebChannel(qt.webChannelTransport, function (channel) {{
                                        channel.objects.handler.{self.action_type}({data})
                                }});""")
        except Exception as e:
            logger.exception(
                "Exception while %s was called: %s", self.action_type, str(e)
            )
