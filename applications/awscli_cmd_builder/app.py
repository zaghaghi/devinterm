from textual import work
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Input, OptionList
from textual.widgets.option_list import Option

from .aws import AWS_CLI_COMPLETER
from .style import CSS


class AWSCommandBuilderApp(App):
    CSS = CSS

    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        input = Input(value="", id="command")
        input.border_title = "aws"
        yield input

        with VerticalScroll(id="results-container"):
            yield OptionList(id="results")

    def on_mount(self) -> None:
        self.input = self.query_one("#command", Input)
        self.input.focus()
        self.option_list = self.query_one("#results", OptionList)
        self.global_args = AWS_CLI_COMPLETER["aws"]["args"]
        self.services = AWS_CLI_COMPLETER["aws"]["commands"]
        self.show_completer_result("")

    async def on_input_changed(self, message: Input.Changed) -> None:
        """A coroutine to handle a text changed message."""
        self.show_completer_result(message.value)

    @work(exclusive=True)
    async def show_completer_result(self, word: str) -> None:
        options = ["pishpil", "kishpil", str(self.input.cursor_width)]
        # options = self.completer.complete(completer_word)
        # if not options and completer_word.endswith(" "):
        #     options = self.completer.complete(f"{completer_word} --")
        if not options:
            rows = [Option("Nothing to show!", disabled=True)]
        else:
            rows = [Option(opt) for opt in options]
        self.option_list.clear_options()
        self.option_list.add_options(rows)

    async def on_option_list_option_selected(self, message: OptionList.OptionSelected) -> None:
        self.input.value = self.input.value + message.option.prompt + " "
        self.input.focus()


if __name__ == "__main__":
    app = AWSCommandBuilderApp()
    app.run()
