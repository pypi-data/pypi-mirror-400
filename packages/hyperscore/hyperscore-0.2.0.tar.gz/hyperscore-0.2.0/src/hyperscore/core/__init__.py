"""
Core time and event primitives for hyperscore.

This module defines the foundational abstractions used throughout
hyperscore:

- TimeSpan: immutable representation of linear time intervals
- NoteEvent: minimal time-bounded musical event
- Score: container and coordinator for events on a time axis
- TimeSpanPipeline: composable transformations over TimeSpans
- ZippedNotes: convenience API for simple sequential note generation

Design principles
-----------------
- Time is represented explicitly and uniformly via TimeSpan.
- Core abstractions are unit-agnostic (milliseconds, ticks, etc.).
- Musical interpretation (harmony, rhythm, MIDI) is handled in
  higher-level modules.
- All core objects favor immutability and composability.

This module is intentionally minimal and free of musical semantics.
It serves as the stable foundation upon which rhythm, theory,
and I/O layers are built.
"""

from .score import NoteEvent, Score, ZippedNotes
from .time import TimeSpan, bpm_to_ms
from .time_pipeline import TimeSpanPipeline
from .time_transforms import (
    drop_if,
    duplicate,
    identity,
    keep_if,
    probability,
    shift,
    split_by,
    split_even,
    stretch,
)

__all__ = [
    "NoteEvent",
    "Score",
    "TimeSpan",
    "TimeSpanPipeline",
    "ZippedNotes",
    "bpm_to_ms",
    "drop_if",
    "duplicate",
    "identity",
    "keep_if",
    "probability",
    "shift",
    "split_by",
    "split_even",
    "stretch",
]
