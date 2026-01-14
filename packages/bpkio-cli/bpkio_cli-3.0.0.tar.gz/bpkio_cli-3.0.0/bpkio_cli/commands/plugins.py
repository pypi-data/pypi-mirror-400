import importlib
import importlib.metadata
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

import click
import cloup
import tomlkit
from loguru import logger
from packaging.utils import canonicalize_name
from packaging.version import InvalidVersion, Version
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.table import Table

from bpkio_cli.click_mods.accepts_plugins_group import AcceptsPluginsGroup
from bpkio_cli.core.config_provider import CONFIG
from bpkio_cli.core.pip_tools import normalize_pep503_repo_url
from bpkio_cli.core.plugin_manager import (
    PLUGINS_ENV_PATH,
    PLUGINS_SOURCE_DIR,
    plugin_manager,
)
from bpkio_cli.core.plugins_dev import PluginsDevManager
from bpkio_cli.writers.breadcrumbs import (
    display_error,
    display_info,
    display_ok,
    display_warning,
)

console = Console(width=120)
plugins_dev = PluginsDevManager(plugin_manager)


def _resolve_plugins_source_path(quiet: bool = False) -> Path | None:
    """
    Resolve the root directory that contains plugin sources.

    Order of preference:
    1. BPKIO_PLUGINS_SOURCE_DIR env var (absolute or relative to CWD)
    2. <current working dir>/bpkio-cli-plugins
    3. <repo root>/bpkio-cli-plugins (parent of the installed CLI repo)
    """
    candidates = plugins_dev.get_plugins_source_candidates()
    resolved = plugins_dev.resolve_plugins_source_path()
    if resolved:
        return resolved

    if not quiet:
        display_error(f"Plugin source directory '{PLUGINS_SOURCE_DIR}' not found.")
        display_info("Tried locations:")
        for candidate in candidates:
            display_info(f"  - {candidate}")
        display_info(
            "Set BPKIO_PLUGINS_SOURCE_DIR to point to your plugins source tree."
        )
    return None


def _get_plugin_site_packages() -> Path | None:
    """Gets the site-packages path for the plugin venv."""
    site_packages = plugin_manager.get_site_packages_path()
    if not site_packages:
        display_error("Could not locate site-packages for plugin environment.")
    return site_packages


def _find_local_plugins() -> list[Path]:
    """Scans the plugin source directory and returns a list of valid plugin paths."""
    plugins_source_path = _resolve_plugins_source_path()
    found_plugins = plugins_dev.find_local_plugins(plugins_source_path)
    if not found_plugins:
        display_warning("No plugin directories with a 'pyproject.toml' found.")
        return []

    return found_plugins


@cloup.group(
    cls=AcceptsPluginsGroup,
    aliases=["plugin"],
    help="Other functionality provided through addons (plugins)",
)
def plugins():
    pass


def _discover_plugin_commands():
    """
    Discover all plugin commands and return mappings.
    Returns:
        tuple: (command_to_plugin dict, local_dev_commands set)
    """
    plugin_manager._add_plugin_env_to_path()

    # Map commands to their plugin packages and track which are local dev
    command_to_plugin = {}
    local_dev_commands = set()

    # Discover commands from entry points (with package names)
    try:
        for ep in importlib.metadata.entry_points(group="bic.plugins"):
            # Get plugin package name from entry point distribution
            plugin_name = "unknown"
            try:
                if hasattr(ep, "dist") and ep.dist:
                    plugin_name = ep.dist.name
                else:
                    # Fallback: try to infer from entry point value
                    module_name = ep.value.split(":")[0].split(".")[0]
                    plugin_name = module_name.replace("_", "-")
            except Exception:
                pass

            # Remove bpkio-cli-plugin- prefix if present
            if plugin_name.startswith("bpkio-cli-plugin-"):
                plugin_name = plugin_name[len("bpkio-cli-plugin-") :]

            loaded_obj = ep.load()
            commands_list = loaded_obj if isinstance(loaded_obj, list) else [loaded_obj]
            for cmd in commands_list:
                if hasattr(cmd, "name"):
                    command_to_plugin[cmd] = plugin_name
    except Exception as e:
        logger.error(f"Error discovering plugins via entry points: {e}")

    # Discover manually loaded commands (from .pth files) and extract package names
    try:
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

                    # Extract package name and entry points from pyproject.toml
                    plugin_name = "local dev"
                    entry_points = {}
                    try:
                        with open(pyproject_path, "r") as pf:
                            toml = tomlkit.parse(pf.read())
                            plugin_name = (
                                toml.get("tool", {})
                                .get("poetry", {})
                                .get("name", "local dev")
                            )
                            entry_points = (
                                toml.get("tool", {})
                                .get("poetry", {})
                                .get("plugins", {})
                                .get("bic.plugins", {})
                            )
                    except Exception:
                        pass

                    # Remove bpkio-cli-plugin- prefix if present
                    if plugin_name.startswith("bpkio-cli-plugin-"):
                        plugin_name = plugin_name[len("bpkio-cli-plugin-") :]

                    # Discover commands from this plugin's entry points
                    try:
                        for name, path_str in entry_points.items():
                            module_path, obj_name = path_str.split(":")
                            if str(src_path) not in sys.path:
                                sys.path.insert(0, str(src_path))

                            module = importlib.import_module(module_path)
                            loaded_obj = getattr(module, obj_name)
                            commands_list = (
                                loaded_obj
                                if isinstance(loaded_obj, list)
                                else [loaded_obj]
                            )
                            for cmd in commands_list:
                                if hasattr(cmd, "name"):
                                    if cmd not in command_to_plugin:
                                        command_to_plugin[cmd] = plugin_name
                                    # Mark as local dev
                                    local_dev_commands.add(cmd)
                    except Exception as e:
                        logger.debug(
                            f"Could not load entry points from {pth_file}: {e}"
                        )
                except Exception as e:
                    logger.warning(f"Could not process .pth file {pth_file}: {e}")
    except Exception as e:
        logger.error(f"Error in manual plugin discovery: {e}")

    return command_to_plugin, local_dev_commands


@plugins.command(
    name="info",
    help="Show detailed information about an installed plugin.",
)
@click.argument("plugin_name", required=True)
def info(plugin_name: str):
    """
    Shows detailed information about an installed plugin, including metadata,
    description, dependencies, and version.
    """
    _show_installed_plugin_info(plugin_name)


@plugins.command(help="List all installed plugins", name="list")
def list_plugins():
    """List all installed plugins with their commands."""
    console.print(f"Plugin Environment: {PLUGINS_ENV_PATH}")
    console.print("[bold]Installed Plugins:[/bold]")

    try:
        command_to_plugin, local_dev_commands = _discover_plugin_commands()

        if not command_to_plugin:
            console.print("  No plugins found.")
            return

        # Group commands by plugin
        plugin_to_commands = {}
        plugin_is_local_dev = {}

        for cmd, plugin_name in command_to_plugin.items():
            if plugin_name not in plugin_to_commands:
                plugin_to_commands[plugin_name] = []
                plugin_is_local_dev[plugin_name] = False
            plugin_to_commands[plugin_name].append(cmd.name)
            if cmd in local_dev_commands:
                plugin_is_local_dev[plugin_name] = True

        table = Table("Plugin", "Dev", "Commands")
        for plugin_name in sorted(plugin_to_commands.keys()):
            dev_mark = "✓" if plugin_is_local_dev[plugin_name] else ""
            commands_list = ", ".join(sorted(plugin_to_commands[plugin_name]))
            table.add_row(plugin_name, dev_mark, commands_list)

        console.print(table)
    except Exception as e:
        display_error(f"Error discovering plugins: {e}")


