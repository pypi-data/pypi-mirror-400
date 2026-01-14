from typing import Any

import bpkio_api.models as models
import click
import cloup
from bpkio_api.credential_provider import TenantProfile

from bpkio_cli.click_mods.accepts_plugins_group import AcceptsPluginsGroup
from bpkio_cli.core.exceptions import UsageError
from bpkio_cli.core.resource_chain import ResourceChain
from bpkio_cli.writers.breadcrumbs import display_tip

ARG_TO_IGNORE = "__ignore_this_arg__"


class SubCommandContext(cloup.Context):
    @property
    def command_path(self):
        cmd_path = super().command_path
        if self.parent is None:
            return cmd_path

        # remove the resource identifier from the command path for commands that don't take it as an argument
        if len(self.parent.command.arguments) > 0:
            metavar = self.parent.command.arguments[0].human_readable_name
            if getattr(self.command, "takes_id_arg", None) is False:
                cmd_path = cmd_path.replace(" " + metavar, "")
            else:
                cmd_path = cmd_path.replace(" " + metavar, "")
        return cmd_path


class ResourceSubCommand(cloup.Command):
    context_class = SubCommandContext

    def __init__(self, *args: Any, **kwargs: Any):
        # Defines whether the sub-command requires or precludes a resource argument
        if "takes_id_arg" in kwargs:
            self.takes_id_arg = kwargs.pop("takes_id_arg")
        else:
            self.takes_id_arg = True

        # Defines whether the sub-command can be used as a default one by its parent, if no sub-command is present on the command line
        if "is_default" in kwargs:
            self.is_default = kwargs.pop("is_default")
        else:
            self.is_default = False

        super().__init__(*args, **kwargs)


def command(
    name=None,
    cls=None,
    takes_id_arg: bool = True,
    is_default: bool = False,
    **attrs,
):
    if cls is None:
        cls = ResourceSubCommand

    def decorator(f):
        cmd = cloup.command(name=name, cls=cls, **attrs)(f)
        cmd.takes_id_arg = takes_id_arg
        cmd.is_default = is_default
        return cmd

    return decorator


def group(
    name=None,
    cls=None,
    takes_id_arg: bool = True,
    is_default: bool = False,
    **attrs,
):
    if cls is None:
        cls = ResourceGroup

    def decorator(f):
        cmd = cloup.group(name=name, cls=cls, **attrs)(f)
        cmd.takes_id_arg = takes_id_arg
        cmd.is_default = is_default
        return cmd

    return decorator


# ====


