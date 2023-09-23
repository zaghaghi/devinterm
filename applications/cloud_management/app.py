from textual.app import App

from .screens import MainScreen


class CloudManagementConsole(App):
    CSS_PATH = "app.tcss"
    TITLE = "Cloud Management In Terminal"

    def on_mount(self) -> None:
        self.push_screen(MainScreen())


def main():
    app = CloudManagementConsole()
    app.run()


if __name__ == "__main__":
    main()