@plugins.command(help="List all plugin commands with details", name="commands")
def list_plugin_commands():
    """List all plugin commands with their details."""
    console.print(f"Plugin Environment: {PLUGINS_ENV_PATH}")
    console.print("[bold]Discovered Plugin Commands (incl. local dev):[/bold]")

    try:
        command_to_plugin, local_dev_commands = _discover_plugin_commands()

        if not command_to_plugin:
            console.print("  No plugins found.")
            return

        table = Table("Name", "Type", "Plugin", "Dev", "Scope")
        for command, plugin_name in sorted(
            command_to_plugin.items(),
            key=lambda x: x[0].name if hasattr(x[0], "name") else "",
        ):
            cmd_name = command.name

            # Introspect to find out more about the command
            cmd_type = "Command"
            if isinstance(command, cloup.Group):
                cmd_type = "Group"

            # Show tick mark for local dev plugins
            dev_mark = "✓" if command in local_dev_commands else ""

            # Extract scope information
            scope_str = ""
            if hasattr(command, "scopes"):
                scopes = command.scopes
                if not scopes or scopes == ["*"]:
                    scope_str = "*"
                else:
                    scope_str = ", ".join(scopes)
            else:
                # No scopes attribute means it's available at top-level
                scope_str = "*"

            table.add_row(cmd_name, cmd_type, plugin_name, dev_mark, scope_str)
        console.print(table)
    except Exception as e:
        display_error(f"Error discovering plugins: {e}")


def _normalize_repo_url(repo_url: str) -> str:
    """
    Normalize a PEP 503 repository URL.
    - Remove /index.html if present
    - Ensure it ends with a single trailing slash
    """
    return normalize_pep503_repo_url(repo_url)


def _parse_metadata(metadata_content: str) -> dict[str, str | list[str]]:
    """
    Parse PKG-INFO/METADATA format into a dict.
    Fields that can appear multiple times (like Requires-Dist) are stored as lists.
    """
    metadata = {}
    lines = metadata_content.splitlines()

    # Find where description body starts (after empty line following Description-Content-Type)
    description_start_idx = None
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("description-content-type"):
            # Look for empty line after this
            for j in range(i + 1, len(lines)):
                if not lines[j].strip():
                    description_start_idx = j + 1
                    break
            break

    # Parse header fields (before description body)
    parse_end = description_start_idx if description_start_idx else len(lines)
    current_field = None
    current_value = []

    for i, line in enumerate(lines[:parse_end]):
        if not line.strip():
            continue
        if line.startswith(" ") or line.startswith("\t"):
            # Continuation line
            if current_field:
                current_value.append(line.strip())
        else:
            # New field
            if current_field:
                field_value = " ".join(current_value) if current_value else ""
                if current_field in ["requires-dist", "classifier"]:
                    if current_field not in metadata:
                        metadata[current_field] = []
                    if field_value:
                        metadata[current_field].append(field_value)
                else:
                    metadata[current_field] = field_value

            if ":" in line:
                current_field, value = line.split(":", 1)
                current_field = current_field.strip().lower()
                current_value = [value.strip()]
            else:
                current_field = None
                current_value = []

    # Don't forget the last field before description
    if current_field:
        field_value = " ".join(current_value) if current_value else ""
        if current_field in ["requires-dist", "classifier"]:
            if current_field not in metadata:
                metadata[current_field] = []
            if field_value:
                metadata[current_field].append(field_value)
        else:
            metadata[current_field] = field_value

    # Parse description body (everything after empty line)
    if description_start_idx and description_start_idx < len(lines):
        description_lines = lines[description_start_idx:]
        description_body = "\n".join(description_lines).strip()
        if description_body:
            metadata["description"] = description_body

    return metadata


def _get_package_metadata(
    repo_url: str, package_name: str, version: str | None = None
) -> dict[str, str | list[str]]:
    """
    Fetch package metadata (description, etc.) from a PEP 503 repository using PEP 658.
    Returns a dict with metadata fields like 'summary', 'author', etc.
    """
    normalized_name = canonicalize_name(package_name)
    wheel_dist_name = normalized_name.replace("-", "_")
    package_dir_url = repo_url + normalized_name + "/"

    # Get the latest version if not specified
    if not version:
        versions = _get_package_versions(repo_url, package_name)
        if not versions:
            return {}
        version = versions[0]

    # Try PEP 658 metadata file (lightweight)
    # Try common wheel filename patterns
    metadata_urls = [
        f"{package_dir_url}{wheel_dist_name}-{version}-py3-none-any.whl.metadata",
        f"{package_dir_url}{wheel_dist_name}-{version}-py3-any-none.whl.metadata",
    ]

    for metadata_url in metadata_urls:
        try:
            with urllib.request.urlopen(metadata_url, timeout=5) as response:
                metadata_content = response.read().decode("utf-8")
                return _parse_metadata(metadata_content)
        except urllib.error.HTTPError:
            continue
        except Exception as e:
            logger.debug(f"Error fetching metadata from {metadata_url}: {e}")
            continue

    return {}


def _get_metadata_from_pyproject(pyproject_path: Path) -> dict[str, str | list[str]]:
    """
    Extract metadata from a pyproject.toml file.
    Returns a dict with metadata fields like 'summary', 'author', etc.
    """
    metadata = {}
    try:
        with open(pyproject_path, "r") as f:
            toml = tomlkit.parse(f.read())

        poetry_data = toml.get("tool", {}).get("poetry", {})

        # Get basic fields
        if poetry_data.get("name"):
            metadata["name"] = poetry_data["name"]
        if poetry_data.get("version"):
            metadata["version"] = str(poetry_data["version"])
        if poetry_data.get("description"):
            metadata["summary"] = poetry_data["description"]
        if poetry_data.get("authors"):
            authors = poetry_data["authors"]
            if isinstance(authors, list) and authors:
                # Poetry authors format: ["Name <email>"]
                author_str = authors[0]
                if "<" in author_str and ">" in author_str:
                    name, email = author_str.rsplit("<", 1)
                    metadata["author"] = name.strip()
                    metadata["author-email"] = email.strip().rstrip(">")
                else:
                    metadata["author"] = author_str

        # Get Python requirement
        deps = poetry_data.get("dependencies", {})
        if "python" in deps:
            python_req = deps["python"]
            if isinstance(python_req, str):
                metadata["requires-python"] = python_req

        # Get dependencies (excluding runtime packages)
        requires_dist = []
        runtime_packages = [
            "bpkio-cli",
            "bpkio-cli-admin",
            "bpkio-python-sdk",
            "bpkio-python-sdk-admin",
        ]
        for dep_name, dep_spec in deps.items():
            if dep_name not in runtime_packages and dep_name != "python":
                if isinstance(dep_spec, str):
                    requires_dist.append(f"{dep_name} {dep_spec}")
                else:
                    requires_dist.append(dep_name)
        if requires_dist:
            metadata["requires-dist"] = requires_dist

        # Try to get description from README.md if available
        readme_file = poetry_data.get("readme")
        if readme_file:
            readme_path = pyproject_path.parent / readme_file
            if readme_path.exists():
                try:
                    description = readme_path.read_text(encoding="utf-8")
                    metadata["description"] = description
                    metadata["description-content-type"] = "text/markdown"
                except Exception:
                    pass

        return metadata
    except Exception as e:
        logger.debug(f"Error parsing pyproject.toml at {pyproject_path}: {e}")
        return {}


def _find_local_dev_plugin(plugin_name: str) -> Path | None:
    """
    Find a local dev plugin by checking .pth files.
    Returns the path to the plugin's pyproject.toml if found, None otherwise.
    """
    # Normalize plugin name (remove prefix for matching)
    search_name = plugin_name
    if search_name.startswith("bpkio-cli-plugin-"):
        search_name = search_name[len("bpkio-cli-plugin-") :]

    site_packages = plugin_manager.get_site_packages_path()
    if not site_packages or not site_packages.is_dir():
        return None

    for pth_file in site_packages.glob("bpkio-dev-*.pth"):
        try:
            # Extract plugin name from pth filename
            pth_plugin_name = pth_file.stem.replace("bpkio-dev-", "")
            if pth_plugin_name != search_name:
                continue

            src_path_str = pth_file.read_text().strip()
            if not src_path_str:
                continue

            src_path = Path(src_path_str)
            pyproject_path = src_path.parent / "pyproject.toml"
            if pyproject_path.exists():
                return pyproject_path
        except Exception:
            continue

    return None


