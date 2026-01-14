import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path

from bpkio_cli.core.config_provider import CONFIG

# Directory containing this script file
here = Path(__file__).resolve().parent
assets_dir = (here / "../assets").resolve()


def chime_down():
    _chime("G4-C4")


def chime_up():
    _chime("C4-G4")


def chime_uphigh():
    _chime("C4-C5")


def chime():
    _chime("E4-E4")


def _is_wsl() -> bool:
    # Best-effort detection for WSL1/WSL2.
    if "WSL_DISTRO_NAME" in os.environ or "WSL_INTEROP" in os.environ:
        return True
    try:
        with open("/proc/version", "r", encoding="utf-8", errors="ignore") as f:
            v = f.read().lower()
        return "microsoft" in v or "wsl" in v
    except OSError:
        return False


def _spawn(cmd: list[str]) -> bool:
    try:
        subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=not sys.platform.startswith("win"),
        )
        return True
    except Exception:
        return False


def _play_windows_wav(path: str) -> bool:
    try:
        import winsound  # stdlib on Windows

        # SND_ASYNC keeps it non-blocking; SND_FILENAME plays a file path.
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        return True
    except Exception:
        return False


def _play_macos(path: str) -> bool:
    afplay = shutil.which("afplay")
    if not afplay:
        return False
    return _spawn([afplay, path])


def _play_linux(path: str) -> bool:
    # Try common native audio players (best-effort).
    # - paplay: PulseAudio / PipeWire compatibility layer
    # - aplay: ALSA
    # - ffplay: fallback if installed
    for tool, args in [
        ("paplay", [path]),
        ("aplay", ["-q", path]),
        ("ffplay", ["-nodisp", "-autoexit", "-loglevel", "quiet", path]),
    ]:
        exe = shutil.which(tool)
        if exe and _spawn([exe, *args]):
            return True
    return False


def _ps_escape_single_quotes(value: str) -> str:
    """Escape single quotes for PowerShell single-quoted strings."""
    return value.replace("'", "''")


def _wslpath_to_windows(path: str) -> str | None:
    """Convert a WSL path to a Windows path using wslpath."""
    wslpath = shutil.which("wslpath")
    if not wslpath:
        return None

    try:
        result = subprocess.check_output(
            [wslpath, "-w", path],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return result if result else None
    except Exception:
        return None


def _play_wsl(path: str) -> bool:
    # WSL: always play on Windows side (no Linux audio attempts)
    ps = shutil.which("powershell.exe")
    if not ps:
        return False

    win_path = _wslpath_to_windows(path)
    if not win_path:
        return False

    win_path_escaped = _ps_escape_single_quotes(win_path)
    script = (
        f"$p = '{win_path_escaped}'; "
        "try { "
        "  $sp = New-Object System.Media.SoundPlayer($p); "
        "  $sp.Play(); "
        "} catch { }"
    )
    return _spawn([ps, "-NoProfile", "-Command", script])


def detect_audio_mechanism() -> str:
    """
    Detect which audio mechanism will be used on this system.
    Returns a descriptive string of the mechanism.
    """
    if _is_wsl():
        if shutil.which("powershell.exe") and shutil.which("wslpath"):
            return "WSL (Windows PowerShell via wslpath)"
        if not shutil.which("powershell.exe"):
            return "WSL (powershell.exe not available)"
        return "WSL (wslpath not available)"

    if sys.platform.startswith("win"):
        # Native Windows
        try:
            import winsound  # noqa: F401

            return "Windows (winsound)"
        except ImportError:
            return "Windows (winsound not available)"

    if sys.platform == "darwin":
        if shutil.which("afplay"):
            return "macOS (afplay)"
        return "macOS (afplay not available)"

    # Native Linux (non-WSL)
    for tool in ["paplay", "aplay", "ffplay"]:
        if shutil.which(tool):
            return f"Linux ({tool})"
    return "Linux (no audio mechanism available)"


def _chime(filename: str) -> None:
    # Check environment variable first (highest priority)
    if os.environ.get("BIC_NO_SOUND", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }:
        return

    # Check config setting (audio-notifications)
    if not CONFIG.get("audio-notifications", cast_type=bool):
        return

    wav = str(assets_dir / f"{filename}.wav")

    def play_sound():
        try:
            # Check WSL first (since sys.platform.startswith("win") is true for WSL too)
            if _is_wsl():
                _play_wsl(wav)
                return
            if sys.platform.startswith("win"):
                _play_windows_wav(wav)
                return
            if sys.platform == "darwin":
                _play_macos(wav)
                return
            # Native Linux (non-WSL)
            _play_linux(wav)
        except Exception:
            # Never let audio issues crash the CLI
            pass

    threading.Thread(target=play_sound, daemon=True).start()