class ResourceGroup(AcceptsPluginsGroup, ResourceSubCommand):
    """A click.Group sub-class that enables the use of command lines that
    1.  have the resource identifier provided *before* the sub-command,
        which is useful to mirror typical REST endpoint structure
        (eg. `mycli sources 123 slots 456`
        -> http://myapi/sources/:source_id/slots/:slot_id)
    2.  Allow for default commands (eg. `list`, `get`) when no sub-command is found on the command line.
        Different default commands can be defined with different requirements for the ID argument
        (eg. `mycli sources` -> `mycli sources list`)
        (eg. `mycli sources 123` -> `mycli sources 123 get`)
    3.  save automatically the ID to the context (for use deeper in the chain)

    Inspired by https://stackoverflow.com/a/44056564/2215413"""

    def __init__(
        self,
        *args: Any,
        resource_type: type | None = None,
        resource_id_type: type = int,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.resource_type = resource_type
        self.resource_id_type = resource_id_type

    def parse_args(self, ctx, args):
        call_for_help = False

        # Flag used by list_commands() to optionally filter commands in help output.
        # In particular, when the user asks for help in the form `<id> --help`,
        # we want to show only the commands that can operate on an ID, while
        # keeping the full command list on `--help` without ID.
        ctx.meta.setdefault("help_for_explicit_id", False)

        # Plugins can be expensive to import. Only discover them when we have a strong
        # signal that the user is invoking a plugin command (i.e. when the subcommand
        # token is unknown among built-ins).
        #
        # Examples:
        # - `bic sources 123 get`          -> no need to discover plugins
        # - `bic session 123 ad-report`    -> discover plugins (ad-report is unknown)
        # - `bic sources --help`          -> discover plugins (help should include plugins)
        if any(a in args for a in ["--help", "-h"]):
            self.discover_plugins(ctx)
        else:
            # If a subcommand token is present and unknown, it might be a plugin command.
            # ResourceGroup patterns:
            # - `<id> <subcmd> ...`  -> subcmd is args[1]
            # - `<subcmd> ...`       -> subcmd is args[0] (no-id commands)
            known = set(self.commands.keys()) | set(
                getattr(self, "alias2name", {}).keys()
            )
            candidate = None
            if len(args) >= 2 and args[1] not in known:
                # Likely `<id> <subcmd>` form
                candidate = args[1]
            elif (
                len(args) >= 1 and args[0] not in known and not args[0].startswith("-")
            ):
                # Could be `<subcmd>` (no id) or `<id>` (with default).
                # We only treat it as a subcommand candidate if there are more args.
                if len(args) >= 2:
                    candidate = args[0]

            if candidate is not None:
                self.discover_plugins(ctx)

        # Find all commands that specify not requiring id
        commands_not_taking_resource_arg = list(
            self._find_subcommands(takes_id_arg=False)
        )

        # Help requested with an explicit ID and no subcommand:
        # eg. `bic live 123 --help` or `bic vc 123 slot 456 --help`
        # -> show help for this group level, but list only id-taking subcommands.
        if (
            len(args) == 2
            and args[1] in ["--help", "-h"]
            and args[0] != ARG_TO_IGNORE
            and args[0] not in self.commands
            and args[0] not in getattr(self, "alias2name", {})
        ):
            ctx.meta["help_for_explicit_id"] = True

        # No sub-command?  Then we fall back onto the first default sub-command that doesn't take an argument
        #  eg. "bic sources" -> "bic sources list"
        if len(args) == 0:
            default_command = next(
                self._find_subcommands(takes_id_arg=False, is_default=True),
                None,
            )
            if default_command is not None:
                args.append(default_command)
                display_tip(
                    f"No sub-command provided, using default command '{default_command}'.",
                )
            else:
                raise UsageError(
                    "No default sub-command found. You need to explicitly state the sub-command you want to use"
                )

        # Some commands do not take an ID argument,
        # so inject an empty one to prevent parse failure
        #  eg. "bic sources list" -> "bic sources 'IGNORE' list"
        if args[0] in commands_not_taking_resource_arg:
            args.insert(0, ARG_TO_IGNORE)

        # Call for help just after the sub-command? Intercept and expedit
        #  eg. "bic sources --help"
        if args[0] in ["--help", "-h"]:
            call_for_help = True

        if not call_for_help:
            # If the first argument is a command that normally takes an ID,
            # but there is a "--help", inject an empty one to allow normal behaviour
            #  eg. "bic sources get --help" -> "bic sources 'IGNORE' get --help"
            if args[0] in self.commands and any(a in args for a in ["--help"]):
                args.insert(0, ARG_TO_IGNORE)

            # If the first argument is "--id", we simply remove it
            # (this option is only used to make it easier to do auto-complete with fig)
            if args[0] in ["--id", "-i"]:
                args.pop(0)

            # Single argument, which is not a sub-command?
            # It must be a resource identifier, and we find the default command that works with resource ID
            #  eg. "bic sources 123" -> "bic sources 123 get"
            #
            # Important: if the user asks for help at this level (eg. "bic live 123 --help"),
            # we must NOT rewrite to the default sub-command ("get"), otherwise click/cloup
            # prints the help for "get" instead of the group ("live").
            if args[0] not in self.commands and args[0] not in self.alias2name:
                if len(args) == 1:
                    default_command = next(
                        self._find_subcommands(takes_id_arg=True, is_default=True),
                        None,
                    )
                    if default_command is not None:
                        args.insert(1, default_command)
                        display_tip(
                            f"No sub-command provided, selecting default command '{default_command}'.",
                        )
                    else:
                        raise UsageError(
                            "No default sub-command found. You need to explicitly state the sub-command you want to use"
                        )

            # If the command is one that require an ID, but there isn't one,
            # we assume that the last one (from the cache) is to be reused
            #  eg. "bic sources get" -> "bic sources $ get"
            if (args[0] in self.commands or args[0] in self.alias2name) and (
                args[0] not in commands_not_taking_resource_arg
            ):
                display_tip(
                    "No ID provided, using '$' to reuse the previous resource.",
                )
                args.insert(0, "$")

            # If there is a resource-based command preceded by a non-ignorable string,
            # that's an error
            #  eg. "bic sources 123 list" -> UsageError
            if args[0] != ARG_TO_IGNORE and args[1] in commands_not_taking_resource_arg:
                raise UsageError(
                    f"The '{args[1]}' command cannot be preceded by a resource ID"
                )

            # actual (non-ignorable) argument before command?  It's the resource ID, or something akin to it.
            # If necessary we look it up in memory save it automatically to the context object
            #  eg. "bic sources 123 get" -> record ID '123'
            if (
                args[0] != ARG_TO_IGNORE
                and args[0] not in self.commands
                and (args[1] in self.commands or args[1] in self.alias2name)
            ):
                target_type = self._get_resource_type()

                # check if the ID can be parsed according to the resource ID type specified
                try:
                    self.resource_id_type(args[0])
                except Exception:
                    if ctx.obj.cache is not None:
                        # Lookup in the cache if the ID is not a recognised value
                        if not args[0].startswith(
                            "-"
                        ):  # possible options, or STDIN passing
                            placeholder = args[0]
                            if target_type not in [TenantProfile]:
                                args[0] = ctx.obj.cache.resolve(
                                    placeholder, target_type
                                )
                            if placeholder != args[0]:
                                display_tip(
                                    f"Resolved '{placeholder}' to {target_type.__name__} with id '{args[0]}'",
                                )

                chain: ResourceChain = ctx.obj.resource_chain
                chain.add_resource(key=args[0], resource=None)

        super(ResourceGroup, self).parse_args(ctx, args)

    def list_commands(self, ctx):
        # Default: show everything
        names = super().list_commands(ctx)

        # If the user asked for help with an explicit ID (eg. `<id> --help`),
        # hide commands that are defined as not taking an ID.
        if not ctx.meta.get("help_for_explicit_id", False):
            return names

        filtered: list[str] = []
        alias2name = getattr(self, "alias2name", {})
        for name in names:
            primary = alias2name.get(name, name)
            cmd = self.commands.get(primary)
            if cmd is None:
                # If we can't resolve metadata, be conservative and keep it.
                filtered.append(name)
                continue
            if getattr(cmd, "takes_id_arg", True) is False:
                continue
            filtered.append(name)
        return filtered

    def list_sections(self, ctx: click.Context):
        # cloup renders help from *sections*.
        sections = super().list_sections(ctx)

        # Only filter for the specific `<id> --help` pattern flagged during parsing.
        if not ctx.meta.get("help_for_explicit_id", False):
            # For normal group-level help (`--help` without explicit id), distinguish
            # between commands that require an id and those that don't, by splitting
            # each section into a "(no id)" subsection plus the original section
            # (implicitly "with id").
            split_sections: list[cloup.Section] = []
            for sec in sections:
                no_id = cloup.Section(
                    f"{sec.title} (without resource id)",
                    is_sorted=getattr(sec, "is_sorted", False),
                )
                with_id = cloup.Section(
                    sec.title,
                    is_sorted=getattr(sec, "is_sorted", False),
                )

                for name, cmd in getattr(sec, "commands", {}).items():
                    if getattr(cmd, "takes_id_arg", True) is False:
                        no_id.add_command(cmd, name)
                    else:
                        with_id.add_command(cmd, name)

                if getattr(no_id, "commands", {}):
                    split_sections.append(no_id)
                if getattr(with_id, "commands", {}):
                    split_sections.append(with_id)

            return split_sections

        filtered_sections: list[cloup.Section] = []
        for sec in sections:
            # Copy the section so we don't mutate the original (important: other help calls
            # like `bic live --help` must still show the full command set).
            new_sec = cloup.Section(
                sec.title,
                is_sorted=getattr(sec, "is_sorted", False),
            )

            # `sec.commands` is a dict[name -> click.Command] in this codebase.
            for name, cmd in getattr(sec, "commands", {}).items():
                if getattr(cmd, "takes_id_arg", True) is False:
                    continue
                new_sec.add_command(cmd, name)

            # Keep the section only if it still has something to show.
            if getattr(new_sec, "commands", {}):
                filtered_sections.append(new_sec)

        return filtered_sections

    def _get_resource_type(self):
        if self.resource_type:
            return self.resource_type
        else:
            return models.BaseResource

    def _find_subcommands(self, **filter_args):
        commands_left = self.commands.copy()
        for k, v in filter_args.items():
            commands_left = {
                name: cmd
                for (name, cmd) in commands_left.items()
                if hasattr(cmd, k) and getattr(cmd, k) == v
            }

        for name in commands_left.keys():
            yield name

    def command(
        self,
        name: str = None,
        cls=None,
        takes_id_arg: bool = True,
        is_default: bool = False,
        **kwargs: Any,
    ):
        make_command = command(
            name=name,
            cls=cls,
            takes_id_arg=takes_id_arg,
            is_default=is_default,
            **kwargs,
        )

        def decorator(f) -> ResourceSubCommand:
            cmd = make_command(f)
            self.add_command(cmd)
            return cmd

        return decorator
