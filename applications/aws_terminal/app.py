from textual import on
from textual.app import App

from .components import ProfileList
from .screens import MainScreen


class AWSConsole(App):
    CSS_PATH = "app.tcss"
    TITLE = "AWS In Term"

    def on_mount(self) -> None:
        self.push_screen(MainScreen(profile_name="admin_development"))

    @on(ProfileList.Selected)
    def handle_profile_selected(self, message: ProfileList.Selected) -> None:
        profile_name = message.profile_name
        self.push_screen(MainScreen(profile_name=profile_name))


def main():
    app = AWSConsole()
    app.run()


if __name__ == "__main__":
    main()
