from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header

from ..components import Footer
from ..models import ServicePath
from ..pages import CloudFormation


class StandaloneScreen(Screen):
    SERVICE_PAGE_MAP = {"cloudformation": CloudFormation}

    def __init__(
        self, service_path: ServicePath, name: str | None = None, id: str | None = None, classes: str | None = None
    ) -> None:
        super().__init__(name, id, classes)
        self.service_path = service_path
        self.service_page = self.SERVICE_PAGE_MAP.get(service_path.service_name)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield self.service_page(self.service_path)
        self._footer = Footer()
        yield self._footer

    def on_mount(self) -> None:
        self.set_footer_service_path(self.service_path)

    def set_footer_service_path(self, service_path: ServicePath) -> None:
        self._footer.session.profile_name = service_path.profile_name
        self._footer.session.region_name = service_path.region_name
        self._footer.session.service_name = service_path.service_name
