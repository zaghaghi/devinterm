from textual import on
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widgets import Input, OptionList
from textual.widgets.option_list import Option

from .components import ProfileList
from .screens import MainScreen, ProfileScreen


class AWSConsole(App):
    CSS_PATH = "app.tcss"

    def on_mount(self) -> None:
        self.push_screen(ProfileScreen())

    @on(ProfileList.Selected)
    def handle_profile_selected(self, message: ProfileList.Selected) -> None:
        profile_name = message.profile_name
        self.push_screen(MainScreen(profile_name=profile_name))


def main():
    app = AWSConsole()
    app.run()


if __name__ == "__main__":
    main()
