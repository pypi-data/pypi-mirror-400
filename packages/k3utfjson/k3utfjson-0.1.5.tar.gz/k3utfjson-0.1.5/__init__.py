"""
# Name

utfjson: force `json.dump` and `json.load` in `utf-8` encoding.

# Status

This library is considered production ready.

"""

# from .proc import CalledProcessError
# from .proc import ProcError

from importlib.metadata import version

__version__ = version("k3utfjson")

from .utfjson import (
    dump,
    load,
)

__all__ = [
    "dump",
    "load",
]
