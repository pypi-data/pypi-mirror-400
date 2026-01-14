from dataclasses import dataclass
from enum import Enum


class TimelineType(Enum):
    PERIOD = "period"
    MEDIA = "media"
    EVENT = "event"

    def __hash__(self):
        return hash(self.name)


@dataclass
class TimelineMarkerDef:
    name: str
    timeline_type: TimelineType  # the main type of timeline
    bg_color: str = None
    border_color: str = None
    border_width: int = 2

    def combine(self, other: "TimelineMarkerDef", new_name: str = None):
        return TimelineMarkerDef(
            timeline_type=self.timeline_type,
            name=new_name if new_name else self.name,
            bg_color=(other.bg_color if other.bg_color else self.bg_color),
            border_color=(
                other.border_color if other.border_color else self.border_color
            ),
            border_width=(
                other.border_width if other.border_width else self.border_width
            ),
        )

    def __hash__(self):
        return hash(
            (
                self.name,
                self.timeline_type,
                self.bg_color,
                self.border_color,
                self.border_width,
            )
        )


class TimelineMarkers:
    # Define sub-type markers
    PERIOD_CONTENT = TimelineMarkerDef(
        name="content",
        timeline_type=TimelineType.PERIOD,
        bg_color="rgba(99, 110, 250, 0.7)",
        border_color="rgba(99, 110, 250, 1)",
    )
    PERIOD_AD = TimelineMarkerDef(
        name="ad",
        timeline_type=TimelineType.PERIOD,
        bg_color="rgba(44, 160, 44, 0.7)",
        border_color="rgba(44, 160, 44, 1)",
    )

    SEGMENT_VIDEO = TimelineMarkerDef(
        name="video",
        timeline_type=TimelineType.MEDIA,
        bg_color="rgba(255, 151, 255, 0.7)",
        border_color="rgba(255, 151, 255, 1)",
    )
    SEGMENT_AUDIO = TimelineMarkerDef(
        name="audio",
        timeline_type=TimelineType.MEDIA,
        bg_color="rgba(254, 203, 82, 0.7)",
        border_color="rgba(254, 203, 82, 1)",
    )
    SEGMENT_TEXT = TimelineMarkerDef(
        name="text",
        timeline_type=TimelineType.MEDIA,
        bg_color="rgba(186, 176, 172, 0.7)",
        border_color="rgba(186, 176, 172, 1)",
    )
    SEGMENT_OTHER = TimelineMarkerDef(
        name="other",
        timeline_type=TimelineType.MEDIA,
        bg_color="rgba(186, 176, 172, 0.7)",
        border_color="rgba(186, 176, 172, 1)",
    )
    SEGMENT_AD = TimelineMarkerDef(
        name="ad",
        timeline_type=TimelineType.MEDIA,
        border_color="rgba(186, 176, 172, 1)",
    )

    MPD_EVENT = TimelineMarkerDef(
        name="MPD event",
        timeline_type=TimelineType.EVENT,
        bg_color="rgba(219, 85, 59, 0.7)",
        border_color="rgba(219, 85, 59, 1)",
    )
    SCTE35_COMMAND = TimelineMarkerDef(
        name="SCTE35 command",
        timeline_type=TimelineType.EVENT,
        bg_color="rgba(239, 85, 59, 0.7)",
        border_color="rgba(239, 85, 59, 1)",
    )
    SCTE35_DESCRIPTOR = TimelineMarkerDef(
        name="SCTE35 descriptor",
        timeline_type=TimelineType.EVENT,
        bg_color="rgba(239, 85, 59, 0.7)",
        border_color="rgba(239, 85, 59, 1)",
    )


MARKER_COLORS = {
    "PERIOD_CONTENT": TimelineMarkerDef(
        name="content",
        timeline_type=TimelineType.PERIOD,
        bg_color="rgba(99, 110, 250, 0.7)",
        border_color="rgba(99, 110, 250, 1)",
    ),
}


__all__ = [
    "TimelineType",
    "TimelineMarkerDef",
    "TimelineMarkers",
]