def _get_installed_plugin_version(package_name: str) -> str | None:
    """
    Get the installed version of a plugin, checking both installed packages and local dev.
    Returns the version string or None if not found.
    """
    # First check if it's a local dev plugin
    pyproject_path = _find_local_dev_plugin(package_name)
    if pyproject_path:
        metadata = _get_metadata_from_pyproject(pyproject_path)
        if metadata and metadata.get("version"):
            return metadata["version"]

    # Otherwise, try to get from installed package
    try:
        plugin_manager._add_plugin_env_to_path()
        dist = importlib.metadata.distribution(package_name)
        return dist.version
    except importlib.metadata.PackageNotFoundError:
        return None
    except Exception as e:
        logger.debug(f"Error getting installed version for {package_name}: {e}")
        return None


def _get_installed_package_metadata(package_name: str) -> dict[str, str | list[str]]:
    """
    Get metadata from an installed package or local dev plugin.
    Returns a dict with metadata fields like 'summary', 'author', etc.
    """
    # First check if it's a local dev plugin
    pyproject_path = _find_local_dev_plugin(package_name)
    if pyproject_path:
        metadata = _get_metadata_from_pyproject(pyproject_path)
        if metadata:
            metadata["_is_local_dev"] = True
            return metadata

    # Otherwise, try to get from installed package
    try:
        plugin_manager._add_plugin_env_to_path()
        dist = importlib.metadata.distribution(package_name)

        metadata = {}

        # Get standard metadata fields
        if dist.metadata.get("Summary"):
            metadata["summary"] = dist.metadata.get("Summary", "")
        if dist.metadata.get("Author"):
            metadata["author"] = dist.metadata.get("Author", "")
        if dist.metadata.get("Author-email"):
            metadata["author-email"] = dist.metadata.get("Author-email", "")
        if dist.metadata.get("Requires-Python"):
            metadata["requires-python"] = dist.metadata.get("Requires-Python", "")
        if dist.metadata.get("Description-Content-Type"):
            metadata["description-content-type"] = dist.metadata.get(
                "Description-Content-Type", ""
            )

        # Get description (can be in Description field or Body)
        description = dist.metadata.get("Description", "")
        if description:
            metadata["description"] = description

        # Get Requires-Dist (dependencies)
        requires_dist = dist.metadata.get_all("Requires-Dist", [])
        if requires_dist:
            metadata["requires-dist"] = list(requires_dist)

        # Get version
        metadata["version"] = dist.version
        metadata["_is_local_dev"] = False

        return metadata
    except importlib.metadata.PackageNotFoundError:
        return {}
    except Exception as e:
        logger.debug(f"Error getting metadata for {package_name}: {e}")
        return {}


def _show_installed_plugin_info(plugin_name: str):
    """
    Show detailed information about an installed plugin.
    """
    # Normalize plugin name (add prefix if missing)
    if not plugin_name.startswith("bpkio-cli-plugin-"):
        plugin_name = f"bpkio-cli-plugin-{plugin_name}"

    # Get metadata from installed package
    metadata = _get_installed_package_metadata(plugin_name)

    if not metadata:
        display_error(f"Plugin '{plugin_name}' is not installed.")
        display_info("Use 'bic plugins list' to see installed plugins.")
        display_info(
            "Use 'bic plugins discover' to see available plugins in repositories."
        )
        return

    # Display plugin information
    console.print()

    # Header with name and version
    version = metadata.get("version", "unknown")
    is_local_dev = metadata.get("_is_local_dev", False)
    status_label = (
        "[dim](local dev)[/dim]" if is_local_dev else "[dim](installed)[/dim]"
    )
    header = (
        f"[bold cyan]{plugin_name}[/bold cyan] [dim]v{version}[/dim] {status_label}"
    )
    console.print(
        Panel(header, border_style="cyan", title="Plugin Information", width=120)
    )
    console.print()

    # Basic metadata table
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column(style="bold blue", width=20)
    info_table.add_column()

    if metadata.get("summary"):
        info_table.add_row("Summary", metadata["summary"])
    if metadata.get("author"):
        author_info = metadata["author"]
        if metadata.get("author-email"):
            author_info += f" <{metadata['author-email']}>"
        info_table.add_row("Author", author_info)
    if metadata.get("requires-python"):
        info_table.add_row("Python", metadata["requires-python"])
    requires_dist = metadata.get("requires-dist")
    if requires_dist:
        # Handle multiple Requires-Dist entries
        if isinstance(requires_dist, list):
            requires_str = "\n".join(f"  • {req}" for req in requires_dist)
        else:
            requires_str = requires_dist
        info_table.add_row("Dependencies", requires_str)

    console.print(info_table)
    console.print()

    # Description (markdown)
    description = metadata.get("description", "")
    if description:
        # Check if description is markdown
        content_type = metadata.get("description-content-type", "").lower()
        if "markdown" in content_type or description.strip().startswith("#"):
            console.print(
                Panel(
                    Markdown(description, code_theme="default", justify="left"),
                    border_style="blue",
                    title="Description",
                    width=120,
                )
            )
        else:
            console.print(
                Panel(description, border_style="blue", title="Description", width=120)
            )
        console.print()


def _show_plugin_details(plugin_name: str, repo_name: str | None):
    """
    Show detailed information about a specific plugin.
    """
    # Normalize plugin name (add prefix if missing)
    if not plugin_name.startswith("bpkio-cli-plugin-"):
        plugin_name = f"bpkio-cli-plugin-{plugin_name}"

    # Get repos to query
    if repo_name:
        repos = CONFIG.get_plugin_repos()
        if repo_name not in repos:
            display_error(f"Repository '{repo_name}' not configured.")
            available = ", ".join(repos.keys()) if repos else "none"
            display_info(f"Available repos: {available}")
            return
        repos_to_query = {repo_name: repos[repo_name]}
    else:
        repos_to_query = CONFIG.get_plugin_repos()
        if not repos_to_query:
            display_error("No plugin repositories configured.")
            display_info("Configure repos with: bic plugins repos set <name> <url>")
            return

    # Search for the plugin in repositories
    found_plugin = None
    found_repo_label = None
    found_repo_url = None

    for repo_label, repo_url in repos_to_query.items():
        normalized_repo = _normalize_repo_url(repo_url)
        versions = _get_package_versions(normalized_repo, plugin_name)
        if versions:
            found_plugin = plugin_name
            found_repo_label = repo_label
            found_repo_url = normalized_repo
            break

    if not found_plugin:
        display_error(f"Plugin '{plugin_name}' not found in any configured repository.")
        display_info("Use 'bic plugins discover' to see available plugins.")
        return

    # Fetch metadata
    metadata = _get_package_metadata(found_repo_url, found_plugin)
    versions = _get_package_versions(found_repo_url, found_plugin)

    if not metadata:
        display_warning(f"Found plugin '{found_plugin}' but could not fetch metadata.")
        display_info(
            f"Available versions: {', '.join(versions) if versions else 'unknown'}"
        )
        return

    # Display plugin information
    console.print()

    # Header with name and version
    latest_version = versions[0] if versions else "unknown"
    header = f"[bold cyan]{found_plugin}[/bold cyan] [dim]v{latest_version}[/dim]"
    if found_repo_label:
        header += f" [dim](from {found_repo_label} repository)[/dim]"
    console.print(
        Panel(header, border_style="cyan", title="Plugin Information", width=120)
    )
    console.print()

    # Basic metadata table
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column(style="bold blue", width=20)
    info_table.add_column()

    if metadata.get("summary"):
        info_table.add_row("Summary", metadata["summary"])
    if metadata.get("author"):
        author_info = metadata["author"]
        if metadata.get("author-email"):
            author_info += f" <{metadata['author-email']}>"
        info_table.add_row("Author", author_info)
    if metadata.get("requires-python"):
        info_table.add_row("Python", metadata["requires-python"])
    if versions:
        versions_str = (
            ", ".join(versions)
            if len(versions) <= 5
            else ", ".join(versions[:5]) + f" ... ({len(versions)} total)"
        )
        info_table.add_row("Versions", versions_str)
    requires_dist = metadata.get("requires-dist")
    if requires_dist:
        # Handle multiple Requires-Dist entries
        if isinstance(requires_dist, list):
            requires_str = "\n".join(f"  • {req}" for req in requires_dist)
        else:
            requires_str = requires_dist
        info_table.add_row("Dependencies", requires_str)

    console.print(info_table)
    console.print()

    # Description (markdown)
    description = metadata.get("description", "")
    if description:
        # Check if description is markdown
        content_type = metadata.get("description-content-type", "").lower()
        if "markdown" in content_type or description.strip().startswith("#"):
            console.print(
                Panel(
                    Markdown(description, code_theme="default", justify="left"),
                    border_style="blue",
                    title="Description",
                    width=120,
                )
            )
        else:
            console.print(
                Panel(description, border_style="blue", title="Description", width=120)
            )
        console.print()

    # Installation command
    install_cmd = f"bic plugins install {found_plugin}"
    if found_repo_label:
        install_cmd += f" --repo-name {found_repo_label}"
    console.print(
        Panel(
            f"[bold green]{install_cmd}[/bold green]",
            border_style="green",
            title="Install",
            width=120,
        )
    )


