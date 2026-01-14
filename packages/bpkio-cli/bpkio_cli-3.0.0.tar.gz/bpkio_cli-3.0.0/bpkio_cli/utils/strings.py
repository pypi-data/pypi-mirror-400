import re


def strip_ansi(text: str) -> str:
    """
    Remove ANSI escape codes (color codes, formatting, etc.) from a string.

    This function removes all ANSI escape sequences including:
    - Color codes (e.g., \\x1b[31m for red)
    - Formatting codes (bold, italic, underline, etc.)
    - Cursor movement codes
    - Other control sequences

    Args:
        text: The string that may contain ANSI escape codes

    Returns:
        The string with all ANSI escape codes removed

    Example:
        >>> colored_text = "\\x1b[31mHello\\x1b[0m"
        >>> strip_ansi(colored_text)
        'Hello'
    """
    # Pattern to match ANSI escape sequences:
    # - \\x1b or \\x1B: ESC character
    # - [: CSI (Control Sequence Introducer)
    # - [0-9;]*: Zero or more digits and semicolons (parameters)
    # - [a-zA-Z]: Final character (command)
    # This covers most common ANSI escape sequences
    ansi_escape_pattern = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")
    return ansi_escape_pattern.sub("", text)

