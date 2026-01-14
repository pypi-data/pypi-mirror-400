import warnings

import click
import cloup

from bpkio_cli.core.bic_top_level_group import BicTopLevelGroup
from bpkio_cli.core.config_provider import CONFIG
from bpkio_cli.core.exceptions import UsageError
from bpkio_cli.core.initialize import initialize
from bpkio_cli.core.logging import get_level_names, set_logging_level

# Run migration early, before any other imports that might use CONFIG
from bpkio_cli.utils.migration import migrate_bpkio_directory
from bpkio_cli.writers.breadcrumbs import (
    display_error,
    display_tenant_info,
    display_warning,
)

# Default log level
set_logging_level("ERROR")


warnings.filterwarnings("ignore", category=UserWarning)

SETTINGS = cloup.Context.settings(
    formatter_settings=cloup.HelpFormatter.settings(
        theme=cloup.HelpTheme.dark(), max_width=120
    ),
    help_option_names=["-h", "--help"],
)


@cloup.group(
    show_subcommand_aliases=True,
    context_settings=SETTINGS,
    cls=BicTopLevelGroup,
)
@click.version_option(
    package_name="bpkio_cli", prog_name="Command Line helpers for broadpeak.io"
)
@click.option(
    "-t",
    "--tenant",
    help="Label of the tenant profile to impersonate. It must have been added to the local credentials file (for example with the `bic config tenant add`)",
    metavar="<tenant-label>",
)
@click.option(
    "-l",
    "--log-level",
    type=click.Choice(get_level_names()),
    required=False,
    show_default=True,
    help="Set the log level",
)
@click.option(
    "-cc / -nc",
    "--cache / --no-cache",
    "use_cache",
    is_flag=True,
    default=True,
    show_default=True,
    help="Enable or disable resource caches",
)
@click.option(
    "-pp / -np",
    "--prompts / --no-prompts",
    "use_prompts",
    is_flag=True,
    default=True,
    show_default=True,
    help="Enable or disable the use of prompts to ask for some information (where supported)",
)
@click.option(
    "-v",
    "verbose",
    count=True,
    type=int,
    default=None,
    help="Verbosity level. The number of 'v' indicates the level, from -v (lowest) to -vvvv (highest)",
)
@click.option(
    "--safe",
    is_flag=True,
    default=False,
    help="Run in safe mode (no plugins)",
)
@click.pass_context
def bic(ctx, tenant, log_level, use_cache, use_prompts, verbose, safe):
    if log_level:
        set_logging_level(log_level)

    migrate_bpkio_directory()

    CONFIG.set_temporary("use_prompts", use_prompts)

    if verbose is not None:
        CONFIG.set_temporary("verbose", verbose - 1)

    requires_api = True
    # TODO - move this to the command definition
    if ctx.invoked_subcommand in [
        "init",
        "configure",
        "record",
        "url",
        "archive",
        "memory",
        "doctor",
        "update",
        "plugins"
    ]:
        requires_api = False

    app_context = initialize(
        tenant_ref=tenant,
        use_cache=use_cache,
        requires_api=requires_api,
        enable_media_muncher=(ctx.invoked_subcommand in ["url", "archive"]),
    )

    if app_context.tenant and ctx.invoked_subcommand not in ["init", "configure"]:
        display_tenant_info(app_context.tenant)

    # TODO - validate the token in the initialisation of BroadpeakApi
    ctx.obj = app_context

    @ctx.call_on_close
    def close_cleanly():
        try:
            # Save the cache to disk
            app_context.cache.save()

            # Save the current command
            with open(".last_command", "w") as f:
                f.write(ctx.invoked_subcommand)

            # Close the local server if it's running
            if app_context.local_server:
                app_context.local_server.stop()

        except Exception:
            pass


def safe_entry_point():
    try:
        bic()
    except Exception as e:
        if hasattr(e, "status_code"):
            st = " [{}] ".format(e.status_code)
        else:
            st = ""
        msg = "{}: {}{}".format(e.__class__.__name__, st, e)

        if isinstance(e, UsageError):
            display_warning(msg)
        else:
            display_error(msg)

        if hasattr(e, "original_message") and e.original_message is not None:
            click.secho("  > {}".format(e.original_message), fg="red")


def debug_entry_point():
    set_logging_level("DEBUG", to_file=True)
    bic(obj={})


def mm_only_entry_point():
    bic.shortcut = "url"
    safe_entry_point()


def archive_only_entry_point():
    bic.shortcut = "archive"
    safe_entry_point()


if __name__ == "__main__":
    debug_entry_point()
    # mm_only_entry_point()