def _get_package_versions(repo_url: str, package_name: str) -> list[str]:
    """
    Fetch available versions for a package from a PEP 503 repository.
    Returns a list of version strings, sorted in descending order.

    Wheel format from Poetry: {distribution}-{version}-{python tag}-{abi tag}-{platform tag}.whl
    Where distribution uses underscores (e.g., bpkio_cli_plugin_admin_services)
    """
    normalized_name = canonicalize_name(package_name)
    # Wheel filenames use underscores, not dashes
    wheel_dist_name = normalized_name.replace("-", "_")
    package_dir_url = repo_url + normalized_name + "/"
    package_index_url = package_dir_url + "index.html"

    try:
        with urllib.request.urlopen(package_index_url, timeout=5) as response:
            content = response.read().decode("utf-8")
            wheel_files = re.findall(r'<a href="([^"]+\.whl)">', content)

            if not wheel_files:
                return []

            versions = []
            for wheel_file in wheel_files:
                # Extract version: everything between distribution name and Python tag (-py)
                # Pattern: {wheel_dist_name}-{version}-py...
                pattern = rf"{re.escape(wheel_dist_name)}-([^-]+)-py"
                match = re.search(pattern, wheel_file)
                if match:
                    version_str = match.group(1)
                    try:
                        Version(version_str)
                        versions.append(version_str)
                    except InvalidVersion:
                        # Skip invalid versions
                        continue

            # Sort versions in descending order
            if versions:
                versions.sort(key=lambda v: Version(v), reverse=True)

            return versions
    except urllib.error.HTTPError as e:
        if e.code == 404:
            logger.debug(f"Package '{package_name}' not found in repository")
        else:
            logger.debug(f"HTTP error fetching package versions: {e.code} - {e.reason}")
        return []
    except Exception as e:
        logger.debug(
            f"Error fetching package versions for '{package_name}': {e}", exc_info=True
        )
        return []


@plugins.command(
    name="discover",
    help="Discover available plugins in configured repositories. Provide a plugin name to see detailed information.",
)
@click.argument("plugin_name", required=False)
@click.option(
    "--repo-name",
    help="Specific repository name to query (e.g., 'public' or 'admin'). If not specified, queries all repos.",
    required=False,
)
@click.option(
    "--show-versions",
    is_flag=True,
    default=False,
    help="Show all available versions for each plugin (default: shows latest version only).",
)
def discover(plugin_name: str | None, repo_name: str | None, show_versions: bool):
    """
    Discovers all available plugins in configured repositories and displays them
    in a table format. Shows repository, package name, and available versions.

    If a plugin name is provided, shows detailed metadata for that plugin.
    """
    # If plugin name is provided, show detailed info for that plugin
    if plugin_name:
        _show_plugin_details(plugin_name, repo_name)
        return

    # Get repos to query
    if repo_name:
        repos = CONFIG.get_plugin_repos()
        if repo_name not in repos:
            display_error(f"Repository '{repo_name}' not configured.")
            available = ", ".join(repos.keys()) if repos else "none"
            display_info(f"Available repos: {available}")
            return
        repos_to_query = {repo_name: repos[repo_name]}
    else:
        repos_to_query = CONFIG.get_plugin_repos()
        if not repos_to_query:
            display_error("No plugin repositories configured.")
            display_info("Configure repos with: bic plugins repos set <name> <url>")
            return

    display_ok(
        f"Discovering plugins from {len(repos_to_query)} repository/repositories..."
    )

    all_packages = {}  # {package_name: {repo: [versions]}}

    for repo_label, repo_url in repos_to_query.items():
        normalized_repo = _normalize_repo_url(repo_url)
        index_url = normalized_repo + "index.html"

        display_info(f"Querying repository '{repo_label}' at {normalized_repo}...")

        try:
            with urllib.request.urlopen(index_url, timeout=10) as response:
                content = response.read().decode("utf-8")
                package_links = re.findall(r'<a href="([^/"]+)/">[^<]+</a>', content)

                if not package_links:
                    display_info(f"  No packages found in repository '{repo_label}'")
                    continue

                display_ok(f"  Found {len(package_links)} package(s) in '{repo_label}'")

                # Filter to only bpkio-cli plugins
                plugin_links = [
                    link
                    for link in package_links
                    if link.startswith("bpkio-cli-plugin-")
                ]

                if not plugin_links:
                    continue

                # Fetch versions and metadata for each package with progress bar
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    console=console,
                ) as progress:
                    task = progress.add_task(
                        f"[cyan]Fetching metadata from '{repo_label}'...",
                        total=len(plugin_links),
                    )

                    for package_link in plugin_links:
                        # Update progress description with current plugin
                        display_name = package_link
                        if display_name.startswith("bpkio-cli-plugin-"):
                            display_name = display_name[len("bpkio-cli-plugin-") :]
                        progress.update(
                            task, description=f"[cyan]Fetching {display_name}..."
                        )

                        versions = _get_package_versions(normalized_repo, package_link)
                        metadata = (
                            _get_package_metadata(normalized_repo, package_link)
                            if versions
                            else {}
                        )
                        if package_link not in all_packages:
                            all_packages[package_link] = {}
                        all_packages[package_link][repo_label] = {
                            "versions": versions,
                            "metadata": metadata,
                        }

                        progress.advance(task)

        except urllib.error.HTTPError as e:
            display_error(
                f"Failed to access repository '{repo_label}': HTTP {e.code} - {e.reason}"
            )
            display_info(f"  URL: {index_url}")
            continue
        except urllib.error.URLError as e:
            display_error(f"Failed to connect to repository '{repo_label}': {e.reason}")
            display_info(f"  URL: {index_url}")
            continue
        except Exception as e:
            display_error(f"Error querying repository '{repo_label}': {e}")
            logger.debug(f"Exception details: {e}", exc_info=True)
            continue

    if not all_packages:
        display_warning("No plugins found in any configured repository.")
        display_info("Make sure repositories are configured correctly and accessible.")
        return

    # Get installed versions for all discovered plugins
    plugin_manager._add_plugin_env_to_path()
    installed_versions = {}
    for package_name in all_packages.keys():
        installed_version = _get_installed_plugin_version(package_name)
        if installed_version:
            installed_versions[package_name] = installed_version

    # Display results in a table
    table = Table(
        "Package Name", "Description", "Installed", "Available Versions", "Repository"
    )
    table.title = "Available Plugins"
    table.expand = True  # Use full terminal width
    # Configure columns
    table.columns[0].width = 20  # Package Name
    table.columns[1].ratio = 3  # Description gets 3x space
    table.columns[1].no_wrap = False  # Allow wrapping for long descriptions
    table.columns[2].width = 12  # Installed
    table.columns[3].width = 20  # Available Versions
    table.columns[4].width = 12  # Repository

    for package_name in sorted(all_packages.keys()):
        for repo_label, data in sorted(all_packages[package_name].items()):
            versions = data.get("versions", [])
            metadata = data.get("metadata", {})
            description = metadata.get("summary", "") or metadata.get("description", "")
            # Don't truncate - let Rich handle wrapping

            # Remove bpkio-cli-plugin- prefix from display name
            display_name = package_name
            if display_name.startswith("bpkio-cli-plugin-"):
                display_name = display_name[len("bpkio-cli-plugin-") :]

            # Get installed version
            installed_version = installed_versions.get(package_name)
            if installed_version:
                installed_str = f"[green]{installed_version}[/green]"
            else:
                installed_str = "[dim]—[/dim]"

            if versions:
                if show_versions:
                    # Show all versions, comma-separated
                    versions_str = ", ".join(versions)
                else:
                    # Show only latest version
                    latest_version = versions[0]
                    # Highlight if update available
                    if installed_version and latest_version != installed_version:
                        try:
                            if Version(latest_version) > Version(installed_version):
                                versions_str = f"[yellow]{latest_version}[/yellow] [dim](update available)[/dim]"
                            else:
                                versions_str = latest_version
                        except Exception:
                            versions_str = latest_version
                    else:
                        versions_str = latest_version
            else:
                versions_str = "unknown"

            table.add_row(
                display_name,
                description,
                installed_str,
                versions_str,
                repo_label,
            )

    console.print()
    console.print(table)
    console.print()
    display_info(
        f"Found {len(all_packages)} plugin(s) across {len(repos_to_query)} repository/repositories."
    )
    display_info(
        "Get more information about a plugin with: bic plugins discover <plugin-name>"
    )
    display_info("Install a plugin with: bic plugins install <plugin-name>")

    if not show_versions:
        display_info(
            "Use --show-versions to see all available versions for each plugin."
        )


