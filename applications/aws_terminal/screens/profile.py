from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header

from ..components import ProfileList


class ProfileScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ProfileList()
