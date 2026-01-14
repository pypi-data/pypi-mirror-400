"""
k3str is a collection of string operation utilily.

>>> repr(to_bytes('我'))
"b'\\\\xe6\\\\x88\\\\x91'"

"""

from importlib.metadata import version

__version__ = version("k3str")

from .str_ext import (
    default_encoding,
    to_bytes,
    to_utf8,
)

__all__ = [
    "default_encoding",
    "to_bytes",
    "to_utf8",
]
