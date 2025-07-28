"""DiffordsFinder - CLI tool for finding cocktail recipes from Difford's Guide."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("diffords-finder")
except PackageNotFoundError:
    __version__ = "0.0.0.dev0"

__all__ = ["__version__"]
