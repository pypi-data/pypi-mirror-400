"""Plot MPD sequence metrics over time from archive files.

This module provides functionality to extract and plot DASH manifest metrics
from archive files, showing how MPD attributes change over time.
"""

import sys
from datetime import datetime, timedelta

import plotly.graph_objects as go
from bpkio_cli.plot.plot_utils import (
    extract_filename_from_uri,
    format_time_only,
    get_period_color_palette,
)
from mpd_inspector import MPDInspector, MPDParser
from plotly.subplots import make_subplots
from trace_shrink import ArchiveReader


def get_period_legend_group_title(period_id, period_idx):
    """Generate legend group title for a period.

    Args:
        period_id: Period ID if available, None otherwise
        period_idx: Period index if available, None otherwise

    Returns:
        String like "Period {period-id}" or "Period {period_idx}"
    """
    if period_id is not None:
        return f"Period {period_id}"
    elif period_idx is not None:
        return f"Period {period_idx}"
    else:
        return "Period"


def parse_mpd_attributes(
    mpd_content: str,
    show_segments: bool = False,
    request_id: str = None,
    request_time: datetime = None,
) -> dict:
    """Parse MPD using mpd-inspector and extract publishTime, availabilityStartTime, and Period start times.

    Args:
        mpd_content: The MPD XML content as a string
        show_segments: If True, also extract all individual segments for each period
        Note: Segments are always extracted for validation purposes, regardless of show_segments
    """
    try:
        parsed_mpd = MPDParser.from_string(mpd_content)
        inspector = MPDInspector(parsed_mpd)
    except Exception as e:
        print(f"Error parsing MPD with mpd-inspector: {e}", file=sys.stderr)
        return {}

    result = {}

    # Extract MPD@publishTime
    publish_time = inspector.publish_time
    result["publishTime"] = publish_time

    # Extract MPD@availabilityStartTime
    availability_start_time = inspector.availability_start_time
    result["availabilityStartTime"] = availability_start_time

    # Extract Period@start and @duration for all Periods
    periods = []
    for period_idx, period in enumerate(inspector.periods):
        period_start = period.start_time
        if period_start is not None:
            periods.append(
                {
                    "start_time": period_start,
                    "period_index": period_idx,
                    "period_id": getattr(period, "id", None),
                }
            )

    result["period_starts"] = periods

    # Extract MPD Events from all periods
    events = []
    try:
        for period_idx, period in enumerate(inspector.periods):
            event_streams = getattr(period, "event_streams", [])
            for event_stream in event_streams:
                stream_events = getattr(event_stream, "events", [])
                for event in stream_events:
                    presentation_time = getattr(event, "presentation_time", None)
                    duration = getattr(event, "duration", None)
                    event_id = getattr(event, "id", None)
                    message_data = getattr(event, "message_data", None)

                    if presentation_time is not None:
                        events.append(
                            {
                                "presentation_time": presentation_time,
                                "duration": duration,
                                "event_id": event_id,
                                "message_data": message_data,
                                "period_index": period_idx,
                                "period_id": getattr(period, "id", None),
                            }
                        )
    except Exception:
        pass

    result["events"] = events

    # Extract segment information from all periods
    period_segment_spans = []
    period_all_segments = []

    for period_idx, period in enumerate(inspector.periods):
        for adaptation_set in period.adaptation_sets:
            mime_type = getattr(adaptation_set, "mime_type", None)
            if mime_type and mime_type.startswith("video/"):
                if adaptation_set.representations:
                    first_representation = adaptation_set.representations[0]
                    try:
                        segment_info = first_representation.segment_information
                        if segment_info:
                            base_url = getattr(first_representation, "base_url", None)
                            segments = list(segment_info.segments)

                            if segments:
                                first_segment = segments[0]
                                first_segment_start = None
                                if first_segment.start_time is not None:
                                    first_segment_start = first_segment.start_time

                                last_segment = segments[-1]
                                last_segment_end = None
                                if (
                                    hasattr(last_segment, "end_time")
                                    and last_segment.end_time is not None
                                ):
                                    last_segment_end = last_segment.end_time

                                if (
                                    first_segment_start is not None
                                    and last_segment_end is not None
                                ):
                                    period_segment_spans.append(
                                        {
                                            "period_index": period_idx,
                                            "period_id": getattr(period, "id", None),
                                            "first_segment_start": first_segment_start,
                                            "last_segment_end": last_segment_end,
                                        }
                                    )

                                all_segments_for_period = []
                                for seg_idx, seg in enumerate(segments):
                                    seg_start = (
                                        seg.start_time
                                        if seg.start_time is not None
                                        else None
                                    )
                                    seg_end = None
                                    if (
                                        hasattr(seg, "end_time")
                                        and seg.end_time is not None
                                    ):
                                        seg_end = seg.end_time
                                    elif seg_start is not None:
                                        seg_end = seg_start

                                    duration = getattr(seg, "duration", None)

                                    segment_uri = None
                                    segment_uri = getattr(seg, "uri", None) or getattr(
                                        seg, "url", None
                                    )

                                    if segment_uri is None and base_url:
                                        try:
                                            rel_path = getattr(
                                                seg, "path", None
                                            ) or getattr(seg, "media", None)
                                            if rel_path:
                                                segment_uri = (
                                                    str(base_url) + "/" + str(rel_path)
                                                    if not str(base_url).endswith("/")
                                                    else str(base_url) + str(rel_path)
                                                )
                                        except Exception:
                                            pass

                                    if segment_uri is None:
                                        try:
                                            segment_uri = str(seg)
                                        except Exception:
                                            segment_uri = None

                                    is_ad = False
                                    if segment_uri and "bpkio-jitt" in str(segment_uri):
                                        is_ad = True

                                    if seg_start is not None:
                                        all_segments_for_period.append(
                                            {
                                                "start_time": seg_start,
                                                "end_time": seg_end,
                                                "duration": duration,
                                                "position": seg_idx + 1,
                                                "uri": segment_uri,
                                                "is_ad": is_ad,
                                            }
                                        )

                                if all_segments_for_period:
                                    period_all_segments.append(
                                        {
                                            "period_index": period_idx,
                                            "period_id": getattr(period, "id", None),
                                            "segments": all_segments_for_period,
                                        }
                                    )
                    except Exception as e:
                        print(
                            f"Warning: Could not access segment information for request {request_id} (at {request_time}), period {period_idx}: {e}",
                            file=sys.stderr,
                        )
                break

    result["period_segment_spans"] = period_segment_spans
    result["period_all_segments"] = period_all_segments

    return result


