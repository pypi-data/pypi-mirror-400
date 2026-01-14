from __future__ import annotations

from dataclasses import dataclass

from .pcset import PitchClass, PitchClassSet

# ============================================================
# Value objects
# ============================================================


@dataclass(frozen=True)
class Scale:
    """
    Musical scale represented as a pitch-class set.

    A Scale is an unordered collection of pitch classes.
    It does not encode melodic order, mode rotation,
    or tonal function.

    This class is primarily intended for:
    - harmonic constraints
    - pitch filtering
    - similarity and set-based analysis
    """

    name: str
    pcs: PitchClassSet

    def transpose(self, n: int, *, name: str | None = None) -> Scale:
        """
        Transpose the scale by ``n`` semitones (mod 12).

        Parameters
        ----------
        n : int
            Transposition interval in semitones.
        name : str or None, optional
            Optional name for the transposed scale.
            If None, a derived name is generated.
        """
        new_name = name if name is not None else f"{self.name}_+{n}"
        return Scale(new_name, self.pcs.transpose(n))


@dataclass(frozen=True)
class Chord:
    """
    Chord defined by pitch-class intervals.

    A Chord is represented as a PitchClassSet of intervals
    relative to an implicit root (0).

    This representation is orderless and register-agnostic.
    """

    name: str
    intervals: PitchClassSet


# ============================================================
# Ordered scale (for mode rotation etc.)
# ============================================================


@dataclass(frozen=True)
class ScaleOrdered:
    """
    Ordered pitch-class sequence.

    This class explicitly represents pitch-class order and
    is intended for:

    - mode rotation
    - melodic generation
    - ordered traversal of scales

    Unlike Scale, this representation is sensitive to order.
    """

    name: str
    pcs: tuple[PitchClass, ...]

    def transpose(self, n: int, *, name: str | None = None) -> ScaleOrdered:
        """
        Transpose the ordered scale by ``n`` semitones (mod 12).
        """
        new_name = name if name is not None else f"{self.name}_+{n}"
        return ScaleOrdered(new_name, tuple((pc + n) % 12 for pc in self.pcs))

    def rotate_mode(self, k: int, *, name: str | None = None) -> ScaleOrdered:
        """
        Rotate the scale to produce a mode.

        Parameters
        ----------
        k : int
            Rotation index.
        name : str or None, optional
            Optional name for the rotated mode.
        """
        if not self.pcs:
            return self
        k = k % len(self.pcs)
        rotated = self.pcs[k:] + self.pcs[:k]
        new_name = name if name is not None else f"{self.name}_mode{k + 1}"
        return ScaleOrdered(new_name, rotated)

    def normalize_to_zero(self) -> ScaleOrdered:
        """
        Normalize the scale so that the first pitch class is zero.

        This is useful for comparing modes independent of transposition.
        """
        if not self.pcs:
            return self
        root = self.pcs[0]
        return ScaleOrdered(
            self.name,
            tuple((pc - root) % 12 for pc in self.pcs),
        )

    def as_set(self) -> PitchClassSet:
        """
        Convert the ordered scale into a pitch-class set.
        """
        return PitchClassSet.from_seq(self.pcs)


# ============================================================
# External conversion (explicit responsibility)
# ============================================================


def ordered_from_scale(scale: Scale) -> ScaleOrdered:
    """
    Convert an unordered Scale into an ordered representation.

    The resulting ScaleOrdered uses ascending pitch-class order.
    """
    return ScaleOrdered(scale.name, scale.pcs.pcs)


# ============================================================
# Scale definitions
# ============================================================

