from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass

from loguru import logger


DEFAULT_EXTRA_INDEX_URL = "https://pypi.org/simple"


def get_cli_pip_command() -> list[str]:
    """Pip command for the *current* interpreter environment (the CLI env)."""
    return [sys.executable, "-m", "pip"]


def normalize_pep503_repo_url(repo_url: str) -> str:
    """
    Normalize a PEP 503 repository URL.
    - Remove /index.html if present
    - Ensure it ends with a single trailing slash
    """
    normalized = repo_url.rstrip("/")
    if normalized.endswith("/index.html"):
        normalized = normalized[:-10]
    return normalized + "/"


@dataclass(frozen=True)
class PipRunResult:
    returncode: int
    stdout: str
    stderr: str


def run_pip(
    pip_cmd: list[str],
    args: list[str],
    *,
    check: bool = False,
    timeout: float | None = None,
) -> PipRunResult:
    cmd = [*pip_cmd, *args]
    logger.debug(f"Running pip: {' '.join(cmd)}")
    proc = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    if check and proc.returncode != 0:
        raise subprocess.CalledProcessError(
            proc.returncode, cmd, output=proc.stdout, stderr=proc.stderr
        )
    return PipRunResult(proc.returncode, proc.stdout or "", proc.stderr or "")


def get_latest_version_from_pip_index(pip_cmd: list[str], package: str) -> str | None:
    """
    Best-effort "latest version" by asking pip which versions are available.

    Notes:
    - Respects user pip configuration (indexes, auth, etc.)
    - Output format varies across pip versions; we parse a few common patterns.
    """
    res = run_pip(pip_cmd, ["index", "versions", package], check=False, timeout=30)
    if res.returncode != 0:
        return None

    text = "\n".join([res.stdout, res.stderr])

    # Common pip output patterns:
    # - "AVAILABLE VERSIONS: 3.2.1, 3.2.0, ..."
    # - "Available versions: 3.2.1, 3.2.0, ..."
    m = re.search(r"available versions:\s*(.+)$", text, flags=re.IGNORECASE | re.MULTILINE)
    if m:
        versions_part = m.group(1).strip()
        first = versions_part.split(",")[0].strip()
        return first or None

    # Some pip versions print:
    # "bpkio-cli (3.2.1) - ..." or "LATEST: 3.2.1"
    m = re.search(r"\bLATEST:\s*([0-9][^\s,)]*)", text, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip()

    m = re.search(rf"^{re.escape(package)}\s*\(([^)]+)\)", text, flags=re.IGNORECASE | re.MULTILINE)
    if m:
        return m.group(1).strip()

    return None


def pip_install_from_repos(
    *,
    pip_cmd: list[str],
    package_spec: str,
    repos: dict[str, str] | None,
    upgrade: bool = True,
    isolated: bool = True,
    constraints_file: str | None = None,
    extra_index_url: str = DEFAULT_EXTRA_INDEX_URL,
) -> None:
    """
    Install/upgrade a package, trying configured PEP503 repos in order.

    If repos is empty/None, falls back to default pip indexes.
    """
    base_args = ["install"]
    if upgrade:
        base_args.append("--upgrade")
    if isolated:
        base_args.append("--isolated")
    if constraints_file:
        base_args += ["-c", constraints_file]

    if not repos:
        args = [*base_args, package_spec]
        if extra_index_url:
            args += ["--extra-index-url", extra_index_url]
        run_pip(pip_cmd, args, check=True)
        return

    last_err: subprocess.CalledProcessError | None = None
    for _, repo_url in repos.items():
        normalized = normalize_pep503_repo_url(repo_url)
        args = [
            *base_args,
            "--index-url",
            normalized,
            package_spec,
        ]
        if extra_index_url:
            args += ["--extra-index-url", extra_index_url]
        try:
            run_pip(pip_cmd, args, check=True)
            return
        except subprocess.CalledProcessError as e:
            last_err = e
            continue

    assert last_err is not None
    raise last_err


