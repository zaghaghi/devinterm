import asyncio

import boto3
from textual import work
from textual.app import ComposeResult
from textual.containers import Center, VerticalScroll
from textual.message import Message
from textual.widgets import Input, OptionList, Static
from textual.widgets.option_list import Option

PROFILE_LIST_INLINE_CSS = """
    #search {
        background: $panel;
        margin: 0 0;
        border: round rgb(255,255,255) 30%;
        width: 60%;
        max-width: 80;
    }

    #search > .input--cursor {
        background: $panel;
        color: rgb(0,0,0) 0%;
        text-style: u;
    }

    #profiles {
        min-height: 5;
        background: $panel;
        border: none;
    }
    
    #profiles > .option-list--option-highlighted {
        background: $secondary;
    }
    #profiles > .option-list--option-hover {
        background: $secondary-darken-3;
    }
    #profiles > .option-list--option-hover-highlighted {
        background: $secondary-lighten-1;
    }

    #profiles:focus {
        border: none;
    }

    #profiles-container {
        width: 60%;
        max-width: 80;
        overflow: hidden auto;
        border: round rgb(255,255,255) 30%;
        scrollbar-background: $panel;
        scrollbar-background-hover: $panel;
        scrollbar-background-active: $panel;
        scrollbar-color: rgb(255,255,255) 50%;
        scrollbar-color-hover: rgb(255,255,255) 70%;
        scrollbar-color-active: rgb(255,255,255) 30%;
        scrollbar-size-vertical: 1;
        max-height: 8;
    }

    #select-container {
        align: right middle;
    }

    #select-btn {
        height: 3;
    }

"""


class ProfileList(Static):
    DEFAULT_CSS = PROFILE_LIST_INLINE_CSS

    class Selected(Message):
        def __init__(self, profile_name: str) -> None:
            self.profile_name = profile_name
            super().__init__()

    def compose(self) -> ComposeResult:
        input = Input(placeholder="Search", id="search")
        with Center(id="profiles-center-container"):
            yield input
            with VerticalScroll(id="profiles-container"):
                yield OptionList(id="profiles")

    def on_mount(self) -> None:
        self.input = self.query_one("#search", Input)
        self.input.focus()
        self.option_list = self.query_one("#profiles", OptionList)
        self.option_list.clear_options()
        self.option_list.add_options([Option(str(i)) for i in range(10)])
        self.find_available_profiles("")

    @work(exclusive=True)
    async def find_available_profiles(self, word: str) -> None:
        session = boto3.Session()
        self.option_list.clear_options()
        for profile in session.available_profiles:
            self.option_list.add_option(Option(profile))

    async def on_option_list_option_selected(self, message: OptionList.OptionSelected) -> None:
        selected_profile = message.option.prompt
        self.input.value = selected_profile
        self.post_message(self.Selected(selected_profile))
