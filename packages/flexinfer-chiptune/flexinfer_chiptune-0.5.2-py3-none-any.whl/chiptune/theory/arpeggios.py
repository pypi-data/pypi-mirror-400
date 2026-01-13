"""Arpeggio patterns for chiptune composition.

Arpeggios are essential in chiptune music for creating the illusion
of chords when limited to a single voice channel.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from chiptune.theory.chords import Chord


class ArpeggioPattern(str, Enum):
    """Common arpeggio patterns."""

    UP = "up"  # Low to high
    DOWN = "down"  # High to low
    UP_DOWN = "up_down"  # Low to high to low
    DOWN_UP = "down_up"  # High to low to high
    RANDOM = "random"  # Random order
    BROKEN = "broken"  # 1-3-2-4 style
    ALBERTI = "alberti"  # Classic 1-5-3-5 pattern


class Note(BaseModel):
    """A single note with pitch and duration."""

    pitch: int  # MIDI pitch (0-127)
    duration: float  # Duration in beats
    velocity: int = 100  # MIDI velocity (0-127)

    def transpose(self, semitones: int) -> Note:
        """Transpose the note by semitones."""
        return Note(
            pitch=max(0, min(127, self.pitch + semitones)),
            duration=self.duration,
            velocity=self.velocity,
        )


class Arpeggio(BaseModel):
    """Chiptune-style arpeggio generator.

    Creates rapid note sequences from chords, essential for
    giving the illusion of harmony on single-voice channels.
    """

    pitches: list[int]  # Base chord pitches
    pattern: ArpeggioPattern = ArpeggioPattern.UP
    octave_spread: int = 1  # Number of octaves to span
    note_duration: float = 0.125  # Duration per note in beats (32nd note at 120bpm)

    @classmethod
    def from_chord(
        cls,
        chord: Chord,
        octave: int = 4,
        pattern: ArpeggioPattern = ArpeggioPattern.UP,
        note_duration: float = 0.125,
    ) -> Arpeggio:
        """Create an arpeggio from a chord.

        Args:
            chord: The chord to arpeggiate
            octave: Base octave
            pattern: Arpeggio pattern
            note_duration: Duration of each note in beats

        Returns:
            Arpeggio instance
        """
        pitches = chord.get_pitches(octave=octave)
        return cls(pitches=pitches, pattern=pattern, note_duration=note_duration)

    def _generate_sequence(self) -> list[int]:
        """Generate the pitch sequence based on pattern."""
        import random

        base = self.pitches.copy()

        # Extend with octave spread
        all_pitches = []
        for oct in range(self.octave_spread):
            all_pitches.extend([p + oct * 12 for p in base])

        match self.pattern:
            case ArpeggioPattern.UP:
                return sorted(all_pitches)
            case ArpeggioPattern.DOWN:
                return sorted(all_pitches, reverse=True)
            case ArpeggioPattern.UP_DOWN:
                up = sorted(all_pitches)
                return up + up[-2:0:-1]  # Exclude first and last to avoid repeats
            case ArpeggioPattern.DOWN_UP:
                down = sorted(all_pitches, reverse=True)
                return down + down[-2:0:-1]
            case ArpeggioPattern.RANDOM:
                shuffled = all_pitches.copy()
                random.shuffle(shuffled)
                return shuffled
            case ArpeggioPattern.BROKEN:
                # 1-3-2-4 style (works best with 4+ notes)
                sorted_p = sorted(all_pitches)
                if len(sorted_p) >= 4:
                    return [sorted_p[0], sorted_p[2], sorted_p[1], sorted_p[3]]
                return sorted_p
            case ArpeggioPattern.ALBERTI:
                # Classic 1-5-3-5 pattern
                sorted_p = sorted(all_pitches)
                if len(sorted_p) >= 3:
                    return [sorted_p[0], sorted_p[2], sorted_p[1], sorted_p[2]]
                return sorted_p
            case _:
                return sorted(all_pitches)

    def to_notes(self, velocity: int = 100) -> list[Note]:
        """Convert arpeggio to a sequence of Note objects.

        Args:
            velocity: MIDI velocity for all notes

        Returns:
            List of Note objects
        """
        sequence = self._generate_sequence()
        return [Note(pitch=p, duration=self.note_duration, velocity=velocity) for p in sequence]

    def repeat(self, times: int) -> list[Note]:
        """Generate repeated arpeggio cycles.

        Args:
            times: Number of repetitions

        Returns:
            List of Note objects
        """
        single = self.to_notes()
        return single * times

    def fill_duration(self, total_beats: float, velocity: int = 100) -> list[Note]:
        """Fill a duration with repeated arpeggios.

        Args:
            total_beats: Total duration to fill in beats
            velocity: MIDI velocity

        Returns:
            List of Note objects filling the duration
        """
        single = self.to_notes(velocity=velocity)
        if not single:
            return []

        cycle_duration = sum(n.duration for n in single)
        if cycle_duration <= 0:
            return []

        full_cycles = int(total_beats / cycle_duration)
        remaining = total_beats - (full_cycles * cycle_duration)

        notes = single * full_cycles

        # Add partial cycle if needed
        elapsed = 0.0
        for note in single:
            if elapsed + note.duration <= remaining:
                notes.append(note)
                elapsed += note.duration
            else:
                break

        return notes


class RapidArpeggio(Arpeggio):
    """Extra-fast arpeggio for chiptune "chord" effect.

    Uses very short note durations (1/64 notes or faster)
    to create the illusion of simultaneous notes.
    """

    note_duration: float = 0.0625  # 64th note

    @classmethod
    def from_chord(
        cls,
        chord: Chord,
        octave: int = 4,
        pattern: ArpeggioPattern = ArpeggioPattern.UP,
        note_duration: float = 0.0625,
    ) -> RapidArpeggio:
        """Create a rapid arpeggio from a chord.

        Args:
            chord: The chord to arpeggiate
            octave: Base octave
            pattern: Arpeggio pattern
            note_duration: Duration per note in beats (default 64th note)

        Returns:
            RapidArpeggio instance
        """
        pitches = chord.get_pitches(octave=octave)
        return cls(pitches=pitches, pattern=pattern, note_duration=note_duration)

    @classmethod
    def from_chord_speed(
        cls,
        chord: Chord,
        octave: int = 4,
        pattern: ArpeggioPattern = ArpeggioPattern.UP,
        speed: str = "fast",
    ) -> RapidArpeggio:
        """Create a rapid arpeggio from a chord using speed preset.

        Args:
            chord: The chord to arpeggiate
            octave: Base octave
            pattern: Arpeggio pattern
            speed: "fast" (64th), "medium" (32nd), "slow" (16th)

        Returns:
            RapidArpeggio instance
        """
        durations = {"fast": 0.0625, "medium": 0.125, "slow": 0.25}
        duration = durations.get(speed, 0.0625)

        pitches = chord.get_pitches(octave=octave)
        return cls(pitches=pitches, pattern=pattern, note_duration=duration)
