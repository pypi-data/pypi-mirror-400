import importlib.metadata
import os
from importlib.metadata import PackageNotFoundError, version
from importlib.util import find_spec
from pathlib import Path

import click
import tomlkit
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text

from bpkio_cli.core.app_context import AppContext
from bpkio_cli.core.paths import get_bpkio_home
from bpkio_cli.core.plugin_manager import plugin_manager

console = Console()


def get_package_version(dist_name: str, module_name: str) -> str:
    """
    Get package version from installed package metadata.

    Uses importlib.metadata to find the distribution, but filters to only
    use distributions installed in site-packages (not from source directories
    that might be on sys.path).
    """
    import sys
    from importlib.metadata import distributions

    # Find the distribution, preferring ones in site-packages
    site_packages_candidates = []
    other_candidates = []

    for dist in distributions():
        if dist.name == dist_name:
            # Get distribution path - try different methods depending on Python version
            try:
                if hasattr(dist, "_path"):
                    dist_path = str(dist._path)
                elif hasattr(dist, "locate_file"):
                    dist_path = str(dist.locate_file(""))
                else:
                    # Fallback: use the distribution's files to infer path
                    files = list(dist.files) if hasattr(dist, "files") else []
                    dist_path = str(files[0].locate().parent) if files else ""
            except Exception:
                dist_path = ""
            # Check if it's in a site-packages directory (the venv where we're installed)
            if "site-packages" in dist_path:
                site_packages_candidates.append((dist.version, dist_path))
            else:
                other_candidates.append((dist.version, dist_path))

    # Prefer site-packages versions, fall back to others if needed
    if site_packages_candidates:
        # If multiple site-packages versions, prefer the one matching our venv
        venv_site_packages = str(
            Path(sys.prefix)
            / "lib"
            / f"python{sys.version_info.major}.{sys.version_info.minor}"
            / "site-packages"
        )
        for ver, path in site_packages_candidates:
            if venv_site_packages in path:
                return ver
        # Return the first site-packages version if no venv match
        return site_packages_candidates[0][0]
    elif other_candidates:
        return other_candidates[0][0]

    # Fallback to standard version() call
    try:
        return version(dist_name)
    except PackageNotFoundError:
        pass

    # Last resort: try pyproject.toml
    try:
        module_spec = find_spec(module_name)
        if module_spec and module_spec.origin:
            module_path = Path(module_spec.origin).parent
            for candidate in [
                module_path.parent.parent / "pyproject.toml",
                module_path.parent / "pyproject.toml",
                module_path / "pyproject.toml",
            ]:
                if candidate.exists() and candidate.is_file():
                    try:
                        with open(candidate, "r") as f:
                            toml_data = tomlkit.parse(f.read())
                            pyproject_version = (
                                toml_data.get("tool", {})
                                .get("poetry", {})
                                .get("version")
                            )
                            if pyproject_version:
                                return str(pyproject_version)
                    except Exception:
                        continue
    except Exception:
        pass

    return "unknown"


