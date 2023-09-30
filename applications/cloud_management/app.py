import argparse

from textual.app import App, CSSPathType
from textual.driver import Driver

from .models import ServicePath
from .screens import MainScreen, StandaloneScreen


class CloudManagementConsole(App):
    CSS_PATH = "app.tcss"
    TITLE = "Cloud Management In Terminal"

    def __init__(
        self,
        initial_service_path: ServicePath,
        driver_class: type[Driver] | None = None,
        css_path: CSSPathType | None = None,
        watch_css: bool = False,
    ):
        super().__init__(driver_class, css_path, watch_css)
        self._initial_service_path = initial_service_path

    def on_mount(self) -> None:
        if self._initial_service_path.completed:
            self.push_screen(StandaloneScreen(self._initial_service_path))
        else:
            self.push_screen(MainScreen())


def parse_arguments() -> ServicePath:
    parser = argparse.ArgumentParser(prog="CloudInTerm", description="Cloud management in terminal")
    parser.add_argument("-p", "--profile", help="profile name", default=None)
    parser.add_argument("-r", "--region", help="region name", default=None)
    parser.add_argument("-s", "--service", help="service name", default=None)
    args = parser.parse_args()
    return ServicePath(profile_name=args.profile, region_name=args.region, service_name=args.service)


def main():
    app = CloudManagementConsole(parse_arguments())
    app.run()


if __name__ == "__main__":
    main()
