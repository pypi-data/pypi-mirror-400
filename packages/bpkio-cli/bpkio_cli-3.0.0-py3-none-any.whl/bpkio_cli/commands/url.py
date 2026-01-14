import datetime
import json as j
import os
import time
from typing import List, Optional

import click
import cloup
from bpkio_api.helpers.source_type import SourceTypeDetector
from bpkio_api.models.Sources import SourceStatusCheck, SourceType
from media_muncher.handlers import ContentHandler, factory
from media_muncher.handlers.dash import DASHHandler
from media_muncher.handlers.hls import HLSHandler
from pydantic import HttpUrl, parse_obj_as
from rich.progress import Progress

import bpkio_cli.click_mods.resource_commands as bic_res_cmd
import bpkio_cli.click_options as bic_options
from bpkio_cli.click_options.options import parse_options
from bpkio_cli.commands.misc.compatibility_check import check_compatibility
from bpkio_cli.commands.source_check import display_source_status
from bpkio_cli.commands.sources import create as source_create
from bpkio_cli.core.app_context import AppContext
from bpkio_cli.core.config_provider import CONFIG
from bpkio_cli.core.exceptions import BroadpeakIoCliError
from bpkio_cli.display.display_mode import DisplayMode
from bpkio_cli.monitor.live_monitor import monitor_hls
from bpkio_cli.plot.plotly_timelines import MpdTimelinePlotter, SubplotInfo
from bpkio_cli.utils.httpserver import LocalHTTPServer
from bpkio_cli.utils.profile_maker import make_transcoding_profile
from bpkio_cli.utils.url_builders import ask_for_user_agent
from bpkio_cli.writers.breadcrumbs import display_error
from bpkio_cli.writers.colorizer import Colorizer as CL
from bpkio_cli.writers.content_display import display_content
from bpkio_cli.writers.players import StreamPlayer


def determine_source_type(full_url) -> SourceType | None:
    source_type = SourceTypeDetector.determine_source_type(full_url)
    if not source_type:
        click.secho(
            "Could not determine the type of source for that URL", fg="red", bold="true"
        )
        return None
    else:
        return source_type


def get_handler(
    sub: int | None = None, user_agent: str | None = None, headers: List[str] = []
) -> ContentHandler:
    ctx = click.get_current_context()
    url = ctx.obj.resource_chain.last_key()

    # if the url is a valid path to a local file, we create an HTTP server.
    # TODO: Move this to media_muncher
    if not url.startswith("http"):
        if not (os.path.isfile(url) and os.path.exists(url)):
            raise BroadpeakIoCliError(
                f"URL '{url}' is not a valid URL or path to a local file"
            )
        folder = os.path.dirname(url)
        ctx.obj.local_server = LocalHTTPServer(directory=folder)
        ctx.obj.local_server.start()
        url = ctx.obj.local_server.get_server_url(os.path.basename(url))

    if user_agent == "SELECT":
        ask_for_user_agent(url)

    handler: ContentHandler = factory.create_handler(
        url,
        user_agent=CONFIG.get_user_agent(user_agent),
        explicit_headers=headers,
    )

    if not sub:
        return handler
    else:
        if handler.has_children():
            return handler.get_child(sub)
        else:
            if not isinstance(handler, DASHHandler):
                click.secho(
                    "`--sub` cannot be used with this source, as it has no children URLs. Using main URL instead",
                    fg="red",
                )
            return handler


# Group: URLs
@bic_res_cmd.group(help="Work directly with URLs", resource_type=HttpUrl)
@cloup.argument(
    "url_str",
    help=("The URL to work with"),
    metavar="<url>",
)
@click.pass_obj
def url(obj: AppContext, url_str: str):
    try:
        full_url = parse_obj_as(HttpUrl, url_str)
    except Exception:
        full_url = url_str
    obj.resource_chain.add_resource(url_str, full_url)
    obj.cache.record(full_url)


# --- INFO Commmand
@bic_res_cmd.command(
    aliases=["content"],
    help="Get detailed information about the content of a URL",
    is_default=True,
)
@bic_options.url()
def info(url: str, header: List[str], user_agent: str, **kwargs):
    handler = get_handler(None, user_agent, header)

    if handler:
        try:
            display_content(
                handler=handler,
                max=1,
                interval=0,
                display_mode=DisplayMode.TABLE,
                trim=0,
            )
        except BroadpeakIoCliError as e:
            pass


# Command: CHECK
@bic_res_cmd.command(help="Checks the type and validity of a URL")
@click.option(
    "--full", help="Provide the full detail (in JSON)", is_flag=True, default=False
)
@click.pass_obj
def check(obj: AppContext, full: bool, **kwargs):
    full_url = obj.resource_chain.last_key()
    source_type = determine_source_type(full_url)

    click.secho("This appears to be a source of type: %s" % source_type.value)

    if source_type:
        result = obj.api.sources.check(
            type=source_type, body=SourceStatusCheck(url=full_url)
        )

        display_source_status(obj, result, as_json=full)


