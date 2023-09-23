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
        pad = " " * 4
        lines: list[Text] = []

        lines.append(Text(pad + "_________ .__                   .___  .___         ___________                   \n"))
        lines.append(Text(pad + "\_   ___ \|  |   ____  __ __  __| _/  |   | ____   \__    ___/__________  _____  \n"))
        lines.append(Text(pad + "/    \  \/|  |  /  _ \|  |  \/ __ |   |   |/    \    |    |/ ___ \_  __ \/     \ \n"))
        lines.append(Text(pad + "\     \___|  |_(  <_> )  |  / /_/ |   |   |   |  \   |    |\  ___/|  | \/  Y Y  \\\n"))
        lines.append(Text(pad + " \________/____/\____/|____/\_____|   |___|___| _/   |____| \___  |__|  |__|_|__/\n"))

        colors = ["#B86B00", "#CF7E00", "#E7920D", "#FEA62B", "#FFBA41", "#FFCF56", "#FFE46B"]
        colors.reverse()
        for idx, line in enumerate(lines):
            line.stylize(colors[idx])
        return Text.assemble(*lines)
