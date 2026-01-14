from urllib.parse import parse_qs, urlparse

from rich.style import Style
from rich.text import Text
from rich.console import Console
from rich.theme import Theme

theme = Theme(
    {
        "id": "yellow",
        "date": "bold magenta",
        "date2": "magenta",
        "dur": "cyan",
        "lang": "green",
        "codec": "cyan",
        "url": "yellow italic",
        "index": "bold black",
        "count": "bold blue",
    }
)
console = Console(theme=theme, force_terminal=True)


class RichColorizer:
    @staticmethod
    def status(text):
        # colorize HTTP status codes
        status = int(text)
        if status == 200:
            return Text(str(text), style="bold green")
        elif status == 202:
            return Text(str(text), style="bold yellow")
        elif status >= 201 and status < 300:
            return Text(str(text), style="bold cyan")
        elif status >= 300 and status < 400:
            return Text(str(text), style="bold magenta")
        elif status >= 400 and status < 500:
            return Text(str(text), style="bold red")
        else:
            return Text(str(text), style="bold white")

    @staticmethod
    def url(url, spaces=True, highlight=True, safe=True):
        styles = {
            "protocol": "white",
            "host": "bold magenta",
            "path": "yellow",
            "path_highlight": "yellow reverse italic",
            "key": "cyan",
            "value": "bright_blue",
            "fragment": "blue",
            "separator": "white dim",
        }

        strings = []
        parsed = urlparse(url)

        # protocol and host
        if parsed.scheme:
            strings.append(
                Text(parsed.scheme + "://", style=Style.parse(styles["protocol"]))
            )
        if parsed.netloc:
            strings.append(Text(parsed.netloc, style=Style.parse(styles["host"])))

        # path
        path_parts = parsed.path.split("/")

        # find index of the part to highlight
        if highlight:
            highlight_index = len(path_parts) - 1
            for i, part in enumerate(path_parts):
                if part == "bpk-sst":
                    highlight_index = i - 1
                    break
        else:
            highlight_index = -1

        for i, part in enumerate(path_parts):
            if i == highlight_index:
                strings.append(
                    Text(
                        part,
                        style=Style.parse(styles["path_highlight"]),
                    )
                )
            else:
                strings.append(Text(part, style=Style.parse(styles["path"])))

            if i < len(path_parts) - 1:
                strings.append(Text("/", style=Style.parse(styles["separator"])))

        # query params
        qs = parse_qs(parsed.query, keep_blank_values=False, strict_parsing=False)
        for i, (k, v) in enumerate(qs.items()):
            separator = "?" if i == 0 else "&"
            if spaces:
                separator = " " + separator + " "
            strings.append(Text(separator, style=Style.parse(styles["separator"])))
            strings.append(
                Text(
                    k,
                    style=Style.parse(styles["key"]),
                )
            )
            strings.append(Text("=", style=Style.parse(styles["separator"])))
            if safe:
                v = [x.replace(" ", "+") for x in v]

            strings.append(Text(v[0], style=Style.parse(styles["value"])))

        if parsed.fragment:
            strings.append(
                Text(
                    "#" + parsed.fragment,
                    style=Style.parse(styles["separator"] + styles["fragment"]),
                )
            )

        # Combine all Text objects into a single Text object
        combined_text = Text.assemble(*strings)
        return combined_text