def _update_plugins_impl(
    plugin_names: tuple[str, ...] | None = None,
    force: bool = False,
    assume_yes: bool = False,
    cli_constraints: dict[str, str] | None = None,
) -> bool:
    """
    Shared implementation for updating plugins.
    Returns True if successful, False otherwise.
    """
    from bpkio_cli.core.pip_tools import get_latest_version_from_pip_index
    from bpkio_cli.core.update_engine import (
        is_downgrade,
        iter_packaged_plugin_distributions,
        upgrade_packaged_plugins,
        write_constraints_file,
    )

    repos = CONFIG.get_plugin_repos()
    if repos:
        display_info(
            f"Updating plugins using configured repos: {', '.join(repos.keys())}"
        )
    else:
        display_warning(
            "No plugin repositories configured; updating plugins using default pip indexes."
        )

    # Get installed plugins
    plugin_manager._add_plugin_env_to_path()
    all_dists = list(iter_packaged_plugin_distributions())

    if plugin_names:
        # Filter to specific plugins
        normalized_names = []
        for name in plugin_names:
            if not name.startswith("bpkio-cli-plugin-"):
                name = f"bpkio-cli-plugin-{name}"
            normalized_names.append(name)

        dists = [d for d in all_dists if d.name in normalized_names]
        if not dists:
            display_error(f"No matching installed plugins found: {plugin_names}")
            return False
    else:
        dists = all_dists
        if not dists:
            display_info("No plugins installed.")
            return True

    # Check for available updates and potential downgrades
    pip_cmd = plugin_manager.get_pip_command()
    plugins_to_update = []
    downgrades = []

    for dist in dists:
        name = dist.metadata.get("Name") or dist.name
        if not name:
            continue

        current_version = dist.version
        # Get latest version from repos
        latest_version = None
        if repos:
            # Try each repo
            for repo_url in repos.values():
                normalized_repo = _normalize_repo_url(repo_url)
                versions = _get_package_versions(normalized_repo, name)
                if versions:
                    latest_version = versions[0]  # Already sorted, latest first
                    break

        if not latest_version:
            # Fallback to pip index
            latest_version = get_latest_version_from_pip_index(pip_cmd, name)

        if latest_version and latest_version != current_version:
            if is_downgrade(current_version, latest_version):
                downgrades.append((name, current_version, latest_version))
            else:
                plugins_to_update.append((name, current_version, latest_version))

    if not plugins_to_update and not downgrades:
        display_ok("All plugins are up to date.")
        return True

    # Show what will be updated
    if plugins_to_update:
        display_info(f"Will update {len(plugins_to_update)} plugin(s):")
        for name, current, latest in plugins_to_update:
            display_name = name
            if display_name.startswith("bpkio-cli-plugin-"):
                display_name = display_name[len("bpkio-cli-plugin-") :]
            display_info(f"  {display_name}: {current} -> {latest}")

    if downgrades:
        display_warning(f"Would downgrade {len(downgrades)} plugin(s):")
        for name, current, latest in downgrades:
            display_name = name
            if display_name.startswith("bpkio-cli-plugin-"):
                display_name = display_name[len("bpkio-cli-plugin-") :]
            display_warning(f"  {display_name}: {current} -> {latest}")
        if not force:
            display_error("Refusing to downgrade plugins without --force.")
            return False

    if not assume_yes:
        if not click.confirm("Proceed with update?", default=True):
            return False

    # Update plugins
    constraints_file = None

    # Prevent downgrading CLI packages in shared mode
    # Use provided constraints or determine from current installation
    if cli_constraints:
        constraints_file = write_constraints_file(cli_constraints)
    elif not plugin_manager.use_isolated_env:
        try:
            current_cli = importlib.metadata.version("bpkio-cli")
            pins = {"bpkio-cli": current_cli}
            try:
                current_admin = importlib.metadata.version("bpkio-cli-admin")
                pins["bpkio-cli-admin"] = current_admin
            except importlib.metadata.PackageNotFoundError:
                pass
            constraints_file = write_constraints_file(pins)
        except Exception:
            pass

    failures = upgrade_packaged_plugins(
        pip_cmd=pip_cmd,
        repos=repos,
        constraints_file=constraints_file,
        dists=dists,
    )

    # Report results
    for name, err in failures:
        display_error(f"Failed to upgrade plugin: {name} ({err})")

    for dist in dists:
        name = dist.metadata.get("Name") or dist.name
        if name and all(n != name for (n, _) in failures):
            display_ok(f"Upgraded plugin: {name}")

    if failures:
        display_warning(f"{len(failures)} plugin(s) failed to upgrade.")
        return False
    else:
        display_ok(f"Successfully updated {len(plugins_to_update)} plugin(s).")
        return True


@plugins.command(
    name="update",
    help="Update installed plugins to their latest available versions.",
)
@click.argument("plugin_names", nargs=-1, required=False)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Allow downgrading plugins (default: refuse downgrades).",
)
@click.option(
    "--yes",
    "assume_yes",
    is_flag=True,
    default=False,
    help="Do not prompt for confirmation.",
)
def update_plugins(plugin_names: tuple[str, ...], force: bool, assume_yes: bool):
    """
    Update installed plugins to their latest available versions.
    Uses configured plugin repositories if available.

    If plugin names are provided, only those plugins will be updated.
    Otherwise, all installed plugins will be checked for updates.
    """
    success = _update_plugins_impl(
        plugin_names=plugin_names if plugin_names else None,
        force=force,
        assume_yes=assume_yes,
    )
    if not success:
        raise SystemExit(1)


@plugins.group(name="repos", help="Manage plugin repositories")
def repos():
    """Manage plugin repository URLs."""
    pass


@repos.command(name="list", help="List configured plugin repositories")
def list_repos():
    """List all configured plugin repositories."""
    repos = CONFIG.get_plugin_repos()
    if repos:
        table = Table("Name", "URL")
        for name, url in repos.items():
            table.add_row(name, url)
        console.print(table)
    else:
        console.print("No repositories configured")


@repos.command(name="set", help="Set a plugin repository URL")
@click.argument("repo_name")  # e.g., "public" or "admin"
@click.argument("repo_url")
def set_repo(repo_name: str, repo_url: str):
    """Set a plugin repository URL."""
    CONFIG.set_plugin_repo(repo_name, repo_url)
    display_ok(f"Set repository '{repo_name}' to: {repo_url}")


@repos.command(name="get", help="Get a plugin repository URL")
@click.argument("repo_name")
def get_repo(repo_name: str):
    """Get a plugin repository URL."""
    repos = CONFIG.get_plugin_repos()
    if repo_name in repos:
        click.echo(repos[repo_name])
    else:
        display_error(f"Repository '{repo_name}' not configured")


