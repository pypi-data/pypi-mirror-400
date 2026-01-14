import importlib.metadata
import os
import shutil
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

import tomlkit
from loguru import logger
from packaging.utils import canonicalize_name

from bpkio_cli.core.plugin_manager import PLUGINS_SOURCE_DIR, PluginManager


# Runtime packages provided by the main CLI installation (or bpkio-cli-admin).
# These should not be installed into an isolated plugin venv and should be filtered
# out during dependency resolution in dev mode.
RUNTIME_PACKAGES = [
    "bpkio-cli",  # Main CLI package
    "bpkio-cli-admin",  # Admin meta-package (subsumes bpkio-cli)
    "bpkio-python-sdk",  # Main SDK
    "bpkio-python-sdk-admin",  # Admin SDK (used by bpkio-cli-admin)
]


@dataclass(frozen=True)
class DevSetupResult:
    plugin_path: Path
    success: bool
    created_pth: Path | None = None
    filtered_runtime_packages: tuple[str, ...] = ()
    removed_from_pyproject: tuple[str, ...] = ()
    error: str | None = None


@dataclass(frozen=True)
class RuntimePackagesCleanupResult:
    removed: tuple[str, ...] = ()
    failed: tuple[str, ...] = ()


class PluginsDevManager:
    """
    Helper for plugin development workflows (local source discovery, dev .pth links,
    dependency install via Poetry export -> pip, etc).

    Kept separate from PluginManager to avoid bloating the core env/discovery logic.
    """

    def __init__(self, plugin_manager: PluginManager):
        self.plugin_manager = plugin_manager

    def get_plugins_source_candidates(self) -> list[Path]:
        """
        Returns candidate locations for the plugins source tree.

        Order of preference:
        1. BPKIO_PLUGINS_SOURCE_DIR env var (absolute or relative to CWD)
        2. <current working dir>/bpkio-cli-plugins
        3. <bpkio-cli repo root>/bpkio-cli-plugins (if running from source checkout)
        """
        candidates: list[Path] = []

        env_override = os.getenv("BPKIO_PLUGINS_SOURCE_DIR")
        if env_override:
            candidates.append(Path(env_override).expanduser())

        candidates.append(Path.cwd() / PLUGINS_SOURCE_DIR)

        # If running from source, this file is at:
        #   <repo>/bpkio-cli/bpkio_cli/core/plugins_dev.py
        # so parents[2] is <repo>/bpkio-cli
        candidates.append(Path(__file__).resolve().parents[2] / PLUGINS_SOURCE_DIR)
        return candidates

    def resolve_plugins_source_path(self) -> Path | None:
        """Resolve the root directory that contains plugin sources."""
        for candidate in self.get_plugins_source_candidates():
            if candidate.is_dir():
                return candidate
        return None

    def find_local_plugins(self, plugins_source_path: Path | None = None) -> list[Path]:
        """
        Scans the plugin source directory and returns a list of valid plugin paths.
        A "valid plugin" is a directory containing a pyproject.toml.
        """
        root = plugins_source_path or self.resolve_plugins_source_path()
        if not root or not root.is_dir():
            return []
        return [
            p for p in root.iterdir() if p.is_dir() and (p / "pyproject.toml").is_file()
        ]

    def is_admin_plugin(self, plugin_path: Path) -> bool:
        """Check if a plugin is marked as admin-only in its pyproject.toml."""
        pyproject_path = plugin_path / "pyproject.toml"
        if not pyproject_path.is_file():
            return False
        try:
            with open(pyproject_path, "r") as f:
                toml_data = tomlkit.parse(f.read())
                bpkio_config = toml_data.get("tool", {}).get("bpkio-cli", {})
                return bool(bpkio_config.get("admin_only", False))
        except Exception:
            return False

    def get_running_cli_version(self) -> str:
        """
        Get the version of the currently running CLI, preferring the source checkout's
        pyproject.toml when available.
        """
        try:
            cli_dir = Path(__file__).resolve().parents[2]  # .../bpkio-cli
            pyproject_path = cli_dir / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "r") as f:
                    toml_data = tomlkit.parse(f.read())
                    cli_version = toml_data.get("tool", {}).get("poetry", {}).get("version")
                    if cli_version:
                        return str(cli_version)
        except Exception:
            pass

        try:
            return importlib.metadata.version("bpkio-cli")
        except Exception:
            return "unknown"

    def cleanup_runtime_packages_in_isolated_env(
        self, runtime_packages: list[str] | None = None
    ) -> RuntimePackagesCleanupResult:
        """
        Ensures runtime packages are NOT installed in the isolated plugin environment.
        No-op in shared mode.
        """
        if not self.plugin_manager.use_isolated_env:
            return RuntimePackagesCleanupResult()

        runtime_packages = runtime_packages or RUNTIME_PACKAGES
        removed: list[str] = []
        failed: list[str] = []

        python_executable = self.plugin_manager.python_executable
        if not python_executable or not python_executable.is_file():
            return RuntimePackagesCleanupResult(removed=(), failed=tuple(runtime_packages))

        for package_name in runtime_packages:
            try:
                check_result = subprocess.run(
                    [str(python_executable), "-m", "pip", "show", package_name],
                    capture_output=True,
                    text=True,
                )
                if check_result.returncode != 0:
                    continue

                uninstall_result = subprocess.run(
                    [
                        str(python_executable),
                        "-m",
                        "pip",
                        "uninstall",
                        "-y",
                        package_name,
                    ],
                    capture_output=True,
                    text=True,
                )
                if uninstall_result.returncode == 0:
                    removed.append(package_name)
                else:
                    failed.append(package_name)
            except Exception:
                failed.append(package_name)

        return RuntimePackagesCleanupResult(
            removed=tuple(removed), failed=tuple(failed)
        )

    def _temporarily_remove_runtime_packages_from_pyproject(
        self, pyproject_path: Path, runtime_packages: list[str]
    ) -> tuple[str | None, list[str]]:
        if not pyproject_path.is_file():
            return None, []

        original_pyproject = pyproject_path.read_text()
        removed: list[str] = []
        try:
            pyproject_data = tomlkit.parse(original_pyproject)
            deps = (
                pyproject_data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            )
            for pkg in runtime_packages:
                if pkg in deps:
                    removed.append(pkg)
                    del deps[pkg]
            if removed:
                pyproject_path.write_text(tomlkit.dumps(pyproject_data))
        except Exception:
            return original_pyproject, []

        return original_pyproject, removed

    def _restore_pyproject(self, pyproject_path: Path, original_pyproject: str | None):
        if original_pyproject is None:
            return
        try:
            if pyproject_path.is_file():
                pyproject_path.write_text(original_pyproject)
        except Exception as e:
            logger.warning(f"Failed to restore {pyproject_path}: {e}")

    def _poetry_export_requirements(self, plugin_path: Path, requirements_out: Path):
        cmd_export = [
            "poetry",
            "export",
            "--without-hashes",
            "-f",
            "requirements.txt",
            "-o",
            str(requirements_out),
        ]
        export_result = subprocess.run(
            cmd_export,
            capture_output=True,
            text=True,
            cwd=plugin_path,
        )
        if export_result.returncode == 0:
            return

        error_output = (export_result.stderr or "") + (export_result.stdout or "")
        error_lower = error_output.lower()
        lock_file_errors = [
            "poetry.lock was last generated",
            "lock file",
            "pyproject.toml changed significantly",
            "run `poetry lock`",
        ]
        if any(err in error_lower for err in lock_file_errors):
            subprocess.run(
                ["poetry", "lock"],
                capture_output=True,
                text=True,
                cwd=plugin_path,
                check=True,
            )
            subprocess.run(
                cmd_export,
                capture_output=True,
                text=True,
                cwd=plugin_path,
                check=True,
            )
            return

        export_result.check_returncode()

    def _filter_runtime_packages_from_requirements(
        self, requirements_in: Path, requirements_out: Path, runtime_packages: list[str]
    ) -> list[str]:
        filtered_packages: list[str] = []
        runtime_lower = [p.lower() for p in runtime_packages]
        with open(requirements_in, "r") as f_in, open(requirements_out, "w") as f_out:
            for line in f_in:
                line_lower = line.strip().lower()
                filtered = False
                for pkg in runtime_lower:
                    if line_lower.startswith(pkg):
                        filtered_packages.append(pkg)
                        filtered = True
                        break
                if not filtered:
                    f_out.write(line)
        return sorted(set(filtered_packages))

    def create_dev_pth_for_plugin(
        self, plugin_path: Path, site_packages: Path | None = None
    ) -> Path:
        site_packages = site_packages or self.plugin_manager.get_site_packages_path()
        if not site_packages or not site_packages.is_dir():
            raise RuntimeError("Could not locate site-packages for plugin environment.")

        src_path = plugin_path / "src"
        if not src_path.is_dir():
            raise RuntimeError(f"'src' directory not found in {plugin_path}.")

        pth_file_name = f"bpkio-dev-{plugin_path.name}.pth"
        pth_file_path = site_packages / pth_file_name
        pth_file_path.write_text(str(src_path.resolve()))
        return pth_file_path

    def remove_all_dev_pth_files(self, site_packages: Path | None = None) -> int:
        site_packages = site_packages or self.plugin_manager.get_site_packages_path()
        if not site_packages or not site_packages.is_dir():
            return 0

        removed = 0
        for pth_file in site_packages.glob("bpkio-dev-*.pth"):
            try:
                pth_file.unlink()
                removed += 1
            except OSError as e:
                logger.warning(f"Error removing file {pth_file}: {e}")
        return removed

    def setup_dev_plugin(
        self,
        plugin_path: Path,
        runtime_packages: list[str] | None = None,
        site_packages: Path | None = None,
    ) -> DevSetupResult:
        runtime_packages = runtime_packages or RUNTIME_PACKAGES
        python_executable = self.plugin_manager.python_executable
        if not python_executable or not python_executable.is_file():
            return DevSetupResult(
                plugin_path=plugin_path,
                success=False,
                error=f"Python executable not found for plugin environment: {self.plugin_manager.python_executable}",
            )

        pyproject_path = plugin_path / "pyproject.toml"
        original_pyproject = None
        removed_from_pyproject: list[str] = []
        temp_requirements_path: Path | None = None
        filtered_requirements_path: Path | None = None
        filtered_runtime_packages: list[str] = []

        try:
            original_pyproject, removed_from_pyproject = (
                self._temporarily_remove_runtime_packages_from_pyproject(
                    pyproject_path, runtime_packages
                )
            )

            tmp = tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".txt", dir=plugin_path
            )
            tmp.close()
            temp_requirements_path = Path(tmp.name)
            self._poetry_export_requirements(plugin_path, temp_requirements_path)

            filtered_requirements_path = Path(str(temp_requirements_path) + ".filtered")
            filtered_runtime_packages = self._filter_runtime_packages_from_requirements(
                temp_requirements_path,
                filtered_requirements_path,
                runtime_packages,
            )

            subprocess.run(
                [
                    str(python_executable),
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    str(filtered_requirements_path),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            created_pth = self.create_dev_pth_for_plugin(
                plugin_path, site_packages=site_packages
            )
            return DevSetupResult(
                plugin_path=plugin_path,
                success=True,
                created_pth=created_pth,
                filtered_runtime_packages=tuple(filtered_runtime_packages),
                removed_from_pyproject=tuple(removed_from_pyproject),
            )
        except FileNotFoundError as e:
            return DevSetupResult(
                plugin_path=plugin_path,
                success=False,
                filtered_runtime_packages=tuple(filtered_runtime_packages),
                removed_from_pyproject=tuple(removed_from_pyproject),
                error=str(e),
            )
        except subprocess.CalledProcessError as e:
            err = (e.stderr or e.stdout or "").strip()
            return DevSetupResult(
                plugin_path=plugin_path,
                success=False,
                filtered_runtime_packages=tuple(filtered_runtime_packages),
                removed_from_pyproject=tuple(removed_from_pyproject),
                error=err or f"Command failed with return code {e.returncode}",
            )
        except Exception as e:
            return DevSetupResult(
                plugin_path=plugin_path,
                success=False,
                filtered_runtime_packages=tuple(filtered_runtime_packages),
                removed_from_pyproject=tuple(removed_from_pyproject),
                error=str(e),
            )
        finally:
            self._restore_pyproject(pyproject_path, original_pyproject)
            try:
                if temp_requirements_path and temp_requirements_path.exists():
                    temp_requirements_path.unlink()
            except Exception:
                pass
            try:
                if filtered_requirements_path and filtered_requirements_path.exists():
                    filtered_requirements_path.unlink()
            except Exception:
                pass

    def get_package_name_from_pyproject(self, plugin_path: Path) -> str | None:
        """Reads the package name from a plugin's pyproject.toml."""
        try:
            pyproject_path = plugin_path / "pyproject.toml"
            if pyproject_path.is_file():
                with open(pyproject_path, "r") as f:
                    toml = tomlkit.parse(f.read())
                    return toml.get("tool", {}).get("poetry", {}).get("name")
        except Exception as e:
            logger.warning(f"Could not read or parse {plugin_path / 'pyproject.toml'}: {e}")
        return None

    def extract_metadata_from_wheel(self, wheel_path: Path) -> str | None:
        """
        Extract METADATA file from a wheel (PEP 658 support).
        Returns the METADATA content as a string, or None if extraction fails.
        """
        try:
            with zipfile.ZipFile(wheel_path, "r") as wheel:
                metadata_files = [
                    f for f in wheel.namelist() if f.endswith(".dist-info/METADATA")
                ]
                if metadata_files:
                    return wheel.read(metadata_files[0]).decode("utf-8")
        except Exception as e:
            logger.debug(f"Could not extract metadata from wheel {wheel_path}: {e}")
        return None

    def build_pep503_repo(
        self,
        repo_path: Path,
        plugin_paths: list[Path],
        dist_path: Path,
    ) -> int:
        """
        Build a PEP 503 "simple" repository for the given plugins.
        Returns the number of plugins included (i.e. those with a name + a built wheel).
        """
        repo_index_content = ["<!DOCTYPE html><html><body>"]
        package_dirs: dict[str, dict] = {}

        included_plugins = 0

        for plugin_path in plugin_paths:
            package_name = self.get_package_name_from_pyproject(plugin_path)
            if not package_name:
                logger.warning(
                    f"Skipping plugin at {plugin_path} because its package name could not be determined."
                )
                continue

            safe_wheel_name = package_name.replace("-", "_")
            wheel_paths = list(dist_path.glob(f"{safe_wheel_name}-*.whl"))
            if not wheel_paths:
                logger.warning(f"Could not find a built wheel for package '{package_name}'.")
                continue

            included_plugins += 1
            normalized_name = canonicalize_name(package_name)

            if normalized_name not in package_dirs:
                package_dir = repo_path / normalized_name
                package_dir.mkdir(exist_ok=True)
                package_dirs[normalized_name] = {"dir": package_dir, "files": []}
                repo_index_content.append(
                    f'  <a href="{normalized_name}/">{normalized_name}</a><br/>'
                )

            for wheel_path in wheel_paths:
                shutil.copy(wheel_path, package_dirs[normalized_name]["dir"])
                package_dirs[normalized_name]["files"].append(wheel_path.name)

                metadata_content = self.extract_metadata_from_wheel(wheel_path)
                if metadata_content:
                    metadata_filename = wheel_path.name + ".metadata"
                    metadata_path = package_dirs[normalized_name]["dir"] / metadata_filename
                    metadata_path.write_text(metadata_content)
                    package_dirs[normalized_name]["files"].append(metadata_filename)

        # Create index.html files for each package directory
        for _, data in package_dirs.items():
            package_index_parts = ["<!DOCTYPE html><html><body>"]
            for filename in data["files"]:
                if filename.endswith(".metadata"):
                    wheel_name = filename[:-10]  # Remove .metadata extension
                    package_index_parts.append(
                        f'<a href="{filename}" data-dist-info-metadata="true">{wheel_name}</a><br/>'
                    )
                else:
                    package_index_parts.append(f'<a href="{filename}">{filename}</a><br/>')
            package_index_parts.append("</body></html>")
            (data["dir"] / "index.html").write_text("\n".join(package_index_parts))

        repo_index_content.append("</body></html>")
        (repo_path / "index.html").write_text("\n".join(repo_index_content))
        return included_plugins

    def sync_to_s3(self, local_path: Path, s3_url: str):
        """
        Sync a local directory to S3 using `aws s3 sync`.
        Raises FileNotFoundError if aws isn't installed, or CalledProcessError on failure.
        """
        result = subprocess.run(
            ["aws", "s3", "sync", str(local_path), s3_url],
            check=True,
            capture_output=True,
            text=True,
        )
        if result.stdout:
            logger.debug(result.stdout)
        if result.stderr:
            logger.debug(result.stderr)