def extract_mpd_data(
    archive: ArchiveReader,
    manifest_url: str,
    show_segments: bool = False,
    query_value: str = None,
):
    """Extract MPD data from archive entries matching the manifest URL.

    Args:
        archive: The archive reader instance
        manifest_url: The manifest URL to filter entries
        show_segments: If True, extract all individual segments for each period
        query_value: Optional query parameter value to filter manifests
    """
    from yarl import URL

    target_url = URL(manifest_url)
    entries = archive.get_entries_for_url(target_url)

    # Sort by request time
    entries.sort(key=lambda e: e.timeline.request_start or datetime.min)

    # Extract data from each MPD
    data_points = []
    first_mpd_url = None

    for entry in entries:
        request_time = entry.timeline.request_start
        if request_time is None:
            continue

        mpd_content = entry.content
        if isinstance(mpd_content, bytes):
            mpd_content = mpd_content.decode("utf-8", errors="ignore")

        mpd_attrs = parse_mpd_attributes(
            mpd_content,
            show_segments=show_segments,
            request_id=entry.id,
            request_time=request_time,
        )

        if mpd_attrs:
            if first_mpd_url is None:
                first_mpd_url = entry.request.url

            data_point = {
                "request_time": request_time,
                "request_id": entry.id,
                "publishTime": mpd_attrs.get("publishTime"),
                "availabilityStartTime": mpd_attrs.get("availabilityStartTime"),
                "period_starts": mpd_attrs.get("period_starts", []),
                "period_segment_spans": mpd_attrs.get("period_segment_spans", []),
                "events": mpd_attrs.get("events", []),
                "period_all_segments": mpd_attrs.get("period_all_segments", []),
            }

            data_points.append(data_point)

    return data_points, first_mpd_url


