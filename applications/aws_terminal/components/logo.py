from rich.console import RenderableType
from rich.text import Text
from textual.widgets import Static


class Logo(Static):
    DEFAULT_CSS = """
        Logo {
            height: 5;
            width: 90;
            # color: $secondary 60%;
        }
    """

    def render(self) -> RenderableType:
        before = " " * 5
        lines: list[Text] = []
        lines.append(Text(before + "    _____  __      __  _________   .___         ___________                    \n"))
        lines.append(Text(before + "   /  _  \/  \    /  \/   _____/   |   | ____   \__    ___/__________  _____   \n"))
        lines.append(Text(before + "  /  /_\  \   \/\/   /\_____  \    |   |/    \    |    |_/ __ \_  __ \/     \  \n"))
        lines.append(Text(before + " /    |    \        / /        \   |   |   |  \   |    |\  ___/|  | \/  Y Y  \ \n"))
        lines.append(Text(before + "/_____|____/\__/\__/ /_________/   |___|___| _/   |____| \____ |__|  |__|_|__/ \n"))
        colors = ["#B86B00", "#CF7E00", "#E7920D", "#FEA62B", "#FFBA41", "#FFCF56", "#FFE46B"]
        colors.reverse()
        for idx, line in enumerate(lines):
            line.stylize(colors[idx])
        return Text.assemble(*lines)
