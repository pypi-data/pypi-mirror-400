"""
Find common prefix of several string, tuples of string, or other nested structure, recursively by default.
It returns the shortest prefix: empty string or empty tuple is removed.
"""

from importlib.metadata import version

__version__ = version("k3pattern")

from .strutil import (
    common_prefix,
)


__all__ = [
    "common_prefix",
]
