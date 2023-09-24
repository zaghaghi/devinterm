from typing import Any

import boto3
from botocore.exceptions import SSOTokenLoadError, UnauthorizedSSOTokenError
from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Label, OptionList, Static
from textual.widgets.option_list import Option, Separator

from ..models import ServicePath


class StackOption(Option):
    def __init__(self, stack_summary: dict[str, Any], id: str | None = None, disabled: bool = False) -> None:
        stack_name = stack_summary.get("StackName", "NoName!")
        stack_status = stack_summary.get("StackStatus", "NO_STATUS")
        status_status_color = (
            ("dark_green" if stack_status.endswith("_COMPLETE") else None)
            or ("dark_orange3" if stack_status.endswith("_IN_PROGRESS") else None)
            or ("dark_red" if stack_status.endswith("_FAILED") else None)
        )
        prompt = Text.assemble(
            Text(f"{stack_name}\n", style="bold"),
            Text(stack_status, style=status_status_color),
            no_wrap=True,
            overflow="ellipsis",
        )
        super().__init__(prompt, id, disabled)


class CloudFormation(Static):
    DEFAULT_CSS = """
        CloudFormation {
            # background: green;
        }

        .main-container {
            padding: 0 0;
        }

        .stack-list-container {
            border: round rgb(255,255,255) 30%;
            width: 1fr;
            # min-width: 10;
            # background: blue;
            margin: 0 0;
        }

        .stack-details-container {
            border: round rgb(255,255,255) 30%;
            width: 4fr;
            # background: red;
            margin: 0 0;
        }
    """

    def __init__(self, service_path: ServicePath, **kwargs) -> None:
        super().__init__(**kwargs)
        if not service_path.completed or service_path.service_name != "cloudformation":
            raise ValueError("Invalid service path len")
        self._service_path = service_path
        self._session = boto3.Session(profile_name=service_path.profile_name, region_name=service_path.region_name)
        self._client = self._session.client(service_path.service_name)

    def compose(self) -> ComposeResult:
        with Horizontal(classes="main-container"):
            with VerticalScroll(classes="stack-list-container"):
                self._option_list = OptionList(id="stack-list")
                yield self._option_list
            with VerticalScroll(classes="stack-details-container"):
                yield Label("Stack Details")

    def on_mount(self) -> None:
        # self.mock_list_stacks()
        self.list_stacks()

    @work(exclusive=True, thread=True)
    def list_stacks(self) -> None:
        try:
            response = self._client.list_stacks()
        except SSOTokenLoadError:
            self.notify(f"Error loading {self._service_path.profile_name} profile SSO token.", severity="error")
            return
        except UnauthorizedSSOTokenError:
            self.notify(f"Unauthorized {self._service_path.profile_name} profile SSO token.", severity="error")
            return
        except Exception:
            self.notify("Can't get list of stacks.", severity="error")
            return

        self.update_option_list(response.get("StackSummaries", []))

    @work(exclusive=True, thread=True)
    def mock_list_stacks(self) -> None:
        example_response = {
            "StackSummaries": [
                {"StackName": "Stack1 from developers who love long names", "StackStatus": "UPDATE_COMPLETE"},
                {"StackName": "Stack2", "StackStatus": "ROLLBACK_IN_PROGRESS"},
                {"StackName": "Stack3", "StackStatus": "UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS"},
                {"StackName": "Stack4", "StackStatus": "CREATE_FAILED"},
            ]
        }
        self.update_option_list(example_response.get("StackSummaries", []))

    def update_option_list(self, stack_summaries: dict[str, Any]) -> None:
        self._option_list.clear_options()
        options = []
        for idx, stack_summary in enumerate(stack_summaries):
            if stack_summary.get("StackStatus") == "DELETE_COMPLETE":
                continue
            if idx > 0:
                options.append(Separator())
            options.append(StackOption(stack_summary))

        self._option_list.add_options(options)
