from __future__ import annotations

import importlib.metadata
from importlib.metadata import PackageNotFoundError

import click
import requests
from rich.console import Console
from rich.table import Table

from bpkio_cli.core.pip_tools import (
    get_cli_pip_command,
    get_latest_version_from_pip_index,
    run_pip,
)
from bpkio_cli.core.update_engine import (
    build_compat_report,
    format_constraint,
    is_downgrade,
    iter_packaged_plugin_distributions,
)
from bpkio_cli.writers.breadcrumbs import (
    display_error,
    display_info,
    display_ok,
    display_warning,
)

console = Console(width=120)


def _get_installed_version(dist_name: str) -> str | None:
    try:
        return importlib.metadata.version(dist_name)
    except PackageNotFoundError:
        return None


def _get_latest_version_from_pypi(dist_name: str) -> str | None:
    # Keep as best-effort fallback. The user may be using private indexes.
    try:
        r = requests.get(f"https://pypi.org/pypi/{dist_name}/json", timeout=10)
        r.raise_for_status()
        return str(r.json()["info"]["version"])
    except Exception:
        return None


def _get_latest_version(dist_name: str, pip_cmd: list[str]) -> str | None:
    return get_latest_version_from_pip_index(
        pip_cmd, dist_name
    ) or _get_latest_version_from_pypi(dist_name)


