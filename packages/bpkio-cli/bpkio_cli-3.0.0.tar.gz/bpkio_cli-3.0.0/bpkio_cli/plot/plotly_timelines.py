import logging
import os
from ast import List
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, List, Optional

import click
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from bpkio_cli.plot.colors import (
    TimelineMarkerDef,
    TimelineMarkers,
    TimelineType,
)
from bpkio_cli.plot.plotly_timeline_dashboard import make_dashboard
from bpkio_cli.utils.datetimes import (
    format_datetime_with_milliseconds,
    seconds_to_timecode,
)
from bpkio_cli.utils.httpserver import find_available_port
from bpkio_cli.writers.breadcrumbs import (
    display_bpkio_session_info,
    display_error,
    display_info,
    display_ok,
    display_tip,
)
from bpkio_cli.writers.colorizer_rich import console as rich_console
from dash import dcc, html
from dash.dependencies import Input, Output, State
from loguru import logger
from media_muncher.handlers.dash import DASHHandler
from mpd_inspector import (
    ContentType,
    EventInspector,
    MediaSegment,
    MPDInspector,
    PeriodInspector,
    RepresentationInspector,
    Scte35EventInspector,
    Scte35XmlEventInspector,
    SpliceCommandType,
)
from mpd_inspector.scte35 import SegmentationType, SpliceCommandType
from plotly.subplots import make_subplots
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing_extensions import Literal

"""
Visually we want:
- 1 subplot per handler / data source
- 1 trace per type of timeline: periods, segments, events, BkYou slots
    clickable on/off in the legend
- different colors for each sub-type, eg. content/ads, video/audio/text, event/segtypeid, computed/real
- different y values for visual timelines: periods, representations, event types, etc.

We generate a single set of data points, with all point/spans, with:
- a trace name (used for group by) - allowing choice between period and period_content, etc
- a y-category (could be the same)
- a color (based on point/span type)
- a legend group name (from which the legend group title is derived)
- a subplot name/position (source, service, BkYou)
- a hover template
- a width (?) for the whole bar

We convert all those to plotly-safe types

"""


@dataclass
class SubplotInfo:
    title: str
    handler: Any
    traces: list[go.Bar] = field(default_factory=list)
    y_categories: list[tuple[str, str]] = field(default_factory=list)
    legend_group: str = None


@dataclass
class SpanMarker:
    type: TimelineMarkerDef  # type of the span (defines colors, names, etc)
    base: pd.Timestamp  # start time
    x: float  # duration (in milliseconds)
    y: str  # category (name of the timeline on the Y axis)
    y_label: str  # label to display on the Y axis
    text: str  # text to display on the marker
    customdata: List[str]  # custom data for the marker, as a list of strings
    hovertemplate: str  # hover template for the marker, which can use the %{customdata[0]} syntax to insert custom data
    bg_color: str  # background color of the marker
    border_color: str = None  # border color of the marker
    border_width: int = 0  # border width of the marker


@dataclass
class TimelineTrace:
    name: str  # name of the trace
    showlegend: bool = True
    legendgroup: str | None = (
        None  # identifier for the legend group (used for grouping in the legend)
    )
    legendgrouptitle_text: str | None = (
        None  # title of the legend group as displayed in the legend
    )
    textposition: Literal["inside", "outside", "auto"] = "inside"
    insidetextanchor: Literal["start", "middle", "end"] = "start"
    xaxis: str = "x1"
    spans: List[SpanMarker] = field(
        default_factory=list
    )  # list of spans to display on the trace
    width: float = 0.7  # width of the trace. 1 is full width and will mean that adjacent traces will be touching

    def first_span(self) -> SpanMarker:
        return self.spans[0] if self.spans else None

    def get_unique_y_categories(self) -> list[tuple[str, str]]:
        category_tuples: list[tuple[str, str]] = []
        for span in self.spans:
            category_tuples.append((span.y, span.y_label))

        unique_categories = list(set(category_tuples))
        # raise error if there are more than one category with the same y
        unique_categories_y = list(set(category[0] for category in unique_categories))
        if len(unique_categories_y) != len(unique_categories):
            raise ValueError(
                f"There are multiple labels for the same y category: {unique_categories_y}"
            )

        return unique_categories


