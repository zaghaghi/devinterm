from textual import on
from textual.app import App

from .components import ProfileList
from .screens import MainScreen


class AWSConsole(App):
    CSS_PATH = "app.tcss"
    TITLE = "AWS In Term"

    def on_mount(self) -> None:
        self.push_screen(MainScreen())


def main():
    app = AWSConsole()
    app.run()


if __name__ == "__main__":
    main()
