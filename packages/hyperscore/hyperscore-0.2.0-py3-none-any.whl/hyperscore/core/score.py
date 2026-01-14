from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass, field, fields
from typing import Generic, Protocol, TypeVar

from .time import TimeSpan

# ============================================================
# Event model (default)
# ============================================================


class HasTimeSpan(Protocol):
    """
    Protocol for time-aware events.

    Any event type stored in a Score must expose
    a ``span`` attribute of type TimeSpan.
    """

    span: TimeSpan


@dataclass(frozen=True)
class NoteEvent:
    """
    Default note event implementation.

    This is a minimal, time-bounded musical event.
    Interpretation (e.g. MIDI, synthesis) is handled
    by downstream systems.
    """

    pitch: int
    velocity: int
    span: TimeSpan
    channel: int


EventT = TypeVar("EventT", bound=HasTimeSpan)

# ============================================================
# Score context
# ============================================================


@dataclass(frozen=True)
class ScoreContext:
    """
    Immutable score evaluation context.

    The context tracks the current temporal cursor
    during event generation.
    """

    cursor: int

    def advance(self, delta: int) -> ScoreContext:
        """
        Return a new context advanced by the given duration.

        Parameters
        ----------
        delta : int
            Time increment in milliseconds.
        """
        return ScoreContext(cursor=self.cursor + delta)


# ============================================================
# ScoreInput protocol (event generator)
# ============================================================


class ScoreInput(Protocol[EventT]):
    """
    Protocol for event generators consumable by Score.

    Implementations generate events based on the given
    ScoreContext and return the updated context.
    """

    def iter_events(
        self,
        ctx: ScoreContext,
    ) -> tuple[list[EventT], ScoreContext]: ...


# ============================================================
# EventFactory protocol
# ============================================================


EventFactory = Callable[..., EventT]

# ============================================================
# ZippedNotes (generic, factory-based)
# ============================================================


@dataclass(frozen=True)
class ZippedNotes(Generic[EventT]):
    """
    Convenience builder for sequential note generation
    using zipped parameter lists.

    Parameters are cycled independently and combined
    position-wise.

    Notes
    -----
    This class is intended for simple use cases.
    For advanced temporal control, prefer:

    - rhythm_tree
    - TimeSpan pipelines
    - Score.add_timespans()
    """

    # ---- core zipped parameters ----
    pitch: Sequence[int] = field(default_factory=lambda: [60])
    velocity: Sequence[int] = field(default_factory=lambda: [100])
    duration: Sequence[int] = field(default_factory=lambda: [1000])
    channel: Sequence[int] = field(default_factory=lambda: [0])

    # ---- extensibility ----
    event_factory: EventFactory[EventT] | None = None

    # --------------------------------

    def _max_len(self) -> int:
        """
        Return the maximum length among zipped parameters.
        """
        return max(len(getattr(self, f.name)) for f in fields(self) if f.name != "event_factory")

    def iter_events(self, ctx: ScoreContext) -> tuple[list[EventT], ScoreContext]:
        """
        Generate events sequentially starting from the given context.

        Parameters
        ----------
        ctx : ScoreContext
            Initial evaluation context.

        Returns
        -------
        list of EventT
            Generated events.
        ScoreContext
            Updated context after all events.
        """
        if self.event_factory is None:
            raise ValueError("event_factory must be provided")

        events: list[EventT] = []
        cur = ctx

        for i in range(self._max_len()):
            d = self.duration[i % len(self.duration)]
            span = TimeSpan(start=cur.cursor, duration=d)

            kwargs = {
                "pitch": self.pitch[i % len(self.pitch)],
                "velocity": self.velocity[i % len(self.velocity)],
                "span": span,
                "channel": self.channel[i % len(self.channel)],
            }

            ev = self.event_factory(**kwargs)
            events.append(ev)

            cur = cur.advance(d)

        return events, cur


# ============================================================
# Score
# ============================================================


