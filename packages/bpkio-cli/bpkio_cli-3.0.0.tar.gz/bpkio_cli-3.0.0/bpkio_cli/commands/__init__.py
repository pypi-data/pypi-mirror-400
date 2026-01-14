"""
Command modules package.

Historically, this module imported *all* CLI commands at import time. That made
startup very slow because heavy dependencies (e.g. dash/pandas/media_muncher)
were imported even when the user only executed a lightweight command.

Do not import command modules here. Import them only when needed by the CLI
dispatcher.
"""

# Intentionally empty: commands are loaded lazily by `bpkio_cli.app`.