class MpdTimelinePlotter:
    def __init__(self):
        self.subplots = []
        self.filters = {}
        self.plotly_config = {}

    def add_subplot(self, subplot_info: SubplotInfo):
        self.subplots.append(subplot_info)

    def set_filters(self, params: dict):
        self.filters = params

    def set_config(self, config: dict):
        self.plotly_config = config

    def plot(
        self,
        interval: int = None,
        open: bool = False,
        debug: bool = False,
        port: Optional[int] = None,
    ):
        if port is None:
            port = find_available_port()

        for subplot_definition in self.subplots:
            display_bpkio_session_info(subplot_definition.handler)

        if interval:
            if open:
                click.launch(f"http://localhost:{port}")
            self._generate_updating_timeline(
                refresh_interval=interval, debug=debug, open_browser=open, port=port
            )
        else:
            output_file = self._generate_static_timeline()
            display_ok(f"Timeline written to: {output_file}")
            if open:
                click.launch("file://" + str(output_file.absolute()))

    def _generate_static_timeline(self):
        # Generate timeline info and figure using the helper function
        fig = self._generate_multi_timeline_figure()

        # Save to appropriate file based on visualization type
        output_file = Path("mpd_timeline.html")

        copy_to_clipboard_js = """
        // {plot_id} is replaced with the actual div id
        var gd = document.getElementById('{plot_id}');
        gd.on('plotly_click', e => {
            const pt = e.points[0];
            const txt = pt.text || '';
            navigator.clipboard.writeText(txt);
        });
        """

        fig.write_html(
            str(output_file),
            config={
                # "showSendToCloud": True,
                **self.plotly_config,
            },
            include_plotlyjs="cdn",
            post_script=copy_to_clipboard_js,
        )

        return output_file.absolute()

    def _generate_updating_timeline(
        self,
        debug: bool = False,
        refresh_interval: int = 10,
        open_browser: bool = False,
        port: int = 8086,
    ):
        # Create a persistent progress bar that grows with each refresh cycle
        persistent_progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            # BarColumn(),
            TextColumn("[progress.completed]"),
            console=rich_console,
            transient=False,  # Keep it visible across refreshes
        )

        # Track the current cycle count
        cycle_count = [0]  # Use list to allow modification in closure
        cycle_task_id = [None]  # Track the task ID
        status_task_id = [None]  # Track the status task ID

        # Start the persistent progress bar
        persistent_progress.start()

        def generate_figure():
            # Increment cycle count
            cycle_count[0] += 1

            # Create or update the cycle progress task (infinite duration, no reset)
            if cycle_task_id[0] is None:
                cycle_task_id[0] = persistent_progress.add_task(
                    "Refresh cycles", total=None
                )

            # Create or reuse the status task for detailed messages
            if status_task_id[0] is None:
                status_task_id[0] = persistent_progress.add_task(
                    "",
                    total=None,  # Infinite duration for status messages
                )

            # Update the cycle progress
            persistent_progress.update(
                cycle_task_id[0],
                completed=cycle_count[0],
                description=f"Refresh cycle: {cycle_count[0]}",
            )

            # Reload the handlers to get fresh content
            for subplot_definition in self.subplots:
                try:
                    persistent_progress.update(
                        status_task_id[0],
                        description=f"Retrieving content for {subplot_definition.title}",
                    )
                    subplot_definition.handler.reload()
                except Exception as e:
                    persistent_progress.update(
                        status_task_id[0],
                        description=f"[red]Error reloading {subplot_definition.title}: {e}[/red]",
                    )
                    continue

            # Generate figure using the helper function
            return self._generate_multi_timeline_figure(
                progress=persistent_progress, task=status_task_id[0]
            )

        app = make_dashboard(
            refresh_interval=refresh_interval,
            plotly_config=self.plotly_config,
            generate_figure_fn=generate_figure,
        )

        # Disable Flask/Werkzeug request logging
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)

        # Start the Dash app
        display_info(
            f"Starting MPD Timeline dashboard with {refresh_interval} seconds refresh interval"
        )
        display_tip("Press Ctrl+C to stop the dashboard")

        try:
            # Run the Dash server directly (blocking call)
            app.run(debug=debug, port=port)
        finally:
            # Clean up the persistent progress bar
            persistent_progress.stop()

    def _generate_multi_timeline_figure(
        self,
        progress: Optional[Progress] = None,
        task: Optional[Any] = None,
    ) -> go.Figure:
        range = None

        service_id: Optional[str] = None
        session_id: Optional[str] = None

        timelines = []

        subplot_definition: SubplotInfo
        for subplot_definition in self.subplots:
            subplot_timelines = []
            handler = subplot_definition.handler

            if progress and task is not None:
                progress.update(
                    task,
                    description=f"Extracting timelines for {subplot_definition.title}",
                )
            else:
                display_info(f"Extracting timelines for {subplot_definition.title}")

            if isinstance(handler, DASHHandler):
                subplot_timelines = self._extract_timelines_from_mpd(
                    handler, progress=progress, task=task
                )

                if handler.service_id:
                    service_id = handler.service_id
                if handler.session_id:
                    session_id = handler.session_id

            # any other handler must have an extract_timelines method with the same type of return
            else:
                try:
                    subplot_timelines = handler.extract_timelines(
                        service_id, session_id
                    )
                except Exception as e:
                    error_msg = f"Error extracting timelines for {subplot_definition.title}: {e}"
                    if progress and task is not None:
                        progress.update(task, description=f"[red]{error_msg}[/red]")
                    else:
                        display_error(error_msg)

            # add the timelines to the overall list
            timelines.extend(subplot_timelines)

            # convert the timelines to traces
            subplot_definition.traces = convert_timelines_to_traces(subplot_timelines)
            subplot_definition.y_categories = list(
                set(
                    y_category
                    for t in subplot_timelines
                    for y_category in t.get_unique_y_categories()
                )
            )

        return create_figure_with_subplots(self.subplots, range)

    # --- methods to handle parsing the MPD and converting to timelines ---

    def _extract_timelines_from_mpd(
        self,
        handler: DASHHandler,
        progress: Optional[Progress] = None,
        task: Optional[Any] = None,
    ) -> list["TimelineTrace"]:
        """Extract the MPD timelines from the handler"""
        try:
            doc = handler.document
        except Exception as e:
            error_msg = f"Error extracting timelines from MPD: {e}"
            if progress and task is not None:
                progress.update(task, description=f"[red]{error_msg}[/red]")
            else:
                display_error(error_msg)
            return []
        mpdi = MPDInspector(doc)

        selected_periods = self.filters.get("selected_periods")
        selected_adaptation_sets = self.filters.get("selected_adaptation_sets")
        selected_representations = self.filters.get("selected_representations")
        selected_segments = self.filters.get("selected_segments")
        ad_pattern = self.filters.get("ad_pattern")

        # extract all spans for the various timelines
        spans = []
        for period in mpdi.select_periods(selected_periods):
            spans.append(self._period_to_span(period, ad_pattern))

            for adaptation_set in period.select_adaptation_sets(
                selected_adaptation_sets
            ):
                for representation in adaptation_set.select_representations(
                    selected_representations
                ):
                    for segment in representation.segment_information.segments:
                        segment_span = self._segment_to_span(
                            segment, representation, ad_pattern
                        )
                        if segment_span is not None:
                            spans.append(segment_span)

            for event_stream in period.event_streams:
                for event in event_stream.events:
                    event_spans = self._mpd_event_to_spans(event)
                    if event_spans:
                        spans.extend(event_spans)

        # group them and turn them into traces
        # --- periods ---
        timelines = []
        period_spans = [
            span for span in spans if span.type.timeline_type == TimelineType.PERIOD
        ]  # single trace for all perdiods, regardless of content type
        # group the spans by marker type
        spans_per_trace = defaultdict(list)
        for span in period_spans:
            spans_per_trace[span.type].append(span)

        for trace_type, trace_spans in spans_per_trace.items():
            timeline = TimelineTrace(
                name=trace_type.name,
                spans=trace_spans,
                legendgroup=trace_type.timeline_type.name,
                legendgrouptitle_text=trace_type.timeline_type.name,
                width=1,
            )
            timelines.append(timeline)

        # --- media ---
        media_spans = [
            span for span in spans if span.type.timeline_type == TimelineType.MEDIA
        ]
        # group them by representation
        spans_per_trace = defaultdict(list)
        for span in media_spans:
            spans_per_trace[span.type].append(span)

        for trace_type, trace_spans in spans_per_trace.items():
            timeline = TimelineTrace(
                name=trace_type.name,
                spans=trace_spans,
                legendgroup=trace_type.timeline_type.name,
                legendgrouptitle_text=trace_type.timeline_type.name,
                width=0.8,
            )
            timelines.append(timeline)

        # --- events ---
        event_spans = [
            span for span in spans if span.type.timeline_type == TimelineType.EVENT
        ]
        spans_per_trace = defaultdict(list)
        for span in event_spans:
            spans_per_trace[span.type].append(span)

        for trace_type, trace_spans in spans_per_trace.items():
            timeline = TimelineTrace(
                name=trace_type.name,
                spans=trace_spans,
                legendgroup=trace_type.timeline_type.name,
                legendgrouptitle_text=trace_type.timeline_type.name,
            )
            timelines.append(timeline)

        return timelines

    def _period_to_span(self, period: PeriodInspector, ad_pattern: str = "bpkio-jitt"):
        """Turn a period into a list of Plotly-safe spans/markers"""

        # If end is None (ie. last period in a live stream), align with the end of the last segment within it
        # (chosen from the first representation, never mind if they don't all have the exact same end time)
        period_end = period.end_time if period.end_time else None

        first_representation = period.adaptation_sets[0].representations[0]
        if period_end is None:
            last_segment_end = first_representation.segment_information.segments[
                -1
            ].end_time
            period_end = last_segment_end

        # check the URLs to determine if this is an ad period
        if any(url for url in first_representation.full_urls if ad_pattern in url):
            marker_type = TimelineMarkers.PERIOD_AD
        else:
            marker_type = TimelineMarkers.PERIOD_CONTENT

        # convert times to Plotly-safe types
        if isinstance(period.start_time, timedelta):
            # must be VOD, we use start of epoch
            span_start = datetime.fromtimestamp(0) + period.start_time
            span_end = datetime.fromtimestamp(0) + period.end_time
            span_duration = (span_end - span_start).total_seconds() * 1000
        else:
            span_start = pd.to_datetime(period.start_time)
            span_end = pd.to_datetime(period_end)
            span_duration = (span_end - span_start).total_seconds() * 1000

        hover_template = _make_hover_template(
            {
                "id": period.id,
                "type": marker_type.name,
                "timing": _to_range(span_start, span_end),
                "duration": _to_dur(span_duration),
            },
            extra=f"#{period.sequence}",
        )
        return SpanMarker(
            type=marker_type,
            base=span_start,
            x=span_duration,
            y=marker_type.name,
            y_label=f"{marker_type.name}<br><i style='font-size: 80%'>periods</i>",
            text=period.id,
            customdata=[period.id, str(period.duration), marker_type.name],
            hovertemplate=hover_template,
            bg_color=marker_type.bg_color,
            border_color=marker_type.border_color,
            border_width=marker_type.border_width,
        )

    def _segment_to_span(
        self,
        segment: MediaSegment,
        representation: RepresentationInspector,
        ad_pattern: Optional[str] = "bpkio-jitt",
    ):
        """Turn a segment into a Plotly-safe span/marker"""

        filename = os.path.basename(segment.urls[0].split("?")[0])
        # create a unique id for the segment
        if segment.number is not None:
            segment_id = str(segment.number)
        else:
            segment_id = str(segment.time)

        if representation.get_content_type() == ContentType.VIDEO:
            marker_type = TimelineMarkers.SEGMENT_VIDEO
        elif representation.get_content_type() == ContentType.AUDIO:
            marker_type = TimelineMarkers.SEGMENT_AUDIO
        elif representation.get_content_type() == ContentType.TEXT:
            marker_type = TimelineMarkers.SEGMENT_TEXT
        else:
            marker_type = TimelineMarkers.SEGMENT_OTHER

        # augment with ad type if the segment is an ad
        if ad_pattern in segment.urls[0]:
            marker_type = marker_type.combine(
                TimelineMarkers.SEGMENT_AD, f"{marker_type.name} (ad)"
            )

        # y-axis is the representation name
        y_value = f"[{representation.adaptation_set.id}] {representation.id}"
        y_label = f"{y_value}<br><i style='font-size: 80%'>representation</i>"

        # convert times to Plotly-safe types
        try:
            if isinstance(segment.start_time, timedelta):
                # must be VOD, we use start of epoch
                span_start = datetime.fromtimestamp(0) + segment.start_time
                span_end = span_start + timedelta(milliseconds=segment.duration)
                span_duration = segment.duration * 1000
            else:
                span_start = pd.to_datetime(segment.start_time)
                span_end = pd.to_datetime(segment.end_time)
                span_duration = (span_end - span_start).total_seconds() * 1000

            hover_template = _make_hover_template(
                {
                    "id": filename,
                    "content type": representation.get_content_type().value,
                    "representation": y_value,
                    "timing": _to_range(span_start, span_end),
                    "duration": _to_dur(span_duration),
                }
            )

            return SpanMarker(
                type=marker_type,
                base=span_start,
                x=span_duration,
                y=y_value,
                y_label=y_label,
                text=segment_id,
                customdata=[filename, str(segment.duration), y_value],
                hovertemplate=hover_template,
                bg_color=marker_type.bg_color,
                border_color=marker_type.border_color,
                border_width=marker_type.border_width,
            )
        except Exception as e:
            display_error(
                f"Error converting segment into usable span: {segment_id}: {e}",
            )
            return None

    def _mpd_event_to_spans(self, event: EventInspector):
        """Turn an MPD event into a Plotly-safe span/marker"""
        marker_type = TimelineMarkers.MPD_EVENT

        # convert times to Plotly-safe types
        span_start = pd.to_datetime(event.presentation_time)
        # 1 second long if no own duration, so it shows on the timeline
        if event.duration is None:
            span_duration = 0
            border_color = "lightgray"
            note = "no duration defined in the MPD"
        else:
            span_duration = event.duration.total_seconds() * 1000
            border_color = marker_type.border_color
            note = ""

        span_end = span_start + pd.Timedelta(milliseconds=span_duration)

        hover_template = _make_hover_template(
            {
                "id": event.id or "",
                "timing": _to_range(span_start, span_end),
                "duration": _to_dur(span_duration),
                "note": note,
            }
        )

        spans = [
            SpanMarker(
                type=marker_type,
                base=span_start,
                x=span_duration,
                y=marker_type.name,
                y_label=f"{marker_type.name}<br><i style='font-size: 80%'>events</i>",
                text=str(event.id or ""),
                customdata=[str(event.id), str(event.duration), note],
                hovertemplate=hover_template,
                bg_color=marker_type.bg_color,
                border_color=border_color,
                border_width=marker_type.border_width,
            )
        ]

        # Then add the SCTE35 commands
        if isinstance(event, Scte35EventInspector):
            spans.extend(self._scte35_event_to_spans(event))

        return spans

    def _scte35_event_to_spans(self, event: Scte35EventInspector):
        """Turn an SCTE35 descriptor into a Plotly-safe span/marker"""
        spans = []
        if event.command_type == SpliceCommandType.SPLICE_INSERT:
            spans.append(self._splice_insert_to_span(event))

        if hasattr(event.content, "segmentation_descriptors"):
            for descriptor in event.content.segmentation_descriptors:
                spans.append(
                    self._scte35_descriptor_to_spans(
                        descriptor, event.presentation_time
                    )
                )

        return spans

    def _scte35_descriptor_to_spans(self, descriptor, presentation_time: datetime):
        marker_type = TimelineMarkers.SCTE35_DESCRIPTOR

        span_start = pd.to_datetime(presentation_time)
        if descriptor.segmentation_duration:
            span_duration_ms = round(descriptor.segmentation_duration / 90000) * 1000
            border_color = marker_type.border_color
            note = ""
        else:
            span_duration_ms = 0
            border_color = "lightgray"
            note = "no duration defined in the descriptor"

        span_end = span_start + pd.Timedelta(milliseconds=span_duration_ms)

        hover_template = _make_hover_template(
            {
                "id": descriptor.segmentation_event_id,
                "segmentation type": SegmentationType.get_name(
                    descriptor.segmentation_type_id
                ),
                "segment num": f"{descriptor.segment_num}/{descriptor.segments_expected}",
                "timing": _to_range(span_start, span_end),
                "duration": _to_dur(span_duration_ms),
                "note": note,
            }
        )

        return SpanMarker(
            type=marker_type,
            base=span_start,
            x=span_duration_ms,
            y=str(descriptor.segmentation_type_id),
            y_label=f"{SegmentationType.to_hexstring(descriptor.segmentation_type_id)}<br><i style='font-size: 80%'>descriptors</i>",
            text=str(descriptor.segmentation_event_id),
            customdata=[
                str(descriptor.segmentation_event_id),
                str(span_duration_ms),
                SegmentationType.get_name(descriptor.segmentation_type_id),
                f"{descriptor.segment_num}/{descriptor.segments_expected}",
                note,
            ],
            hovertemplate=hover_template,
            bg_color=marker_type.bg_color,
            border_color=border_color,
            border_width=marker_type.border_width,
        )

    def _splice_insert_to_span(self, event: Scte35EventInspector):
        """Turn a splice insert into a Plotly-safe span/marker"""
        marker_type = TimelineMarkers.SCTE35_COMMAND

        event_id = event.content.splice_insert.splice_event_id
        out_of_network = (
            "out" if event.content.splice_insert.out_of_network_indicator else "in"
        )

        if event.duration is None:
            event_duration = 0
            border_color = "lightgray"
            note = "no duration defined in the command"
        else:
            event_duration = event.duration.total_seconds() * 1000
            border_color = marker_type.border_color
            note = ""

        # convert times to Plotly-safe types
        span_start = pd.to_datetime(event.presentation_time)
        span_duration = event_duration
        span_end = span_start + pd.Timedelta(milliseconds=span_duration)

        hover_template = _make_hover_template(
            {
                "id": event_id,
                "type": "splice_insert",
                "timing": _to_range(span_start, span_end),
                "duration": _to_dur(event_duration),
                "out of network": out_of_network,
                "note": note,
            }
        )

        return SpanMarker(
            type=marker_type,
            base=span_start,
            x=span_duration,
            y=marker_type.name,
            y_label=f"{marker_type.name}<br><i style='font-size: 80%'>events</i>",
            text=str(event_id),
            customdata=[str(event_id), str(event_duration), out_of_network, note],
            hovertemplate=hover_template,
            bg_color=marker_type.bg_color,
            border_color=marker_type.border_color,
            border_width=marker_type.border_width,
        )