class Score(Generic[EventT], Iterable[EventT]):
    """
    Container and coordinator for time-bounded events.

    Score does not enforce musical semantics.
    It manages event ordering, temporal queries,
    and integration of event sources.
    """

    def __init__(self):
        self._context: ScoreContext = ScoreContext(cursor=0)
        self._events: list[EventT] = []
        self._sorted_by_start: list[EventT] = []
        self._dirty: bool = False

    def __iter__(self) -> Iterator[EventT]:
        """
        Iterate over all events in ascending start-time order.
        """
        self._ensure_sorted()
        return iter(self._sorted_by_start)

    # ---------------- cursor ----------------

    def get_cursor(self) -> int:
        """
        Return the current score cursor position.
        """
        return self._context.cursor

    def set_cursor(self, cursor: int) -> None:
        """
        Set the score cursor to an explicit position.

        This affects subsequent event generation.
        """
        self._context = ScoreContext(cursor=cursor)

    # ---------------- add ----------------

    def add(
        self,
        source: ScoreInput[EventT] | None = None,
        *,
        pitch: Sequence[int] | None = None,
        velocity: Sequence[int] | None = None,
        duration: Sequence[int] | None = None,
        channel: Sequence[int] | None = None,
        start: int | None = None,
        event_factory: EventFactory[EventT] | None = None,
    ) -> None:
        """
        Add events to the score using a convenience API.

        This method supports either:
        - a ScoreInput source, or
        - zipped parameter lists with an event factory.

        Notes
        -----
        This API is intentionally simple.
        For explicit temporal structure, prefer
        ``add_timespans()``.
        """
        ctx = self._context

        if start is not None:
            ctx = ScoreContext(cursor=start)

        if source is not None:
            events, ctx = source.iter_events(ctx)
            self._events.extend(events)
            self._context = ctx
            self._dirty = True
            return

        if event_factory is None:
            raise ValueError("event_factory must be provided when using zipped parameters")

        kwargs = {
            "pitch": pitch,
            "velocity": velocity,
            "duration": duration,
            "channel": channel,
        }

        source_ = ZippedNotes[EventT](
            **{k: v for k, v in kwargs.items() if v is not None},  # type: ignore[arg-type]
            event_factory=event_factory,
        )

        events, ctx = source_.iter_events(ctx)
        self._events.extend(events)
        self._context = ctx
        self._dirty = True

    def add_timespans(
        self,
        spans: Iterable[TimeSpan],
        *,
        factory: Callable[[TimeSpan], EventT],
    ) -> None:
        """
        Add events generated from explicit TimeSpans.

        Score does not interpret TimeSpan contents.
        It only stores the resulting events.
        """
        for span in spans:
            ev = factory(span)
            self._events.append(ev)

        self._dirty = True

    # ---------------- query ----------------

    def _ensure_sorted(self) -> None:
        """
        Ensure events are sorted by start time.
        """
        if self._dirty:
            self._sorted_by_start = sorted(
                self._events,
                key=lambda e: e.span.start,
            )
            self._dirty = False

    def events_between_span(self, span: TimeSpan) -> list[EventT]:
        """
        Return events whose TimeSpan overlaps the given span.
        """
        self._ensure_sorted()

        if not self._sorted_by_start:
            return []

        result: list[EventT] = []

        for e in self._sorted_by_start:
            if e.span.overlaps(span):
                result.append(e)

            # optimization: early exit due to ordering
            if e.span.start >= span.end:
                break

        return result

    def events_between(
        self,
        start: int = 0,
        end: int | None = None,
    ) -> list[EventT]:
        """
        Return events whose start time lies within the given time window.

        Parameters
        ----------
        start : int
            Inclusive start position on the score time axis.
        end : int or None
            Exclusive end position.
            If None, all events starting at or after ``start`` are returned.

        Returns
        -------
        list of EventT
            Events matching the given time range.

        Notes
        -----
        - Time values are interpreted in the same unit used by TimeSpan
          (typically milliseconds or ticks).
        - This method filters by event start time, not full TimeSpan overlap.
          For overlap-based queries, use ``events_between_span()``.
        - The returned list is ordered by start time.
        """
        if end is None:
            self._ensure_sorted()
            return [e for e in self._sorted_by_start if e.span.start >= start]

        span = TimeSpan(
            start=start,
            duration=end - start,
        )
        return self.events_between_span(span)
