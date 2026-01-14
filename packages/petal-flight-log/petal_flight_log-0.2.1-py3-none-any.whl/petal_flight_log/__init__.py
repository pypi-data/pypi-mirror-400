import logging
from importlib.metadata import PackageNotFoundError, version as _pkg_version

logger = logging.getLogger(__name__)

try:
    # ⚠️ Use the *distribution* name (what you put in pyproject.toml), not necessarily the import name
    __version__ = _pkg_version("petal-flight-log")
except PackageNotFoundError:
    # Useful during local development before install; pick what you prefer here
    __version__ = "0.0.0"