""" General tools for working with wheels

Tools that aren't specific to delocate or auditwheel.
"""

from .wheeltools import *

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0.0+unknown"
