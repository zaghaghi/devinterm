from textual import on
from textual.app import ComposeResult
from textual.message import Message
from textual.widgets import Input, Label, ListItem, ListView, Static

SERVICE_LIST_INLINE_CSS = """
    #search {
        background: $panel;
        margin: 0 0;
        border: none;
        border-bottom: solid rgb(255,255,255) 30%;
    }

    #service-list {
        background: $panel;
        height: 5;
        # border: round rgb(255,255,255) 30%;
        scrollbar-background: $panel;
        scrollbar-background-hover: $panel;
        scrollbar-background-active: $panel;
        scrollbar-color: rgb(255,255,255) 50%;
        scrollbar-color-hover: rgb(255,255,255) 70%;
        scrollbar-color-active: rgb(255,255,255) 30%;
        scrollbar-size-vertical: 1;
        max-height: 8;
        border-title-align: center;
    }

    .components-service-item {
        padding: 0 1;
        width: 100%;
    }

    #service-list > .list-view--item-highlighted {
        background: $secondary;
    }

    #service-list > .list-view--item-not-highlighted {
        background: $panel;
    }
"""


class ServiceList(Static):
    DEFAULT_CSS = SERVICE_LIST_INLINE_CSS

    class Selected(Message):
        def __init__(self, service_name: str) -> None:
            self.service_name = service_name
            super().__init__()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._service_list = {
            "s3": "S3",
            "cloudformation": "CloudFormation",
            "ecs": "Elastic Container Service",
            "logs": "CloudWatch",
            "lambda": "Lambda Functions",
            "cloudmap": "CloudMap",
        }

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search", id="search")
        yield ListView(
            *(
                ListItem(Label(value, classes="components-service-item"), id=key)
                for key, value in self._service_list.items()
            ),
            classes="components-service-list",
            id="service-list",
        )

    def on_mount(self) -> None:
        list_view = self.query_one("#service-list", ListView)
        list_view.focus()

    @on(ListView.Highlighted)
    def handle_item_highlighted(self, message: ListView.Highlighted) -> None:
        for item in message.list_view.children:
            item.remove_class("list-view--item-highlighted")
            item.add_class("list-view--item-not-highlighted")
        message.item.remove_class("list-view--item-not-highlighted")
        message.item.add_class("list-view--item-highlighted")

    @on(ListView.Selected)
    def handle_item_selected(self, message: ListView.Selected) -> None:
        self.post_message(self.Selected(message.item.id))