def get_plugin_info():
    """
    Get information about all plugins (installed and dev mode).
    Returns a list of tuples: (plugin_name, version, status, location)
    where status is either "installed" or "dev"
    """
    plugin_info = []

    # Get installed plugins via entry points
    try:
        plugin_manager._add_plugin_env_to_path()
        for ep in importlib.metadata.entry_points(group="bic.plugins"):
            plugin_name = ep.name
            try:
                # Get the distribution that provides this entry point
                dist_version = "unknown"
                dist_location = None

                # Try to find the distribution by checking which one provides this entry point
                try:
                    # Load the entry point to get its module
                    ep.load()  # This ensures the entry point is valid

                    # Try to get version from the distribution name
                    # Entry points are typically in format: package.module:object
                    module_name = ep.value.split(":")[0].split(".")[0]

                    # Try common naming patterns for plugin packages
                    for candidate in [
                        f"bpkio-cli-plugin-{plugin_name}",
                        f"bpkio-cli-plugin-{plugin_name.replace('_', '-')}",
                        module_name.replace("_", "-"),
                        plugin_name,
                    ]:
                        try:
                            dist_version = version(candidate)
                            # Try to get location
                            try:
                                dist = importlib.metadata.distribution(candidate)
                                if hasattr(dist, "_path"):
                                    dist_location = str(dist._path)
                                elif hasattr(dist, "locate_file"):
                                    dist_location = str(dist.locate_file(""))
                            except Exception:
                                pass
                            break
                        except PackageNotFoundError:
                            continue
                except Exception:
                    pass

                plugin_info.append(
                    (plugin_name, dist_version, "installed", dist_location)
                )
            except Exception:
                plugin_info.append((plugin_name, "unknown", "installed", None))
    except Exception:
        pass

    # Get dev mode plugins via .pth files
    site_packages = plugin_manager.get_site_packages_path()
    if site_packages and site_packages.is_dir():
        for pth_file in site_packages.glob("bpkio-dev-*.pth"):
            try:
                src_path_str = pth_file.read_text().strip()
                if not src_path_str:
                    continue

                src_path = Path(src_path_str)
                pyproject_path = src_path.parent / "pyproject.toml"
                if not pyproject_path.exists():
                    continue

                # Extract plugin name from pth filename (bpkio-dev-<name>.pth)
                plugin_name = pth_file.stem.replace("bpkio-dev-", "")

                # Get version from pyproject.toml
                try:
                    with open(pyproject_path, "r") as f:
                        toml_data = tomlkit.parse(f.read())
                        plugin_version = (
                            toml_data.get("tool", {})
                            .get("poetry", {})
                            .get("version", "unknown")
                        )
                        # Also get package name to check if it's already in installed list
                        package_name = (
                            toml_data.get("tool", {}).get("poetry", {}).get("name")
                        )

                        # Get entry point names from pyproject.toml to better match installed plugins
                        entry_points = (
                            toml_data.get("tool", {})
                            .get("poetry", {})
                            .get("plugins", {})
                            .get("bic.plugins", {})
                        )
                        entry_point_names = (
                            list(entry_points.keys()) if entry_points else [plugin_name]
                        )

                        # Check if this plugin is already listed as installed
                        # (dev mode takes precedence, so we'll update it)
                        existing_idx = None
                        for idx, (name, _, status, _) in enumerate(plugin_info):
                            # Match by plugin name, package name, or entry point names
                            if (
                                name == plugin_name
                                or (package_name and name in package_name)
                                or name in entry_point_names
                            ):
                                existing_idx = idx
                                break

                        plugin_version_str = (
                            str(plugin_version) if plugin_version else "unknown"
                        )
                        location = str(src_path.parent)

                        # Use the first entry point name as the display name, or plugin_name as fallback
                        display_name = (
                            entry_point_names[0] if entry_point_names else plugin_name
                        )

                        if existing_idx is not None:
                            # Update existing entry to dev mode
                            plugin_info[existing_idx] = (
                                display_name,
                                plugin_version_str,
                                "dev",
                                location,
                            )
                        else:
                            # Add new dev mode entry
                            plugin_info.append(
                                (display_name, plugin_version_str, "dev", location)
                            )
                except Exception:
                    plugin_info.append(
                        (plugin_name, "unknown", "dev", str(src_path.parent))
                    )
            except Exception:
                continue

    return plugin_info


