from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable

import click

# A loader registers one or more click commands into the CLI.
Loader = Callable[[], None]
# A condition decides whether a command token should be visible/available.
Condition = Callable[[], bool]


@dataclass
class LazyCommandRegistry:
    """Token-based registry for lazily loading CLI commands (and their aliases).

    - `loaders[token]` loads and registers the command(s) for a token.
    - `conditions[token]` indicates whether the token should be available.
    - `alias_to_primary[alias]` maps an alias token to a canonical token.
    """

    loaders: Dict[str, Loader] = field(default_factory=dict)
    conditions: Dict[str, Condition] = field(default_factory=dict)
    alias_to_primary: Dict[str, str] = field(default_factory=dict)

    def register(self, token: str, *, loader: Loader, condition: Condition) -> None:
        self.loaders[token] = loader
        self.conditions[token] = condition

    def register_aliases(self, primary: str, aliases: Iterable[str]) -> None:
        for alias in aliases:
            self.alias_to_primary[alias] = primary
            # Keep loader/condition available by alias token as well (for completion/help).
            if primary in self.loaders:
                self.loaders[alias] = self.loaders[primary]
            if primary in self.conditions:
                self.conditions[alias] = self.conditions[primary]

    def resolve_token(self, token: str) -> str:
        return self.alias_to_primary.get(token, token)


def build_core_registry(*, add: Callable[[click.Command, str], None]) -> LazyCommandRegistry:
    """Build the core CLI registry.

    `add(cmd, section_name)` must register the command into the group.
    """
    reg = LazyCommandRegistry()

    def is_not_mm_only() -> bool:
        return not os.getenv("BIC_MM_ONLY")

    # ---- Configuration (split per command to keep imports minimal)
    def load_hello():
        from bpkio_cli.commands.hello import hello

        add(hello, "Configuration")

    reg.register("hello", loader=load_hello, condition=lambda: True)

    def load_init():
        from bpkio_cli.commands.configure import init

        add(init, "Configuration")

    reg.register("init", loader=load_init, condition=lambda: True)

    def load_configure():
        from bpkio_cli.commands.configure import configure

        add(configure, "Configuration")

    reg.register("configure", loader=load_configure, condition=lambda: True)
    reg.register_aliases("configure", ["config", "cfg"])

    def load_update():
        from bpkio_cli.commands.update import update

        add(update, "Configuration")

    reg.register("update", loader=load_update, condition=lambda: True)

    def load_doctor():
        from bpkio_cli.commands.doctor import doctor

        add(doctor, "Configuration")

    reg.register("doctor", loader=load_doctor, condition=lambda: True)

    # ---- Sources (family)
    def load_sources():
        from bpkio_cli.commands.sources import get_sources_commands

        for cmd in get_sources_commands():
            add(cmd, "Sources")

    for token in [
        "source",
        "asset",
        "live",
        "asset-catalog",
        "ad-server",
        "slate",
        "origin",
    ]:
        reg.register(token, loader=load_sources, condition=is_not_mm_only)

    reg.register_aliases("source", ["src", "sources"])
    reg.register_aliases("asset", ["assets"])
    reg.register_aliases("asset-catalog", ["catalog", "catalogs"])
    reg.register_aliases("ad-server", ["ads"])
    reg.register_aliases("slate", ["slates"])
    reg.register_aliases("origin", ["origins"])

    # ---- Services (family)
    def load_services():
        from bpkio_cli.commands.services import get_services_commands

        for cmd in get_services_commands():
            add(cmd, "Services")

    for token in [
        "service",
        "content-replacement",
        "ad-insertion",
        "virtual-channel",
        "adaptive-streaming-cdn",
    ]:
        reg.register(token, loader=load_services, condition=is_not_mm_only)

    reg.register_aliases("service", ["svc", "services"])
    reg.register_aliases("content-replacement", ["cr"])
    reg.register_aliases("ad-insertion", ["dai", "ssai"])
    reg.register_aliases("virtual-channel", ["vc"])
    reg.register_aliases("adaptive-streaming-cdn", ["cdn"])

    # ---- Other resources
    def load_profile():
        from bpkio_cli.commands.profiles import profile

        add(profile, "Other resources")

    reg.register("profile", loader=load_profile, condition=is_not_mm_only)
    reg.register_aliases("profile", ["prf", "profiles", "transcoding-profile"])

    def load_categories():
        from bpkio_cli.commands.categories import get_categories_command

        add(get_categories_command(), "Other resources")

    reg.register("categories", loader=load_categories, condition=is_not_mm_only)
    reg.register_aliases("categories", ["category", "cat"])

    def load_session():
        from bpkio_cli.commands.sessions import session

        add(session, "Other resources")

    reg.register("session", loader=load_session, condition=is_not_mm_only)
    reg.register_aliases("session", ["sessions", "sess"])

    # ---- Media muncher
    def load_url():
        from bpkio_cli.commands.url import url

        add(url, "Media muncher")

    reg.register("url", loader=load_url, condition=lambda: True)

    def load_archive():
        from bpkio_cli.commands.archive import archive

        add(archive, "Media muncher")

    reg.register("archive", loader=load_archive, condition=lambda: True)

    # ---- Account resources
    def load_users_family():
        from bpkio_cli.commands.users import get_users_commands

        for cmd in get_users_commands():
            add(cmd, "Account resources")

    for token in ["user", "tenant"]:
        reg.register(token, loader=load_users_family, condition=is_not_mm_only)
    reg.register_aliases("user", ["usr", "users"])

    def load_consumption():
        from bpkio_cli.commands.consumption import consumption

        add(consumption, "Account resources")

    reg.register("consumption", loader=load_consumption, condition=is_not_mm_only)

    # ---- Advanced
    def load_package():
        from bpkio_cli.commands.package import package

        add(package, "Advanced")

    reg.register("package", loader=load_package, condition=is_not_mm_only)

    def load_record():
        from bpkio_cli.commands.recorder import record

        add(record, "Advanced")

    reg.register("record", loader=load_record, condition=is_not_mm_only)

    def load_memory():
        from bpkio_cli.commands.memory import memory

        add(memory, "Advanced")

    reg.register("memory", loader=load_memory, condition=lambda: True)

    def load_plugins():
        from bpkio_cli.commands.plugins import plugins

        add(plugins, "Advanced")

    reg.register("plugins", loader=load_plugins, condition=lambda: True)
    reg.register_aliases("plugins", ["plugin"])

    return reg


