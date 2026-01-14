"""
Rhythmic structure processing for hyperscore.

This module provides facilities for describing and expanding
rhythmic structures independently of absolute time.

Core responsibilities
---------------------
- Parsing a rhythm DSL into a structural representation
- Normalizing rhythmic structures into a canonical form
- Expanding relative durations into concrete TimeSpan sequences

Design principles
-----------------
- Rhythm is treated as structure, not notation.
- Relative proportions are resolved before absolute timing.
- No assumptions are made about tempo, meter, or performance.

The rhythm layer bridges symbolic rhythmic intent and
explicit time representation, while remaining agnostic
to musical interpretation.
"""

from .rhythm_tree import (
    parse_rhythm,
    rhythm_ast_to_timespans,
)

__all__ = [
    "parse_rhythm",
    "rhythm_ast_to_timespans",
]
