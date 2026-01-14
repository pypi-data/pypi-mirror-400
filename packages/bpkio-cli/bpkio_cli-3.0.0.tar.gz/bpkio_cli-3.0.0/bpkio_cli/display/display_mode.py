from enum import Enum


class DisplayMode(Enum):
    RAW = "raw"
    HIGHLIGHT = "highlight"
    TABLE = "table"
    TREE = "tree"
    TIMELINE = "timeline"
    DIFF = "diff"
    QUIET = "none"
