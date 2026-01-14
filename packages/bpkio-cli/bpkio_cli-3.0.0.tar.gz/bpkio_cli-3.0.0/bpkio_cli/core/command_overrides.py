from __future__ import annotations

import importlib.metadata
from functools import lru_cache
from typing import Iterable

import click


def _iter_override_entry_points() -> Iterable[importlib.metadata.EntryPoint]:
    """
    Discover entry points for core-command overrides.

    This intentionally looks at the *current interpreter environment* (not the plugin venv),
    so meta-packages like `bpkio-cli-admin` can override built-in commands without being a
    plugin installed into the plugin environment.
    """
    try:
        eps = importlib.metadata.entry_points(group="bic.overrides")
        # Python 3.12+ supports `entry_points(group=...)`; older versions may raise TypeError.
        return list(eps)
    except TypeError:
        eps = importlib.metadata.entry_points()
        # Python 3.10/3.11 return EntryPoints with `.select()`
        if hasattr(eps, "select"):
            return list(eps.select(group="bic.overrides"))
        # Older mapping style
        return list(eps.get("bic.overrides", []))


@lru_cache(maxsize=1)
def get_override_tokens() -> tuple[str, ...]:
    tokens = []
    for ep in _iter_override_entry_points():
        if ep.name:
            tokens.append(ep.name)
    # Preserve deterministic order
    return tuple(sorted(set(tokens)))


@lru_cache(maxsize=None)
def get_override_command(token: str) -> click.Command | None:
    """
    Return the overriding click command for a given token, if any.

    The entry point may resolve to:
    - a click.Command
    - a zero-arg callable returning a click.Command
    """
    for ep in _iter_override_entry_points():
        if ep.name != token:
            continue
        try:
            obj = ep.load()
            if isinstance(obj, click.Command):
                return obj
            if callable(obj):
                cmd = obj()
                if isinstance(cmd, click.Command):
                    return cmd
        except Exception:
            # If loading fails, skip this entry point (may be misconfigured)
            continue
    return None


