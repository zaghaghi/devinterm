import boto3
from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Horizontal
from textual.screen import Screen
from textual.widgets import ContentSwitcher, Header, TabbedContent, TabPane

from ..components import Footer, Logo, SearchableList
from ..components.footer import FooterSession


class MainScreen(Screen):
    CSS = """
        .main-screen-container {
            margin: 1 0;
        }

        .main-screen-list-select {
            width: 30;
            # margin: 1 20;
            border: round rgb(255,255,255) 30%;
        }
        .main-screen-list-select:focus-within {
            border: round $secondary 60%;
        }
        .main-screen-lists-container {
            width: 90;
            height: auto;
        }

        #current-selection-session {
            width: 90;
            height: 1;
            # content-align: center middle;
        }
    """

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="welcome") as self.tabbed_content:
            with TabPane("Welcome", id="welcome"):
                with Center(classes="main-screen-container"):
                    yield Logo()
                    with Horizontal(classes="main-screen-lists-container"):
                        yield SearchableList(
                            "Profile",
                            self.get_available_profiles,
                            id="profile-list",
                            classes="main-screen-list-select",
                        )
                        yield SearchableList(
                            "Region", self.get_available_regions, id="region-list", classes="main-screen-list-select"
                        )
                        yield SearchableList(
                            "Services",
                            self.get_available_services,
                            id="service-list",
                            classes="main-screen-list-select",
                        )
                    self._footer_session = FooterSession(id="current-selection-session")
                    yield self._footer_session
        self._footer = Footer()
        yield self._footer

    def on_mount(self) -> None:
        self._content_switcher = self.tabbed_content.get_child_by_type(ContentSwitcher)

    def get_available_regions(self) -> list[SearchableList.ItemDatum]:
        session = boto3.Session()
        regions = session.get_available_regions("cloudformation")
        return [SearchableList.ItemDatum(title=region, id=region) for region in regions]

    def get_available_profiles(self) -> list[SearchableList.ItemDatum]:
        session = boto3.Session()
        profiles = session.available_profiles
        return [SearchableList.ItemDatum(title=profile, id=profile) for profile in profiles]

    def get_available_services(self) -> list[SearchableList.ItemDatum]:
        return [SearchableList.ItemDatum(title="CloudFormation", id="cloudformation", user_data={})]

    @on(SearchableList.Selected)
    def handle_list_item_selected(self, message: SearchableList.Selected) -> None:
        list_id = message.control.id
        if list_id == "profile-list":
            self._footer.session.profile_name = message.item.title
            self._footer_session.profile_name = message.item.title
        elif list_id == "region-list":
            self._footer.session.region_name = message.item.title
            self._footer_session.region_name = message.item.title
        elif list_id == "service-list":
            self._footer.session.service_name = message.item.title
            self._footer_session.service_name = message.item.title
        else:
            ...
