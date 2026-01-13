"""
Download module for EasyLCSC4KiCAD.

Provides functionality to download and generate KiCad footprints, symbols,
and 3D models from LCSC/EasyEDA component data.
"""

from easylcsc4kicad.download.component import download_component

__all__ = ["download_component"]
