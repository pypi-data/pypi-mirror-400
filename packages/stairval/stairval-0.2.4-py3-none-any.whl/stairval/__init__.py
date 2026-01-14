"""
Stairval is a framework for validating hierarchical data structures.
"""

from importlib.metadata import version

from ._api import Level, Issue
from ._auditor import Auditor, ITEM

__version__ = version("stairval")

__all__ = [
    "Auditor",
    "Issue",
    "Level",
    "ITEM",
]
