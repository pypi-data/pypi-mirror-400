from datetime import datetime, timedelta
from typing import List

from bpkio_cli.utils.datetimes import (
    format_datetime_with_milliseconds,
    format_timedelta,
)
from media_muncher.analysers.dash import DashAnalyser
from media_muncher.analysers.hls import HlsAnalyser
from media_muncher.handlers.dash import DASHHandler
from media_muncher.handlers.hls import HLSHandler
from media_muncher.models.timeline_models import TimelineSpan
from rich.console import Console
from rich.table import Table

from .renderer import ViewRenderer

console = Console()


class TimelineView(ViewRenderer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._data_source = None
        self.data: List[TimelineSpan] = []

    @property
    def data_source(self):
        return self._data_source

    @data_source.setter
    def data_source(self, new_data):
        self._data_source = new_data

        if isinstance(self._data_source, HLSHandler):
            self.data = HlsAnalyser(self._data_source).get_timeline_spans()
        elif isinstance(self._data_source, DASHHandler):
            self.data = DashAnalyser(self._data_source).get_timeline_spans()
        else:
            raise NotImplementedError("This data_source is not supported")

    def render(self):
        def timedelta_or_datetime_to_str(value, time_only: bool = False):
            if isinstance(value, datetime):
                return format_datetime_with_milliseconds(value, time_only=time_only)
            if isinstance(value, timedelta):
                return format_timedelta(value)

        table = Table()
        table.add_column("#")
        table.add_column("Start")
        table.add_column("End")
        table.add_column("Duration")
        table.add_column("Segments")
        table.add_column("Trigger")
        table.add_column("Type")
        for i, span in enumerate(self.data):
            row = [
                str(i),
                timedelta_or_datetime_to_str(span.start),
                (
                    timedelta_or_datetime_to_str(span.end, time_only=True)
                    if span.end
                    else ""
                ),
                format_timedelta(span.duration) if span.duration else "",
                str(span.num_segments),
                span.start_trigger,
                span.span_type,
            ]

            table.add_row(*row)

        console.print(table)
