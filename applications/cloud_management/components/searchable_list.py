from dataclasses import dataclass
from typing import Callable

from textual import on, work
from textual.app import ComposeResult
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Input, Label, ListItem, ListView, Static

SEARCHABLE_LIST_INLINE_CSS = """
    #search {
        background: $panel;
        margin: 0 0;
        border: none;
        border-bottom: solid rgb(255,255,255) 30%;
    }

    #items-list {
        background: $panel;
        height: 5;
        scrollbar-background: $panel;
        scrollbar-background-hover: $panel;
        scrollbar-background-active: $panel;
        scrollbar-color: rgb(255,255,255) 50%;
        scrollbar-color-hover: rgb(255,255,255) 70%;
        scrollbar-color-active: $secondary 70%;
        scrollbar-size-vertical: 1;
        max-height: 8;
        border-title-align: center;
    }

    .list-view-item {
        padding: 0 1;
        width: 100%;
    }

    #items-list > .list-view--item-selected {
        background: $secondary;
    }

    #items-list > .list-view--item-not-selected {
        background: $panel;
    }

    #items-list > .list-view--item-highlighted {
        background: $secondary-background;
    }

    #items-list > .list-view--item-highlighted.list-view--item-selected {
        background: $secondary;
    }

    Label.footer {
        content-align: right middle;
        color: white 20%;
        width: 100%;
        padding: 0 1;
    }
"""


class SearchableList(Static, can_focus_children=True):
    DEFAULT_CSS = SEARCHABLE_LIST_INLINE_CSS

    footer: reactive[str] = reactive("")

    @dataclass
    class ItemDatum:
        title: str
        id: str
        user_data: dict | None = None

    class Selected(Message):
        def __init__(self, list: "SearchableList", item: "SearchableList.ItemDatum") -> None:
            self.item = item
            self.list = list
            super().__init__()

        @property
        def control(self) -> "SearchableList":
            return self.list

    def __init__(self, search_placeholder: str, item_factory: Callable[[], list[ItemDatum]], **kwargs) -> None:
        super().__init__(**kwargs)
        self._item_factory = item_factory
        self._search_placeholder = search_placeholder

    def compose(self) -> ComposeResult:
        self._search_input = Input(placeholder=self._search_placeholder, id="search")
        self._list_view = ListView(id="items-list")
        yield self._search_input
        yield self._list_view
        self._footer_label = Label(self.footer, classes="footer")
        yield self._footer_label

    def on_mount(self) -> None:
        self.compose_items()

    @on(ListView.Highlighted)
    def handle_item_highlighted(self, message: ListView.Highlighted) -> None:
        self.fix_highlighted_classes(message)

    @on(ListView.Selected)
    def handle_item_selected(self, message: ListView.Selected) -> None:
        self.fix_selected_classes(message)
        selected_item = self._items_index.get(message.item.id)
        if selected_item:
            self.post_message(self.Selected(self, selected_item))

    def fix_selected_classes(self, message: ListView.Selected) -> None:
        if not message.item:
            return
        for item in message.list_view.children:
            item.remove_class("list-view--item-selected")
            item.add_class("list-view--item-not-selected")
        message.item.remove_class("list-view--item-not-selected")
        message.item.add_class("list-view--item-selected")

    def fix_highlighted_classes(self, message: ListView.Highlighted) -> None:
        if not message.item:
            return
        for item in message.list_view.children:
            item.remove_class("list-view--item-highlighted")
        message.item.add_class("list-view--item-highlighted")

    @work(exclusive=True)
    async def compose_items(self) -> None:
        self._items = self._item_factory()
        self._items_index = {item.id: item for item in self._items}
        self.update_items(self._items)

    async def on_input_changed(self, message: Input.Changed) -> None:
        """A coroutine to handle a text changed message."""
        self.filter_items(message.value)

    @work(exclusive=True)
    async def filter_items(self, word: str) -> None:
        filtered_items = (
            [item for item in self._items if word.lower().strip() in item.title.lower()]
            if word.strip()
            else self._items
        )
        self.update_items(filtered_items)

    def update_items(self, items: list["SearchableList.ItemDatum"]) -> None:
        self._list_view.clear()
        for item in items:
            self._list_view.append(
                ListItem(
                    Label(item.title, classes="list-view-item"), id=item.id, classes="list-view--item-not-selected"
                )
            )
        self._footer_label.update(f"{len(items)}/{len(self._items)}")
