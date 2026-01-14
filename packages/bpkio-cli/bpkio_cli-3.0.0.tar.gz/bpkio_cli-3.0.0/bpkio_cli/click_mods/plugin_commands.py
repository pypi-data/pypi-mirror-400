from __future__ import annotations

from typing import Any

import click
import cloup

import bpkio_cli.click_mods.resource_commands as bic_res_cmd


class PluginCommand(bic_res_cmd.ResourceSubCommand):
    def __init__(
        self,
        *args,
        admin_only: bool = False,
        scopes: list = [],
        allow_package: bool = True,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.scopes = scopes or []
        self.admin_only = admin_only
        self.allow_package = allow_package


class PluginGroup(bic_res_cmd.ResourceSubCommand, cloup.Group):
    def __init__(
        self,
        *args,
        admin_only: bool = False,
        scopes: list = [],
        allow_package: bool = True,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.scopes = scopes or []
        self.admin_only = admin_only
        self.allow_package = allow_package


class PluginResourceGroup(PluginGroup):
    """Opt-in plugin group supporting `bic <plugin> <id> <subcommand>` patterns.

    This mirrors the core CLI convention of placing the resource identifier before
    the sub-command, without changing the default behavior of all plugins.
    """

    def parse_args(self, ctx: click.Context, args: list[str]) -> None:
        if not args:
            return super().parse_args(ctx, args)

        # Preserve normal help behavior.
        if args[0] in ("--help", "-h"):
            return super().parse_args(ctx, args)

        def is_cmd(token: str) -> bool:
            return token in self.commands or token in getattr(self, "alias2name", {})

        commands_not_taking_id = {
            name
            for name, cmd in self.commands.items()
            if getattr(cmd, "takes_id_arg", True) is False
        }

        # Support `bic <plugin> <subcommand>` by using '$' to reuse the previous id
        # (mirrors ResourceGroup behavior).
        if len(args) == 1 and is_cmd(args[0]) and args[0] not in commands_not_taking_id:
            args.insert(1, "$")

        # Support `bic <plugin> <id>` by selecting the default id-taking subcommand.
        if len(args) == 1 and not is_cmd(args[0]):
            default_cmd = next(
                (
                    name
                    for name, cmd in self.commands.items()
                    if getattr(cmd, "takes_id_arg", True) is True
                    and getattr(cmd, "is_default", False) is True
                ),
                None,
            )
            if default_cmd is not None:
                args.insert(0, default_cmd)

        # Support `bic <plugin> <id> <subcommand> ...` by swapping id and subcommand.
        if len(args) >= 2 and (not is_cmd(args[0])) and is_cmd(args[1]):
            if args[1] in commands_not_taking_id:
                raise click.UsageError(
                    f"The '{args[1]}' command cannot be preceded by an ID. "
                    f"Use: {ctx.command_path} {args[1]}",
                    ctx=ctx,
                )
            args[0], args[1] = args[1], args[0]

        return super().parse_args(ctx, args)

    def command(
        self,
        name: str | None = None,
        cls=None,
        takes_id_arg: bool = True,
        is_default: bool = False,
        **kwargs: Any,
    ):
        """Register a subcommand with `takes_id_arg` / `is_default` metadata.

        This matches `bpkio_cli.click_mods.resource_commands` conventions and enables
        `PluginResourceGroup.parse_args()` to operate safely.
        """
        if cls is None:
            cls = PluginCommand

        make_command = bic_res_cmd.command(
            name=name,
            cls=cls,
            takes_id_arg=takes_id_arg,
            is_default=is_default,
            **kwargs,
        )

        def decorator(f):
            cmd = make_command(f)
            self.add_command(cmd)
            return cmd

        return decorator


def command(
    name=None,
    cls=None,
    scopes: list = [],
    admin_only: bool = False,
    allow_package: bool = True,
    **attrs,
):
    if cls is None:
        cls = PluginCommand

    def decorator(f):
        cmd = cloup.command(name=name, cls=cls, **attrs)(f)
        cmd.scopes = scopes
        cmd.admin_only = admin_only
        cmd.allow_package = allow_package
        return cmd

    return decorator


def group(
    name=None,
    cls=None,
    scopes: list = [],
    admin_only: bool = False,
    allow_package: bool = True,
    **attrs,
):
    if cls is None:
        cls = PluginGroup

    def decorator(f):
        grp = cloup.group(name=name, cls=cls, **attrs)(f)
        grp.scopes = scopes
        grp.admin_only = admin_only
        grp.allow_package = allow_package
        return grp

    return decorator
