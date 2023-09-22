import boto3
from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Horizontal
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import ContentSwitcher, Header, TabbedContent, TabPane

from ..commands import RegionCommands
from ..components import Footer, Logo, SearchableList, ServiceList


class MainScreen(Screen):
    COMMANDS = {RegionCommands}
    CSS = """
        .main-screen-container {
            margin: 1 0;
        }

        .main-screen-service-select {
            width: 30;
            # margin: 1 20;
            border: round rgb(255,255,255) 30%;
        }
        .main-screen-lists-container {
            width: 90;
            height: auto;
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
        with TabbedContent(initial="welcome") as self.tabbed_content:
            with TabPane("Welcome", id="welcome"):
                with Center(classes="main-screen-container"):
                    yield Logo()
                    with Horizontal(classes="main-screen-lists-container"):
                        yield SearchableList(
                            "Profile", self.get_available_profiles, classes="main-screen-service-select"
                        )
                        yield SearchableList("Region", self.get_available_regions, classes="main-screen-service-select")
                        yield SearchableList(
                            "Services", self.get_available_services, classes="main-screen-service-select"
                        )
                        # yield SearchableList(
                        #     "Reesource", self.get_available_resources, classes="main-screen-service-select"
                        # )
                        # yield ServiceList(classes="main-screen-service-select")
        yield Footer()

    def on_mount(self) -> None:
        self._footer = self.query_one(Footer)
        self._footer.profile_name = self._session.profile_name
        self._footer.region_name = self._session.region_name
        self._footer.set_session_info(self._profile_name, self._region_name, self._service_name)
        self._content_switcher = self.tabbed_content.get_child_by_type(ContentSwitcher)

    def get_available_regions(self) -> list[SearchableList.ItemDatum]:
        regions = self._session.get_available_regions("cloudformation")
        return [SearchableList.ItemDatum(title=region, id=region) for region in regions]

    def get_available_profiles(self) -> list[SearchableList.ItemDatum]:
        profiles = self._session.available_profiles
        return [SearchableList.ItemDatum(title=profile, id=profile) for profile in profiles]

    def get_available_resources(self) -> list[SearchableList.ItemDatum]:
        resources = self._session.get_available_resources()
        return [SearchableList.ItemDatum(title=resource, id=resource) for resource in resources]

    def get_available_services(self) -> list[SearchableList.ItemDatum]:
        services = self._session.get_available_services()
        return [SearchableList.ItemDatum(title=service, id=service) for service in services]

    @on(RegionCommands.Selected)
    def handle_profile_selected(self, message: RegionCommands.Selected) -> None:
        self._region_name = message.region_name
        self._session = boto3.Session(profile_name=self._profile_name, region_name=self._region_name)
        self._footer.set_session_info(self._profile_name, self._region_name, self._service_name)

    @on(ServiceList.Selected)
    def handle_service_selected(self, message: ServiceList.Selected) -> None:
        self._service_name = message.service_name
        self._footer.set_session_info(self._profile_name, self._region_name, self._service_name)
        try:
            service_pane = self._content_switcher.get_child_by_id(self._service_name, TabPane)
        except NoMatches:
            service_pane = TabPane(self._service_name.title(), id=self._service_name)
            self.tabbed_content.add_pane(service_pane)
        self.tabbed_content.active = self._service_name
        self.tabbed_content.show_tab(self._service_name)
