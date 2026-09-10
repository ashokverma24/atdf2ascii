from importlib.metadata import PackageNotFoundError, version

from .cli import atdf_to_ascii

try:
    __version__ = version("atdf2ascii")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["__version__", "atdf_to_ascii"]
