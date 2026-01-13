"""Chord definitions and progressions for chiptune composition."""

from __future__ import annotations

from enum import Enum
from typing import ClassVar

from pydantic import BaseModel

from chiptune.theory.keys import MIDI_TO_NOTE, NOTE_TO_MIDI, Key, Mode


class ChordQuality(str, Enum):
    """Chord qualities/types."""

    MAJOR = "major"
    MINOR = "minor"
    DIMINISHED = "dim"
    AUGMENTED = "aug"
    DOMINANT_7 = "7"
    MAJOR_7 = "maj7"
    MINOR_7 = "m7"
    SUSPENDED_2 = "sus2"
    SUSPENDED_4 = "sus4"
    POWER = "5"  # Root + fifth only


# Intervals from root for each chord quality
CHORD_INTERVALS: dict[ChordQuality, tuple[int, ...]] = {
    ChordQuality.MAJOR: (0, 4, 7),
    ChordQuality.MINOR: (0, 3, 7),
    ChordQuality.DIMINISHED: (0, 3, 6),
    ChordQuality.AUGMENTED: (0, 4, 8),
    ChordQuality.DOMINANT_7: (0, 4, 7, 10),
    ChordQuality.MAJOR_7: (0, 4, 7, 11),
    ChordQuality.MINOR_7: (0, 3, 7, 10),
    ChordQuality.SUSPENDED_2: (0, 2, 7),
    ChordQuality.SUSPENDED_4: (0, 5, 7),
    ChordQuality.POWER: (0, 7),
}


class Chord(BaseModel):
    """A musical chord with root and quality."""

    root: str  # e.g., "C", "F#"
    quality: ChordQuality = ChordQuality.MAJOR
    inversion: int = 0  # 0 = root position, 1 = first inversion, etc.

    @classmethod
    def parse(cls, chord_str: str) -> Chord:
        """Parse a chord string like 'Cm', 'F#maj7', 'Bb7'.

        Args:
            chord_str: Chord notation string

        Returns:
            Parsed Chord object
        """
        # Extract root note
        if len(chord_str) >= 2 and chord_str[1] in ("#", "b"):
            root = chord_str[:2]
            suffix = chord_str[2:]
        else:
            root = chord_str[0]
            suffix = chord_str[1:]

        # Parse quality from suffix
        suffix_lower = suffix.lower()
        if suffix_lower in ("", "maj"):
            quality = ChordQuality.MAJOR
        elif suffix_lower in ("m", "min"):
            quality = ChordQuality.MINOR
        elif suffix_lower in ("dim", "o"):
            quality = ChordQuality.DIMINISHED
        elif suffix_lower in ("aug", "+"):
            quality = ChordQuality.AUGMENTED
        elif suffix_lower == "7":
            quality = ChordQuality.DOMINANT_7
        elif suffix_lower in ("maj7", "M7"):
            quality = ChordQuality.MAJOR_7
        elif suffix_lower in ("m7", "min7"):
            quality = ChordQuality.MINOR_7
        elif suffix_lower == "sus2":
            quality = ChordQuality.SUSPENDED_2
        elif suffix_lower == "sus4":
            quality = ChordQuality.SUSPENDED_4
        elif suffix_lower == "5":
            quality = ChordQuality.POWER
        else:
            quality = ChordQuality.MAJOR

        return cls(root=root, quality=quality)

    @property
    def root_midi(self) -> int:
        """Get MIDI pitch of root note (octave 4)."""
        return NOTE_TO_MIDI.get(self.root, 60)

    @property
    def intervals(self) -> tuple[int, ...]:
        """Get intervals for this chord quality."""
        return CHORD_INTERVALS[self.quality]

    def get_pitches(self, octave: int = 4) -> list[int]:
        """Get MIDI pitches for the chord.

        Args:
            octave: Base octave

        Returns:
            List of MIDI pitches
        """
        base = self.root_midi + (octave - 4) * 12
        pitches = [base + interval for interval in self.intervals]

        # Apply inversion
        for _ in range(self.inversion % len(pitches)):
            pitches[0] += 12
            pitches = pitches[1:] + [pitches[0]]

        return sorted(pitches)

    def transpose(self, semitones: int) -> Chord:
        """Transpose the chord by semitones."""
        new_midi = (self.root_midi + semitones) % 12
        new_root = MIDI_TO_NOTE[new_midi]
        return Chord(root=new_root, quality=self.quality, inversion=self.inversion)

    def to_power_chord(self) -> Chord:
        """Convert to power chord (root + fifth only)."""
        return Chord(root=self.root, quality=ChordQuality.POWER, inversion=0)


