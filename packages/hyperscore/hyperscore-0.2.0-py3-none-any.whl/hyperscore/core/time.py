from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeSpan:
    """
    Immutable representation of a half-open time interval.

    A TimeSpan represents a duration on a linear time axis,
    measured in milliseconds (or any consistent time unit).

    Attributes
    ----------
    start : int
        Inclusive start position.
    duration : int
        Non-negative duration.

    Notes
    -----
    - The interval is half-open: [start, end)
    - No ordering or global timeline is enforced.
    - Musical interpretation is handled elsewhere.
    """

    start: int
    duration: int

    @property
    def end(self) -> int:
        """
        Return the exclusive end position of the span.
        """
        return self.start + self.duration

    def shift(self, delta: int) -> TimeSpan:
        """
        Return a new TimeSpan shifted along the time axis.

        Parameters
        ----------
        delta : int
            Time shift in milliseconds.
            Positive values move the span forward,
            negative values move it backward.
        """
        return TimeSpan(self.start + delta, self.duration)

    def stretch(self, factor: float) -> TimeSpan:
        """
        Return a new TimeSpan with scaled duration.

        The start position is preserved.

        Parameters
        ----------
        factor : float
            Duration scaling factor.
        """
        return TimeSpan(self.start, round(self.duration * factor))

    def overlaps(self, other: TimeSpan) -> bool:
        """
        Return True if this span overlaps with another span.
        """
        return not (self.end <= other.start or other.end <= self.start)

    def contains(self, t: int) -> bool:
        """
        Return True if the given time point lies within this span.
        """
        return self.start <= t < self.end


def bpm_to_ms(bpm: float, note_division: float = 1.0) -> float:
    """
    Convert a musical duration at a given BPM into milliseconds.

    This function performs a purely arithmetic conversion.
    It does not assume any time signature or rhythmic structure.

    Parameters
    ----------
    bpm : float
        Tempo in beats per minute.
    note_division : float, optional
        Beat multiplier or subdivision.
        For example:
        - 1.0 = quarter note
        - 0.5 = eighth note
        - 2.0 = half note

    Returns
    -------
    float
        Duration in milliseconds.
    """
    return 60_000.0 / bpm * note_division
