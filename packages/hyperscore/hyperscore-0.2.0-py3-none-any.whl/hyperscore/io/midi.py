from __future__ import annotations

import time
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from os import PathLike
from pathlib import Path

import mido
from mido import Message, MetaMessage, MidiFile, MidiTrack

from hyperscore.core import NoteEvent

# ============================================================
# Time conversion utilities
# ============================================================


@dataclass(frozen=True)
class MidiTimebase:
    """
    MIDI timebase configuration.

    This class defines the mapping between real time expressed
    in milliseconds and discrete MIDI ticks.

    Notes
    -----
    - MIDI timing is inherently discrete and quantized.
    - This class provides only linear conversion utilities;
      no musical interpretation is applied here.
    """

    ticks_per_beat: int = 480
    tempo_us_per_beat: int = 500_000  # 120 BPM

    @property
    def ticks_per_second(self) -> float:
        """
        Return the number of MIDI ticks per second.

        This value is derived from ticks_per_beat and tempo.
        """
        return self.ticks_per_beat * 1_000_000 / self.tempo_us_per_beat

    def ms_to_ticks_float(self, ms: int) -> float:
        """
        Convert milliseconds to fractional MIDI ticks.

        This method performs no rounding and is intended
        for internal use prior to quantization.
        """
        return ms * self.ticks_per_second / 1000.0


def ms_to_ticks_int(
    times_ms: Sequence[int],
    *,
    timebase: MidiTimebase,
) -> list[int]:
    """
    Quantize absolute times (milliseconds) into MIDI ticks
    using simple truncation.

    Notes
    -----
    - Each time value is converted independently.
    - This favors local temporal consistency over
      global error minimization.
    - This behavior is intentional: MIDI is treated
      as a lossy output format.
    """
    return [int(timebase.ms_to_ticks_float(t)) for t in times_ms]


# ============================================================
# Event → MIDI message expansion (TimeSpan-based)
# ============================================================


def note_events_to_midi_messages(
    events: Iterable[NoteEvent],
    *,
    timebase: MidiTimebase,
) -> list[tuple[int, Message]]:
    """
    Convert NoteEvents into absolute-time MIDI messages.

    Each NoteEvent is expanded into exactly two messages:
    - note_on  at span.start
    - note_off at span.end

    Absolute times are converted from milliseconds to
    MIDI ticks using independent quantization.

    Notes
    -----
    - Quantization is performed per event boundary,
      not globally.
    - Relative ordering between note_on and note_off
      for a single event is preserved.
    - MIDI timing inaccuracies within ±1 tick are
      considered acceptable.
    """

    # ---- build absolute ms times ----
    times_ms: list[int] = []
    msg_specs: list[tuple[str, NoteEvent]] = []

    for e in events:
        times_ms.append(e.span.start)
        msg_specs.append(("on", e))

        times_ms.append(e.span.end)
        msg_specs.append(("off", e))

    # ---- quantize ms -> ticks ----
    times_ticks = ms_to_ticks_int(times_ms, timebase=timebase)

    # ---- build MIDI messages ----
    messages: list[tuple[int, Message]] = []

    for (kind, e), tick in zip(msg_specs, times_ticks):
        if kind == "on":
            msg = Message(
                "note_on",
                note=e.pitch,
                velocity=e.velocity,
                channel=e.channel,
                time=0,
            )
        else:
            msg = Message(
                "note_off",
                note=e.pitch,
                velocity=0,
                channel=e.channel,
                time=0,
            )

        messages.append((tick, msg))

    # ---- sort by absolute tick ----
    # note_off is ordered before note_on at the same tick
    messages.sort(key=lambda x: (x[0], 0 if x[1].type == "note_off" else 1))
    return messages


def absolute_to_delta(messages: list[tuple[int, Message]]) -> list[Message]:
    """
    Convert absolute-tick MIDI messages into delta-time messages.

    This function assumes that input messages are sorted
    by absolute tick.

    Notes
    -----
    - The returned Message objects are mutated in-place
      to populate the delta-time field.
    """

    out: list[Message] = []
    last_tick = 0

    for tick, msg in messages:
        msg.time = tick - last_tick
        last_tick = tick
        out.append(msg)

    return out


# ============================================================
# MIDI Exporter
# ============================================================


class MidiExporter:
    """
    MIDI file exporter for TimeSpan-based NoteEvents.

    This exporter converts hyperscore NoteEvents into
    a standard MIDI file.

    Notes
    -----
    - MIDI is treated as a lossy output format.
    - Timing is quantized to integer ticks.
    - Structural correctness is enforced at the
      TimeSpan level, not the MIDI level.
    """

    def __init__(
        self,
        *,
        ticks_per_beat: int = 480,
        tempo_us_per_beat: int = 500_000,
    ):
        """
        Initialize the exporter with a given MIDI timebase.
        """
        self.timebase = MidiTimebase(
            ticks_per_beat=ticks_per_beat,
            tempo_us_per_beat=tempo_us_per_beat,
        )

    def export(
        self,
        events: Iterable[NoteEvent],
        path: str | PathLike[str],
        *,
        channel: int | None = None,
    ) -> None:
        """
        Export NoteEvents to a MIDI file.

        Parameters
        ----------
        events : iterable of NoteEvent
            Input note events.
        path : str or PathLike
            Output MIDI file path.
        channel : int or None, optional
            If specified, only events on this channel
            are exported.
        """
        midi = MidiFile(ticks_per_beat=self.timebase.ticks_per_beat)
        track = MidiTrack()
        midi.tracks.append(track)

        track.append(
            MetaMessage(
                "set_tempo",
                tempo=self.timebase.tempo_us_per_beat,
                time=0,
            )
        )

        if channel is not None:
            events = [e for e in events if e.channel == channel]

        abs_msgs = note_events_to_midi_messages(
            events,
            timebase=self.timebase,
        )

        for msg in absolute_to_delta(abs_msgs):
            track.append(msg)

        midi.save(Path(path))


# ============================================================
# MIDI Player (TimeSpan-based, lightweight)
# ============================================================


class MidiPlayer:
    """
    Lightweight real-time MIDI player for NoteEvents.

    This class is intended for preview and debugging,
    not for sample-accurate performance.
    """

    def __init__(
        self,
        *,
        output: mido.ports.BaseOutput,
        timebase: MidiTimebase | None = None,
    ):
        """
        Initialize the MIDI player.
        """
        self.output = output
        self.timebase = timebase or MidiTimebase()

    def play(
        self,
        events: Iterable[NoteEvent],
        *,
        channel: int | None = None,
    ) -> None:
        """
        Play NoteEvents in real time via a MIDI output port.

        Notes
        -----
        - Scheduling is based on wall-clock time.
        - Timing resolution is limited by the OS scheduler.
        - This method is unsuitable for precise timing evaluation.
        """
        if channel is not None:
            events = [e for e in events if e.channel == channel]

        abs_msgs = note_events_to_midi_messages(
            events,
            timebase=self.timebase,
        )
        delta_msgs = absolute_to_delta(abs_msgs)

        with mido.open_output(self.output, autoreset=True) as outport:  # type: ignore
            logical_time = time.time()

            for msg in delta_msgs:
                delta_sec = msg.time / self.timebase.ticks_per_second  # type: ignore
                logical_time += delta_sec

                sleep_time = logical_time - time.time()
                if sleep_time > 0:
                    time.sleep(sleep_time)

                outport.send(msg)
