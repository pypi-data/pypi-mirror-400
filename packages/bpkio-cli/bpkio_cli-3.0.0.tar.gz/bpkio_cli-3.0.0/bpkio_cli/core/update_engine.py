from __future__ import annotations

import importlib.metadata
import tempfile
from dataclasses import dataclass
from typing import Iterable

from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import InvalidVersion, Version

from bpkio_cli.core.pip_tools import pip_install_from_repos
from bpkio_cli.core.plugin_manager import plugin_manager


@dataclass(frozen=True)
class PluginCompat:
    dist_name: str
    dist_version: str
    specs: dict[str, SpecifierSet | None]
    status: str  # "ok" | "incompatible" | "unknown"


def is_downgrade(current_version: str | None, target_version: str) -> bool:
    """
    Check if target_version would be a downgrade from current_version.
    Returns True if target < current, False otherwise.
    If current_version is None (not installed), returns False (any version is fine).
    """
    if current_version is None:
        return False
    
    try:
        current_v = Version(current_version)
        target_v = Version(target_version)
        return target_v < current_v
    except InvalidVersion:
        # If versions can't be parsed, conservatively assume it's not a downgrade
        # (let pip handle it)
        return False


def iter_packaged_plugin_distributions() -> list[importlib.metadata.Distribution]:
    """
    Enumerate packaged plugin distributions from the plugin environment's site-packages,
    without importing plugin code / entry points.
    """
    site_packages = plugin_manager.get_site_packages_path()
    if not site_packages:
        return []
    try:
        dists = list(importlib.metadata.distributions(path=[str(site_packages)]))
    except TypeError:
        # Older stdlib signatures: distributions() without path, best-effort fallback.
        dists = list(importlib.metadata.distributions())

    plugins: list[importlib.metadata.Distribution] = []
    for dist in dists:
        name = (dist.metadata.get("Name") or dist.name or "").lower()
        if name.startswith("bpkio-cli-plugin-"):
            plugins.append(dist)
    return plugins


def extract_dependency_specs(
    dist: importlib.metadata.Distribution, *, package_names: Iterable[str]
) -> dict[str, SpecifierSet | None]:
    wanted = {n.lower().replace("_", "-") for n in package_names}
    out: dict[str, SpecifierSet | None] = {n: None for n in wanted}
    for raw in dist.requires or []:
        try:
            req = Requirement(raw)
        except Exception:
            continue
        n = req.name.lower().replace("_", "-")
        if n in wanted:
            out[n] = req.specifier
    return out


def build_compat_report(
    *,
    target_version: str,
    package_names: Iterable[str],
    primary_package: str,
    dists: Iterable[importlib.metadata.Distribution] | None = None,
) -> list[PluginCompat]:
    """
    Build a compatibility report by checking plugin dependency constraints.

    - If a plugin declares a constraint for `primary_package`, we evaluate it.
    - If it declares only other constraints (or none), status is "unknown".
    """
    target_v = Version(target_version)
    primary = primary_package.lower().replace("_", "-")
    pkg_names_norm = [n.lower().replace("_", "-") for n in package_names]

    if dists is None:
        dists = iter_packaged_plugin_distributions()

    report: list[PluginCompat] = []
    for dist in dists:
        dist_name = dist.metadata.get("Name") or dist.name or "unknown"
        dist_version = dist.version or "unknown"
        specs = extract_dependency_specs(dist, package_names=pkg_names_norm)

        primary_spec = specs.get(primary)
        if primary_spec:
            status = "ok" if target_v in primary_spec else "incompatible"
        elif any(specs.values()):
            status = "unknown"
        else:
            status = "unknown"

        report.append(
            PluginCompat(
                dist_name=dist_name,
                dist_version=dist_version,
                specs=specs,
                status=status,
            )
        )

    report.sort(key=lambda r: r.dist_name.lower())
    return report


def format_constraint(
    specs: dict[str, SpecifierSet | None], *, preferred: Iterable[str]
) -> str:
    for name in preferred:
        n = name.lower().replace("_", "-")
        spec = specs.get(n)
        if spec:
            return f"{n}{spec}"
    return "(none)"


def write_constraints_file(pins: dict[str, str]) -> str | None:
    """
    Write a pip constraints file pinning the given packages to exact versions.
    Returns the file path, or None if pins is empty.
    """
    if not pins:
        return None
    tmp = tempfile.NamedTemporaryFile(mode="w", delete=False)
    for name, version in pins.items():
        if version:
            tmp.write(f"{name}=={version}\n")
    tmp.flush()
    return tmp.name


def upgrade_packaged_plugins(
    *,
    pip_cmd: list[str],
    repos: dict[str, str] | None,
    constraints_file: str | None,
    dists: Iterable[importlib.metadata.Distribution] | None = None,
) -> list[tuple[str, str]]:
    """
    Upgrade all packaged plugins (bpkio-cli-plugin-*) in the plugin environment.
    Returns list of (plugin_name, error) failures.
    """
    if dists is None:
        dists = iter_packaged_plugin_distributions()

    failures: list[tuple[str, str]] = []
    for dist in dists:
        name = dist.metadata.get("Name") or dist.name
        if not name:
            continue
        try:
            pip_install_from_repos(
                pip_cmd=pip_cmd,
                package_spec=name,
                repos=repos,
                upgrade=True,
                isolated=True,
                constraints_file=constraints_file,
            )
        except Exception as e:
            failures.append((name, str(e)))
    return failures