class ChordProgression(BaseModel):
    """A sequence of chords, typically using Roman numeral notation."""

    key: Key
    numerals: list[str]  # e.g., ["I", "IV", "V", "I"]

    # Common progressions for game music
    PRESETS: ClassVar[dict[str, list[str]]] = {
        "victory": ["I", "IV", "V", "I"],
        "heroic": ["I", "V", "vi", "IV"],
        "epic": ["I", "IV", "I", "V"],
        "danger": ["i", "bVI", "bVII", "i"],
        "boss": ["i", "iv", "V", "i"],
        "mysterious": ["i", "bVII", "bVI", "V"],
        "sad": ["vi", "IV", "I", "V"],
        "peaceful": ["I", "vi", "IV", "V"],
        "exploration": ["I", "V", "vi", "iii", "IV", "I", "IV", "V"],
        "tension": ["i", "bII", "V", "i"],
        "resolution": ["V", "I"],
        "fanfare": ["I", "IV", "V", "I"],
    }

    @classmethod
    def from_preset(cls, preset: str, key: Key | None = None) -> ChordProgression:
        """Create a progression from a preset name.

        Args:
            preset: Preset name (e.g., "victory", "boss")
            key: Musical key (defaults to C major)

        Returns:
            ChordProgression instance
        """
        if key is None:
            key = Key(root="C", mode=Mode.IONIAN)

        numerals = cls.PRESETS.get(preset.lower(), ["I", "IV", "V", "I"])
        return cls(key=key, numerals=numerals)

    def _numeral_to_chord(self, numeral: str) -> Chord:
        """Convert Roman numeral to Chord in current key."""
        # Parse numeral
        is_flat = numeral.startswith("b")
        if is_flat:
            numeral = numeral[1:]

        is_minor = numeral.islower()
        numeral_upper = numeral.upper()

        # Roman to degree
        degree_map = {"I": 0, "II": 2, "III": 4, "IV": 5, "V": 7, "VI": 9, "VII": 11}
        semitones = degree_map.get(numeral_upper.rstrip("7"), 0)

        if is_flat:
            semitones -= 1

        # Calculate root
        root_midi = (self.key.root_midi + semitones) % 12
        root = MIDI_TO_NOTE[root_midi]

        # Determine quality
        if "7" in numeral:
            quality = ChordQuality.MINOR_7 if is_minor else ChordQuality.DOMINANT_7
        elif is_minor:
            quality = ChordQuality.MINOR
        else:
            quality = ChordQuality.MAJOR

        return Chord(root=root, quality=quality)

    def get_chords(self) -> list[Chord]:
        """Convert numerals to Chord objects."""
        return [self._numeral_to_chord(n) for n in self.numerals]

    def transpose(self, semitones: int) -> ChordProgression:
        """Transpose the entire progression."""
        new_key = self.key.transpose(semitones)
        return ChordProgression(key=new_key, numerals=self.numerals)

    def extend(self, other: ChordProgression) -> ChordProgression:
        """Combine with another progression."""
        return ChordProgression(key=self.key, numerals=self.numerals + other.numerals)

    def repeat(self, times: int) -> ChordProgression:
        """Repeat the progression multiple times."""
        return ChordProgression(key=self.key, numerals=self.numerals * times)