# --- READ Command
@bic_res_cmd.command(
    help="Loads and displays the content of a URL"
    ", optionally highlighted with relevant information"
)
@bic_options.display_mode
@bic_options.read
@bic_options.url()
@bic_options.dash
@bic_options.save
def read(
    sub: int,
    display_mode: DisplayMode,
    top: bool,
    tail: bool,
    pager: bool,
    ad_pattern: str,
    user_agent: str,
    header: List[str],
    trim: int,
    output_directory: str = None,
    **kwargs,
):
    handler = get_handler(sub, user_agent, header)

    display_content(
        handler=handler,
        max=1,
        interval=0,
        display_mode=display_mode,
        top=top,
        tail=tail,
        pager=pager,
        trim=trim,
        ad_pattern=ad_pattern,
        output_directory=output_directory,
        **kwargs,
    )


# --- POLL Command
@bic_res_cmd.command(help="Similar to `read`, but regularly re-load the URL's content")
@bic_options.display_mode
@bic_options.read
@bic_options.url()
@bic_options.poll
@bic_options.save
@bic_options.dash
def poll(
    sub: int,
    user_agent: str,
    header: List[str],
    max: int,
    interval: Optional[int],
    top: bool,
    tail: bool,
    pager: bool,
    clear: bool,
    display_mode: DisplayMode,
    silent: bool,
    trim: int,
    ad_pattern: str,
    output_directory: str,
    **kwargs,
):
    if not sub:
        sub = 1

    handler = get_handler(sub, user_agent, header)

    display_content(
        handler=handler,
        max=max,
        interval=interval,
        display_mode=display_mode,
        top=top,
        tail=tail,
        pager=pager,
        clear=clear,
        silent=silent,
        trim=trim,
        ad_pattern=ad_pattern,
        output_directory=output_directory,
        **kwargs,
    )


# --- MONITOR Command
@bic_res_cmd.command(help="Check a live stream for significant markers")
@bic_options.url()
@bic_options.read
@bic_options.poll
@bic_options.monitor
@bic_options.save
def monitor(
    user_agent: str,
    sub: int,
    max: int,
    interval: Optional[int],
    silent: bool,
    header: str,
    with_schedule: bool,
    with_map: bool,
    with_signals: bool,
    with_adinfo: bool,
    with_frames: bool,
    ad_pattern: str,
    output_directory: str = None,
    **kwargs,
):
    handler = get_handler(sub, user_agent, header)

    source_type = determine_source_type(handler.url)

    if source_type != SourceType.LIVE:
        raise BroadpeakIoCliError(
            "Monitoring can only be done for Live resources (sources or services)"
        )

    if isinstance(handler, DASHHandler):
        raise NotImplementedError(
            "Monitoring of DASH streams not yet implemented in BIC"
        )

    if isinstance(handler, HLSHandler) and handler.has_children():
        handler = handler.get_child(1)

    monitor_hls(
        handler,
        max,
        interval,
        silent,
        with_schedule=with_schedule,
        with_map=with_map,
        with_signals=with_signals,
        with_adinfo=with_adinfo,
        with_frames=with_frames,
        ad_pattern=ad_pattern,
        output_directory=output_directory,
    )


# --- PLAY Command
@bic_res_cmd.command(help="Open the URL in a web player", aliases=["open"])
@click.option(
    "-s",
    "--sub",
    type=int,
    default=None,
    help="For HLS, reads a sub-playlist (by index - "
    "as given by the `read ID --table` option with the main playlist)",
)
@click.option(
    "-p",
    "--player",
    default="CONFIG",
    help="The template for a player URL",
    type=str,
    is_flag=False,
    flag_value="CHOICE",
)
def play(sub: int, player: str):
    handler = get_handler(sub)

    if player == "CONFIG":
        player = CONFIG.get("default-player")

    if player == "CHOICE":
        player = StreamPlayer.prompt_player()

    StreamPlayer().launch(stream_url=handler.url, key=player, name="")


