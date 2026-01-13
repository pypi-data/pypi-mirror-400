"""Key and mode definitions for music composition."""

from __future__ import annotations

from enum import Enum
from typing import ClassVar

from pydantic import BaseModel


class Mode(str, Enum):
    """Musical modes with their interval patterns."""

    IONIAN = "ionian"  # Major scale
    DORIAN = "dorian"  # Minor with raised 6th
    PHRYGIAN = "phrygian"  # Minor with lowered 2nd
    LYDIAN = "lydian"  # Major with raised 4th
    MIXOLYDIAN = "mixolydian"  # Major with lowered 7th
    AEOLIAN = "aeolian"  # Natural minor
    LOCRIAN = "locrian"  # Diminished

    # Aliases
    MAJOR = "ionian"
    MINOR = "aeolian"


# Interval patterns for each mode (semitones from root)
MODE_INTERVALS: dict[Mode, tuple[int, ...]] = {
    Mode.IONIAN: (0, 2, 4, 5, 7, 9, 11),
    Mode.DORIAN: (0, 2, 3, 5, 7, 9, 10),
    Mode.PHRYGIAN: (0, 1, 3, 5, 7, 8, 10),
    Mode.LYDIAN: (0, 2, 4, 6, 7, 9, 11),
    Mode.MIXOLYDIAN: (0, 2, 4, 5, 7, 9, 10),
    Mode.AEOLIAN: (0, 2, 3, 5, 7, 8, 10),
    Mode.LOCRIAN: (0, 1, 3, 5, 6, 8, 10),
}

# Note names to MIDI pitch (middle C = 60)
NOTE_TO_MIDI: dict[str, int] = {
    "C": 60,
    "C#": 61,
    "Db": 61,
    "D": 62,
    "D#": 63,
    "Eb": 63,
    "E": 64,
    "F": 65,
    "F#": 66,
    "Gb": 66,
    "G": 67,
    "G#": 68,
    "Ab": 68,
    "A": 69,
    "A#": 70,
    "Bb": 70,
    "B": 71,
}

MIDI_TO_NOTE: dict[int, str] = {
    0: "C",
    1: "C#",
    2: "D",
    3: "D#",
    4: "E",
    5: "F",
    6: "F#",
    7: "G",
    8: "G#",
    9: "A",
    10: "A#",
    11: "B",
}


class Key(BaseModel):
    """Musical key with root note and mode."""

    root: str  # e.g., "C", "F#", "Bb"
    mode: Mode = Mode.MAJOR

    # Emotion to mode mapping for semantic selection
    EMOTION_MAP: ClassVar[dict[str, Mode]] = {
        "heroic": Mode.IONIAN,
        "epic": Mode.LYDIAN,
        "triumphant": Mode.IONIAN,
        "adventurous": Mode.MIXOLYDIAN,
        "mysterious": Mode.DORIAN,
        "dark": Mode.PHRYGIAN,
        "danger": Mode.LOCRIAN,
        "tense": Mode.PHRYGIAN,
        "sad": Mode.AEOLIAN,
        "melancholy": Mode.AEOLIAN,
        "peaceful": Mode.IONIAN,
        "calm": Mode.IONIAN,
        "ethereal": Mode.LYDIAN,
        "nostalgic": Mode.DORIAN,
    }

    @classmethod
    def from_emotion(cls, emotion: str, root: str = "C") -> Key:
        """Create a key based on emotional context.

        Args:
            emotion: Emotional descriptor (e.g., "heroic", "mysterious", "danger")
            root: Root note of the key

        Returns:
            Key configured for the emotional context
        """
        mode = cls.EMOTION_MAP.get(emotion.lower(), Mode.IONIAN)
        return cls(root=root, mode=mode)

    @property
    def root_midi(self) -> int:
        """Get MIDI pitch of root note (octave 4)."""
        return NOTE_TO_MIDI.get(self.root, 60)

    def get_scale_pitches(self, octave: int = 4, num_octaves: int = 1) -> list[int]:
        """Get MIDI pitches for the scale.

        Args:
            octave: Starting octave (4 = middle C)
            num_octaves: Number of octaves to span

        Returns:
            List of MIDI pitch numbers
        """
        base = self.root_midi + (octave - 4) * 12
        intervals = MODE_INTERVALS[self.mode]

        pitches = []
        for oct in range(num_octaves):
            for interval in intervals:
                pitches.append(base + oct * 12 + interval)
        # Add the octave above final note
        pitches.append(base + num_octaves * 12)

        return pitches

    def pitch_in_scale(self, pitch: int) -> bool:
        """Check if a MIDI pitch is in this key's scale."""
        pitch_class = pitch % 12
        root_class = self.root_midi % 12
        relative = (pitch_class - root_class) % 12
        return relative in MODE_INTERVALS[self.mode]

    def nearest_scale_pitch(self, pitch: int) -> int:
        """Find the nearest pitch that's in this key's scale."""
        if self.pitch_in_scale(pitch):
            return pitch

        # Check one semitone up and down
        if self.pitch_in_scale(pitch - 1):
            return pitch - 1
        if self.pitch_in_scale(pitch + 1):
            return pitch + 1

        # Check two semitones
        if self.pitch_in_scale(pitch - 2):
            return pitch - 2
        return pitch + 2

    def transpose(self, semitones: int) -> Key:
        """Transpose the key by semitones."""
        new_pitch = (self.root_midi + semitones) % 12
        new_root = MIDI_TO_NOTE[new_pitch]
        return Key(root=new_root, mode=self.mode)

    def relative_minor(self) -> Key:
        """Get the relative minor of a major key."""
        if self.mode in (Mode.IONIAN, Mode.MAJOR):
            return self.transpose(-3).model_copy(update={"mode": Mode.AEOLIAN})
        return self

    def relative_major(self) -> Key:
        """Get the relative major of a minor key."""
        if self.mode in (Mode.AEOLIAN, Mode.MINOR):
            return self.transpose(3).model_copy(update={"mode": Mode.IONIAN})
        return self

    def parallel_minor(self) -> Key:
        """Get the parallel minor (same root, minor mode)."""
        return Key(root=self.root, mode=Mode.AEOLIAN)

    def parallel_major(self) -> Key:
        """Get the parallel major (same root, major mode)."""
        return Key(root=self.root, mode=Mode.IONIAN)
