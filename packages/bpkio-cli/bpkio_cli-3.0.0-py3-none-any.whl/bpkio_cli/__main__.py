"""Entry point for running bpkio_cli as a module with python3 -m bpkio_cli"""

from bpkio_cli.app import safe_entry_point

if __name__ == "__main__":
    safe_entry_point()