# --- DOWNLOAD Command
@bic_res_cmd.command(help="Download the content of the URL to a local folder")
@bic_options.read
@bic_options.url()
@cloup.argument(
    "output_path",
    help="Local path to save the downloaded stream",
    type=str,
    default=None,
    required=False,
)
@cloup.option(
    "-s",
    "--num-segments",
    "num_segments",
    help="Number of segments to download",
    type=int,
    default=0,
)
def download(
    sub: int,
    header: List[str],
    user_agent: str,
    output_path: Optional[str] = None,
    num_segments: int = 0,
    **kwargs,
):
    handler = get_handler(sub=sub, user_agent=user_agent, headers=header)
    prefix = handler.__class__.__name__

    if not output_path:
        # Create a folder name with the current date and time
        output_path = (
            f"{prefix}_download_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        )

    # Make a progressbar with Rich
    with Progress() as progress:
        task = progress.add_task("Downloading...", total=None)

        def update_progress(message, total=None):
            if total is not None:
                progress.update(task, description=message, total=total)
            else:
                progress.update(task, description=message, advance=1)
                time.sleep(0.2)  # just to allow it to update

        handler.download(
            output_path=output_path,
            num_segments=num_segments,
            progress_callback=update_progress,
        )

    click.secho(CL.ok(f"Downloaded manifest to {output_path}"))


# --- STORE Command
@bic_res_cmd.command(help="Create a Source from the URL")
@cloup.option("--name", help="Name for the source", required=False)
@click.pass_context
def store(ctx, name):
    full_url = ctx.obj.resource_chain.last_key()

    ctx.invoke(source_create, url=full_url, name=name)


# --- PROFILE Command
@bic_res_cmd.command(help="Create a Transcoding Profile from the content of the URL")
@bic_options.url()
@click.option(
    "--schema",
    type=str,
    default="bkt-v2.1",
    help="Version of the transcoding profile schema",
)
@click.option(
    "--name",
    type=str,
    default="",
    help="Name for the transcoding profile",
)
@click.option(
    "--save",
    is_flag=True,
    default=False,
    help="Save the profile to a file",
)
@click.option(
    "--option",
    "options",
    type=str,
    multiple=True,
    callback=parse_options,
    help="Additional options in key=value format",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Force the generation of the profile even if errors are raised",
)
@click.pass_obj
def profile(
    obj: AppContext,
    save: bool,
    schema: int,
    name: str,
    sub: str,
    header: str,
    user_agent: str,
    options: dict,
    force: bool,
    **kwargs,
):
    handler = get_handler(sub, user_agent, header)

    (profile, messages) = make_transcoding_profile(
        handler, schema_version=schema, name=name, options=options, force=force
    )

    obj.response_handler.treat_single_resource(profile, format="json")

    if save:
        filename = "profile.json"
        with open(filename, "w") as f:
            j.dump(profile, f, indent=4)
        click.secho(f"Profile saved to {filename}", fg="green")

    if messages:
        for message in messages:
            msg = message.message
            if message.topic != "-":
                msg = f"({message.topic})  {message.message}"
            click.echo(CL.log(msg, message.level), err=True)
        click.secho(
            "Since errors or warnings have been raised, you may want to review the profile payload to ensure it is usable",
            fg="yellow",
            err=True,
        )


# --- PLOT Command
@bic_res_cmd.command(help=f"Plot a visual timeline of the content")
@bic_options.poll
@bic_options.url()
@bic_options.dash
@click.option(
    "--open/--no-open",
    "-o",
    is_flag=True,
    default=True,
    help="Open the timeline in the browser",
)
@click.option(
    "--per-period",
    "-p",
    is_flag=True,
    help="Show individual representation timelines for each period",
)
@click.option(
    "--debug",
    "-d",
    is_flag=True,
    help="Show debug information",
)
@click.pass_obj
def plot(
    obj: AppContext,
    sub: int,
    url: str,
    query: List[str],
    header: List[str],
    user_agent: str,
    session: Optional[str] = None,
    fqdn: Optional[str] = None,
    open: bool = False,
    per_period: bool = False,
    interval: Optional[int] = None,
    debug: bool = False,
    ad_pattern: Optional[str] = "bpkio-jitt",
    **kwargs,
):
    handler = get_handler(sub, user_agent, header)

    if not isinstance(handler, DASHHandler):
        display_error("This command is only implemented with MPEG-DASH content")
        return

    plotter = MpdTimelinePlotter()
    plotter.set_filters(
        {
            "selected_periods": kwargs.get("mpd_period"),
            "selected_adaptation_sets": kwargs.get("mpd_adaptation_set"),
            "selected_representations": kwargs.get("mpd_representation"),
            "selected_segments": kwargs.get("mpd_segments"),
            "ad_pattern": ad_pattern,
        }
    )
    plotter.set_config({"scrollZoom": True})
    resource_name = handler.original_url
    plotter.add_subplot(
        SubplotInfo(
            title=resource_name,
            handler=handler,
        )
    )

    plotter.plot(interval=interval, open=open, debug=debug)


url.add_section(
    cloup.Section(
        "Content Commands",
        [check, info, read, poll, monitor, plot, play, download, profile],
    )
)

url.add_section(cloup.Section("Other Commands", [store, check_compatibility]))
