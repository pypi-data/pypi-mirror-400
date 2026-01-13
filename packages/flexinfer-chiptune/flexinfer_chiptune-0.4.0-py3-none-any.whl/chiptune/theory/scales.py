"""Scale definitions and utilities for chiptune composition."""

from __future__ import annotations

from enum import Enum
from typing import ClassVar

from pydantic import BaseModel

from chiptune.theory.keys import NOTE_TO_MIDI, Key, Mode


class ScaleType(str, Enum):
    """Common scale types for game music."""

    MAJOR = "major"
    MINOR = "minor"
    PENTATONIC_MAJOR = "pentatonic_major"
    PENTATONIC_MINOR = "pentatonic_minor"
    BLUES = "blues"
    CHROMATIC = "chromatic"
    WHOLE_TONE = "whole_tone"
    DIMINISHED = "diminished"


# Interval patterns for special scales (semitones from root)
SCALE_INTERVALS: dict[ScaleType, tuple[int, ...]] = {
    ScaleType.MAJOR: (0, 2, 4, 5, 7, 9, 11),
    ScaleType.MINOR: (0, 2, 3, 5, 7, 8, 10),
    ScaleType.PENTATONIC_MAJOR: (0, 2, 4, 7, 9),
    ScaleType.PENTATONIC_MINOR: (0, 3, 5, 7, 10),
    ScaleType.BLUES: (0, 3, 5, 6, 7, 10),
    ScaleType.CHROMATIC: tuple(range(12)),
    ScaleType.WHOLE_TONE: (0, 2, 4, 6, 8, 10),
    ScaleType.DIMINISHED: (0, 2, 3, 5, 6, 8, 9, 11),  # Half-whole diminished
}


