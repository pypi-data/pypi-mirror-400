"""
Operating system utility functions.
"""

import platform


def is_wsl():
    """
    Detect if the current environment is Windows Subsystem for Linux (WSL).

    Returns:
        bool: True if running in WSL, False otherwise
    """
    if platform.system() != "Linux":
        return False

    try:
        with open("/proc/version", "r") as f:
            return "microsoft" in f.read().lower()
    except:
        return False
