"""
EasyLCSC4KiCAD - Search LCSC and EasyEDA for schematics and footprints.

A Python library and CLI tool for searching electronic components
from LCSC and EasyEDA databases.
"""

from easylcsc4kicad.client import EasyEDAClient
from easylcsc4kicad.models import Component, Footprint, SearchResult, Symbol
from easylcsc4kicad.search import get_by_lcsc_id, search

__version__ = "0.1.0"
__all__ = [
    "EasyEDAClient",
    "Component",
    "Symbol",
    "Footprint",
    "SearchResult",
    "search",
    "get_by_lcsc_id",
]
