"""
Firebird database backend for Django.

Supports Firebird 2.5, 3.0, 4.0, and 5.0+
Requires firebird-driver >= 1.10.0
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("django-firebird")
except PackageNotFoundError:
    # Package is not installed (development mode)
    try:
        from ._version import __version__
    except ImportError:
        __version__ = "0.0.0.dev0"

__author__ = "joseanoxp"


# Register custom expressions when Django loads
def _setup():
    try:
        from . import expressions  # noqa: F401
    except ImportError:
        pass


_setup()
