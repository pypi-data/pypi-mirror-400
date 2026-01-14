"""
Utilities package.

Keep this module **lightweight**: it is imported very early by the CLI startup
path. Avoid importing optional/heavy dependencies here (e.g. dateparser,
prompt_toolkit, etc.).
"""

from bpkio_cli.click_mods.option_eat_all import OptionEatAll

__all__ = ["OptionEatAll"]
