from __future__ import annotations

from typing import Dict

import click
import cloup
from bpkio_cli.click_mods.accepts_plugins_group import AcceptsPluginsGroup
from bpkio_cli.click_mods.accepts_shortcuts import AcceptsShortcutsGroup
from bpkio_cli.click_mods.default_last_command import DefaultLastSubcommandGroup
from bpkio_cli.core.command_overrides import get_override_command, get_override_tokens
from bpkio_cli.core.lazy_command_registry import (
    LazyCommandRegistry,
    build_core_registry,
)


class BicTopLevelGroup(
    DefaultLastSubcommandGroup, AcceptsShortcutsGroup, AcceptsPluginsGroup
):
    """
    Top-level group with:
    - default-last-command behavior
    - shortcuts
    - plugin discovery (lazy)
    - core command discovery (lazy)
    """

    def _ensure_core_registry(self) -> None:
        if getattr(self, "_core_lazy_registry_ready", False):
            return
        self._core_lazy_registry_ready = True

        # section name -> cloup.Section
        self._core_sections: Dict[str, cloup.Section] = {}

        def section(name: str) -> cloup.Section:
            sec = self._core_sections.get(name)
            if sec is None:
                sec = cloup.Section(name, is_sorted=True)
                self._core_sections[name] = sec
            return sec

        def add(cmd: click.Command, section_name: str) -> None:
            self.add_command(cmd, cmd.name, section=section(section_name))

        self._core_registry: LazyCommandRegistry = build_core_registry(add=add)

    def get_command(self, ctx, name):
        self._ensure_core_registry()

        # Resolve core aliases (works even before the underlying command is registered).
        name = self._core_registry.resolve_token(name)

        # Generic core overrides (implemented by external packages via `bic.overrides`).
        override = get_override_command(name)
        if override is not None:
            return override

        # Fast-path (already loaded) WITHOUT triggering plugin discovery:
        cmd = cloup.Group.get_command(self, ctx, name)
        if cmd is not None:
            return cmd

        # Lazy-load core commands (and their command families) on-demand.
        loader = self._core_registry.loaders.get(name)
        if loader is not None:
            cond = self._core_registry.conditions.get(name, lambda: True)
            if not cond():
                return None
            loader()
            return cloup.Group.get_command(self, ctx, name)

        # Not a core command: now allow plugin resolution (may trigger plugin discovery).
        return super().get_command(ctx, name)

    def list_sections(self, ctx):
        """
        cloup renders help from *sections*, not from `list_commands()`.
        Since we register core commands lazily, we must populate sections when help
        is requested, otherwise `--help` would show no sub-commands.
        """
        self._ensure_core_registry()

        # When help is being rendered, eagerly register core commands so cloup can
        # display them. This may import more modules, but it's only for `--help`.
        if not getattr(self, "_core_help_loaded", False):
            self._core_help_loaded = True
            seen = set()
            for token, loader in self._core_registry.loaders.items():
                if loader in seen:
                    continue
                cond = self._core_registry.conditions.get(token, lambda: True)
                try:
                    if cond():
                        loader()
                        seen.add(loader)
                except Exception:
                    pass

        # Include plugin commands in help output (can be expensive; only for `--help`).
        try:
            if not getattr(self, "plugins_discovered", False) and not ctx.params.get(
                "safe"
            ):
                self.discover_plugins(ctx)
        except Exception:
            pass

        # Ensure overrides show up in help and replace any matching core commands.
        try:
            for token in get_override_tokens():
                cmd = get_override_command(token)
                if cmd is None:
                    continue
                # Put overrides in the same section as core configuration commands by default.
                sec = self._core_sections.get("Configuration")
                if sec is None:
                    sec = cloup.Section("Configuration", is_sorted=True)
                    self._core_sections["Configuration"] = sec
                self.add_command(cmd, token, section=sec)
        except Exception:
            pass

        return cloup.Group.list_sections(self, ctx)

    def list_commands(self, ctx):
        # Include lazy core command names so completion / help can see them.
        self._ensure_core_registry()
        names = set(super().list_commands(ctx))
        for token, cond in self._core_registry.conditions.items():
            try:
                if cond():
                    names.add(token)
            except Exception:
                pass
        try:
            names.update(get_override_tokens())
        except Exception:
            pass
        return sorted(names)
