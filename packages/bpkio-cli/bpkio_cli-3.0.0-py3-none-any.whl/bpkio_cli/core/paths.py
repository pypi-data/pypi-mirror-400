"""
Path utilities for bpkio-cli.

Provides centralized functions for determining bpkio home directory and related paths.
"""

import os
from pathlib import Path


def get_bpkio_home() -> Path:
    """
    Get the bpkio home directory path.

    Checks for BPKIO_HOME environment variable first, then falls back to ~/.bpkio.

    Returns:
        Path: The bpkio home directory path
    """
    bpkio_home = os.getenv("BPKIO_HOME")
    if bpkio_home:
        return Path(bpkio_home).expanduser()
    return Path.home() / ".bpkio"