@click.command()
@click.option(
    "--check-only",
    is_flag=True,
    help="Only run the plugin compatibility check against the target CLI version.",
)
@click.option(
    "--force",
    is_flag=True,
    help="Proceed even if incompatible plugins are detected.",
)
@click.option(
    "--yes",
    "assume_yes",
    is_flag=True,
    help="Do not prompt for confirmation.",
)
def update(check_only: bool, force: bool, assume_yes: bool):
    """
    Update bpkio-cli (or bpkio-cli-admin if installed) and then upgrade installed plugins.

    Flow:
    1) Preflight: check installed plugin package constraints against target version
    2) Upgrade bpkio-cli-admin (if installed) or bpkio-cli
    3) Upgrade installed plugin packages (via configured plugin repos when available)
    """
    pip_cmd_cli = get_cli_pip_command()

    # Check if admin is installed
    has_admin = _get_installed_version("bpkio-cli-admin") is not None

    current_cli = _get_installed_version("bpkio-cli")
    current_admin = _get_installed_version("bpkio-cli-admin") if has_admin else None

    # Determine what to update
    target_admin: str | None = None
    target_cli: str | None = None

    if has_admin:
        # Admin installation: update admin (which will update bpkio-cli as dependency)
        target_admin = get_latest_version_from_pip_index(pip_cmd_cli, "bpkio-cli-admin")
        display_info(f"Current bpkio-cli-admin: {current_admin or 'not installed'}")
        if target_admin:
            display_info(f"Target bpkio-cli-admin: {target_admin}")
        else:
            display_info(
                "Target bpkio-cli-admin: (unknown; will use pip --upgrade to get latest)"
            )

        # Check for downgrade (only if we have both versions)
        if target_admin and current_admin and is_downgrade(current_admin, target_admin):
            display_error(
                f"Refusing to downgrade from {current_admin} to {target_admin}. "
                "Use --force to override this check."
            )
            if not force:
                raise SystemExit(1)

        # Use target version if available, otherwise fall back to current for compat checks
        target_version = target_admin or current_admin or "0.0.0"
        primary_package = "bpkio-cli-admin"
        preferred_packages = ["bpkio-cli-admin", "bpkio-cli"]
    else:
        # Regular CLI installation: update bpkio-cli
        target_cli = _get_latest_version("bpkio-cli", pip_cmd_cli)
        if not target_cli:
            display_error(
                "Could not determine latest bpkio-cli version (pip index and PyPI fallback failed)."
            )
            return

        display_info(f"Current bpkio-cli: {current_cli or 'not installed'}")
        display_info(f"Target bpkio-cli: {target_cli}")

        # Check for downgrade
        if is_downgrade(current_cli, target_cli):
            display_error(
                f"Refusing to downgrade from {current_cli} to {target_cli}. "
                "Use --force to override this check."
            )
            if not force:
                raise SystemExit(1)

        target_version = target_cli
        primary_package = "bpkio-cli"
        preferred_packages = ["bpkio-cli", "bpkio-cli-admin"]

    # --- Phase 1: preflight plugin compatibility
    dists = iter_packaged_plugin_distributions()
    report = build_compat_report(
        target_version=target_version,
        package_names=["bpkio-cli", "bpkio-cli-admin"],
        primary_package=primary_package,
        dists=dists,
    )
    incompatible = [p for p in report if p.status == "incompatible"]
    unknown = [p for p in report if p.status == "unknown"]

    if report:
        table = Table("Plugin", "Installed", "Constraint", "Status")
        for p in report:
            constraint = format_constraint(p.specs, preferred=preferred_packages)
            table.add_row(
                p.dist_name,
                p.dist_version,
                constraint,
                "[green]ok[/green]"
                if p.status == "ok"
                else "[red]incompatible[/red]"
                if p.status == "incompatible"
                else "[yellow]unknown[/yellow]",
            )
        console.print(table)
    else:
        display_info(
            "No packaged plugins (bpkio-cli-plugin-*) detected in the plugin environment."
        )

    if check_only:
        if incompatible:
            raise SystemExit(2)
        return

    if incompatible and not force:
        display_error(
            "Incompatible plugins detected; refusing to update without --force."
        )
        if not assume_yes:
            proceed = click.confirm("Proceed anyway?", default=False)
            if not proceed:
                raise SystemExit(2)
        else:
            raise SystemExit(2)
    elif (unknown and not assume_yes) and not force:
        constraint_name = "bpkio-cli-admin" if has_admin else "bpkio-cli"
        display_warning(
            f"Some plugins declare no {constraint_name} constraint; compatibility cannot be preflighted."
        )
        proceed = click.confirm("Proceed with update anyway?", default=True)
        if not proceed:
            raise SystemExit(2)

    # --- Phase 2: upgrade CLI/admin
    try:
        if has_admin:
            if target_admin:
                spec = f"bpkio-cli-admin=={target_admin}"
            else:
                spec = "bpkio-cli-admin"
            display_ok(f"Upgrading: {spec}")
            run_pip(pip_cmd_cli, ["install", "--upgrade", spec], check=True)
        else:
            display_ok(f"Upgrading: bpkio-cli=={target_cli}")
            run_pip(
                pip_cmd_cli,
                ["install", "--upgrade", f"bpkio-cli=={target_cli}"],
                check=True,
            )
    except Exception as e:
        display_error(f"Failed to upgrade CLI packages: {e}")
        raise SystemExit(1)

    # Re-read installed versions after upgrade
    new_cli = _get_installed_version("bpkio-cli")
    if has_admin:
        new_admin = _get_installed_version("bpkio-cli-admin")
        if new_admin:
            display_ok(f"Updated bpkio-cli-admin to {new_admin}")
        elif target_admin:
            display_ok(f"Updated bpkio-cli-admin to {target_admin}")
        else:
            display_ok("Updated bpkio-cli-admin (version unknown)")
        if new_cli:
            display_ok(f"bpkio-cli is now {new_cli}")
    else:
        new_cli = new_cli or target_cli
        display_ok(f"Updated bpkio-cli to {new_cli}")

    # --- Phase 3: upgrade installed plugins
    # Use the shared update implementation from plugins module
    from bpkio_cli.commands.plugins import _update_plugins_impl

    # Pass CLI version constraints to prevent downgrades
    cli_constraints = {}
    if new_cli:
        cli_constraints["bpkio-cli"] = new_cli
    if has_admin and new_admin:
        cli_constraints["bpkio-cli-admin"] = new_admin

    success = _update_plugins_impl(
        force=force, assume_yes=assume_yes, cli_constraints=cli_constraints
    )
    if not success:
        raise SystemExit(2)
