from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

# ============================================================
# Basic type
# ============================================================

PitchClass = int  # 0-11


def _mod12(x: int) -> int:
    """
    Reduce an integer to a pitch class modulo 12.
    """
    return x % 12


# ============================================================
# Pitch-class set
# ============================================================


@dataclass(frozen=True)
class PitchClassSet:
    """
    Immutable pitch-class set.

    A PitchClassSet represents an unordered collection of
    pitch classes (0-11), with the following properties:

    - Orderless (set semantics)
    - Unique elements
    - Canonicalized (sorted, modulo 12)

    This class models pitch-class collections in a purely
    structural manner. It does not encode tonal function,
    voice leading, or register.
    """

    pcs: tuple[PitchClass, ...]

    # ---------- special methods ----------

    def __contains__(self, pc: int) -> bool:
        """
        Return True if the pitch class is contained in the set.
        """
        return _mod12(pc) in self.pcs

    def __len__(self) -> int:
        """
        Return the number of pitch classes in the set.
        """
        return len(self.pcs)

    # ---------- constructors ----------

    @staticmethod
    def from_seq(seq: Sequence[int]) -> PitchClassSet:
        """
        Construct a PitchClassSet from a sequence of integers.

        All values are reduced modulo 12, duplicates are removed,
        and the result is sorted.
        """
        return PitchClassSet(tuple(sorted({_mod12(x) for x in seq})))

    # ---------- set operations ----------

    def union(self, other: PitchClassSet) -> PitchClassSet:
        """
        Return the union of this set and another.
        """
        return PitchClassSet.from_seq(tuple(set(self.pcs) | set(other.pcs)))

    def intersection(self, other: PitchClassSet) -> PitchClassSet:
        """
        Return the intersection of this set and another.
        """
        return PitchClassSet.from_seq(tuple(set(self.pcs) & set(other.pcs)))

    def difference(self, other: PitchClassSet) -> PitchClassSet:
        """
        Return the symmetric difference of this set and another.
        """
        return PitchClassSet.from_seq(tuple(set(self.pcs) ^ set(other.pcs)))

    # ---------- transformation ----------

    def transpose(self, n: int) -> PitchClassSet:
        """
        Transpose all pitch classes by ``n`` semitones (mod 12).

        Parameters
        ----------
        n : int
            Transposition interval in semitones.
        """
        return PitchClassSet.from_seq(tuple(pc + n for pc in self.pcs))

    # ---------- similarity metrics ----------

    def jaccard(self, other: PitchClassSet) -> float:
        """
        Compute the Jaccard similarity between two pitch-class sets.

        Defined as:
            |A ∩ B| / |A U B|

        Returns a value in the range [0, 1].
        """
        a, b = set(self.pcs), set(other.pcs)
        inter = len(a & b)
        uni = len(a | b)
        return inter / uni if uni else 0.0

    def dice(self, other: PitchClassSet) -> float:
        """
        Compute the Dice similarity between two pitch-class sets.

        Defined as:
            2 * |A ∩ B| / (|A| + |B|)

        Returns a value in the range [0, 1].
        """
        a, b = set(self.pcs), set(other.pcs)
        inter = len(a & b)
        denom = len(a) + len(b)
        return (2 * inter / denom) if denom else 0.0

    def overlap(self, other: PitchClassSet) -> float:
        """
        Compute the overlap coefficient between two pitch-class sets.

        Defined as:
            |A ∩ B| / min(|A|, |B|)

        Returns a value in the range [0, 1].
        """
        a, b = set(self.pcs), set(other.pcs)
        inter = len(a & b)
        denom = min(len(a), len(b))
        return (inter / denom) if denom else 0.0