# Collection of predefined scales.
#
# These definitions are provided as a convenience and
# reference set. They are not exhaustive and do not imply
# stylistic or theoretical endorsement.
SCALES: dict[str, Scale] = {
    # Five-note scales
    "min_pent": Scale("min_pent", PitchClassSet.from_seq([0, 3, 5, 7, 10])),
    "maj_pent": Scale("maj_pent", PitchClassSet.from_seq([0, 2, 4, 7, 9])),
    "ritusen": Scale("ritusen", PitchClassSet.from_seq([0, 2, 5, 7, 9])),
    "egyptian": Scale("egyptian", PitchClassSet.from_seq([0, 2, 5, 7, 10])),
    "kumai": Scale("kumai", PitchClassSet.from_seq([0, 2, 3, 7, 9])),
    "hirajoshi": Scale("hirajoshi", PitchClassSet.from_seq([0, 2, 3, 7, 8])),
    "iwato": Scale("iwato", PitchClassSet.from_seq([0, 1, 5, 6, 10])),
    "chinese": Scale("chinese", PitchClassSet.from_seq([0, 4, 6, 7, 11])),
    "indian": Scale("indian", PitchClassSet.from_seq([0, 4, 5, 7, 10])),
    "pelog": Scale("pelog", PitchClassSet.from_seq([0, 1, 3, 7, 8])),
    # Pentatonic relatives
    "prometheus": Scale("prometheus", PitchClassSet.from_seq([0, 2, 4, 6, 11])),
    "scriabin": Scale("scriabin", PitchClassSet.from_seq([0, 1, 4, 7, 9])),
    # Han Chinese pentatonic
    "gong": Scale("gong", PitchClassSet.from_seq([0, 2, 4, 7, 9])),
    "shang": Scale("shang", PitchClassSet.from_seq([0, 2, 5, 7, 10])),
    "jiao": Scale("jiao", PitchClassSet.from_seq([0, 3, 5, 8, 10])),
    "zhi": Scale("zhi", PitchClassSet.from_seq([0, 2, 5, 7, 9])),
    "yu": Scale("yu", PitchClassSet.from_seq([0, 3, 5, 7, 10])),
    # 6-note scales
    "whole": Scale("whole", PitchClassSet.from_seq([0, 2, 4, 6, 8, 10])),
    "augmented": Scale("augmented", PitchClassSet.from_seq([0, 3, 4, 7, 8, 11])),
    "augmented2": Scale("augmented2", PitchClassSet.from_seq([0, 1, 4, 5, 8, 9])),
    # Hexatonic modes
    "hex_major7": Scale("hex_major7", PitchClassSet.from_seq([0, 2, 4, 7, 9, 11])),
    "hex_dorian": Scale("hex_dorian", PitchClassSet.from_seq([0, 2, 3, 5, 7, 10])),
    "hex_phrygian": Scale("hex_phrygian", PitchClassSet.from_seq([0, 1, 3, 5, 8, 10])),
    "hex_sus": Scale("hex_sus", PitchClassSet.from_seq([0, 2, 5, 7, 9, 10])),
    "hex_major6": Scale("hex_major6", PitchClassSet.from_seq([0, 2, 4, 5, 7, 9])),
    "hex_aeolian": Scale("hex_aeolian", PitchClassSet.from_seq([0, 3, 5, 7, 8, 10])),
    # 7-note scales
    "major": Scale("major", PitchClassSet.from_seq([0, 2, 4, 5, 7, 9, 11])),
    "ionian": Scale("ionian", PitchClassSet.from_seq([0, 2, 4, 5, 7, 9, 11])),
    "dorian": Scale("dorian", PitchClassSet.from_seq([0, 2, 3, 5, 7, 9, 10])),
    "phrygian": Scale("phrygian", PitchClassSet.from_seq([0, 1, 3, 5, 7, 8, 10])),
    "lydian": Scale("lydian", PitchClassSet.from_seq([0, 2, 4, 6, 7, 9, 11])),
    "mixolydian": Scale("mixolydian", PitchClassSet.from_seq([0, 2, 4, 5, 7, 9, 10])),
    "aeolian": Scale("aeolian", PitchClassSet.from_seq([0, 2, 3, 5, 7, 8, 10])),
    "minor": Scale("minor", PitchClassSet.from_seq([0, 2, 3, 5, 7, 8, 10])),
    "locrian": Scale("locrian", PitchClassSet.from_seq([0, 1, 3, 5, 6, 8, 10])),
    "harmonic_minor": Scale("harmonic_minor", PitchClassSet.from_seq([0, 2, 3, 5, 7, 8, 11])),
    "harmonic_major": Scale("harmonic_major", PitchClassSet.from_seq([0, 2, 4, 5, 7, 8, 11])),
    "melodic_minor": Scale("melodic_minor", PitchClassSet.from_seq([0, 2, 3, 5, 7, 9, 11])),
    "melodic_minor_desc": Scale("melodic_minor_desc", PitchClassSet.from_seq([0, 2, 3, 5, 7, 8, 10])),
    "melodic_major": Scale("melodic_major", PitchClassSet.from_seq([0, 2, 4, 5, 7, 8, 10])),
    # Raga modes
    "todi": Scale("todi", PitchClassSet.from_seq([0, 1, 3, 6, 7, 8, 11])),
    "purvi": Scale("purvi", PitchClassSet.from_seq([0, 1, 4, 6, 7, 8, 11])),
    "marva": Scale("marva", PitchClassSet.from_seq([0, 1, 4, 6, 7, 9, 11])),
    "bhairav": Scale("bhairav", PitchClassSet.from_seq([0, 1, 4, 5, 7, 8, 11])),
    "ahirbhairav": Scale("ahirbhairav", PitchClassSet.from_seq([0, 1, 4, 5, 7, 9, 10])),
    # More modes
    "super_locrian": Scale("super_locrian", PitchClassSet.from_seq([0, 1, 3, 4, 6, 8, 10])),
    "romanian_minor": Scale("romanian_minor", PitchClassSet.from_seq([0, 2, 3, 6, 7, 9, 10])),
    "hungarian_minor": Scale("hungarian_minor", PitchClassSet.from_seq([0, 2, 3, 6, 7, 8, 11])),
    "neapolitan_minor": Scale("neapolitan_minor", PitchClassSet.from_seq([0, 1, 3, 5, 7, 8, 11])),
    "enigmatic": Scale("enigmatic", PitchClassSet.from_seq([0, 1, 4, 6, 8, 10, 11])),
    "spanish": Scale("spanish", PitchClassSet.from_seq([0, 1, 4, 5, 7, 8, 10])),
    # Whole-tone variants
    "leading_whole": Scale("leading_whole", PitchClassSet.from_seq([0, 2, 4, 6, 8, 10, 11])),
    "lydian_minor": Scale("lydian_minor", PitchClassSet.from_seq([0, 2, 4, 6, 7, 8, 10])),
    "neapolitan_major": Scale("neapolitan_major", PitchClassSet.from_seq([0, 1, 3, 5, 7, 9, 11])),
    "locrian_major": Scale("locrian_major", PitchClassSet.from_seq([0, 2, 4, 5, 6, 8, 10])),
    # 8-note scales
    "diminished": Scale("diminished", PitchClassSet.from_seq([0, 1, 3, 4, 6, 7, 9, 10])),
    "diminished2": Scale("diminished2", PitchClassSet.from_seq([0, 2, 3, 5, 6, 8, 9, 11])),
    # Messiaen modes of limited transposition
    "messiaen3": Scale("messiaen3", PitchClassSet.from_seq([0, 2, 3, 4, 6, 7, 8, 10, 11])),
    "messiaen4": Scale("messiaen4", PitchClassSet.from_seq([0, 1, 2, 5, 6, 7, 8, 11])),
    "messiaen5": Scale("messiaen5", PitchClassSet.from_seq([0, 1, 5, 6, 7, 11])),
    "messiaen6": Scale("messiaen6", PitchClassSet.from_seq([0, 2, 4, 5, 6, 8, 10, 11])),
    "messiaen7": Scale("messiaen7", PitchClassSet.from_seq([0, 1, 2, 3, 5, 6, 7, 8, 9, 11])),
    # Chromatic
    "chromatic": Scale("chromatic", PitchClassSet.from_seq(list(range(12)))),
}