@plugins.command(name="install", help="Install a plugin from a repository.")
@click.argument("packages", nargs=-1, required=True)
@click.option(
    "--repo-name",
    help="Specific repository name to use (e.g., 'public' or 'admin'). If not specified, tries all repos.",
    required=False,
)
@click.option(
    "--repo-url",
    help="Specific repository URL to use (overrides config).",
    required=False,
)
def install(packages: tuple[str], repo_name: str | None, repo_url: str | None):
    """
    Installs one or more plugins from configured repositories.
    - In isolated mode: installs into the dedicated plugins venv.
    - In shared mode: installs into the current CLI environment.
    """
    # Get repos to try
    if repo_url:
        repos_to_try = {"custom": repo_url}
    elif repo_name:
        repos = CONFIG.get_plugin_repos()
        if repo_name not in repos:
            display_error(f"Repository '{repo_name}' not configured.")
            available = ", ".join(repos.keys()) if repos else "none"
            display_info(f"Available repos: {available}")
            return
        repos_to_try = {repo_name: repos[repo_name]}
    else:
        repos_to_try = CONFIG.get_plugin_repos()
        if not repos_to_try:
            display_error("No plugin repositories configured.")
            display_info("Configure repos with: bic plugins repos set <name> <url>")
            return

    pip_cmd = plugin_manager.get_pip_command()

    for package_name in packages:
        installed = False

        # Always prefix with bpkio-cli-plugin- if missing
        if not package_name.startswith("bpkio-cli-plugin-"):
            try_package_name = f"bpkio-cli-plugin-{package_name}"
        else:
            try_package_name = package_name

        for repo_label, repo in repos_to_try.items():
            normalized_repo = _normalize_repo_url(repo)

            display_ok(
                f"Trying to install '{try_package_name}' from {repo_label} ({normalized_repo})..."
            )

            command = [
                *pip_cmd,
                "install",
                "--isolated",
                "--index-url",
                normalized_repo,
                try_package_name,
                "--extra-index-url",
                "https://pypi.org/simple",
            ]

            logger.debug(f"Running pip command: {' '.join(command)}")

            # Also check if the package directory exists and is accessible
            normalized_package = canonicalize_name(try_package_name)
            package_dir_url = normalized_repo + normalized_package + "/"
            package_index_url = package_dir_url + "index.html"
            logger.debug(f"Package directory URL: {package_dir_url}")
            logger.debug(f"Package index URL: {package_index_url}")

            try:
                with urllib.request.urlopen(package_index_url, timeout=5) as response:
                    content = response.read().decode("utf-8")
                    logger.debug(f"Package index.html content:\n{content}")

                    wheel_files = re.findall(r'<a href="([^"]+\.whl)">', content)
                    logger.debug(
                        f"Found {len(wheel_files)} wheel file(s) in package directory: {wheel_files}"
                    )
                    if not wheel_files:
                        logger.warning(
                            "Package directory exists but contains no wheel files!"
                        )
                    else:
                        # Check if wheel file URLs are accessible
                        for wheel_file in wheel_files:
                            wheel_url = package_dir_url + wheel_file
                            logger.debug(
                                f"Checking wheel file accessibility: {wheel_url}"
                            )
                            try:
                                wheel_response = urllib.request.urlopen(
                                    wheel_url, timeout=5
                                )
                                logger.debug(
                                    f"Wheel file accessible: {wheel_file} (size: {wheel_response.headers.get('Content-Length', 'unknown')} bytes)"
                                )
                                wheel_response.close()
                            except Exception as wheel_error:
                                logger.warning(
                                    f"Wheel file not accessible: {wheel_file} - {wheel_error}"
                                )
            except urllib.error.HTTPError as e:
                logger.warning(
                    f"Could not access package directory: HTTP {e.code} - {e.reason}"
                )
                logger.debug(f"Package directory URL: {package_index_url}")
            except Exception as e:
                logger.debug(f"Could not check package directory: {e}")

            try:
                result = subprocess.run(
                    command, check=True, capture_output=True, text=True
                )
                logger.debug(f"Pip stdout: {result.stdout}")
                # Only show pip output in debug mode (it's verbose with all dependencies)
                if result.stdout:
                    logger.debug(f"Pip output: {result.stdout}")
                display_ok(
                    f"Successfully installed '{try_package_name}' from {repo_label}."
                )
                installed = True
                break  # Break out of repos_to_try loop
            except subprocess.CalledProcessError as e:
                error_output = e.stderr or e.stdout or ""
                logger.debug(f"Pip failed with return code {e.returncode}")
                logger.debug(f"Pip stdout: {e.stdout}")
                logger.debug(f"Pip stderr: {e.stderr}")

                # Check if pip is checking multiple indexes (which might cause issues)
                if e.stdout and "Looking in indexes:" in e.stdout:
                    logger.debug(
                        "Pip is checking multiple indexes - this might cause conflicts"
                    )

                # Check if this is a dependency resolution error (should always be shown)
                is_dependency_error = (
                    "Could not find a version that satisfies the requirement"
                    in error_output
                    and "from "
                    in error_output  # Indicates it's a dependency, not the main package
                )

                if (
                    "Could not find a version" in error_output
                    or "No matching distribution" in error_output
                    or "404" in error_output
                ):
                    # If it's a dependency resolution error, show it even without debug
                    if is_dependency_error:
                        display_error(
                            f"Failed to install '{try_package_name}' from {repo_label} due to dependency resolution error:"
                        )
                        display_error(f"PIP Stderr:\n{e.stderr}")
                        # Don't continue to next repo if it's a dependency issue
                        # The package exists but has unsatisfiable dependencies
                        continue

                    # Package not found, try next repo
                    display_info(
                        f"Package '{try_package_name}' not found in {repo_label}, trying next..."
                    )
                    continue  # Try next repository
                else:
                    display_error(
                        f"Failed to install '{try_package_name}' from {repo_label}."
                    )
                    display_error(f"PIP Stderr:\n{e.stderr}")
                    continue  # Try next repository

            if installed:
                break  # Break out of repos_to_try loop

        if not installed:
            display_error(
                f"Could not install '{package_name}' from any configured repository."
            )
            logger.debug(f"Tried repositories: {', '.join(repos_to_try.keys())}")
            logger.debug(f"Tried package name: {try_package_name}")
            # Show what's available in each repository
            for repo_label, repo in repos_to_try.items():
                normalized_repo = _normalize_repo_url(repo)
                try:
                    index_url = normalized_repo + "index.html"
                    logger.debug(
                        f"Checking available packages in {repo_label}: {index_url}"
                    )
                    with urllib.request.urlopen(index_url, timeout=5) as response:
                        content = response.read().decode("utf-8")

                        package_links = re.findall(
                            r'<a href="([^/"]+)/">[^<]+</a>', content
                        )
                        logger.info(
                            f"Repository '{repo_label}' contains {len(package_links)} package(s): {', '.join(package_links)}"
                        )
                except Exception as e:
                    logger.debug(f"Could not check repository {repo_label}: {e}")


# -------------------------------------------------------------------------------------------------
# Development commands
# -------------------------------------------------------------------------------------------------


@plugins.group(name="dev")
def dev():
    """
    Development commands for plugins.
    """
    pass


