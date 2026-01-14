from importlib.metadata import PackageNotFoundError, version

try:
    # When installed as a distribution.
    __version__ = version("bpkio-cli")
except PackageNotFoundError:
    # When running from a source checkout (no installed dist metadata).
    __version__ = "0.0.0"