# --- Pure Plotly methods ---


def convert_timelines_to_traces(timelines: list[TimelineTrace]) -> list[go.Bar]:
    """Turn a list of timelines into a list of Plotly traces"""
    traces = []
    for timeline in timelines:
        bar_trace = go.Bar(
            name=timeline.name,
            # ensure that spans with no duration are at least 1000ms long
            # so they show up on the timeline
            x=[s.x if s.x > 0 else 1000 for s in timeline.spans],
            y=[s.y for s in timeline.spans],
            base=[s.base for s in timeline.spans],
            text=[s.text for s in timeline.spans],
            marker=dict(
                color=[s.bg_color for s in timeline.spans],
                line=dict(
                    color=[s.border_color for s in timeline.spans],
                    width=[s.border_width for s in timeline.spans],
                ),
            ),
            customdata=[s.customdata for s in timeline.spans],
            hovertemplate=[s.hovertemplate for s in timeline.spans],
            orientation="h",
            textposition=timeline.textposition,
            insidetextanchor=timeline.insidetextanchor,
            showlegend=timeline.showlegend,
            legendgroup=timeline.legendgroup,
            legendgrouptitle_text=timeline.legendgrouptitle_text,
            xaxis=timeline.xaxis,
            width=timeline.width,
        )
        traces.append(bar_trace)
    return traces


