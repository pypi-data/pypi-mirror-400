"""
Visual Width - A Python library for calculating visual width of text.

This package provides utilities for:
- Calculating visual width of text for subtitle display
- Supporting multiple character sets (CJK, Latin, Arabic, etc.)
- Accurate width calculation based on Unicode properties
"""

from .visual_width import VisualWidth

__version__ = "0.1.1"

__all__ = [
    "VisualWidth",
]
