import boto3
from rich.text import Text
from textual.app import ComposeResult, RenderResult
from textual.reactive import reactive
from textual.widget import Widget


class FooterSession(Widget):
    profile_name: reactive[str] = reactive("")
    region_name: reactive[str] = reactive("")
    service_name: reactive[str] = reactive("S3")
    DEFAULT_CSS = """
        FooterSession {
            dock: left;
            padding: 0 1;
            width: 50%;
            content-align: left middle;
        }

    """

    def render(self) -> RenderResult:
        return Text(f"{self.profile_name} 〉{self.region_name} 〉{self.service_name}", no_wrap=True, overflow="ellipsis")


class FooterInfo(Widget):
    DEFAULT_CSS = """
        FooterInfo {
            dock: right;
            padding: 0 1;
            width: 50%;
            content-align: right middle;
        }
    """

    def render(self) -> RenderResult:
        return Text(f"SDK: v{boto3.__version__}", no_wrap=True, overflow="ellipsis")


class Footer(Widget):
    DEFAULT_CSS = """
        Footer {
            dock: bottom;
            height: 1;
            width: 100%;
            background: $secondary-background;
        }
    """

    def compose(self) -> ComposeResult:
        yield FooterInfo()
        yield FooterSession()

    def set_session_info(self, profile_name: str, region_name: str, service_name: str) -> None:
        self.query_one(FooterSession).profile_name = profile_name
        self.query_one(FooterSession).region_name = region_name
        self.query_one(FooterSession).service_name = service_name
