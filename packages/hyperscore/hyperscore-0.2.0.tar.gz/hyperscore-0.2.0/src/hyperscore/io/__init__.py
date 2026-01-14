"""
Input/output interfaces for hyperscore.

This module provides adapters between hyperscore's internal
time-based representations and external systems.

Currently supported I/O:
- MIDI file export (MidiExporter)
- Real-time MIDI playback (MidiPlayer)

Design principles
-----------------
- I/O is treated as an explicit, lossy boundary.
- Internal representations are never modified to fit
  external formats.
- Timing is derived from TimeSpan and globally quantized
  when required.

The I/O layer is intentionally thin and pragmatic.
It is designed for interoperability, preview, and export,
not as a substitute for a DAW or real-time audio engine.
"""

from .midi import MidiExporter, MidiPlayer

__all__ = [
    "MidiExporter",
    "MidiPlayer",
]
