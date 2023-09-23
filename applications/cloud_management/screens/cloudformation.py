import boto3
from textual import on
from textual.app import ComposeResult
from textual.containers import Center
from textual.screen import Screen
from textual.widgets import Header, Label

from ..commands import RegionCommands
from ..components import Footer, Logo, ServiceList


class CloudformationScreen(Screen):
    COMMANDS = {RegionCommands}
    CSS = """
        .main-screen-container {
            margin: 1 0;
        }

        .main-screen-service-select {
            width: 40;
            margin: 1 20;
            border: round rgb(255,255,255) 30%;
        }
    """

    def __init__(
        self,
        profile_name: str,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self._profile_name = profile_name
        self._session = boto3.Session(profile_name=profile_name)
        self._region_name = self._session.region_name
        self._service_name = ""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Center(classes="main-screen-container"):
            yield Label("Welcome to")
            yield Logo()
            yield ServiceList(classes="main-screen-service-select")
        yield Footer()

    def on_mount(self) -> None:
        self._footer = self.query_one(Footer)
        self._footer.profile_name = self._session.profile_name
        self._footer.region_name = self._session.region_name
        self._footer.set_session_info(self._profile_name, self._region_name, self._service_name)

    def get_available_regions(self) -> list[str]:
        regions = self._session.get_available_regions(self._service_name)
        return regions

    @on(RegionCommands.Selected)
    def handle_profile_selected(self, message: RegionCommands.Selected) -> None:
        self._region_name = message.region_name
        self._session = boto3.Session(profile_name=self._profile_name, region_name=self._region_name)
        self._footer.set_session_info(self._profile_name, self._region_name, self._service_name)

    @on(ServiceList.Selected)
    def handle_service_selected(self, message: ServiceList.Selected) -> None:
        self._service_name = message.service_name
        self._footer.set_session_info(self._profile_name, self._region_name, self._service_name)