class Scale(BaseModel):
    """Musical scale with utilities for melody generation."""

    root: str  # e.g., "C", "F#"
    scale_type: ScaleType = ScaleType.MAJOR

    # Emotion to scale type mapping
    EMOTION_MAP: ClassVar[dict[str, tuple[ScaleType, Mode | None]]] = {
        "heroic": (ScaleType.MAJOR, Mode.IONIAN),
        "epic": (ScaleType.MAJOR, Mode.LYDIAN),
        "triumphant": (ScaleType.MAJOR, Mode.IONIAN),
        "adventurous": (ScaleType.MAJOR, Mode.MIXOLYDIAN),
        "mysterious": (ScaleType.MINOR, Mode.DORIAN),
        "dark": (ScaleType.MINOR, Mode.PHRYGIAN),
        "danger": (ScaleType.DIMINISHED, None),
        "tense": (ScaleType.CHROMATIC, None),
        "sad": (ScaleType.MINOR, Mode.AEOLIAN),
        "melancholy": (ScaleType.MINOR, Mode.AEOLIAN),
        "peaceful": (ScaleType.PENTATONIC_MAJOR, None),
        "calm": (ScaleType.PENTATONIC_MAJOR, None),
        "ethereal": (ScaleType.WHOLE_TONE, None),
        "bluesy": (ScaleType.BLUES, None),
        "nostalgic": (ScaleType.PENTATONIC_MINOR, None),
        "intense": (ScaleType.DIMINISHED, None),
        "chaotic": (ScaleType.CHROMATIC, None),
    }

    @classmethod
    def from_emotion(cls, emotion: str, root: str = "C") -> Scale:
        """Create a scale based on emotional context.

        Args:
            emotion: Emotional descriptor
            root: Root note

        Returns:
            Scale configured for the emotional context
        """
        scale_type, _ = cls.EMOTION_MAP.get(emotion.lower(), (ScaleType.MAJOR, None))
        return cls(root=root, scale_type=scale_type)

    @classmethod
    def from_key(cls, key: Key) -> Scale:
        """Create a scale from a Key object."""
        # Map mode to scale type
        mode_to_scale = {
            Mode.IONIAN: ScaleType.MAJOR,
            Mode.AEOLIAN: ScaleType.MINOR,
            Mode.DORIAN: ScaleType.MINOR,  # Dorian is minor-ish
            Mode.PHRYGIAN: ScaleType.MINOR,
            Mode.LYDIAN: ScaleType.MAJOR,
            Mode.MIXOLYDIAN: ScaleType.MAJOR,
            Mode.LOCRIAN: ScaleType.DIMINISHED,
        }
        scale_type = mode_to_scale.get(key.mode, ScaleType.MAJOR)
        return cls(root=key.root, scale_type=scale_type)

    @property
    def root_midi(self) -> int:
        """Get MIDI pitch of root note (octave 4)."""
        return NOTE_TO_MIDI.get(self.root, 60)

    @property
    def intervals(self) -> tuple[int, ...]:
        """Get the interval pattern for this scale."""
        return SCALE_INTERVALS[self.scale_type]

    def get_pitches(self, octave: int = 4, num_octaves: int = 2) -> list[int]:
        """Get MIDI pitches spanning the scale.

        Args:
            octave: Starting octave (4 = middle C)
            num_octaves: Number of octaves to include

        Returns:
            List of MIDI pitch values
        """
        base = self.root_midi + (octave - 4) * 12
        pitches = []

        for oct in range(num_octaves):
            for interval in self.intervals:
                pitches.append(base + oct * 12 + interval)

        # Add final octave note
        pitches.append(base + num_octaves * 12)
        return pitches

    def degree_to_pitch(self, degree: int, octave: int = 4) -> int:
        """Convert scale degree (1-7) to MIDI pitch.

        Args:
            degree: Scale degree (1 = root, 2 = second, etc.)
            octave: Base octave

        Returns:
            MIDI pitch value
        """
        intervals = self.intervals
        # Degrees are 1-indexed
        idx = (degree - 1) % len(intervals)
        octave_offset = (degree - 1) // len(intervals)

        base = self.root_midi + (octave - 4) * 12
        return base + intervals[idx] + octave_offset * 12

    def pitch_in_scale(self, pitch: int) -> bool:
        """Check if a MIDI pitch is in this scale."""
        pitch_class = (pitch - self.root_midi) % 12
        return pitch_class in self.intervals

    def nearest_pitch(self, pitch: int) -> int:
        """Find the nearest pitch that's in this scale."""
        if self.pitch_in_scale(pitch):
            return pitch

        # Check surrounding pitches
        for offset in range(1, 7):
            if self.pitch_in_scale(pitch - offset):
                return pitch - offset
            if self.pitch_in_scale(pitch + offset):
                return pitch + offset

        return pitch  # Fallback

    def random_pitch(self, low: int = 60, high: int = 84, prefer_chord_tones: bool = True) -> int:
        """Get a random pitch from the scale within a range.

        Args:
            low: Minimum MIDI pitch
            high: Maximum MIDI pitch
            prefer_chord_tones: Weight chord tones (1, 3, 5) higher

        Returns:
            Random MIDI pitch in scale
        """
        import random

        pitches = [p for p in self.get_pitches(octave=3, num_octaves=4) if low <= p <= high]

        if not pitches:
            return low

        if prefer_chord_tones:
            # Chord tones are degrees 1, 3, 5 (indices 0, 2, 4)
            chord_indices = {0, 2, 4}
            weighted = []
            for p in pitches:
                relative = (p - self.root_midi) % 12
                try:
                    idx = self.intervals.index(relative)
                    weight = 3 if idx in chord_indices else 1
                except ValueError:
                    weight = 1
                weighted.extend([p] * weight)
            return random.choice(weighted)

        return random.choice(pitches)

    def transpose(self, semitones: int) -> Scale:
        """Transpose the scale by semitones."""
        new_midi = (self.root_midi + semitones) % 12
        from chiptune.theory.keys import MIDI_TO_NOTE

        new_root = MIDI_TO_NOTE[new_midi]
        return Scale(root=new_root, scale_type=self.scale_type)