# Command: DOCTOR
@click.command(hidden=True)
@click.pass_obj
def doctor(obj: AppContext):
    print()

    # Home directory check
    bpkio_home = get_bpkio_home()
    bpkio_home_env = os.environ.get("BPKIO_HOME")
    if bpkio_home_env:
        home_text = Text.from_markup(
            f"[bold]BPKIO_HOME[/bold]: [bold blue]{bpkio_home}[/bold blue]\n"
            f" -> Set via [yellow]BPKIO_HOME[/yellow] environment variable: [magenta]{bpkio_home_env}[/magenta]"
        )
    else:
        default_home = Path.home() / ".bpkio"
        home_text = Text.from_markup(
            f"[bold]BPKIO_HOME[/bold]: [bold blue]{bpkio_home}[/bold blue]\n"
            f" -> Using default location: [magenta]{default_home}[/magenta]"
        )

    home_panel = Panel(
        home_text,
        title="Configuration",
        expand=False,
        border_style="blue",
        title_align="left",
    )
    console.print(home_panel)

    # Module check
    texts = []
    # Map: (display_name, distribution_name, module_name)
    for display_name, dist_name, module_name in [
        ("bpkio_cli", "bpkio-cli", "bpkio_cli"),
        ("bpkio_python_sdk", "bpkio-python-sdk", "bpkio_api"),
        ("media_muncher", "media-muncher", "media_muncher"),
    ]:
        module_spec = find_spec(module_name)
        pkg_version = get_package_version(dist_name, module_name)
        texts.append(
            Text.from_markup(
                f"[bold]{display_name}[/bold] - version: [bold blue]{pkg_version}[/bold blue] \n -> [magenta]{module_spec.origin}[/magenta]"
            )
        )

    module_panel = Panel(
        Group(*texts),
        title="Installed modules",
        expand=False,
        border_style="green",
        title_align="left",
    )
    console.print(module_panel)

    # Mode check
    admin_texts = []
    module_spec = find_spec("bpkio_api_admin")
    if module_spec and module_spec.origin:
        try:
            pkg_version = get_package_version(
                "bpkio-python-sdk-admin", "bpkio_api_admin"
            )
            admin_text = Text.from_markup(
                f"[bold]bpkio-python-sdk-admin[/bold] - version: [bold blue]{pkg_version}[/bold blue] \n -> [magenta]{module_spec.origin}[/magenta]"
            )
            admin_texts.append(admin_text)
        except Exception:
            pass

    module_spec = find_spec("bpkio_cli_admin")
    if module_spec and module_spec.origin:
        try:
            pkg_version = get_package_version("bpkio-cli-admin", "bpkio_cli_admin")
            admin_text = Text.from_markup(
                f"[bold]bpkio-cli-admin[/bold] - version: [bold blue]{pkg_version}[/bold blue] \n -> [magenta]{module_spec.origin}[/magenta]"
            )
            admin_texts.append(admin_text)
        except Exception:
            pass

    if admin_texts:
        admin_panel = Panel(
            Group(*admin_texts),
            title="Admin mode",
            expand=False,
            border_style="red",
            title_align="left",
        )
        console.print(admin_panel)

    if os.environ.get("BIC_MM_ONLY"):
        console.print(
            Panel(
                "Running in Media Muncher only mode",
                width=80,
                border_style="yellow",
                title_align="left",
            )
        )

    # Plugin check
    plugin_info = get_plugin_info()
    if plugin_info:
        plugin_texts = []
        for plugin_name, plugin_version, status, location in sorted(
            plugin_info, key=lambda x: x[0]
        ):
            status_color = "yellow" if status == "dev" else "green"
            status_label = "[dev]" if status == "dev" else "[installed]"
            if location:
                plugin_texts.append(
                    Text.from_markup(
                        f"[bold]{plugin_name}[/bold] - version: [bold blue]{plugin_version}[/bold blue] "
                        f"[{status_color}]{status_label}[/{status_color}] \n -> [magenta]{location}[/magenta]"
                    )
                )
            else:
                plugin_texts.append(
                    Text.from_markup(
                        f"[bold]{plugin_name}[/bold] - version: [bold blue]{plugin_version}[/bold blue] "
                        f"[{status_color}]{status_label}[/{status_color}]"
                    )
                )

        plugin_panel = Panel(
            Group(*plugin_texts),
            title="Plugins",
            expand=False,
            border_style="cyan",
            title_align="left",
        )
        console.print(plugin_panel)
    else:
        console.print(
            Panel(
                "No plugins found",
                width=80,
                border_style="cyan",
                title_align="left",
            )
        )
