"""
Pitch-class theory utilities for hyperscore.

This module defines theory-level abstractions for working with
pitch-class structures, independent of time and performance.

Core responsibilities
---------------------
- Representation of pitch-class sets
- Definition of scales and chords as value objects
- Basic transformations such as transposition and mode rotation

Design principles
-----------------
- Theory objects are immutable and order-agnostic by default.
- No tonal function, voice leading, or stylistic rules are assumed.
- Set-based and ordered representations are explicitly separated.

The theory layer provides structural vocabulary for pitch space.
Interpretation and usage are left to higher-level systems.
"""

from .pcset import PitchClassSet
from .scales import (
    CHORDS,
    SCALES,
    Chord,
    Scale,
    ScaleOrdered,
    ordered_from_scale,
)

__all__ = [
    "CHORDS",
    "SCALES",
    "Chord",
    "PitchClassSet",
    "Scale",
    "ScaleOrdered",
    "ordered_from_scale",
]