def plot_mpd_metrics(
    data_points,
    first_mpd_url=None,
    show_segments=False,
    show_publish_time=True,
    show_availability_start_time=True,
    show_period_starts=True,
):
    """Plot MPD metrics using plotly express with subplots.

    Args:
        data_points: List of MPD data points to plot
        first_mpd_url: Optional URL of the first MPD for subtitle
        show_segments: If True, show individual segment dots in the Period Segments plot
        show_publish_time: If True, show MPD Publish Time plot (default: True)
        show_availability_start_time: If True, show MPD Availability Start Time plot (default: True)
        show_period_starts: If True, show Period Start Time plot (default: True)
    """
    if not data_points:
        print("No data points to plot.", file=sys.stderr)
        return None

    # Prepare data for plotting
    request_times = [dp["request_time"] for dp in data_points]

    # Build list of enabled plots with their metadata
    enabled_plots = []
    plot_metadata = {
        1: {"title": "MPD Publish Time", "height": 150, "enabled": show_publish_time},
        2: {
            "title": "MPD Availability Start Time",
            "height": 100,
            "enabled": show_availability_start_time,
        },
        3: {"title": "Period Start Time", "height": 200, "enabled": show_period_starts},
        4: {
            "title": "Period Segments (Start & End)",
            "height": 500,
            "enabled": True,
        },
        5: {
            "title": "Period Span Overview",
            "height": 100,
            "enabled": True,
        },
    }

    # Create mapping from logical plot number to actual row number
    plot_to_row = {}
    subplot_titles = []
    row_heights = []

    for plot_num in [1, 2, 3, 4, 5]:
        if plot_metadata[plot_num]["enabled"]:
            actual_row = len(enabled_plots) + 1
            plot_to_row[plot_num] = actual_row
            enabled_plots.append(plot_num)
            subplot_titles.append(plot_metadata[plot_num]["title"])
            row_heights.append(plot_metadata[plot_num]["height"])

    if 4 not in plot_to_row or 5 not in plot_to_row:
        raise RuntimeError(
            "Plots 4 and 5 must always be enabled. This is a programming error."
        )

    num_rows = len(enabled_plots)
    if num_rows == 0:
        raise RuntimeError("At least one plot must be enabled.")

    fig = make_subplots(
        rows=num_rows,
        cols=1,
        subplot_titles=tuple(subplot_titles),
        vertical_spacing=0.12,
        shared_xaxes=False,
        row_heights=row_heights,
    )

    # Left-align all subplot titles
    for annotation in fig.layout.annotations:
        if annotation.text:
            annotation.xanchor = "left"
            annotation.x = 0.0

    def get_row(plot_num):
        row = plot_to_row.get(plot_num)
        if row is None:
            raise ValueError(
                f"Plot {plot_num} is not enabled. Cannot get row number. "
                f"Enabled plots: {list(plot_to_row.keys())}"
            )
        if row > num_rows:
            raise ValueError(
                f"Plot {plot_num} has row {row} but subplot only has {num_rows} rows."
            )
        return row

    # Plot 1: MPD@publishTime
    if show_publish_time:
        publish_times = [dp["publishTime"] for dp in data_points]
        valid_indices_1 = [i for i, pt in enumerate(publish_times) if pt is not None]
        if valid_indices_1:
            hover_data_1 = [
                [
                    data_points[i]["request_id"],
                    format_time_only(request_times[i]),
                    format_time_only(publish_times[i]),
                ]
                for i in valid_indices_1
            ]
            fig.add_trace(
                go.Scatter(
                    x=[request_times[i] for i in valid_indices_1],
                    y=[publish_times[i] for i in valid_indices_1],
                    mode="markers+lines",
                    name="publishTime",
                    marker=dict(size=6),
                    hovertemplate="<b>Request ID:</b> %{customdata[0]}<br>"
                    + "<b>PublishTime:</b> %{customdata[2]}<extra></extra>",
                    customdata=hover_data_1,
                ),
                row=get_row(1),
                col=1,
            )

    # Plot 2: MPD@availabilityStartTime
    if show_availability_start_time:
        availability_start_times = [dp["availabilityStartTime"] for dp in data_points]
        valid_indices_2 = [
            i for i, ast in enumerate(availability_start_times) if ast is not None
        ]
        if valid_indices_2:
            hover_data_2 = [
                [
                    data_points[i]["request_id"],
                    format_time_only(request_times[i]),
                    format_time_only(availability_start_times[i]),
                ]
                for i in valid_indices_2
            ]
            fig.add_trace(
                go.Scatter(
                    x=[request_times[i] for i in valid_indices_2],
                    y=[availability_start_times[i] for i in valid_indices_2],
                    mode="markers+lines",
                    name="availabilityStartTime",
                    marker=dict(size=6, color="blue"),
                    line=dict(color="blue"),
                    hovertemplate="<b>Request ID:</b> %{customdata[0]}<br>"
                    + "<b>AvailabilityStartTime:</b> %{customdata[2]}<extra></extra>",
                    customdata=hover_data_2,
                ),
                row=get_row(2),
                col=1,
            )

            # Add red error lines when value changes
            prev_value = None
            error_lines_x = []
            for idx in valid_indices_2:
                current_value = availability_start_times[idx]
                if prev_value is not None and current_value != prev_value:
                    error_lines_x.append(request_times[idx])
                prev_value = current_value

            if error_lines_x:
                y_values = [availability_start_times[i] for i in valid_indices_2]
                y_min = min(y_values)
                y_max = max(y_values)
                y_range = y_max - y_min
                y_bottom = y_min - y_range * 0.05
                y_top = y_max + y_range * 0.05

                for error_x in error_lines_x:
                    error_time_str = format_time_only(error_x)
                    fig.add_trace(
                        go.Scatter(
                            x=[error_x, error_x],
                            y=[y_bottom, y_top],
                            mode="lines",
                            name="Error",
                            line=dict(color="rgba(255, 0, 0, 0.5)", width=5),
                            showlegend=False,
                            hovertemplate="<b>Availability Start Time Error</b><br>"
                            + "<b>Request Time:</b> "
                            + error_time_str
                            + "<br>"
                            + "<b>Issue:</b> Availability start time changed<br>"
                            + "<extra></extra>",
                        ),
                        row=get_row(2),
                        col=1,
                    )

    # Build period color mapping
    period_colors = get_period_color_palette()
    period_id_order = []
    period_id_seen = set()

    for dp in data_points:
        for period_info in dp["period_starts"]:
            if isinstance(period_info, dict):
                period_idx = period_info.get("period_index")
                period_id = period_info.get("period_id")
            else:
                period_idx = None
                period_id = None

            color_key = (
                period_id
                if period_id is not None
                else (f"idx_{period_idx}" if period_idx is not None else None)
            )
            if color_key and color_key not in period_id_seen:
                period_id_order.append(color_key)
                period_id_seen.add(color_key)

    for dp in data_points:
        period_spans = dp.get("period_segment_spans", [])
        for period_span in period_spans:
            period_idx = period_span.get("period_index")
            period_id = period_span.get("period_id")
            color_key = period_id if period_id is not None else f"idx_{period_idx}"
            if color_key and color_key not in period_id_seen:
                period_id_order.append(color_key)
                period_id_seen.add(color_key)

    period_id_to_color = {}
    for idx, color_key in enumerate(period_id_order):
        period_id_to_color[color_key] = period_colors[idx % len(period_colors)]

    # Plot 3: Period@start
    if show_period_starts:
        period_data = []
        for dp in data_points:
            request_time = dp["request_time"]
            request_id = dp["request_id"]
            for period_info in dp["period_starts"]:
                if isinstance(period_info, dict):
                    period_start = period_info.get("start_time")
                    period_idx = period_info.get("period_index")
                    period_id = period_info.get("period_id")
                else:
                    period_start = period_info
                    period_idx = None
                    period_id = None

                if isinstance(period_start, datetime):
                    period_data.append(
                        {
                            "request_time": request_time,
                            "request_id": request_id,
                            "period_start": period_start,
                            "period_index": period_idx,
                            "period_id": period_id,
                        }
                    )

        periods_seen = set()

        if period_data:
            all_period_y_values = [pd["period_start"] for pd in period_data]
            all_y_min = min(all_period_y_values)
            all_y_max = max(all_period_y_values)
            all_y_range = all_y_max - all_y_min
            if isinstance(all_y_range, timedelta):
                all_y_bottom = all_y_min - timedelta(
                    seconds=all_y_range.total_seconds() * 0.05
                )
                all_y_top = all_y_max + timedelta(
                    seconds=all_y_range.total_seconds() * 0.05
                )
            else:
                all_y_bottom = all_y_min - all_y_range * 0.05
                all_y_top = all_y_max + all_y_range * 0.05

            for pd in period_data:
                period_id = pd.get("period_id")
                period_idx = pd.get("period_index")
                color_key = (
                    period_id
                    if period_id is not None
                    else (f"idx_{period_idx}" if period_idx is not None else None)
                )
                if color_key not in period_id_to_color:
                    color_index = len(period_id_to_color) % len(period_colors)
                    period_id_to_color[color_key] = period_colors[color_index]

            for color_key in period_id_to_color:
                color = period_id_to_color[color_key]
                filtered_data = []
                for pd in period_data:
                    pd_period_id = pd.get("period_id")
                    pd_period_idx = pd.get("period_index")
                    pd_color_key = (
                        pd_period_id
                        if pd_period_id is not None
                        else (
                            f"idx_{pd_period_idx}"
                            if pd_period_idx is not None
                            else None
                        )
                    )
                    if pd_color_key == color_key:
                        filtered_data.append(pd)

                if not filtered_data:
                    continue

                first_pd = filtered_data[0]
                period_id = first_pd.get("period_id")
                period_idx = first_pd.get("period_index")
                legend_group_title = get_period_legend_group_title(
                    period_id, period_idx
                )
                show_legend = color_key not in periods_seen
                if show_legend:
                    periods_seen.add(color_key)

                customdata_list = []
                for pd in filtered_data:
                    pd_period_id = pd.get("period_id")
                    pd_period_idx = pd.get("period_index")
                    period_display = (
                        pd_period_id
                        if pd_period_id
                        else (
                            f"Period {pd_period_idx}"
                            if pd_period_idx is not None
                            else "Unknown"
                        )
                    )
                    customdata_list.append(
                        [
                            pd["request_id"],
                            format_time_only(pd["request_time"]),
                            format_time_only(pd["period_start"]),
                            period_display,
                        ]
                    )

                fig.add_trace(
                    go.Scatter(
                        x=[pd["request_time"] for pd in filtered_data],
                        y=[pd["period_start"] for pd in filtered_data],
                        mode="markers+lines",
                        name="Start time",
                        marker=dict(size=6, color=color),
                        line=dict(color=color),
                        hovertemplate="<b>Request ID:</b> %{customdata[0]}<br>"
                        + "<b>Period@start:</b> %{customdata[2]}<br>"
                        + "<b>Period:</b> %{customdata[3]}<extra></extra>",
                        customdata=customdata_list,
                        showlegend=show_legend,
                        legendgroup=f"period_{color_key}",
                        legendgrouptitle_text=legend_group_title,
                    ),
                    row=get_row(3),
                    col=1,
                )

                sorted_filtered_data = sorted(
                    filtered_data, key=lambda x: x["request_time"]
                )
                prev_value = None
                error_lines_x = []
                for pd in sorted_filtered_data:
                    current_value = pd["period_start"]
                    if prev_value is not None and current_value != prev_value:
                        error_lines_x.append(pd["request_time"])
                    prev_value = current_value

                if error_lines_x:
                    for error_x in error_lines_x:
                        error_time_str = format_time_only(error_x)
                        fig.add_trace(
                            go.Scatter(
                                x=[error_x, error_x],
                                y=[all_y_bottom, all_y_top],
                                mode="lines",
                                name="Error",
                                line=dict(color="rgba(255, 0, 0, 0.5)", width=5),
                                showlegend=False,
                                hovertemplate="<b>Period Start Time Error</b><br>"
                                + "<b>Request Time:</b> "
                                + error_time_str
                                + "<br>"
                                + "<b>Issue:</b> Period start time changed<br>"
                                + "<extra></extra>",
                            ),
                            row=get_row(3),
                            col=1,
                        )

    # Plot 5: Horizontal bar chart showing period spans
    all_period_spans_for_bars = []
    for dp in data_points:
        period_spans = dp.get("period_segment_spans", [])
        for period_span in period_spans:
            first_start = period_span.get("first_segment_start")
            last_end = period_span.get("last_segment_end")
            if first_start is not None and last_end is not None:
                if isinstance(first_start, datetime) and isinstance(last_end, datetime):
                    all_period_spans_for_bars.append(
                        {
                            "period_index": period_span.get("period_index"),
                            "period_id": period_span.get("period_id"),
                            "start": first_start,
                            "end": last_end,
                        }
                    )

    if all_period_spans_for_bars:
        periods_overall_spans = {}
        for span in all_period_spans_for_bars:
            period_idx = span["period_index"]
            period_id = span.get("period_id")
            color_key = period_id if period_id is not None else f"idx_{period_idx}"

            if color_key not in periods_overall_spans:
                periods_overall_spans[color_key] = {
                    "period_id": period_id,
                    "period_idx": period_idx,
                    "earliest_start": span["start"],
                    "latest_end": span["end"],
                    "has_ads": False,
                }
            else:
                if span["start"] < periods_overall_spans[color_key]["earliest_start"]:
                    periods_overall_spans[color_key]["earliest_start"] = span["start"]
                if span["end"] > periods_overall_spans[color_key]["latest_end"]:
                    periods_overall_spans[color_key]["latest_end"] = span["end"]

        for dp in data_points:
            period_all_segments = dp.get("period_all_segments", [])
            for period_segments_info in period_all_segments:
                seg_period_idx = period_segments_info.get("period_index")
                seg_period_id = period_segments_info.get("period_id")
                segments = period_segments_info.get("segments", [])

                for color_key, period_info in periods_overall_spans.items():
                    period_id = period_info["period_id"]
                    period_idx = period_info["period_idx"]

                    if (seg_period_id is not None and seg_period_id == period_id) or (
                        seg_period_id is None and seg_period_idx == period_idx
                    ):
                        for seg in segments:
                            if seg.get("is_ad", False):
                                periods_overall_spans[color_key]["has_ads"] = True
                                break
                        if periods_overall_spans[color_key]["has_ads"]:
                            break

        sorted_periods = sorted(
            periods_overall_spans.items(), key=lambda x: x[1]["earliest_start"]
        )

        period_labels = []
        bar_starts = []
        bar_ends = []
        bar_colors = []
        hover_texts = []
        period_has_ads = []
        period_color_keys = []

        for i, (color_key, period_info) in enumerate(sorted_periods):
            period_id = period_info["period_id"]
            period_idx = period_info["period_idx"]

            if period_id is not None:
                period_label = f"Period {period_id}"
            elif period_idx is not None:
                period_label = f"Period {period_idx}"
            else:
                period_label = "Period"

            period_labels.append(period_label)
            period_color_keys.append(color_key)

            if color_key not in period_id_to_color:
                color_index = len(period_id_to_color) % len(period_colors)
                period_id_to_color[color_key] = period_colors[color_index]

            bar_colors.append(period_id_to_color[color_key])

            earliest_start = period_info["earliest_start"]
            latest_end = period_info["latest_end"]
            has_ads = period_info.get("has_ads", False)

            bar_starts.append(earliest_start)
            bar_ends.append(latest_end)
            period_has_ads.append(has_ads)

            duration = latest_end - earliest_start
            duration_seconds = duration.total_seconds()
            duration_str = f"{duration_seconds:.2f}s"

            hover_texts.append(
                f"<b>{period_label}</b><br>"
                + f"<b>Start:</b> {format_time_only(earliest_start)}<br>"
                + f"<b>End:</b> {format_time_only(latest_end)}<br>"
                + f"<b>Duration:</b> {duration_str}<extra></extra>"
            )

        for i, (label, start, end, color, hover_text, has_ads, color_key) in enumerate(
            zip(
                period_labels,
                bar_starts,
                bar_ends,
                bar_colors,
                hover_texts,
                period_has_ads,
                period_color_keys,
            )
        ):
            period_info = periods_overall_spans[color_key]
            period_id = period_info["period_id"]
            period_idx = period_info["period_idx"]
            legend_group_title = get_period_legend_group_title(period_id, period_idx)
            mid_time = start + (end - start) / 2

            if has_ads:
                fig.add_trace(
                    go.Scatter(
                        x=[start, end],
                        y=[0, 0],
                        mode="lines",
                        name="Ad Period",
                        line=dict(color="gold", width=35),
                        showlegend=False,
                        hoverinfo="skip",
                        legendgroup=f"period_{color_key}",
                        legendgrouptitle_text=legend_group_title,
                    ),
                    row=get_row(5),
                    col=1,
                )

            fig.add_trace(
                go.Scatter(
                    x=[start, end],
                    y=[0, 0],
                    mode="lines",
                    name=label,
                    line=dict(color=color, width=20),
                    showlegend=False,
                    hovertemplate=hover_text,
                    legendgroup=f"period_{color_key}",
                    legendgrouptitle_text=legend_group_title,
                ),
                row=get_row(5),
                col=1,
            )

            annotation_text = "A" if has_ads else "C"
            fig.add_trace(
                go.Scatter(
                    x=[mid_time],
                    y=[0],
                    mode="text",
                    text=[annotation_text],
                    textfont=dict(size=10, color="black"),
                    showlegend=False,
                    hoverinfo="skip",
                    legendgroup=f"period_{color_key}",
                    legendgrouptitle_text=legend_group_title,
                ),
                row=get_row(5),
                col=1,
            )

        fig.update_xaxes(
            title_text="Media Timeline",
            title_standoff=0,
            type="date",
            matches=None,
            row=get_row(5),
            col=1,
        )

        fig.update_yaxes(
            showticklabels=False,
            showgrid=False,
            title_text="",
            row=get_row(5),
            col=1,
        )

    # Plot 4: Segment span (first segment start to last segment end) for all periods
    # Show vertical bars representing the span of segments for each MPD, with different colors per period
    all_period_spans = []
    for dp in data_points:
        request_time = dp["request_time"]
        request_id = dp["request_id"]
        period_spans = dp.get("period_segment_spans", [])

        for period_span in period_spans:
            first_start = period_span.get("first_segment_start")
            last_end = period_span.get("last_segment_end")

            if first_start is not None and last_end is not None:
                if isinstance(first_start, datetime) and isinstance(last_end, datetime):
                    all_period_spans.append(
                        {
                            "request_time": request_time,
                            "request_id": request_id,
                            "period_index": period_span.get("period_index"),
                            "period_id": period_span.get("period_id"),
                            "start": first_start,
                            "end": last_end,
                        }
                    )

    if all_period_spans:
        # Calculate y-axis range for Plot 4 (for validation error lines)
        all_span_y_values = []
        for span in all_period_spans:
            all_span_y_values.append(span["start"])
            all_span_y_values.append(span["end"])

        # Also include event presentation times and end times
        for dp in data_points:
            events = dp.get("events", [])
            for event in events:
                presentation_time = event.get("presentation_time")
                if presentation_time is not None:
                    all_span_y_values.append(presentation_time)
                    duration = event.get("duration")
                    if duration is not None:
                        if isinstance(duration, timedelta):
                            end_time = presentation_time + duration
                        elif isinstance(duration, (int, float)):
                            end_time = presentation_time + timedelta(seconds=duration)
                        else:
                            end_time = presentation_time
                        all_span_y_values.append(end_time)

        if all_span_y_values:
            plot4_y_min = min(all_span_y_values)
            plot4_y_max = max(all_span_y_values)
            plot4_y_range = plot4_y_max - plot4_y_min
            if isinstance(plot4_y_range, timedelta):
                plot4_y_bottom = plot4_y_min - timedelta(
                    seconds=plot4_y_range.total_seconds() * 0.05
                )
                plot4_y_top = plot4_y_max + timedelta(
                    seconds=plot4_y_range.total_seconds() * 0.05
                )
            else:
                plot4_y_bottom = plot4_y_min - plot4_y_range * 0.05
                plot4_y_top = plot4_y_max + plot4_y_range * 0.05
        else:
            plot4_y_bottom = None
            plot4_y_top = None

        # Group spans by period (color_key)
        spans_by_period = {}
        for span in all_period_spans:
            period_idx = span["period_index"]
            period_id = span.get("period_id")
            color_key = period_id if period_id is not None else f"idx_{period_idx}"

            # Get color from the mapping created in Plot 3 (or assign if somehow missing)
            if color_key not in period_id_to_color:
                # Fallback: assign next available color
                color_index = len(period_id_to_color) % len(period_colors)
                period_id_to_color[color_key] = period_colors[color_index]

            if color_key not in spans_by_period:
                spans_by_period[color_key] = []
            spans_by_period[color_key].append(span)

        # Collect events from all data points and group by period
        # Also track events by request_time for validation
        events_by_period = {}
        events_by_request = {}  # Track events by request_time for validation

        for dp in data_points:
            request_time = dp["request_time"]
            request_id = dp["request_id"]
            events = dp.get("events", [])

            # Store events for this request
            events_by_request[request_time] = []

            for event in events:
                presentation_time = event.get("presentation_time")
                if presentation_time is not None:
                    period_idx = event.get("period_index")
                    period_id = event.get("period_id")

                    # Create color_key same as used for periods
                    color_key = (
                        period_id if period_id is not None else f"idx_{period_idx}"
                    )

                    if color_key not in events_by_period:
                        events_by_period[color_key] = {
                            "with_duration": [],
                            "without_duration": [],
                        }

                    event_data = {
                        "request_time": request_time,
                        "request_id": request_id,
                        "presentation_time": presentation_time,
                        "duration": event.get("duration"),
                        "event_id": event.get("event_id"),
                        "message_data": event.get("message_data"),
                        "period_idx": period_idx,
                        "period_id": period_id,
                        "color_key": color_key,
                    }

                    events_by_request[request_time].append(event_data)

                    if event_data["duration"] is not None:
                        events_by_period[color_key]["with_duration"].append(event_data)
                    else:
                        events_by_period[color_key]["without_duration"].append(
                            event_data
                        )

        # Validation: Check for event issues
        # 1. Events with ID that change presentation_time
        # 2. Events with duration that disappear but segments still exist in that span
        event_validation_errors = []

        # Sort request times
        sorted_request_times = sorted(events_by_request.keys())

        # Track previous events by period, then by ID and by (presentation_time, duration)
        prev_events_by_period = {}

        for request_time in sorted_request_times:
            current_events = events_by_request[request_time]

            # Group current events by period
            current_events_by_period = {}
            for e in current_events:
                color_key = e["color_key"]
                if color_key not in current_events_by_period:
                    current_events_by_period[color_key] = {
                        "by_id": {},
                        "by_key": {},
                    }

                # Track by ID if available
                if e.get("event_id") is not None:
                    current_events_by_period[color_key]["by_id"][e["event_id"]] = e

                # Track by (presentation_time, duration) if duration exists
                if e.get("duration") is not None:
                    duration = e["duration"]
                    if isinstance(duration, timedelta):
                        duration_seconds = duration.total_seconds()
                    elif isinstance(duration, (int, float)):
                        duration_seconds = duration
                    else:
                        duration_seconds = 0

                    key = (e["presentation_time"], duration_seconds)
                    current_events_by_period[color_key]["by_key"][key] = e

            # Get all periods we need to check (both current and previous)
            all_periods_to_check = set(current_events_by_period.keys())
            all_periods_to_check.update(prev_events_by_period.keys())

            # Check each period (including periods that had events before but not now)
            for color_key in all_periods_to_check:
                # Get current events for this period (empty dict if no events)
                current_period_events = current_events_by_period.get(
                    color_key, {"by_id": {}, "by_key": {}}
                )
                if color_key not in prev_events_by_period:
                    prev_events_by_period[color_key] = {
                        "by_id": {},
                        "by_key": {},
                    }

                prev_period_events = prev_events_by_period[color_key]

                # Check for events with ID that changed presentation_time
                for event_id, prev_event in prev_period_events["by_id"].items():
                    if event_id in current_period_events["by_id"]:
                        current_event = current_period_events["by_id"][event_id]
                        if (
                            current_event["presentation_time"]
                            != prev_event["presentation_time"]
                        ):
                            # Event ID changed presentation_time
                            event_validation_errors.append(
                                {
                                    "request_time": request_time,
                                    "issue": "event_presentation_time_changed",
                                    "event_id": event_id,
                                    "prev_presentation_time": prev_event[
                                        "presentation_time"
                                    ],
                                    "current_presentation_time": current_event[
                                        "presentation_time"
                                    ],
                                    "period_idx": current_event["period_idx"],
                                    "period_id": current_event["period_id"],
                                    "color_key": color_key,
                                }
                            )

                # Check for events with duration that disappeared
                for key, prev_event in prev_period_events["by_key"].items():
                    if key not in current_period_events["by_key"]:
                        # Event disappeared - check if segments still exist in that span
                        presentation_time, duration_seconds = key
                        if isinstance(duration_seconds, (int, float)):
                            end_time = presentation_time + timedelta(
                                seconds=duration_seconds
                            )
                        else:
                            end_time = presentation_time

                        # Find the data point for current request
                        current_dp = next(
                            (
                                dp
                                for dp in data_points
                                if dp["request_time"] == request_time
                            ),
                            None,
                        )

                        if current_dp:
                            # Check if segments exist in this time span for ANY period
                            period_all_segments = current_dp.get(
                                "period_all_segments", []
                            )

                            segments_exist = False
                            # Check all periods' segments, not just the same period
                            for period_segments_info in period_all_segments:
                                # Check if any segment start_time is within the event span
                                for seg in period_segments_info.get("segments", []):
                                    seg_start = seg.get("start_time")
                                    if seg_start is not None:
                                        if presentation_time <= seg_start <= end_time:
                                            segments_exist = True
                                            break
                                if segments_exist:
                                    break

                            if segments_exist:
                                # Event disappeared but segments still exist
                                event_validation_errors.append(
                                    {
                                        "request_time": request_time,
                                        "issue": "event_disappeared_with_segments",
                                        "presentation_time": presentation_time,
                                        "duration": duration_seconds,
                                        "end_time": end_time,
                                        "period_idx": prev_event["period_idx"],
                                        "period_id": prev_event["period_id"],
                                        "color_key": color_key,
                                    }
                                )

                # Update previous events for this period
                prev_events_by_period[color_key] = {
                    "by_id": current_period_events["by_id"].copy(),
                    "by_key": current_period_events["by_key"].copy(),
                }

        periods_seen = set()

        # Process each period group
        for color_key, period_spans in spans_by_period.items():
            # Sort spans by request_time for this period
            sorted_spans = sorted(period_spans, key=lambda x: x["request_time"])

            # Get period info from first span
            first_span = sorted_spans[0]
            period_idx = first_span["period_index"]
            period_id = first_span.get("period_id")
            color = period_id_to_color[color_key]

            # Generate legend group title
            legend_group_title = get_period_legend_group_title(period_id, period_idx)

            # Only show legend for the first occurrence of each period ID
            show_legend = color_key not in periods_seen
            if show_legend:
                periods_seen.add(color_key)

            # Extract data for connecting lines
            request_times = [span["request_time"] for span in sorted_spans]
            start_times = [span["start"] for span in sorted_spans]
            end_times = [span["end"] for span in sorted_spans]

            # Set line width and opacity based on show_segments
            if show_segments:
                line_width = 6
                line_opacity = 0.3
            else:
                line_width = 3
                line_opacity = 1.0

            # Plot events for this period BEFORE span lines (so they appear behind)
            if color_key in events_by_period:
                period_events = events_by_period[color_key]
                events_shown_in_legend_for_period = False

                # Plot events with duration as vertical lines
                for event in period_events["with_duration"]:
                    presentation_time = event["presentation_time"]
                    duration = event["duration"]
                    request_time = event["request_time"]

                    # Calculate end time (presentation_time + duration)
                    if isinstance(duration, timedelta):
                        end_time = presentation_time + duration
                        duration_seconds = duration.total_seconds()
                    elif isinstance(duration, (int, float)):
                        end_time = presentation_time + timedelta(seconds=duration)
                        duration_seconds = duration
                    else:
                        end_time = presentation_time
                        duration_seconds = 0

                    event_id = event.get("event_id", "")
                    message_data = event.get("message_data", "")

                    # Format hover text
                    duration_str = f"{duration_seconds:.2f}s"
                    hover_text = "<b>MPD Event</b><br>"
                    if event_id:
                        hover_text += f"<b>Event ID:</b> {event_id}<br>"
                    hover_text += (
                        f"<b>Presentation Time:</b> {format_time_only(presentation_time)}<br>"
                        + f"<b>Duration:</b> {duration_str}"
                    )
                    if message_data:
                        hover_text += f"<br><b>Message Data:</b> {message_data}"
                    hover_text += "<extra></extra>"

                    # Use 9px wide semi-transparent vertical line (green for events)
                    fig.add_trace(
                        go.Scatter(
                            x=[request_time, request_time],
                            y=[presentation_time, end_time],
                            mode="lines",
                            name="Events",
                            line=dict(color="green", width=9),
                            opacity=0.10,
                            showlegend=False,
                            hovertemplate=hover_text,
                            legendgroup=f"period_{color_key}",
                            legendgrouptitle_text=legend_group_title,
                        ),
                        row=get_row(4),
                        col=1,
                    )

                    # Add triangle-down marker at presentation_time
                    fig.add_trace(
                        go.Scatter(
                            x=[request_time],
                            y=[presentation_time],
                            mode="markers",
                            name="Events",
                            marker=dict(
                                size=8, color="green", symbol="triangle-down-open"
                            ),
                            showlegend=not events_shown_in_legend_for_period,
                            hovertemplate=hover_text,
                            legendgroup=f"period_{color_key}",
                            legendgrouptitle_text=legend_group_title,
                        ),
                        row=get_row(4),
                        col=1,
                    )

                    # Add triangle-up marker at end_time
                    fig.add_trace(
                        go.Scatter(
                            x=[request_time],
                            y=[end_time],
                            mode="markers",
                            name="Event End",
                            marker=dict(
                                size=8, color="green", symbol="triangle-up-open"
                            ),
                            showlegend=False,
                            hovertemplate=hover_text,
                            legendgroup=f"period_{color_key}",
                            legendgrouptitle_text=legend_group_title,
                        ),
                        row=get_row(4),
                        col=1,
                    )
                    events_shown_in_legend_for_period = True

                # Plot events without duration as markers
                if period_events["without_duration"]:
                    hover_data = [
                        [
                            event.get("event_id", ""),
                            format_time_only(event["presentation_time"]),
                            event.get("message_data", ""),
                        ]
                        for event in period_events["without_duration"]
                    ]

                    fig.add_trace(
                        go.Scatter(
                            x=[
                                e["request_time"]
                                for e in period_events["without_duration"]
                            ],
                            y=[
                                e["presentation_time"]
                                for e in period_events["without_duration"]
                            ],
                            mode="markers",
                            name="Events",
                            marker=dict(size=12, color="green", symbol="triangle-down"),
                            showlegend=not events_shown_in_legend_for_period,
                            hovertemplate="<b>MPD Event</b><br>"
                            + (
                                "<b>Event ID:</b> %{customdata[0]}<br>"
                                if any(
                                    e.get("event_id")
                                    for e in period_events["without_duration"]
                                )
                                else ""
                            )
                            + "<b>Presentation Time:</b> %{customdata[1]}<br>"
                            + (
                                "<b>Message Data:</b> %{customdata[2]}<br>"
                                if any(
                                    e.get("message_data")
                                    for e in period_events["without_duration"]
                                )
                                else ""
                            )
                            + "<extra></extra>",
                            customdata=hover_data,
                            legendgroup=f"period_{color_key}",
                            legendgrouptitle_text=legend_group_title,
                        ),
                        row=get_row(4),
                        col=1,
                    )

            # Plot ad spans for this period
            # Find ad segments and group them into spans
            ad_spans_shown_in_legend_for_period = False
            for dp in data_points:
                request_time = dp["request_time"]
                request_id = dp["request_id"]
                period_all_segments = dp.get("period_all_segments", [])

                # Find segments for this period
                for period_segments_info in period_all_segments:
                    seg_period_idx = period_segments_info.get("period_index")
                    seg_period_id = period_segments_info.get("period_id")

                    # Match by period_id if available, otherwise by period_index
                    if (seg_period_id is not None and seg_period_id == period_id) or (
                        seg_period_id is None and seg_period_idx == period_idx
                    ):
                        segments = period_segments_info.get("segments", [])

                        # Group consecutive ad segments into spans
                        ad_spans = []
                        current_ad_span = None

                        for seg in segments:
                            if seg.get("is_ad", False):
                                seg_start = seg.get("start_time")
                                seg_end = seg.get("end_time")

                                if seg_start is not None:
                                    if current_ad_span is None:
                                        # Start new ad span
                                        current_ad_span = {
                                            "start": seg_start,
                                            "end": seg_end if seg_end else seg_start,
                                        }
                                    else:
                                        # Extend current ad span
                                        if seg_end:
                                            current_ad_span["end"] = seg_end
                                        else:
                                            current_ad_span["end"] = seg_start
                            else:
                                # Non-ad segment - close current span if any
                                if current_ad_span is not None:
                                    ad_spans.append(current_ad_span)
                                    current_ad_span = None

                        # Close any remaining span
                        if current_ad_span is not None:
                            ad_spans.append(current_ad_span)

                        # Plot ad spans
                        for ad_span in ad_spans:
                            span_start = ad_span["start"]
                            span_end = ad_span["end"]

                            # Plot as semi-transparent gold vertical line
                            fig.add_trace(
                                go.Scatter(
                                    x=[request_time, request_time],
                                    y=[span_start, span_end],
                                    mode="lines",
                                    name="Ad",
                                    line=dict(color="gold", width=11),
                                    opacity=0.9,
                                    showlegend=not ad_spans_shown_in_legend_for_period,
                                    hoverinfo="skip",
                                    legendgroup=f"period_{color_key}",
                                    legendgrouptitle_text=legend_group_title,
                                ),
                                row=get_row(4),
                                col=1,
                            )
                            ad_spans_shown_in_legend_for_period = True

                        # Only process segments for this period once
                        break

            # Add vertical lines from start to end for each span
            # Only show legend for the first trace of this period
            for idx, span in enumerate(sorted_spans):
                request_id = span["request_id"]
                period_id_display = period_id if period_id else f"Period {period_idx}"
                start_time_str = format_time_only(span["start"])
                end_time_str = format_time_only(span["end"])

                # Calculate total segment duration and count for this span
                total_duration = None
                segment_count = 0
                # Find the data point that corresponds to this span
                for dp in data_points:
                    if dp["request_id"] == request_id:
                        period_all_segments = dp.get("period_all_segments", [])
                        # Find segments for this period
                        for period_segments_info in period_all_segments:
                            seg_period_idx = period_segments_info.get("period_index")
                            seg_period_id = period_segments_info.get("period_id")

                            # Match by period_id if available, otherwise by period_index
                            if (
                                seg_period_id is not None and seg_period_id == period_id
                            ) or (
                                seg_period_id is None and seg_period_idx == period_idx
                            ):
                                segments = period_segments_info.get("segments", [])
                                segment_count = len(segments)
                                # Sum all segment durations
                                durations = [
                                    seg.get("duration")
                                    for seg in segments
                                    if seg.get("duration") is not None
                                ]
                                if durations:
                                    total_duration = sum(durations)
                                break
                        break

                # Format total duration for display
                total_duration_str = (
                    f"{total_duration:.2f}s" if total_duration is not None else "N/A"
                )

                fig.add_trace(
                    go.Scatter(
                        x=[span["request_time"], span["request_time"]],
                        y=[span["start"], span["end"]],
                        mode="lines+markers",
                        name="Span",
                        line=dict(width=line_width, color=color),
                        marker=dict(size=4),
                        opacity=line_opacity,
                        showlegend=show_legend
                        and idx == 0,  # Only show legend for first trace
                        legendgroup=f"period_{color_key}",
                        legendgrouptitle_text=legend_group_title,
                        hovertemplate="<b><u>Period:</u></b> "
                        + period_id_display
                        + "<br>"
                        + "<b>Request ID:</b> "
                        + request_id
                        + "<br>"
                        + "<b>Number of Segments:</b> "
                        + str(segment_count)
                        + "<br>"
                        + "<b>Segments:</b> "
                        + start_time_str
                        + " -> "
                        + end_time_str
                        + "<br>"
                        + "<b>Duration:</b> "
                        + total_duration_str
                        + "<extra></extra>",
                    ),
                    row=get_row(4),
                    col=1,
                )

            # Add individual segment dots if show_segments is True
            if show_segments:
                # Collect segments only from data points that have a span for this period
                span_request_ids = {span["request_id"] for span in sorted_spans}

                all_segment_dots = []
                for dp in data_points:
                    # Only process data points that have a span for this period
                    if dp["request_id"] not in span_request_ids:
                        continue

                    request_time = dp["request_time"]
                    request_id = dp["request_id"]
                    period_all_segments = dp.get("period_all_segments", [])

                    # Find segments for this period
                    for period_segments_info in period_all_segments:
                        seg_period_idx = period_segments_info.get("period_index")
                        seg_period_id = period_segments_info.get("period_id")

                        # Match by period_id if available, otherwise by period_index
                        if seg_period_id is not None and seg_period_id == period_id:
                            # Match by period_id
                            for seg in period_segments_info.get("segments", []):
                                seg_start = seg.get("start_time")
                                if seg_start is not None:
                                    all_segment_dots.append(
                                        {
                                            "request_time": request_time,
                                            "request_id": request_id,
                                            "start_time": seg_start,
                                            "duration": seg.get("duration"),
                                            "position": seg.get("position", 0),
                                            "uri": seg.get("uri"),
                                            "period_id": period_id,
                                        }
                                    )
                            break
                        elif seg_period_idx == period_idx:
                            # Match by period_index
                            for seg in period_segments_info.get("segments", []):
                                seg_start = seg.get("start_time")
                                if seg_start is not None:
                                    all_segment_dots.append(
                                        {
                                            "request_time": request_time,
                                            "request_id": request_id,
                                            "start_time": seg_start,
                                            "duration": seg.get("duration"),
                                            "position": seg.get("position", 0),
                                            "uri": seg.get("uri"),
                                            "period_id": period_id,
                                        }
                                    )
                            break

                # Plot individual segments as dots
                if all_segment_dots:
                    hover_data = [
                        [
                            dot["position"],
                            extract_filename_from_uri(dot.get("uri", "") or ""),
                            format_time_only(dot["start_time"]),
                            f"{dot['duration']:.2f}s"
                            if dot["duration"] is not None
                            else "N/A",
                        ]
                        for dot in all_segment_dots
                    ]

                    fig.add_trace(
                        go.Scatter(
                            x=[dot["request_time"] for dot in all_segment_dots],
                            y=[dot["start_time"] for dot in all_segment_dots],
                            mode="markers",
                            name="Segments",
                            marker=dict(size=4, color=color),
                            showlegend=show_legend,  # Show legend only for first period
                            legendgroup=f"period_{color_key}",
                            legendgrouptitle_text=legend_group_title,
                            hovertemplate="<b>Segment</b> #%{customdata[0]}<br>"
                            + "<b>Segment URL:</b> %{customdata[1]}<br>"
                            + "<b>At:</b> %{customdata[2]}<br>"
                            + "<b>Duration:</b> %{customdata[3]}<extra></extra>",
                            customdata=hover_data,
                        ),
                        row=get_row(4),
                        col=1,
                    )

            # Add lines connecting consecutive start points
            if len(sorted_spans) > 1:
                fig.add_trace(
                    go.Scatter(
                        x=request_times,
                        y=start_times,
                        mode="lines",
                        name="Start connection",
                        line=dict(width=1, color=color, dash="dot"),
                        showlegend=False,
                        legendgroup=f"period_{color_key}",
                        legendgrouptitle_text=legend_group_title,
                        hoverinfo="skip",
                    ),
                    row=get_row(4),
                    col=1,
                )

            # Add lines connecting consecutive end points
            if len(sorted_spans) > 1:
                fig.add_trace(
                    go.Scatter(
                        x=request_times,
                        y=end_times,
                        mode="lines",
                        name="End connection",
                        line=dict(width=1, color=color, dash="dot"),
                        showlegend=False,
                        legendgroup=f"period_{color_key}",
                        legendgrouptitle_text=legend_group_title,
                        hoverinfo="skip",
                    ),
                    row=get_row(4),
                    col=1,
                )

        # Add validation error bars for events
        if (
            event_validation_errors
            and plot4_y_bottom is not None
            and plot4_y_top is not None
        ):
            for error in event_validation_errors:
                request_time = error["request_time"]
                error_time_str = format_time_only(request_time)

                if error["issue"] == "event_presentation_time_changed":
                    issue_text = (
                        f"Event ID {error['event_id']} presentation time changed"
                    )
                    prev_time_str = format_time_only(error["prev_presentation_time"])
                    curr_time_str = format_time_only(error["current_presentation_time"])
                    hover_text = (
                        "<b>Event Validation Error</b><br>"
                        + f"<b>Request Time:</b> {error_time_str}<br>"
                        + f"<b>Issue:</b> {issue_text}<br>"
                        + f"<b>Previous:</b> {prev_time_str}<br>"
                        + f"<b>Current:</b> {curr_time_str}<extra></extra>"
                    )
                elif error["issue"] == "event_disappeared_with_segments":
                    pres_time_str = format_time_only(error["presentation_time"])
                    end_time_str = format_time_only(error["end_time"])
                    duration_str = f"{error['duration']:.2f}s"
                    issue_text = "Event disappeared but segments still exist in span"
                    hover_text = (
                        "<b>Event Validation Error</b><br>"
                        + f"<b>Request Time:</b> {error_time_str}<br>"
                        + f"<b>Issue:</b> {issue_text}<br>"
                        + f"<b>Event Span:</b> {pres_time_str} - {end_time_str} ({duration_str})<extra></extra>"
                    )
                else:
                    hover_text = (
                        "<b>Event Validation Error</b><br>"
                        + f"<b>Request Time:</b> {error_time_str}<br>"
                        + f"<b>Issue:</b> {error['issue']}<extra></extra>"
                    )

                fig.add_trace(
                    go.Scatter(
                        x=[request_time, request_time],
                        y=[plot4_y_bottom, plot4_y_top],
                        mode="lines",
                        name="Error",
                        line=dict(color="rgba(255, 0, 0, 0.5)", width=5),
                        showlegend=False,
                        hovertemplate=hover_text,
                    ),
                    row=get_row(4),
                    col=1,
                )

    # Build subtitle from first MPD URL
    subtitle_parts = []
    if first_mpd_url:
        domain_path = (
            f"<b>Domain:</b> {first_mpd_url.host} | <b>Path:</b> {first_mpd_url.path}"
        )
        subtitle_parts.append(domain_path)

        bpkio_sessionid = first_mpd_url.query.get("bpkio_sessionid")
        bpkio_serviceid = first_mpd_url.query.get("bpkio_serviceid")
        if bpkio_serviceid:
            subtitle_parts.append(f"<b>Service ID:</b> {bpkio_serviceid}")
        if bpkio_sessionid:
            subtitle_parts.append(f"<b>Session ID:</b> {bpkio_sessionid}")

    subtitle = " | ".join(subtitle_parts) if subtitle_parts else None

    total_height = sum(row_heights)
    layout_dict = {
        "height": total_height,
        "showlegend": True,
        "hovermode": "closest",
        "hoversubplots": "axis",  # Enable cross-subplot hover with spike lines
        "legend": dict(indentation=20),
        "modebar_add": [
            "toggleSpikeLines",
            "toggleSpikes",
            "toggleRangeSelector",
            "toggleHover",
            "toggleSpikey",
        ],
    }
    if subtitle:
        layout_dict["title"] = {
            "text": "Live DASH Analysis",
            "subtitle": {"text": subtitle},
        }
    else:
        layout_dict["title"] = "Live DASH Analysis"

    fig.update_layout(**layout_dict)

    # Update x-axis labels
    first_request_time_row = None
    for plot_num in [1, 2, 3, 4]:
        if plot_num in plot_to_row:
            first_request_time_row = plot_to_row[plot_num]
            break

    for plot_num in [1, 2, 3, 4, 5]:
        if plot_num not in plot_to_row:
            continue
        actual_row = plot_to_row[plot_num]

        if plot_num == 5:
            # Plot 5: Independent x-axis (Segment Time) - add spike lines for crosshair
            fig.update_xaxes(
                showspikes=True,
                spikemode="across",
                spikesnap="cursor",
                spikedash="solid",
                spikethickness=1,
                spikecolor="gray",
                row=actual_row,
                col=1,
            )
            continue
        elif plot_num == 4:
            if first_request_time_row and actual_row != first_request_time_row:
                matches_ref = (
                    f"x{first_request_time_row}" if first_request_time_row > 1 else "x"
                )
                fig.update_xaxes(
                    title_text="Request Time",
                    title_standoff=0,
                    matches=matches_ref,
                    showspikes=True,
                    spikemode="across",
                    spikesnap="cursor",
                    spikedash="solid",
                    spikethickness=1,
                    spikecolor="gray",
                    row=actual_row,
                    col=1,
                )
            else:
                fig.update_xaxes(
                    title_text="Request Time",
                    title_standoff=0,
                    showspikes=True,
                    spikemode="across",
                    spikesnap="cursor",
                    spikedash="solid",
                    spikethickness=1,
                    spikecolor="gray",
                    row=actual_row,
                    col=1,
                )
        else:
            if first_request_time_row and actual_row != first_request_time_row:
                matches_ref = (
                    f"x{first_request_time_row}" if first_request_time_row > 1 else "x"
                )
                fig.update_xaxes(
                    title_text="",
                    matches=matches_ref,
                    showspikes=True,
                    spikemode="across",
                    spikesnap="cursor",
                    spikedash="solid",
                    spikethickness=1,
                    spikecolor="gray",
                    row=actual_row,
                    col=1,
                )
            else:
                fig.update_xaxes(
                    title_text="",
                    showspikes=True,
                    spikemode="across",
                    spikesnap="cursor",
                    spikedash="solid",
                    spikethickness=1,
                    spikecolor="gray",
                    row=actual_row,
                    col=1,
                )

    # Update y-axis labels with spike lines for crosshair
    if show_publish_time and 1 in plot_to_row:
        fig.update_yaxes(
            title_text="Media Timeline",
            title_standoff=0,
            row=get_row(1),
            col=1,
            autorange="reversed",
            showspikes=True,
            spikemode="across",
            spikesnap="cursor",
            spikedash="solid",
            spikethickness=1,
            spikecolor="gray",
        )
    if show_availability_start_time and 2 in plot_to_row:
        fig.update_yaxes(
            title_text="Media Timeline",
            title_standoff=0,
            row=get_row(2),
            col=1,
            autorange="reversed",
            showspikes=True,
            spikemode="across",
            spikesnap="cursor",
            spikedash="solid",
            spikethickness=1,
            spikecolor="gray",
        )
    if show_period_starts and 3 in plot_to_row:
        fig.update_yaxes(
            title_text="Media Timeline",
            title_standoff=0,
            row=get_row(3),
            col=1,
            autorange="reversed",
            showspikes=True,
            spikemode="across",
            spikesnap="cursor",
            spikedash="solid",
            spikethickness=1,
            spikecolor="gray",
        )
    if 4 in plot_to_row:
        fig.update_yaxes(
            title_text="Media Timeline",
            title_standoff=0,
            row=get_row(4),
            col=1,
            autorange="reversed",
            showspikes=True,
            spikemode="across",
            spikesnap="cursor",
            spikedash="solid",
            spikethickness=1,
            spikecolor="gray",
        )

    return fig