def create_figure_with_subplots(
    subplots: list[SubplotInfo],
    range: Optional[list[pd.Timestamp]] = None,
):
    """Create a Plotly figure with subplots from a list of subplots"""

    valid_subplots = [s for s in subplots if s.traces]

    fig = make_subplots(
        rows=len(valid_subplots),
        cols=1,
        shared_xaxes=True,
        subplot_titles=[s.title for s in valid_subplots],
        vertical_spacing=0.1,
    )

    for i, subplot in enumerate(valid_subplots):
        for trace in subplot.traces:  # type: ignore
            trace.legend = f"legend{i + 1}"
            fig.add_trace(trace, row=i + 1, col=1)

        # Set y-axis labels
        fig.update_yaxes(
            tickvals=[y_category[0] for y_category in subplot.y_categories],
            ticktext=[y_category[1] for y_category in subplot.y_categories],
            title_text="",
            autorange="reversed",
            row=i + 1,
            col=1,
        )

        # Range slider for the last subplot
        if i == len(valid_subplots) - 1:
            fig.update_xaxes(
                rangeslider=dict(
                    visible=True,
                    thickness=0.05,
                    autorange=True,
                ),
                rangeselector=dict(
                    buttons=list(
                        [
                            dict(
                                count=1, label="1m", step="minute", stepmode="backward"
                            ),
                            dict(
                                count=5, label="5m", step="minute", stepmode="backward"
                            ),
                            dict(
                                count=15,
                                label="15m",
                                step="minute",
                                stepmode="backward",
                            ),
                            dict(
                                count=30,
                                label="30m",
                                step="minute",
                                stepmode="backward",
                            ),
                            dict(step="all"),
                        ]
                    )
                ),
                row=i + 1,
                col=1,
            )

    fig.update_xaxes(
        type="date",
        title_text="",
        showticklabels=True,
        showspikes=True,
        spikemode="across",
        showline=True,
        spikesnap="cursor",
        spikedash="solid",
        spikethickness=1,
        spikecolor="gray",
    )

    if range:
        fig.update_xaxes(
            range=range,
        )

    # Set layout
    fig.update_layout(
        barmode="stack",
        legend=dict(groupclick="toggleitem"),
        hovermode="closest",
        hoversubplots="axis",
        modebar_add=[
            "toggleSpikeLines",
            "toggleSpikes",
            "toggleRangeSelector",
            "toggleHover",
            "toggleSpikey",
        ],
    )

    # place the legends
    for i, subplot in enumerate(valid_subplots):
        fig.update_layout(
            {
                f"legend{i + 1}": dict(
                    y=1 - ((1 / len(valid_subplots) + 0.1) * i),
                    title_text=subplot.legend_group or "",
                    yref="paper",
                    borderwidth=1,
                    bgcolor="rgba(255, 255, 255, 0.5)",
                ),
            }
        )

    # Force a single xaxis to allow spike lines to span all subplots
    fig.update_traces(xaxis=f"x{len(valid_subplots)}")

    return fig


