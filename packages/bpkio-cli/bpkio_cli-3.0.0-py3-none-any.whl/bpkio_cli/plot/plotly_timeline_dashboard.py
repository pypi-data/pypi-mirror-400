from datetime import datetime
from pathlib import Path
from typing import Callable

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from dash import dcc, html
from dash.dependencies import Input, Output, State
from loguru import logger


def make_dashboard(
    title: str = "bic - Interactive Timeline",
    refresh_interval: int = 10,
    plotly_config: dict = None,
    generate_figure_fn: Callable = None,
):
    app = dash.Dash(
        "MPDTimeline",
        title=title,
        external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    )

    # Create the layout with Bootstrap styling
    app.layout = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(html.H3(title, className="mt-4 mb-4"), width="auto"),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Button(
                                                    [
                                                        html.I(
                                                            className="bi bi-camera-fill me-1"
                                                        ),
                                                        "Save Snapshot",
                                                    ],
                                                    id="save-button",
                                                    color="secondary",
                                                    size="sm",
                                                ),
                                            ],
                                            width="auto",
                                        ),
                                    ],
                                    className="align-items-center",
                                ),
                                className="p-2",
                            ),
                            className="mb-3",
                        ),
                        width="auto",
                        className="ms-auto",
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                children=[
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.InputGroup(
                                                        [
                                                            dbc.InputGroupText(
                                                                "Auto-refresh:"
                                                            ),
                                                            dbc.Input(
                                                                id="refresh-interval-input",
                                                                type="number",
                                                                min=1,
                                                                max=60,
                                                                value=refresh_interval,
                                                                style={"width": "70px"},
                                                            ),
                                                            dbc.InputGroupText(
                                                                "seconds"
                                                            ),
                                                            dbc.Button(
                                                                [
                                                                    html.I(
                                                                        className="bi bi-pause-fill me-1"
                                                                    ),
                                                                    "Pause",
                                                                ],
                                                                id="pause-button",
                                                                color="danger",
                                                                size="sm",
                                                            ),
                                                        ],
                                                        size="sm",
                                                    ),
                                                ],
                                                width="auto",
                                            ),
                                            dbc.Col(
                                                dbc.Button(
                                                    [
                                                        html.I(
                                                            className="bi bi-arrow-clockwise me-1"
                                                        ),
                                                        "Refresh Now",
                                                    ],
                                                    id="manual-refresh-button",
                                                    color="primary",
                                                    size="sm",
                                                    className="me-3",
                                                ),
                                                width="auto",
                                            ),
                                            dbc.Col(
                                                dcc.Loading(
                                                    id="update-status-loading",
                                                    type="dot",  # Using a small spinner
                                                    parent_className="ms-2 d-inline-block",  # Align spinner
                                                    children=[
                                                        html.Div(
                                                            id="update-status-icon",
                                                            className="ms-3 me-3",
                                                            style={
                                                                "display": "inline-block",
                                                            },
                                                        )
                                                    ],
                                                ),
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Span(
                                                        "Last updated: ",
                                                        className="ms-3 me-1",
                                                    ),
                                                    html.Span(
                                                        id="last-update-time",
                                                        style={"fontWeight": "bold"},
                                                    ),
                                                ],
                                                width="auto",
                                                className="ms-auto align-items-center d-flex",  # Keep flex alignment
                                            ),
                                        ],
                                        className="align-items-center",
                                    ),
                                    # dbc.Row(
                                    #     "You will need to pause first, if you want to interact with the graph"
                                    # ),
                                ],
                                className="p-2",
                            ),
                            className="mb-3",
                        ),
                        width="auto",
                        className="ms-auto",
                    ),
                ],
                className="align-items-center",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Graph(
                                id="timeline-graph",
                                style={"height": "100%"},
                                config=plotly_config,
                            )
                        ]
                    )
                ],
                style={"flex": "1"},
            ),
            dcc.Interval(
                id="interval-component",
                interval=refresh_interval * 1000,  # in milliseconds
                n_intervals=0,
                max_intervals=-1,  # Run indefinitely by default
            ),
            # Store to keep track of paused state
            dcc.Store(id="pause-state", data={"paused": False}),
            # Toast for save status
            dbc.Toast(
                id="save-toast",
                header="Notification",
                icon="primary",
                duration=4000,
                is_open=False,
                dismissable=True,
                style={
                    "position": "fixed",
                    "top": 20,
                    "right": 20,
                    "width": 350,
                    "zIndex": 9999,
                },
            ),
        ],
        fluid=True,
        className="px-4",
        style={"height": "100vh", "display": "flex", "flexDirection": "column"},
    )

    # Define callback to update the graph
    @app.callback(
        [
            Output("timeline-graph", "figure"),
            Output("last-update-time", "children"),
            Output("update-status-icon", "children"),
        ],
        [
            Input("interval-component", "n_intervals"),
            Input("manual-refresh-button", "n_clicks"),
        ],
        [
            State("pause-state", "data"),
            State("timeline-graph", "relayoutData"),
            State("timeline-graph", "figure"),
        ],
    )
    def update_graph(
        n_intervals, manual_refresh, pause_state, relayout_data, previous_fig_state
    ):
        """Update the graph with the latest MPD data."""
        ctx = dash.callback_context
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if pause_state.get("paused", False) and trigger_id == "interval-component":
            return dash.no_update, dash.no_update, dash.no_update

        logger.debug(f"Refreshing graph - triggered by {trigger_id}")
        attempt_time = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            fig = generate_figure_fn()
            fig.update_layout(margin=dict(t=45, b=0))

            # Preserve trace visibility from previous figure state
            if previous_fig_state and "data" in previous_fig_state:
                # Create a lookup for visibility status from the previous figure's JSON data
                previous_traces_visibility = {}
                for prev_trace_json in previous_fig_state[
                    "data"
                ]:  # prev_trace_json is a dict from the captured figure state
                    name = prev_trace_json.get("name")
                    if name is not None:
                        # Plotly uses True, False, or 'legendonly' for visibility
                        previous_traces_visibility[name] = prev_trace_json.get(
                            "visible", True
                        )

                # fig.data from the new figure contains graph objects (e.g., go.Bar).
                # Modify the 'visible' property of these objects directly.
                # These modifications alter the objects within the fig.data tuple.
                for (
                    trace_obj
                ) in fig.data:  # trace_obj is a graph_object instance (e.g., go.Bar)
                    if (
                        hasattr(trace_obj, "name")
                        and trace_obj.name is not None
                        and trace_obj.name in previous_traces_visibility
                    ):
                        trace_obj.visible = previous_traces_visibility[trace_obj.name]
                    # If a trace in the new fig doesn't have a 'name' attribute or wasn't in the old fig (e.g. new trace added),
                    # its visibility remains as set by generate_figure_fn().

            # Preserve zoom/pan and autorange states if relayout_data is available
            if relayout_data:
                layout_updates = {}

                axis_name_with_slider = None
                # Inspect the newly generated fig to find which x-axis has the active rangeslider
                # Checks xaxis, then xaxis2, xaxis3, ...
                for i in range(
                    1, 11
                ):  # Check up to 10 x-axes (arbitrary practical limit)
                    ax_key_str = (
                        f"xaxis{i if i > 1 else ''}"  # Generates 'xaxis', 'xaxis2', ...
                    )
                    if hasattr(fig.layout, ax_key_str):
                        axis_obj = getattr(fig.layout, ax_key_str)
                        if (
                            hasattr(axis_obj, "rangeslider")
                            and axis_obj.rangeslider
                            and axis_obj.rangeslider.visible
                        ):
                            axis_name_with_slider = ax_key_str
                            break
                # Fallback if only a single default 'xaxis' exists and wasn't caught by loop (e.g. i=1 needs '' not '1')
                if not axis_name_with_slider and hasattr(fig.layout, "xaxis"):
                    if (
                        hasattr(fig.layout.xaxis, "rangeslider")
                        and fig.layout.xaxis.rangeslider
                        and fig.layout.xaxis.rangeslider.visible
                    ):
                        axis_name_with_slider = "xaxis"

                # Process x-axes (e.g., xaxis, xaxis2, ...)
                x_axis_names = list(
                    set(
                        key.split(".")[0]
                        for key in relayout_data
                        if key.startswith("xaxis")
                    )
                )
                for axis_name in x_axis_names:
                    autorange_key = f"{axis_name}.autorange"
                    range0_key = f"{axis_name}.range[0]"
                    range1_key = f"{axis_name}.range[1]"

                    if autorange_key in relayout_data and relayout_data[autorange_key]:
                        layout_updates[f"{axis_name}.autorange"] = True
                        plotly_range_key = f"{axis_name}_range"
                        if plotly_range_key in layout_updates:
                            del layout_updates[plotly_range_key]

                        if axis_name == axis_name_with_slider:
                            layout_updates[f"{axis_name}.rangeslider.autorange"] = True
                            if f"{axis_name}.rangeslider.range" in layout_updates:
                                del layout_updates[f"{axis_name}.rangeslider.range"]

                    elif range0_key in relayout_data and range1_key in relayout_data:
                        current_range = [
                            relayout_data[range0_key],
                            relayout_data[range1_key],
                        ]
                        plotly_range_key = f"{axis_name}_range"
                        layout_updates[plotly_range_key] = current_range
                        layout_updates[f"{axis_name}.autorange"] = False

                        if axis_name == axis_name_with_slider:
                            layout_updates[f"{axis_name}.rangeslider.autorange"] = False
                            layout_updates[f"{axis_name}.rangeslider.range"] = (
                                current_range
                            )

                # Process y-axes (e.g., yaxis, yaxis2, ...)
                # Y-axes are typically not shared in the same way for subplots unless explicitly configured.
                y_axis_names = list(
                    set(
                        key.split(".")[0]
                        for key in relayout_data
                        if key.startswith("yaxis")
                    )
                )
                for axis_name in y_axis_names:  # axis_name is 'yaxis', 'yaxis2', etc.
                    autorange_key = f"{axis_name}.autorange"
                    range0_key = f"{axis_name}.range[0]"
                    range1_key = f"{axis_name}.range[1]"

                    if autorange_key in relayout_data and relayout_data[autorange_key]:
                        layout_updates[f"{axis_name}.autorange"] = True
                        plotly_range_key = (
                            f"{axis_name}_range"  # e.g. yaxis_range, yaxis2_range
                        )
                        if plotly_range_key in layout_updates:
                            del layout_updates[plotly_range_key]
                    elif range0_key in relayout_data and range1_key in relayout_data:
                        plotly_range_key = (
                            f"{axis_name}_range"  # e.g. yaxis_range, yaxis2_range
                        )
                        layout_updates[plotly_range_key] = [
                            relayout_data[range0_key],
                            relayout_data[range1_key],
                        ]
                        layout_updates[f"{axis_name}.autorange"] = False

                if layout_updates:
                    fig.update_layout(layout_updates)

            # Update time to reflect successful refresh
            current_time = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            status_icon = html.I(className="bi bi-check-circle-fill text-success")
            return fig, current_time, status_icon
        except Exception as e:
            logger.error(f"Error during figure generation or update: {e}")
            status_icon = html.I(className="bi bi-x-circle-fill text-danger")
            # Keep the old figure, update time to show an attempt was made, and show error icon
            return dash.no_update, attempt_time, status_icon

    # Define callback to update the refresh interval
    @app.callback(
        Output("interval-component", "interval"),
        [Input("refresh-interval-input", "value")],
    )
    def update_interval(value):
        if value is None:
            return dash.no_update
        # Make sure we have a valid value
        try:
            interval_value = int(value)
            if interval_value < 1:
                interval_value = 1
            elif interval_value > 60:
                interval_value = 60
            logger.info(f"Auto-refresh interval changed to {interval_value} seconds")
            return interval_value * 1000  # convert to milliseconds
        except (ValueError, TypeError):
            return dash.no_update

    # Callback for pause/resume functionality
    @app.callback(
        [
            Output("pause-button", "children"),
            Output("pause-button", "color"),
            Output("interval-component", "max_intervals"),
            Output("pause-state", "data"),
        ],
        [Input("pause-button", "n_clicks")],
        [State("pause-state", "data")],
    )
    def toggle_pause(n_clicks, pause_state):
        if n_clicks is None:
            # Set initial state if no clicks yet, ensuring icon is present
            initial_button_content = [
                html.I(className="bi bi-pause-fill me-1"),
                "Pause",
            ]
            return initial_button_content, "danger", dash.no_update, dash.no_update

        # Toggle the pause state
        paused = not pause_state.get("paused", False)

        logger.info(f"Toggle pause - new state: {'paused' if paused else 'running'}")

        if paused:
            # Paused state - user pressed Pause, button should now show Resume
            button_content = [html.I(className="bi bi-play-fill me-1"), "Resume"]
            button_color = "success"  # Green for resume
            max_intervals = 0
        else:
            # Resume state - user pressed Resume, button should now show Pause
            button_content = [html.I(className="bi bi-pause-fill me-1"), "Pause"]
            button_color = "danger"  # Red for pause
            max_intervals = -1

        return button_content, button_color, max_intervals, {"paused": paused}

    # Separate callback to handle refresh on resume
    @app.callback(
        Output("interval-component", "n_intervals"),
        [Input("pause-button", "n_clicks")],
        [State("pause-state", "data"), State("interval-component", "n_intervals")],
        prevent_initial_call=True,
    )
    def refresh_on_resume(n_clicks, pause_state, current_n_intervals):
        if n_clicks is None:
            return dash.no_update

        # Only trigger refresh when resuming (was paused, now unpausing)
        if pause_state.get("paused", True):
            logger.info("Triggering refresh due to resume")
            return current_n_intervals + 1

        return dash.no_update

    # Callback to save the current figure as HTML
    @app.callback(
        [
            Output("save-toast", "is_open"),
            Output("save-toast", "header"),
            Output("save-toast", "children"),
            Output("save-toast", "icon"),
        ],
        Input("save-button", "n_clicks"),
        State("timeline-graph", "figure"),
        prevent_initial_call=True,
    )
    def save_figure(n_clicks, fig_data):
        if n_clicks is None or fig_data is None:
            return False, dash.no_update, dash.no_update, dash.no_update

        try:
            # Recreate the figure object from the data, using only data and layout
            layout = fig_data["layout"]

            # There is a bug in Plotly where the rangeslider is not properly serialized
            # so we need to remove it from the layout
            keys_to_remove = []
            for key, value in layout.items():
                if key.startswith("xaxis"):
                    if "rangeslider" in value:
                        for subkey, subvalue in value["rangeslider"].items():
                            if subkey.startswith("yaxis"):
                                keys_to_remove.append(subkey)
                        for key_to_remove in keys_to_remove:
                            del value["rangeslider"][key_to_remove]
            fig_obj = go.Figure(data=fig_data["data"], layout=layout)

            # Generate timestamp and filename
            timestamp = datetime.now().isoformat(timespec="seconds")
            filename = f"mpd_timeline_{timestamp}.html"
            filepath = Path(filename)

            # Save the figure
            pio.write_html(fig_obj, file=str(filepath), full_html=True)

            save_message = f"Snapshot saved to: {filepath.absolute()}"
            logger.info(save_message)
            # Create a clickable link for the filepath
            link = html.A(
                href=f"file://{filepath.absolute()}",
                children=str(filepath.absolute()),
                target="_blank",
            )
            toast_message = html.Div(["Snapshot saved to: ", link])
            return True, "Success", toast_message, "success"

        except Exception as e:
            error_message = f"Error saving snapshot: {e}"
            logger.error(error_message)
            return True, "Error", error_message, "danger"

    return app
