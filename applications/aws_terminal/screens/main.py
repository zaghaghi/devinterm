from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Label


class MainScreen(Screen):
    def __init__(
        self,
        profile_name: str,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self._profile_name = profile_name

    def compose(self) -> ComposeResult:
        if self._profile_name:
            yield Label(self._profile_name)
        else:
            yield Label("NONE")
        yield Footer()