# ============================================================
# Chord definitions
# ============================================================

# Collection of predefined chords.
#
# Chords are represented as pitch-class interval sets
# relative to an implicit root.
CHORDS: dict[str, Chord] = {
    # Major
    "major": Chord("major", PitchClassSet.from_seq([0, 4, 7])),
    "aug": Chord("aug", PitchClassSet.from_seq([0, 4, 8])),
    "six": Chord("six", PitchClassSet.from_seq([0, 4, 7, 9])),
    "six_nine": Chord("six_nine", PitchClassSet.from_seq([0, 4, 7, 9, 14])),
    "major7": Chord("major7", PitchClassSet.from_seq([0, 4, 7, 11])),
    "major9": Chord("major9", PitchClassSet.from_seq([0, 4, 7, 11, 14])),
    "add9": Chord("add9", PitchClassSet.from_seq([0, 4, 7, 14])),
    "major11": Chord("major11", PitchClassSet.from_seq([0, 4, 7, 11, 14, 17])),
    "add11": Chord("add11", PitchClassSet.from_seq([0, 4, 7, 17])),
    "major13": Chord("major13", PitchClassSet.from_seq([0, 4, 7, 11, 14, 21])),
    "add13": Chord("add13", PitchClassSet.from_seq([0, 4, 7, 21])),
    # Dominant
    "dom7": Chord("dom7", PitchClassSet.from_seq([0, 4, 7, 10])),
    "dom9": Chord("dom9", PitchClassSet.from_seq([0, 4, 7, 14])),
    "dom11": Chord("dom11", PitchClassSet.from_seq([0, 4, 7, 17])),
    "dom13": Chord("dom13", PitchClassSet.from_seq([0, 4, 7, 21])),
    "seven_flat5": Chord("seven_flat5", PitchClassSet.from_seq([0, 4, 6, 10])),
    "seven_sharp5": Chord("seven_sharp5", PitchClassSet.from_seq([0, 4, 8, 10])),
    "seven_flat9": Chord("seven_flat9", PitchClassSet.from_seq([0, 4, 7, 10, 13])),
    "nine": Chord("nine", PitchClassSet.from_seq([0, 4, 7, 10, 14])),
    "eleven": Chord("eleven", PitchClassSet.from_seq([0, 4, 7, 10, 14, 17])),
    "thirteen": Chord("thirteen", PitchClassSet.from_seq([0, 4, 7, 10, 14, 17, 21])),
    # Minor
    "minor": Chord("minor", PitchClassSet.from_seq([0, 3, 7])),
    "diminished": Chord("diminished", PitchClassSet.from_seq([0, 3, 6])),
    "minor_sharp5": Chord("minor_sharp5", PitchClassSet.from_seq([0, 3, 8])),
    "minor6": Chord("minor6", PitchClassSet.from_seq([0, 3, 7, 9])),
    "minor_six_nine": Chord("minor_six_nine", PitchClassSet.from_seq([0, 3, 7, 9, 14])),
    "minor7flat5": Chord("minor7flat5", PitchClassSet.from_seq([0, 3, 6, 10])),
    "minor7": Chord("minor7", PitchClassSet.from_seq([0, 3, 7, 10])),
    "minor7sharp5": Chord("minor7sharp5", PitchClassSet.from_seq([0, 3, 8, 10])),
    "minor7flat9": Chord("minor7flat9", PitchClassSet.from_seq([0, 3, 7, 10, 13])),
    "minor7sharp9": Chord("minor7sharp9", PitchClassSet.from_seq([0, 3, 7, 10, 15])),
    "diminished7": Chord("diminished7", PitchClassSet.from_seq([0, 3, 6, 9])),
    "minor9": Chord("minor9", PitchClassSet.from_seq([0, 3, 7, 10, 14])),
    "minor11": Chord("minor11", PitchClassSet.from_seq([0, 3, 7, 10, 14, 17])),
    "minor13": Chord("minor13", PitchClassSet.from_seq([0, 3, 7, 10, 14, 17, 21])),
    "minor_major7": Chord("minor_major7", PitchClassSet.from_seq([0, 3, 7, 11])),
    # Other
    "one": Chord("one", PitchClassSet.from_seq([0])),
    "five": Chord("five", PitchClassSet.from_seq([0, 7])),
    "sus2": Chord("sus2", PitchClassSet.from_seq([0, 2, 7])),
    "sus4": Chord("sus4", PitchClassSet.from_seq([0, 5, 7])),
    "seven_sus2": Chord("seven_sus2", PitchClassSet.from_seq([0, 2, 7, 10])),
    "seven_sus4": Chord("seven_sus4", PitchClassSet.from_seq([0, 5, 7, 10])),
    "nine_sus4": Chord("nine_sus4", PitchClassSet.from_seq([0, 5, 7, 10, 14])),
    # Questionable / extended
    "seven_flat10": Chord("seven_flat10", PitchClassSet.from_seq([0, 4, 7, 10, 15])),
    "nine_sharp5": Chord("nine_sharp5", PitchClassSet.from_seq([0, 1, 13])),
    "minor9sharp5": Chord("minor9sharp5", PitchClassSet.from_seq([0, 1, 14])),
    "seven_sharp5flat9": Chord("seven_sharp5flat9", PitchClassSet.from_seq([0, 4, 8, 10, 13])),
    "minor7sharp5flat9": Chord("minor7sharp5flat9", PitchClassSet.from_seq([0, 3, 8, 10, 13])),
    "eleven_sharp": Chord("eleven_sharp", PitchClassSet.from_seq([0, 4, 7, 10, 14, 18])),
    "minor11sharp": Chord("minor11sharp", PitchClassSet.from_seq([0, 3, 7, 10, 14, 18])),
}
