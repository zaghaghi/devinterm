from typing import Any

import boto3
from botocore.exceptions import SSOTokenLoadError, UnauthorizedSSOTokenError
from rich.text import Text
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import DataTable, Label, OptionList, Pretty, Static, TabbedContent, TabPane
from textual.widgets.option_list import Option, Separator

from ..models import ServicePath


class StackOption(Option):
    def __init__(self, stack_summary: dict[str, Any], id: str | None = None, disabled: bool = False) -> None:
        self.stack_summary = stack_summary
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

    @property
    def stack_name(self) -> str:
        return self.stack_summary.get("StackName", "NoName!")

    @property
    def stack_status(self) -> str:
        return self.stack_summary.get("StackStatus", "NO_STATUS")

    @property
    def stack_id(self) -> str | None:
        return self.stack_summary.get("StackId")


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
            margin: 0 0;
        }
        # DataTable {
        #     background: red;
        #     height: 100%;
        #     width: 100%;
        # }
        TabPane.stack-tab-pane {
            height: 1fr;
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
                with TabbedContent() as self.tabbed_content:
                    with TabPane("Properties", id="properties", classes="stack-tab-pane"):
                        self.properties_table = DataTable(name="properties", id="properties-table")
                        self.properties_table.add_columns("Name", "Value")
                        yield self.properties_table
                    with TabPane("Parameters", id="parameters", classes="stack-tab-pane"):
                        self.parameters_table = DataTable(name="parameters", id="parameters-table")
                        self.parameters_table.add_columns("Key", "Value", "Resolved Valued")
                        yield self.parameters_table
                    with TabPane("Outputs", id="outputs", classes="stack-tab-pane"):
                        self.outputs_table = DataTable(name="Outputs", id="outputs-table")
                        self.outputs_table.add_columns("Key", "Value", "Description", "Export Name")
                        yield self.outputs_table
                    with TabPane("Tags", id="tags", classes="stack-tab-pane"):
                        self.tags_table = DataTable(name="Tags", id="tags-table")
                        self.tags_table.add_columns("Key", "Value")
                        yield self.tags_table
                    with TabPane("Events", id="events", classes="stack-tab-pane"):
                        yield Label("Events")
                    with TabPane("Resources", id="resources", classes="stack-tab-pane"):
                        yield Label("Resources")
                    with TabPane("Response", id="response", classes="stack-tab-pane"):
                        yield Pretty({})

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

    @work(exclusive=True, thread=True)
    def describe_stacks(self, stack_id: str) -> dict[str, Any]:
        try:
            response = self._client.describe_stacks(StackName=stack_id)
            return response
        except Exception:
            self.notify("Can't get stack information", severity="error")
            return {}

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

    @on(OptionList.OptionSelected)
    async def handle_selected_stack(self, message: OptionList.OptionSelected) -> None:
        if not isinstance(message.option, StackOption):
            return
        stack_desc = await self.describe_stacks(message.option.stack_id).wait()
        self.update_stack_details(stack_desc)

    def update_stack_details(self, stacks_description: dict[str, Any]) -> None:
        self.properties_table.clear()
        self.parameters_table.clear()
        self.outputs_table.clear()
        self.tags_table.clear()

        stacks = stacks_description.get("Stacks")
        if not stacks:
            return
        stack = stacks[0]

        fields = ["StackName", "CreationTime", "LastUpdatedTime", "StackStatus", "RoleARN"]
        self.properties_table.add_rows((field, stack.get(field, "")) for field in fields)

        fields = ["ParameterKey", "ParameterValue", "ResolvedValue"]
        for parameter in stack.get("Parameters", []):
            self.parameters_table.add_row(*(parameter.get(field, "") for field in fields))

        fields = ["OutputKey", "OutputValue", "Description", "ExportName"]
        for output in stack.get("Outputs", []):
            self.outputs_table.add_row(*(output.get(field, "") for field in fields))

        fields = ["Key", "Value"]
        for tag in stack.get("Tags", []):
            self.tags_table.add_row(*(tag.get(field, "") for field in fields))

        self.query_one(Pretty).update(stacks_description)
