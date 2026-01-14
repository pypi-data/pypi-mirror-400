"""
#   Name

k3shell

#   Status

The library is considered production ready.

"""

from importlib.metadata import version

__version__ = version("k3shell")

from .command import (
    command,
)

__all__ = [
    "command",
]