def _make_hover_template(items: dict[str, str], extra: str = None) -> str:
    """Make a hover template from a list of items"""
    string = ""
    note = None
    for key, value in items.items():
        if key == "note":
            note = value
            continue
        elif value is not None and value != "":
            string += f"<span>{key}</span>: <b>{str(value)}</b><br>"

    if note:
        string += f"<br>⚠️ <span style='color: orange'>{note}</span><br>"

    if extra:
        string += f"<extra>{str(extra)}</extra>"
    else:
        string += "<extra></extra>"

    return string


def _to_hms(timestamp: pd.Timestamp) -> str:
    """Convert a timestamp to a human-readable string"""
    return format_datetime_with_milliseconds(timestamp, time_only=True)


def _to_dur(duration_ms: float | timedelta) -> str:
    """Convert a duration to a human-readable string"""

    if isinstance(duration_ms, timedelta):
        duration_ms = duration_ms.total_seconds() * 1000

    if duration_ms == 0:
        return None

    duration_s = duration_ms / 1000
    if duration_s < 60:
        return f"{duration_s:.3f} s"
    else:
        return seconds_to_timecode(duration_s, with_milliseconds=True)


def _to_range(start: pd.Timestamp, end: pd.Timestamp) -> str:
    """Convert a start and end timestamp to a human-readable string"""
    if end and end != start:
        return f"{_to_hms(start)}  <i>to</i>  {_to_hms(end)}"
    else:
        return f"{_to_hms(start)} <i>(no end)</i>"
