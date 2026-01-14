import os
from pathlib import PosixPath
from typing import Optional

import click
import cloup
from media_muncher.handlers import factory
from media_muncher.handlers.dash import DASHHandler
from pydantic import FilePath, TypeAdapter
from trace_shrink import ArchiveReader, open_archive
from trace_shrink.formats import Format

import bpkio_cli.click_options as bic_options
from bpkio_cli.click_mods.resource_commands import ARG_TO_IGNORE, ResourceGroup
from bpkio_cli.core.app_context import AppContext
from bpkio_cli.core.exceptions import BroadpeakIoCliError
from bpkio_cli.core.output_store import OutputStore
from bpkio_cli.display.display_mode import DisplayMode
from bpkio_cli.plot.plot_mpd_sequence import (
    extract_mpd_data,
    plot_mpd_metrics,
)
from bpkio_cli.plot.plot_utils import save_plot_with_crosshair
from bpkio_cli.plot.plotly_timelines import MpdTimelinePlotter, SubplotInfo
from bpkio_cli.utils import prompt
from bpkio_cli.writers.breadcrumbs import display_error, display_info, display_ok
from bpkio_cli.writers.colorizer import Colorizer as CL
from bpkio_cli.writers.content_display import display_content


# Group: Archive
@cloup.group(
    cls=ResourceGroup,
    help="Explore archive files, such as HAR captures",
    resource_type=PosixPath,
)
@cloup.argument(
    "archive_path", help=("The local file to work with"), metavar="<archive-file>"
)
@click.pass_obj
def archive(obj: AppContext, archive_path: str):
    if archive_path and archive_path != ARG_TO_IGNORE:
        if archive_path == "$":
            archive_path = obj.current_resource
        archive_file = TypeAdapter(FilePath).validate_python(archive_path)
        obj.resource_chain.add_resource(archive_path, archive_file)
        obj.cache.record(archive_file)


def _get_archive(obj: AppContext) -> ArchiveReader:
    """Get the Archive instance from the resource chain."""
    # Get the archive path from the resource chain (it should be the first resource)
    archive_path = None

    # Iterate through the resource chain to find the archive path
    for key, resource in obj.resource_chain._chain:
        if isinstance(resource, PosixPath):
            archive_path = resource
            break
        elif isinstance(resource, str) and (
            resource.endswith((".har", ".json")) or "/" in resource or "\\" in resource
        ):
            # Try to parse as FilePath
            try:
                archive_path = TypeAdapter(FilePath).validate_python(resource)
                break
            except Exception:
                pass

    if not archive_path:
        raise BroadpeakIoCliError("No archive file specified in resource chain")

    try:
        return open_archive(str(archive_path))
    except Exception as e:
        raise BroadpeakIoCliError(f"Could not load archive file: {e}")


def _get_entry_by_id(archive: ArchiveReader, request_id: str):
    """Get an entry from the archive by its ID."""
    try:
        entry = archive.get_entry_by_id(request_id)
        if entry is None:
            raise BroadpeakIoCliError(
                f"Request with ID '{request_id}' not found in archive"
            )
        return entry
    except BroadpeakIoCliError:
        raise
    except Exception as e:
        raise BroadpeakIoCliError(
            f"Request with ID '{request_id}' not found in archive: {e}"
        )


def _create_handler_from_entry(entry) -> factory.ContentHandler:
    """Create an appropriate handler from an archive entry."""
    url = str(entry.request.url)
    content = entry.content

    # Ensure content is bytes
    if isinstance(content, str):
        content = content.encode("utf-8")
    elif content is None:
        content = b""

    # Extract content type from response headers if available
    content_type = None
    if hasattr(entry.response, "headers"):
        content_type = entry.response.headers.get("content-type")

    # Use factory to create handler with content type and content
    try:
        return factory.create_handler(
            url,
            from_url_only=True,  # Don't make HTTP request, we have content
            content_type=content_type,
            content=content,
        )
    except Exception as e:
        raise BroadpeakIoCliError(
            f"Could not determine handler type for request {entry.id}. "
            f"URL: {url}, Content-Type: {content_type}, Error: {e}"
        )


# Group: Request
@archive.group(
    cls=ResourceGroup,
    aliases=["req"],
    help="Work with a specific request from the archive",
    resource_type=str,
    resource_id_type=str,
)
@cloup.argument(
    "request_id",
    help="The ID of the request to work with",
    metavar="<request-id>",
)
@click.pass_obj
def request(obj: AppContext, request_id: str):
    if request_id and request_id != ARG_TO_IGNORE:
        if request_id == "$":
            request_id = obj.current_resource

        # Pre-compute archive, entry, and handler for subcommands
        archive_reader = _get_archive(obj)
        entry = _get_entry_by_id(archive_reader, request_id)
        handler = _create_handler_from_entry(entry)

        # Store entry in resource chain (so obj.current_resource returns the entry)
        obj.resource_chain.add_resource(request_id, entry)
        obj.cache.record(request_id)

        # Store handler for subcommands to access
        obj.archive_handler = handler


# --- READ Command
@request.command(
    help="Load and display the content of a request from the archive",
    aliases=["content"],
)
@bic_options.display_mode
@bic_options.read
@bic_options.save
@click.pass_obj
def read(
    obj: AppContext,
    display_mode: DisplayMode,
    top: int,
    tail: int,
    trim: int,
    ad_pattern: str,
    pager: bool,
    output_directory: Optional[str] = None,
    **kwargs,
):
    handler = obj.archive_handler

    display_content(
        handler=handler,
        max=1,
        interval=0,
        display_mode=display_mode,
        top=top,
        tail=tail,
        trim=trim,
        ad_pattern=ad_pattern,
        pager=pager,
        output_directory=output_directory,
        **kwargs,
    )


