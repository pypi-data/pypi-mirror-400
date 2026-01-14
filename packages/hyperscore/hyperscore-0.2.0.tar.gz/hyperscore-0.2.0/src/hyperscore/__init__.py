"""
hyperscore: a structural music composition framework.

hyperscore provides a minimal, composable foundation for
algorithmic and structural music composition.

Key ideas
---------
- Music is modeled as explicit structure, not notation.
- Time is represented uniformly using immutable TimeSpan objects.
- Pitch is handled as pitch-class structure, independent of register.
- External formats (e.g. MIDI) are treated as lossy boundaries.

The library is organized into clear layers:
- core: time and event primitives
- rhythm: structural rhythm descriptions
- theory: pitch-class and scale structures
- io: adapters to external systems

hyperscore is designed for experimentation, analysis,
and integration with other algorithmic systems,
rather than for direct score engraving or DAW replacement.
"""

from hyperscore.core import Score, ZippedNotes
from hyperscore.rhythm import parse_rhythm
from hyperscore.theory import CHORDS, SCALES

__all__ = [
    "CHORDS",
    "SCALES",
    "Score",
    "ZippedNotes",
    "parse_rhythm",
]
