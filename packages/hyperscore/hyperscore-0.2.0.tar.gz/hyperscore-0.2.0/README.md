# hyperscore

**hyperscore** is a structural music composition framework that models music as explicit, composable structure rather than notation or performance.

Time is represented uniformly using immutable time spans, pitch is handled as pitch-class structure independent of register, and rhythm is expressed as relative proportions that are resolved into concrete time only when needed. External formats such as MIDI are treated as lossy boundaries rather than as the source of truth.

hyperscore is designed for experimentation, analysis, and integration with algorithmic systems, rather than for score engraving or DAW-style workflows.

---

## Minimal example

This minimal example demonstrates the core hyperscore workflow: selecting pitch material using theory objects, describing rhythm structurally, generating time-based events, and exporting the result to MIDI.

```python
from hyperscore import CHORDS, Score, parse_rhythm
from hyperscore.core import NoteEvent, bpm_to_ms
from hyperscore.io import MidiExporter
from hyperscore.rhythm import rhythm_ast_to_timespans

# ----------------
# theory
# ----------------
chord = CHORDS["major7"]

pitches = [n for n in range(60, 72) if n % 12 in chord.intervals]
pitch_iter = iter(pitches)

# ----------------
# rhythm
# ----------------
ast = parse_rhythm("1*4")
total = int(bpm_to_ms(120, 1))
spans = rhythm_ast_to_timespans(ast, total=total)

# ----------------
# score
# ----------------
score = Score()

score.add_timespans(
    spans,
    factory=lambda span: NoteEvent(
        pitch=next(pitch_iter),
        velocity=100,
        span=span,
        channel=0,
    ),
)

# ----------------
# output
# ----------------
MidiExporter().export(score, "example.mid")
```

This example intentionally avoids musical interpretation and focuses on structural composition. Pitch, rhythm, and time are treated as independent layers that are combined explicitly.

---

## What this example demonstrates

- Rhythm is expressed as **structure**, not notation
- Time is handled explicitly via immutable `TimeSpan` objects
- Pitch and rhythm are **independent layers**
- MIDI is treated as a **lossy output format**

For more advanced usage, see:

- `examples/`
- `tests/test_smoke.py`

---

## Optional: ZippedNotes shortcut

For simple sequential note generation without explicit TimeSpan construction, hyperscore provides the `ZippedNotes` convenience API.

This approach is suitable for basic sketches or quick tests, but offers less control than TimeSpan-based workflows.

```python
from hyperscore import Score
from hyperscore.core import NoteEvent

score = Score()

score.add(
    pitch=[60, 64, 67, 71],  # C major 7 chord tones
    velocity=[100],
    duration=[125],
    channel=[0],
    event_factory=lambda **kw: NoteEvent(
        pitch=kw["pitch"],
        velocity=kw["velocity"],
        span=kw["span"],
        channel=kw["channel"],
    ),
)
```

For complex timing, transformations, or algorithmic rhythm generation, prefer TimeSpan-based workflows using `parse_rhythm`, `rhythm_ast_to_timespans`, and `TimeSpanPipeline`.

---

## Project status

- Python >= 3.10
- Typed (`py.typed`)
- Experimental / research-oriented
- API may evolve between minor versions

hyperscore favors clarity of structure and explicitness of time over completeness or stylistic prescription.
