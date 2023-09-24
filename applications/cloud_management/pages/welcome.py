import boto3
from rich.console import RenderableType
from textual import on
from textual.app import ComposeResult
from textual.containers import Center, Horizontal
from textual.message import Message
from textual.widgets import Static

from ..components import Logo, SearchableList
from ..models import ServicePath
from ..strings import AWS_REGION_MAP, AWS_SERVICE_MAP

WELCOME_DEFAULT_CSS = """
    .main-screen-container {
        margin: 1 0;
    }

    .main-screen-lists-container {
        width: 90;
        height: auto;
    }

    .main-screen-list-select {
        width: 30;
        border: round rgb(255,255,255) 30%;
    }

    .main-screen-list-select:focus-within {
        border: round $secondary 60%;
    }


    #current-selection-session {
        width: 90;
        height: 1;
    }

    #help {
        width: 90;
        color: $text 40%;
        text-align: center;
    }
"""


class Help(Static):
    def render(self) -> RenderableType:
        return (
            "Select profile, region and service, "
            "then click [@click='screen.open_service()']here[/] or press [Ctrl+G] "
            "to open service."
        )


class Welcome(Static):
    DEFAULT_CSS = WELCOME_DEFAULT_CSS

    class ServicePathChanged(Message):
        def __init__(self, service_path: ServicePath) -> None:
            self.service_path = service_path
            super().__init__()

    class ServiceOpen(Message):
        def __init__(self, list: "SearchableList", item: "SearchableList.ItemDatum") -> None:
            self.item = item
            self.list = list
            super().__init__()

        @property
        def control(self) -> "SearchableList":
            return self.list

    def compose(self) -> ComposeResult:
        with Center(classes="main-screen-container"):
            yield Logo()
            yield Help(id="help")
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

    def on_mount(self) -> None:
        self._service_path = ServicePath()

    def get_available_regions(self) -> list[SearchableList.ItemDatum]:
        return [
            SearchableList.ItemDatum(title=f"{region} ({data.get('name')})", id=region)
            for region, data in AWS_REGION_MAP.items()
        ]

    def get_available_profiles(self) -> list[SearchableList.ItemDatum]:
        session = boto3.Session()
        profiles = session.available_profiles
        return [SearchableList.ItemDatum(title=profile, id=profile) for profile in profiles]

    def get_available_services(self) -> list[SearchableList.ItemDatum]:
        return [
            SearchableList.ItemDatum(title=data.get("name", service), id=service, user_data=data)
            for service, data in AWS_SERVICE_MAP.items()
        ]

    @on(SearchableList.Selected)
    def handle_list_item_selected(self, message: SearchableList.Selected) -> None:
        list_id = message.control.id
        if list_id == "profile-list":
            self._service_path.profile_name = message.item.id
        elif list_id == "region-list":
            self._service_path.region_name = message.item.id
        elif list_id == "service-list":
            self._service_path.service_name = message.item.id
        else:
            ...
        if self._service_path.completed:
            self.post_message(self.ServicePathChanged(self._service_path))