@dev.command(
    name="setup",
    help="Set up all local plugins for development by linking them to the plugin environment.",
)
def setup():
    """
    Scans for all plugins in the 'bpkio-cli-plugins' directory and sets them up for development.
    For each plugin, it:
    1. Installs its dependencies ONLY into the shared plugin environment.
    2. Creates a .pth file in the environment's site-packages to make the plugin's source code importable.
    """
    plugins_source_path = _resolve_plugins_source_path()
    if not plugins_source_path:
        return

    display_ok(f"Scanning for plugins in {plugins_source_path}...")

    found_plugins = _find_local_plugins()
    if not found_plugins:
        return

    site_packages = _get_plugin_site_packages()
    if not site_packages:
        return

    # Ensure runtime packages are NOT installed in an isolated plugins venv
    cleanup = plugins_dev.cleanup_runtime_packages_in_isolated_env()
    if cleanup.removed:
        for pkg in cleanup.removed:
            display_ok(f"Removed {pkg} from plugins environment (provided at runtime).")
    if cleanup.failed:
        for pkg in cleanup.failed:
            display_warning(
                f"Could not remove {pkg} from plugins environment (may not be installed)."
            )

    for plugin_path in found_plugins:
        click.echo("-" * 40)
        display_ok(f"Setting up development mode for plugin: {plugin_path.name}")

        result = plugins_dev.setup_dev_plugin(plugin_path, site_packages=site_packages)
        if result.success:
            if result.removed_from_pyproject:
                packages_str = ", ".join(
                    f"'{p}'" for p in result.removed_from_pyproject
                )
                display_info(
                    f"Temporarily removed {packages_str} from pyproject.toml for dependency resolution."
                )
            if result.filtered_runtime_packages:
                packages_str = ", ".join(
                    f"'{p}'" for p in sorted(set(result.filtered_runtime_packages))
                )
                display_warning(
                    f"Filtered out {packages_str} from dependencies for '{plugin_path.name}'. "
                    "These packages are provided at runtime by the main CLI."
                )
            display_ok(f"Successfully created dev-mode link for {plugin_path.name}.")
        else:
            display_error(
                f"Failed during dependency installation for {plugin_path.name}."
            )
            if result.error and "poetry" in result.error.lower():
                display_error("The 'poetry' command was not found.")
            if result.error:
                display_error(result.error)
            continue

    click.echo("-" * 40)
    display_ok("Development setup complete for all found plugins.")


@dev.command(name="teardown", help="Remove all plugins from local development mode.")
def teardown():
    """
    Removes all .pth files, taking all plugins out of development mode.
    This does NOT uninstall plugin dependencies.
    """
    display_ok("Uninstalling all dev-mode plugins...")

    site_packages = _get_plugin_site_packages()
    if not site_packages:
        return

    removed = plugins_dev.remove_all_dev_pth_files(site_packages=site_packages)
    if removed > 0:
        display_ok(f"\nRemoved {removed} development plugin link(s).")
    else:
        display_warning("No development plugin links were found to remove.")


@dev.command(name="package", help="Package all local plugins into wheels.")
def package():
    """
    Scans for all plugins in the 'bpkio-cli-plugins' directory, builds them,
    and places the resulting wheel and sdist files in a common 'bpkio-cli-plugins/dist' directory.

    Automatically adds bpkio-cli dependency with version constraint before building,
    then restores the original pyproject.toml after packaging.
    """
    plugins_source_path = _resolve_plugins_source_path()
    if not plugins_source_path:
        return

    output_dir = plugins_source_path / "dist"
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        display_error(f"Could not create output directory {output_dir}: {e}")
        return

    display_ok(f"Packaging plugins into: {output_dir.resolve()}")

    found_plugins = _find_local_plugins()
    if not found_plugins:
        return

    # Get current CLI version for default constraint (only used if plugin doesn't declare bpkio-cli or bpkio-cli-admin)
    cli_version = plugins_dev.get_running_cli_version()
    if cli_version == "unknown":
        display_warning(
            "Could not determine bpkio-cli version, using '>=2.0.0' as default"
        )
        default_bpkio_cli_constraint = ">=2.0.0"
    else:
        # Extract major version for a permissive default (e.g., 2.11.0 -> >=2.0.0)
        # This allows plugins to work with any version in the same major release
        try:
            major_version = cli_version.split(".")[0]
            default_bpkio_cli_constraint = f">={major_version}.0.0"
        except (IndexError, AttributeError):
            default_bpkio_cli_constraint = ">=2.0.0"

    success_count = 0
    failure_count = 0
    for plugin_path in found_plugins:
        click.echo("-" * 40)
        display_ok(f"Packaging plugin: {plugin_path.name}")

        pyproject_path = plugin_path / "pyproject.toml"
        original_pyproject = None

        try:
            # Read and modify pyproject.toml to add bpkio-cli if not present
            if pyproject_path.is_file():
                with open(pyproject_path, "r") as f:
                    original_pyproject = f.read()
                    pyproject_data = tomlkit.parse(original_pyproject)

                # Check if bpkio-cli or bpkio-cli-admin is already in dependencies
                deps = (
                    pyproject_data.get("tool", {})
                    .get("poetry", {})
                    .get("dependencies", {})
                )
                has_cli = "bpkio-cli" in deps
                has_cli_admin = "bpkio-cli-admin" in deps

                if not has_cli and not has_cli_admin:
                    # Neither is declared, add bpkio-cli with default version constraint
                    deps["bpkio-cli"] = default_bpkio_cli_constraint
                    display_info(
                        f"Added bpkio-cli = '{default_bpkio_cli_constraint}' to dependencies for packaging (plugin can override with explicit constraint)"
                    )
                elif has_cli:
                    # Respect existing bpkio-cli declaration
                    existing_constraint = deps["bpkio-cli"]
                    display_info(
                        f"Using existing bpkio-cli constraint: '{existing_constraint}'"
                    )
                elif has_cli_admin:
                    # Respect existing bpkio-cli-admin declaration
                    existing_constraint = deps["bpkio-cli-admin"]
                    display_info(
                        f"Using existing bpkio-cli-admin constraint: '{existing_constraint}'"
                    )

                    # Write modified pyproject.toml
                    with open(pyproject_path, "w") as f:
                        f.write(tomlkit.dumps(pyproject_data))

            # Run poetry build
            cmd = ["poetry", "build"]
            display_info(f"Running: {' '.join(cmd)} in {plugin_path}")
            subprocess.run(
                cmd, cwd=plugin_path, check=True, capture_output=True, text=True
            )

            # Move the built artifacts
            plugin_dist_path = plugin_path / "dist"
            artifacts = list(plugin_dist_path.glob("*"))
            if not artifacts:
                display_warning(f"No build artifacts found for {plugin_path.name}")
            else:
                for artifact in artifacts:
                    dest_path = output_dir / artifact.name
                    display_info(f"Moving {artifact.name} to {output_dir}")
                    shutil.move(str(artifact), str(dest_path))

                display_ok(f"Successfully packaged {plugin_path.name}.")
                success_count += 1

        except subprocess.CalledProcessError as e:
            display_error(f"Failed to build plugin {plugin_path.name}.")
            click.echo(click.style(e.stdout, fg="yellow"))
            click.echo(click.style(e.stderr, fg="red"))
            failure_count += 1
        except FileNotFoundError:
            display_error(
                "The 'poetry' command was not found. Please ensure Poetry is installed and in your PATH."
            )
            # If poetry isn't installed, it will fail for all of them.
            return
        finally:
            # Restore original pyproject.toml if we modified it
            if original_pyproject is not None and pyproject_path.is_file():
                try:
                    with open(pyproject_path, "w") as f:
                        f.write(original_pyproject)
                    display_info(
                        f"Restored original pyproject.toml for {plugin_path.name}"
                    )
                except Exception as e:
                    display_warning(
                        f"Failed to restore pyproject.toml for {plugin_path.name}: {e}"
                    )

    click.echo("-" * 40)
    if failure_count == 0:
        display_ok(f"Successfully packaged {success_count} plugins.")
    else:
        display_warning(
            f"Completed packaging with {success_count} successes and {failure_count} failures."
        )


