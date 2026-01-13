from importlib.metadata import PackageNotFoundError, version as _version
from ._client import TogglAPI, AsyncTogglAPI

__all__ = ["TogglAPI", "AsyncTogglAPI"]


_PACKAGE_NAME = "toggl-api-python"

try:
    __version__ = _version(_PACKAGE_NAME)
except PackageNotFoundError:
    __version__ = "0.0.0"
