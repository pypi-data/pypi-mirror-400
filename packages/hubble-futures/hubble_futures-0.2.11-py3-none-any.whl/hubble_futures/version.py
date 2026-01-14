"""Version information for hubble-futures package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("hubble-futures")
except PackageNotFoundError:
    __version__ = "0.2.11"
