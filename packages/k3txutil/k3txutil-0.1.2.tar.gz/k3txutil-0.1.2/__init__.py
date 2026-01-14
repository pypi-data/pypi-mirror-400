"""
#   Name

txutil

#   Status

This library is considered production ready.

#   Description

A collection of helper functions to implement transactional operations.

#   Exceptions

##  CASConflict

**syntax**:
`CASConflict()`

User should raise this exception when a CAS conflict detect in a user defined
`set` function.

"""

# from .proc import CalledProcessError
# from .proc import ProcError

from importlib.metadata import version

__version__ = version("k3txutil")

from .txutil import (
    CASConflict,
    cas_loop,
)

__all__ = [
    "CASConflict",
    "cas_loop",
]
