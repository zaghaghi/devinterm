from textual import on
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer

from ..components import ProfileList


class ProfileScreen(Screen):
    def compose(self) -> ComposeResult:
        yield ProfileList()
        yield Footer()
