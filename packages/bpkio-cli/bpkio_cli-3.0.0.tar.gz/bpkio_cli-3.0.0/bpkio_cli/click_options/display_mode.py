import functools

import cloup
from cloup import option, option_group

from bpkio_cli.display.display_mode import DisplayMode


def display_mode_options(fn):
    @option_group(
        "Display Options",
        option(
            "--raw",
            is_flag=True,
            default=False,
            help="Get the raw content, unchanged",
        ),
        option(
            "--highlight",
            is_flag=True,
            default=False,
            help="Display the content with syntax highlighting. This is the default mode.",
        ),
        option(
            "--diff",
            is_flag=True,
            default=False,
            help="Display the diff between the current and previous content",
        ),
        option(
            "--table",
            is_flag=True,
            default=False,
            help="Show key information in tabular format",
        ),
        option(
            "--tree",
            is_flag=True,
            default=False,
            help="Display content in a tree structure",
        ),
        option(
            "--timeline",
            is_flag=True,
            default=False,
            help="Display a timeline representation of the content",
        ),
        option(
            "--quiet",
            is_flag=True,
            default=False,
            help="Do not display any content",
        ),
        constraint=cloup.constraints.mutually_exclusive,
    )
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        # Determine the display_mode based on flags
        raw = kwargs.pop("raw", False)
        table = kwargs.pop("table", False)
        tree = kwargs.pop("tree", False)
        timeline = kwargs.pop("timeline", False)
        highlight = kwargs.pop("highlight", False)
        diff = kwargs.pop("diff", False)
        quiet = kwargs.pop("quiet", False)
        display_mode = DisplayMode.HIGHLIGHT  # Set a default mode

        # Priority: RAW > TABLE > TREE
        if raw:
            display_mode = DisplayMode.RAW
        elif table:
            display_mode = DisplayMode.TABLE
        elif tree:
            display_mode = DisplayMode.TREE
        elif timeline:
            display_mode = DisplayMode.TIMELINE
        elif highlight:
            display_mode = DisplayMode.HIGHLIGHT
        elif diff:
            display_mode = DisplayMode.DIFF
        elif quiet:
            display_mode = DisplayMode.QUIET

        kwargs["display_mode"] = display_mode

        return fn(*args, **kwargs)

    return wrapper
