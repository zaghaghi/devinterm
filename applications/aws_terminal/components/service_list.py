from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static


class ServiceList(Static):
    def compose(self) -> ComposeResult:
        yield Static(" Windows ", id="title")
        yield Static("Press any key to continue [blink]_[/]", id="any-key")