# --- PLOT Command
@request.command(help="Plot a visual timeline of the request content")
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
    open: bool = False,
    per_period: bool = False,
    interval: Optional[int] = None,
    debug: bool = False,
    ad_pattern: Optional[str] = "bpkio-jitt",
    **kwargs,
):
    entry = obj.current_resource
    handler = obj.archive_handler

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
    resource_name = str(entry.request.url)
    plotter.add_subplot(
        SubplotInfo(
            title=resource_name,
            handler=handler,
        )
    )

    plotter.plot(interval=interval, open=open, debug=debug)


# --- SAVE Command
@request.command(help="Save the content of the request to a local file")
@bic_options.save
@click.pass_obj
def save(
    obj: AppContext,
    output_directory: Optional[str] = None,
    **kwargs,
):
    request_id = obj.resource_chain.last_key()
    handler = obj.archive_handler

    # Get the file extension from the handler
    extension = ""
    if hasattr(handler, "file_extensions") and handler.file_extensions:
        extension = handler.file_extensions[0]
    elif hasattr(handler, "media_format"):
        # Fallback: try to determine extension from media format
        if handler.media_format.value == "HLS":
            extension = ".m3u8"
        elif handler.media_format.value == "DASH":
            extension = ".mpd"

    # Get content from handler
    content = handler.content
    if isinstance(content, bytes):
        content = content.decode("utf-8", errors="replace")
    elif content is None:
        content = ""

    # Create output store and save
    if output_directory is None:
        output_directory = "."

    output_store = OutputStore(output_directory)
    filename = f"{request_id}{extension}"
    output_store.save_text(filename, content)

    file_path = os.path.join(output_store.path(ensure=True), filename)
    click.secho(CL.ok(f"Saved request content to {file_path}"))


# --- PLOT Command (archive-level)
@archive.command(
    help="Plot MPD sequence metrics over time from the archive", name="plot"
)
@click.option(
    "--show-segments",
    is_flag=True,
    default=False,
    help="Show individual segment dots in the Period Segments plot",
)
@click.option(
    "--pubt/--no-pubt",
    "show_publish_time",
    is_flag=True,
    default=True,
    help="Hide MPD Publish Time plot",
)
@click.option(
    "--ast/--no-ast",
    "show_availability_start_time",
    is_flag=True,
    default=True,
    help="Hide MPD Availability Start Time plot",
)
@click.option(
    "--pstart/--no-pstart",
    "show_period_starts",
    is_flag=True,
    default=True,
    help="Hide Period Start Time plot",
)
@click.option(
    "--open/--no-open",
    "open_browser",
    is_flag=True,
    default=True,
    help="Open the plot in the browser",
)
@bic_options.save
@click.pass_obj
def plot_mpd_sequence(
    obj: AppContext,
    show_segments: bool = False,
    show_publish_time: bool = True,
    show_availability_start_time: bool = True,
    show_period_starts: bool = True,
    open_browser: bool = True,
    output_directory: Optional[str] = None,
    **kwargs,
):
    """Plot MPD sequence metrics over time from the archive.

    This command finds all DASH manifest URLs in the archive and prompts the user
    to select one if multiple manifests are found. It then extracts and plots MPD
    metrics showing how manifest attributes change over time.
    """
    archive_reader = _get_archive(obj)

    # Get all DASH manifest URLs
    dash_urls = archive_reader.get_abr_manifest_urls(format=Format.DASH)

    if not dash_urls:
        display_error("No DASH manifest URLs found in the archive")
        return

    # If multiple manifests, prompt user to select one
    manifest_url = None
    if len(dash_urls) == 1:
        manifest_url = str(dash_urls[0].url)
        display_info(f"Found 1 DASH manifest: {manifest_url}")
    else:
        display_info(f"Found {len(dash_urls)} DASH manifests. Please select one:")
        choices = [
            dict(value=str(dash_url.url), name=f"{dash_url.url}")
            for dash_url in dash_urls
        ]
        manifest_url = prompt.fuzzy(
            message="Select a manifest URL to plot",
            choices=choices,
        )

    if not manifest_url:
        display_error("No manifest URL selected")
        return

    # Extract MPD data
    display_info(f"Extracting MPD data from manifest: {manifest_url}")
    data_points, first_mpd_url = extract_mpd_data(
        archive_reader,
        manifest_url,
        show_segments=show_segments,
    )

    if not data_points:
        display_error(f"No MPD entries found for manifest: {manifest_url}")
        return

    display_info(f"Found {len(data_points)} MPD entries")
    display_info("Generating plot...")

    # Generate plot
    fig = plot_mpd_metrics(
        data_points,
        first_mpd_url=first_mpd_url,
        show_segments=show_segments,
        show_publish_time=show_publish_time,
        show_availability_start_time=show_availability_start_time,
        show_period_starts=show_period_starts,
    )

    if fig is None:
        display_error("Failed to generate plot")
        return

    # Save plot using OutputStore to determine output directory
    if output_directory is None:
        output_directory = "."

    output_store = OutputStore(output_directory)
    output_store.path(ensure=True)  # Ensure the directory exists

    # Use OutputStore's directory path with save_plot_with_crosshair
    filename = "mpd_sequence_plot.html"
    output_path = os.path.join(output_store.path(ensure=True), filename)

    # Save plot with crosshair functionality
    output_file = save_plot_with_crosshair(fig, output_path)
    display_ok(f"Plot saved to: {output_file}")

    if open_browser:
        click.launch("file://" + str(output_file))
