from nicegui import ui


class LabelWithDescription(ui.label):
    def __init__(self, text: str, tooltip=str | None):
        super().__init__(text)
        self.classes(
            "underline underline-offset-2 decoration-1 decoration-dotted cursor-help"
        )
        with self:
            ui.tooltip(tooltip or "").classes("text-sm").props(
                "anchor='center middle' self='center left'"
            )
