import functools

import click
from cloup import option, option_group


def dash_options(fn):
    @option_group(
        "DASH MPD filters",
        option(
            "--level",
            "mpd_level",
            help="Level of information to display. 1=Period, 2=AdaptationSet, 3=Representation, 4=Segment Info, 5=Segments",
            type=int,
            default=None,
            callback=validate_level,
        ),
        option(
            "--period",
            "mpd_period",
            help="Extract one or multiple periods (accepts a single index, a period id, or a range of them in the format 'x:y'. "
            "The first period has index 1, use negative numbers to count from the end)",
            default=None,
        ),
        option(
            "--adapt",
            "--adapset",
            "--adaptation-set",
            "--adaptset",
            "mpd_adaptation_set",
            help="Extract specific adaptation sets (by id, or partial match on mimetype, content type)",
            default=None,
        ),
        option(
            "--repr",
            "--representation",
            "mpd_representation",
            help="Extract one or multiple representations (accepts a single index, or a range in the format 'x:y'. "
            "The first representation has index 1, use negative numbers to count from the end)",
            default=None,
        ),
        option(
            "--segments",
            "mpd_segments",
            help="Extract just the first and last N segments of each period",
            default=None,
            type=int,
        ),
        option(
            "--events/--no-events",
            "mpd_events",
            is_flag=True,
            help="Extract events from the MPD",
            default=True,
        ),
    )
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper


def validate_level(ctx, param, value):
    if value is None:
        if ctx.params.get("tree"):
            return 3
        else:
            return 5
    if value not in range(1, 6):
        raise click.BadParameter(f"'{value}' is not a valid level")
    return value
