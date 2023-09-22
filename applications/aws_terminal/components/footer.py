import boto3
from rich.text import Text
from textual.app import ComposeResult, RenderResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static


class FooterSession(Static):
    profile_name: reactive[str] = reactive("")
    region_name: reactive[str] = reactive("")
    service_name: reactive[str] = reactive("")
    DEFAULT_CSS = """
        FooterSession {
            padding: 0 1;
        }

    """

    def render(self) -> RenderResult:
        available_items = [item for item in [self.profile_name, self.region_name, self.service_name] if item]
        session_line = " 〉".join(available_items)
        return Text(session_line, no_wrap=True, overflow="ellipsis")


class FooterInfo(Widget):
    DEFAULT_CSS = """
        FooterInfo {
            padding: 0 1;
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
        Footer > FooterSession {
            dock: left;
            width: 50%;
            content-align: left middle;
        }
        Footer > FooterInfo {
            dock: right;
            width: 50%;
            content-align: right middle;
        }
    """

    def compose(self) -> ComposeResult:
        self.info = FooterInfo()
        self.session = FooterSession()
        yield self.info
        yield self.session
