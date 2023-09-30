from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import ContentSwitcher, Header, TabbedContent, TabPane

from ..components import Footer
from ..models import ServicePath
from ..pages import CloudFormation, Welcome
from ..strings import AWS_SERVICE_MAP


class MainScreen(Screen):
    CSS = """
        TabPane {
            padding: 0 0;
        }
    """
    BINDINGS = [
        Binding("ctrl+g", "open_service", "Open Service", show=True),
    ]

    SERVICE_PAGE_MAP = {"cloudformation": CloudFormation}
    WELCOME_PAGE_ID = "welcome"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial=self.WELCOME_PAGE_ID) as self.tabbed_content:
            with TabPane("Welcome", id=self.WELCOME_PAGE_ID):
                yield Welcome()
        self._footer = Footer()
        yield self._footer

    def on_mount(self) -> None:
        self._content_switcher = self.tabbed_content.get_child_by_type(ContentSwitcher)
        self._service_path_index: dict[str, ServicePath] = {}

    @on(Welcome.ServicePathChanged)
    def handle_service_path_changed(self, message: Welcome.ServicePathChanged) -> None:
        self._service_path_index[self.WELCOME_PAGE_ID] = message.service_path.clone()
        self.set_footer_service_path(message.service_path)

    @on(TabbedContent.TabActivated)
    def handle_tab_activates(self, message: TabbedContent.TabActivated) -> None:
        active_tab_service_path = self._service_path_index.get(message.tab.id)
        if not active_tab_service_path:
            return
        self.set_footer_service_path(active_tab_service_path)

    def action_open_service(self) -> None:
        service_path = self._service_path_index.get(self.WELCOME_PAGE_ID)
        if not service_path or not service_path.completed:
            self.notify("Select profile, region and service first.")
            return
        _ = self.get_or_create_service_pane(service_path)

    def get_or_create_service_pane(self, service_path: ServicePath) -> TabPane | None:
        try:
            service_pane = self._content_switcher.get_child_by_id(service_path.id, TabPane)
        except NoMatches:
            service_title = AWS_SERVICE_MAP.get(service_path.service_name, {}).get("name", service_path.service_name)
            service_page = self.SERVICE_PAGE_MAP.get(service_path.service_name)
            if not service_page:
                self.notify("Can't find a page for the selected service.")
                return None
            self._service_path_index[service_path.id] = service_path.clone()
            service_pane = TabPane(service_title, service_page(service_path), id=service_path.id)
            self.tabbed_content.add_pane(service_pane)

        self.tabbed_content.active = service_path.id
        self.tabbed_content.show_tab(service_path.id)
        return service_pane

    def set_footer_service_path(self, service_path: ServicePath) -> None:
        self._footer.session.profile_name = service_path.profile_name
        self._footer.session.region_name = service_path.region_name
        self._footer.session.service_name = service_path.service_name
