# libsrg (Code and Documentation) is published under an MIT License
# Copyright (c) 2023,2024 Steven Goncalo
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# 2024 Steven Goncalo
from importlib.metadata import version
from logging import getLevelName

"""
Logging utilities provides a few helpful static methods.
"""


def libsrg_version():
    """Return the version of the libsrg package."""
    try:
        ver = version('libsrg')
    except (ImportError, AttributeError):
        ver = "unknown"
    return f"libsrg {ver} {__file__} "


def level2str(lev) -> str:
    """Convert a level to a string."""
    if not isinstance(lev, str):
        lev = getLevelName(lev)
    return lev


def level2int(lev) -> int:
    """Convert a level to a number."""
    if isinstance(lev, str):
        lev = getLevelName(lev)
    return lev
