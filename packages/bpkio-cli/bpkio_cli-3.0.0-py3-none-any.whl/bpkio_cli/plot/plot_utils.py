"""Common utilities for plotting validation scripts."""

from datetime import datetime
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Figure


def extract_filename_from_uri(uri: str) -> str:
    """Extract just the filename (last path segment) from a URI, removing query parameters.

    Also removes any substring starting with '/bpk-sst/' from the path before extraction.
    """
    if not uri:
        return ""
    # Remove query parameters
    uri_without_query = uri.split("?")[0]

    # Remove any substring starting with '/bpk-sst/' from the path
    if "/bpk-sst/" in uri_without_query:
        # Find the position of '/bpk-sst/' and remove everything from that point
        bpk_sst_pos = uri_without_query.find("/bpk-sst/")
        if bpk_sst_pos != -1:
            # Keep everything before '/bpk-sst/'
            uri_without_query = uri_without_query[:bpk_sst_pos]

    # Get the last path segment
    filename = uri_without_query.split("/")[-1]
    return filename


def format_time_only(dt: datetime) -> str:
    """Format datetime to HH:MM:SS.ms format without date."""
    if dt is None:
        return ""
    return dt.strftime("%H:%M:%S.%f")[:-3]  # Remove last 3 digits to get milliseconds


def get_period_color_palette():
    """Get the custom color palette for periods/playlists.

    Returns:
        List of color strings from Plotly qualitative palettes
    """
    return [
        px.colors.qualitative.Plotly[0],
        px.colors.qualitative.Plotly[2],
        px.colors.qualitative.Plotly[3],
        # px.colors.qualitative.Plotly[4],
        px.colors.qualitative.Plotly[5],
        px.colors.qualitative.Plotly[6],
        px.colors.qualitative.G10[4],
    ]


# JavaScript code for vertical crosshair functionality (spans all subplots)
CROSSHAIR_JS = """
    <script>
    (function() {
        function addCrosshair() {
            const plotDivs = document.querySelectorAll('.plotly');
            plotDivs.forEach(function(plotDiv) {
                // Check if crosshair already exists
                if (plotDiv.querySelector('#crosshair-line-vertical')) return;
                
                // Create vertical crosshair line element
                const crosshairVertical = document.createElement('div');
                crosshairVertical.id = 'crosshair-line-vertical';
                crosshairVertical.style.position = 'absolute';
                crosshairVertical.style.width = '2px';
                crosshairVertical.style.backgroundColor = 'rgba(128, 128, 128, 0.5)';
                crosshairVertical.style.pointerEvents = 'none';
                crosshairVertical.style.display = 'none';
                crosshairVertical.style.zIndex = '1000';
                crosshairVertical.style.top = '0px';
                
                plotDiv.style.position = 'relative';
                plotDiv.appendChild(crosshairVertical);
                
                // Track mouse position
                plotDiv.addEventListener('mousemove', function(e) {
                    const rect = plotDiv.getBoundingClientRect();
                    const mouseX = e.clientX - rect.left;
                    
                    // Update vertical line (full height)
                    crosshairVertical.style.left = mouseX + 'px';
                    crosshairVertical.style.height = plotDiv.offsetHeight + 'px';
                    crosshairVertical.style.display = 'block';
                });
                
                plotDiv.addEventListener('mouseleave', function() {
                    crosshairVertical.style.display = 'none';
                });
            });
        }
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', addCrosshair);
        } else {
            addCrosshair();
        }
        
        // Also try after a short delay in case Plotly hasn't rendered yet
        setTimeout(addCrosshair, 500);
    })();
    </script>
    """


def save_plot_with_crosshair(fig: Figure, output_path: str | None = None):
    """Save plot to file with crosshair functionality.

    Args:
        fig: Plotly figure object
        output_path: Optional path to save HTML file. If None, saves to mpd_sequence_plot.html
    """
    if output_path is None:
        output_path = "mpd_sequence_plot.html"

    html_str = fig.to_html(
        include_plotlyjs="cdn",
        config={
            "scrollZoom": True,
            "modeBarButtonsToAdd": [
                "drawline",
                "drawopenpath",
                "drawclosedpath",
                "drawcircle",
                "drawrect",
                "eraseshape",
                "v1hovermode",
                "hoverclosest",
                "hovercompare",
                "togglespikelines",
            ],
        },
    )
    html_str = html_str.replace("</body>", CROSSHAIR_JS + "</body>")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_str)

    return Path(output_path).absolute()


def add_error_line(
    fig,
    error_x,
    y_bottom,
    y_top,
    row,
    col=1,
    error_message: str = None,
    error_time_str: str = None,
):
    """Add a vertical error line to a plot with consistent styling.

    Args:
        fig: Plotly figure object
        error_x: X coordinate for the error line
        y_bottom: Bottom Y coordinate
        y_top: Top Y coordinate
        row: Subplot row number
        col: Subplot column number (default: 1)
        error_message: Optional error message for hover tooltip
        error_time_str: Optional formatted time string for hover tooltip
    """
    if error_message and error_time_str:
        hovertemplate = (
            f"<b>{error_message}</b><br>"
            + "<b>Request Time:</b> "
            + error_time_str
            + "<br>"
            + "<extra></extra>"
        )
    else:
        hovertemplate = "<extra></extra>"

    fig.add_trace(
        go.Scatter(
            x=[error_x, error_x],
            y=[y_bottom, y_top],
            mode="lines",
            name="Error",
            line=dict(color="rgba(255, 0, 0, 0.5)", width=5),
            showlegend=False,
            hovertemplate=hovertemplate,
        ),
        row=row,
        col=col,
    )