@dev.command(name="publish", help="Prepare local plugin packages for publishing.")
@click.option(
    "--separate-admin",
    is_flag=True,
    default=True,
    help="Create separate public and admin repositories (default: True).",
)
@click.option(
    "--s3",
    "s3_url",
    help="S3 URL to sync repositories to (e.g., 's3://my-bucket/plugins'). If separate-admin is True, will sync to '<s3-url>/public/' and '<s3-url>/admin/'.",
    required=False,
)
def publish(separate_admin: bool, s3_url: str | None):
    """
    Builds PEP 503 Simple Repositories from the packaged plugins, ready for synchronization with S3.
    By default, creates separate 'public-pep503-repo' and 'admin-pep503-repo' directories.
    If --s3 is provided, automatically syncs the repositories to the specified S3 location.
    """
    plugins_source_path = _resolve_plugins_source_path()
    if not plugins_source_path:
        return

    dist_path = plugins_source_path / "dist"
    if not dist_path.is_dir() or not any(dist_path.iterdir()):
        display_warning(
            f"No packaged plugins found in {dist_path}. Running 'package' command first."
        )
        # Call the package command's logic directly
        package.callback()

    wheels = list(dist_path.glob("*.whl"))
    if not wheels:
        display_error("No wheel files found to publish, even after packaging.")
        return

    found_plugins = _find_local_plugins()
    if not found_plugins:
        return

    if separate_admin:
        # Create two separate repos
        public_repo_path = dist_path / "public-pep503-repo"
        admin_repo_path = dist_path / "admin-pep503-repo"

        for repo_path_obj in [public_repo_path, admin_repo_path]:
            if repo_path_obj.exists():
                display_info(f"Cleaning existing repository at: {repo_path_obj}")
                shutil.rmtree(repo_path_obj)
            repo_path_obj.mkdir()

        display_info("Building separate repositories: public and admin")

        # Separate plugins by admin_only flag
        public_plugins = []
        admin_plugins = []

        for plugin_path in found_plugins:
            if plugins_dev.is_admin_plugin(plugin_path):
                admin_plugins.append(plugin_path)
            else:
                public_plugins.append(plugin_path)

        # Build public repo
        if public_plugins:
            included = plugins_dev.build_pep503_repo(
                public_repo_path, public_plugins, dist_path
            )
            display_ok(f"Built public repository with {included} plugin(s)")
            display_ok(f"Public repository: {public_repo_path}")
        else:
            display_warning("No public plugins found to publish")

        # Build admin repo
        if admin_plugins:
            included = plugins_dev.build_pep503_repo(
                admin_repo_path, admin_plugins, dist_path
            )
            display_ok(f"Built admin repository with {included} plugin(s)")
            display_ok(f"Admin repository: {admin_repo_path}")
        else:
            display_warning("No admin plugins found to publish")

        if s3_url:
            # Sync public repo if it has plugins
            if public_plugins:
                target = f"{s3_url.rstrip('/')}/public/"
                display_info(f"Syncing public repository to {target}...")
                try:
                    plugins_dev.sync_to_s3(public_repo_path, target)
                    display_ok(f"Successfully synced public repository to {target}")
                except FileNotFoundError:
                    display_error(
                        "AWS CLI not found. Please install it or sync manually using 'aws s3 sync'."
                    )
                except subprocess.CalledProcessError as e:
                    display_error(f"Failed to sync to S3: {e.stderr}")
                    raise
            # Sync admin repo if it has plugins
            if admin_plugins:
                target = f"{s3_url.rstrip('/')}/admin/"
                display_info(f"Syncing admin repository to {target}...")
                try:
                    plugins_dev.sync_to_s3(admin_repo_path, target)
                    display_ok(f"Successfully synced admin repository to {target}")
                except FileNotFoundError:
                    display_error(
                        "AWS CLI not found. Please install it or sync manually using 'aws s3 sync'."
                    )
                except subprocess.CalledProcessError as e:
                    display_error(f"Failed to sync to S3: {e.stderr}")
                    raise
            display_ok("Repositories synced to S3 successfully.")
        else:
            display_info(
                f"Next step: Sync these directories to your S3 buckets, e.g.,\n"
                f"  'aws s3 sync {public_repo_path} s3://your-bucket/plugins/public/'\n"
                f"  'aws s3 sync {admin_repo_path} s3://your-bucket/plugins/admin/'\n"
                f"  Or use --s3 to sync automatically."
            )
    else:
        # Original single repo behavior (for backward compatibility)
        local_repo_path = dist_path / "local-pep503-repo"
        if local_repo_path.exists():
            display_info(f"Cleaning existing local repository at: {local_repo_path}")
            shutil.rmtree(local_repo_path)
        local_repo_path.mkdir()

        display_ok(f"Building single repository at: {local_repo_path.resolve()}")
        included = plugins_dev.build_pep503_repo(
            local_repo_path, found_plugins, dist_path
        )
        display_ok(f"Built unified repository with {included} plugin(s)")

        display_ok(f"Local repository successfully built at '{local_repo_path}'.")
        if s3_url:
            # Sync to S3
            target = s3_url.rstrip("/") + "/"
            display_ok(f"Syncing unified repository to {target}...")
            try:
                plugins_dev.sync_to_s3(local_repo_path, target)
                display_ok(f"Successfully synced unified repository to {target}")
            except FileNotFoundError:
                display_error(
                    "AWS CLI not found. Please install it or sync manually using 'aws s3 sync'."
                )
            except subprocess.CalledProcessError as e:
                display_error(f"Failed to sync to S3: {e.stderr}")
                raise
            display_ok("Repository synced to S3 successfully.")
        else:
            display_info(
                f"Next step: Sync this directory to your S3 bucket, e.g., 'aws s3 sync {local_repo_path} s3://your-bucket-name/'.\n"
                f"  Or use --s3 to sync automatically."
            )


@dev.command(name="init", help="Initialize a new plugin skeleton.")
@click.argument("plugin_name")
def init(plugin_name: str):
    """
    Creates a new plugin directory with a standard structure and boilerplate files.
    """
    plugins_root = _resolve_plugins_source_path(quiet=True)
    if not plugins_root:
        plugins_root = Path.cwd() / PLUGINS_SOURCE_DIR
        try:
            plugins_root.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            display_error(f"Failed to create plugin root directory: {e}")
            return

    safe_plugin_name = plugin_name.lower().replace(" ", "-").replace("_", "-")
    package_name = safe_plugin_name.replace("-", "_")

    plugin_dir = plugins_root / safe_plugin_name
    if plugin_dir.exists():
        display_error(f"Plugin directory '{plugin_dir}' already exists.")
        return

    display_ok(f"Initializing new plugin: {safe_plugin_name}")

    # Create directory structure
    src_dir = plugin_dir / "src" / f"bpkio_cli_plugin_{package_name}"
    try:
        src_dir.mkdir(parents=True)
    except OSError as e:
        display_error(f"Failed to create directory structure: {e}")
        return

    # Create boilerplate files
    try:
        python_version = f"^{sys.version_info.major}.{sys.version_info.minor}"
        # pyproject.toml
        pyproject_content = f"""[tool.poetry]
name = "bpkio-cli-plugin-{safe_plugin_name}"
version = "0.1.0"
description = "A bpkio-cli plugin for {safe_plugin_name}."
authors = ["Your Name <you@example.com>"]
readme = "README.md"
packages = [{{ include = "bpkio_cli_plugin_{package_name}", from = "src" }}]

[tool.poetry.dependencies]
bpkio-cli = "^{importlib.metadata.version("bpkio-cli")}"
python = "{python_version}"
click = "*"

[tool.poetry.plugins."bic.plugins"]
"{safe_plugin_name}" = "bpkio_cli_plugin_{package_name}.commands:{package_name}_plugin"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""
        (plugin_dir / "pyproject.toml").write_text(pyproject_content)

        # README.md
        readme_content = f"# bpkio-cli-plugin-{safe_plugin_name}\\n\\nA bpkio-cli plugin for {safe_plugin_name}.\\n"
        (plugin_dir / "README.md").write_text(readme_content)

        # src/__init__.py
        (src_dir / "__init__.py").touch()

        # src/commands.py
        commands_content = f"""import click

@click.command(name="{safe_plugin_name}")
def {package_name}_plugin():
    \"\"\"
    A sample command from the {safe_plugin_name} plugin.
    \"\"\"
    click.echo("Hello from the {safe_plugin_name} plugin!")
"""
        (src_dir / "commands.py").write_text(commands_content)

    except OSError as e:
        display_error(f"Failed to write boilerplate files: {e}")
        # Clean up created directory if file writing fails
        shutil.rmtree(plugin_dir)
        return

    # Ask the user for confirmation before proceeding
    if not click.confirm(
        f"\nDo you want to create the plugin skeleton in '{plugin_dir.resolve()}'?",
        default=True,
    ):
        display_warning("Plugin creation aborted by user.")
        # Clean up the created directory if the user aborts
        shutil.rmtree(plugin_dir)
        return

    display_ok(f"Successfully created plugin skeleton at: {plugin_dir}")
    display_info(
        "Next steps: customize the pyproject.toml and start coding in src/commands.py!"
    )
