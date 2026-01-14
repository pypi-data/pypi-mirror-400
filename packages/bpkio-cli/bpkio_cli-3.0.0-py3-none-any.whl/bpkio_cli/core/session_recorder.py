import os
import random
import string
import tempfile
from pathlib import Path

from bpkio_cli.core.paths import get_bpkio_home

SENTINEL = get_bpkio_home() / "cli_session"


def sentinel_exists():
    return SENTINEL.exists()


def remove_sentinel():
    if SENTINEL.exists():
        os.remove(SENTINEL)


def get_session_file():
    session_file = None
    # open it and extract the path to the session file.
    if SENTINEL.exists():
        with open(SENTINEL, "r") as f:
            session_file = f.read()
    return session_file


def make_session_file(session_id):
    # Create the session file
    if not session_id:
        session_id = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=8)
        )

    temp_dir = tempfile.gettempdir()
    path = os.path.join(temp_dir, "bpkio_cli", "sessions", session_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Write the path to the sentinel
    SENTINEL.parent.mkdir(parents=True, exist_ok=True)
    with open(SENTINEL, "w") as f:
        f.write(path)

    return path


def destroy_session_file():
    session_file = get_session_file()
    if session_file:
        os.remove(session_file)
