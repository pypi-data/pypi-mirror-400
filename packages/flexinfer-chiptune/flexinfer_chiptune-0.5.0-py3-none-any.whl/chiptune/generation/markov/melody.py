"""Markov chain melody generator."""

from __future__ import annotations

from pydantic import BaseModel, Field

from chiptune.generation.markov.chain import WeightedMarkovChain
from chiptune.theory.arpeggios import Note

# Interval representations for Markov training
# Using intervals (semitones from previous note) makes patterns key-independent
Interval = int  # Semitones: 0=unison, 2=whole step, 7=fifth, etc.


class MelodyState(BaseModel):
    """State for melody generation combining pitch and rhythm."""

    interval: int  # Interval from previous note
    duration: float  # Note duration in beats

    def __hash__(self) -> int:
        return hash((self.interval, self.duration))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MelodyState):
            return False
        return self.interval == other.interval and self.duration == other.duration


class MarkovMelodyGenerator(BaseModel):
    """Generate melodies using Markov chains.

    Trains separate chains for intervals (pitch movement) and rhythms,
    then combines them to generate complete melodies.

    Attributes:
        order: Markov chain order (1-3 recommended)
        temperature: Randomness (0=deterministic, 1=normal, >1=chaotic)
        interval_chain: Chain for pitch intervals
        rhythm_chain: Chain for note durations
    """

    order: int = Field(default=2, ge=1, le=4)
    temperature: float = Field(default=1.0, ge=0.0, le=3.0)
    interval_chain: WeightedMarkovChain[int] = Field(
        default_factory=lambda: WeightedMarkovChain[int](order=2)
    )
    rhythm_chain: WeightedMarkovChain[float] = Field(
        default_factory=lambda: WeightedMarkovChain[float](order=2)
    )

    def model_post_init(self, __context) -> None:
        """Initialize chains with correct order and temperature."""
        self.interval_chain.order = self.order
        self.interval_chain.temperature = self.temperature
        self.rhythm_chain.order = self.order
        self.rhythm_chain.temperature = self.temperature

    def train_from_notes(self, notes: list[Note]) -> None:
        """Train from a list of notes.

        Args:
            notes: Notes to learn from
        """
        if len(notes) < 2:
            return

        # Extract intervals between consecutive notes
        intervals = []
        for i in range(1, len(notes)):
            interval = notes[i].pitch - notes[i - 1].pitch
            intervals.append(interval)

        # Extract durations
        durations = [n.duration for n in notes]

        self.interval_chain.train(intervals)
        self.rhythm_chain.train(durations)

    def train_from_midi_pitches(
        self, pitches: list[int], durations: list[float] | None = None
    ) -> None:
        """Train from MIDI pitch values.

        Args:
            pitches: List of MIDI note numbers
            durations: Optional list of durations (defaults to 1.0)
        """
        if len(pitches) < 2:
            return

        if durations is None:
            durations = [1.0] * len(pitches)

        # Convert to intervals
        intervals = []
        for i in range(1, len(pitches)):
            intervals.append(pitches[i] - pitches[i - 1])

        self.interval_chain.train(intervals)
        self.rhythm_chain.train(durations)

    def generate(
        self,
        length: int,
        start_pitch: int = 60,
        seed: int | None = None,
        pitch_range: tuple[int, int] = (48, 84),
    ) -> list[Note]:
        """Generate a melody.

        Args:
            length: Number of notes to generate
            start_pitch: Starting MIDI pitch
            seed: Random seed
            pitch_range: (min, max) MIDI pitch bounds

        Returns:
            List of generated notes
        """
        if not self.interval_chain.is_trained:
            return []

        # Generate intervals
        intervals = self.interval_chain.generate(length - 1, seed=seed)

        # Generate rhythms
        if self.rhythm_chain.is_trained:
            durations = self.rhythm_chain.generate(length, seed=seed)
        else:
            durations = [1.0] * length

        # Build notes from intervals
        notes = []
        current_pitch = start_pitch

        for i in range(length):
            # Clamp pitch to range
            current_pitch = max(pitch_range[0], min(pitch_range[1], current_pitch))

            duration = durations[i] if i < len(durations) else 1.0
            notes.append(Note(pitch=current_pitch, duration=duration, velocity=100))

            # Apply next interval
            if i < len(intervals):
                current_pitch += intervals[i]

        return notes

    def generate_in_scale(
        self,
        length: int,
        scale_pitches: list[int],
        start_pitch: int | None = None,
        seed: int | None = None,
    ) -> list[Note]:
        """Generate melody constrained to a scale.

        Args:
            length: Number of notes
            scale_pitches: Valid MIDI pitches in the scale
            start_pitch: Starting pitch (picks from scale if None)
            seed: Random seed

        Returns:
            Generated notes constrained to scale
        """
        if not scale_pitches:
            return []

        if start_pitch is None:
            # Pick a starting pitch from middle of scale
            mid_idx = len(scale_pitches) // 2
            start_pitch = scale_pitches[mid_idx]

        # Generate raw melody
        raw_notes = self.generate(length, start_pitch, seed)

        # Snap to scale
        result = []
        for note in raw_notes:
            # Find closest scale pitch
            closest = min(scale_pitches, key=lambda p: abs(p - note.pitch))
            result.append(Note(pitch=closest, duration=note.duration, velocity=note.velocity))

        return result


class MelodyStyle(BaseModel):
    """Pre-trained melody style with characteristic patterns."""

    name: str
    generator: MarkovMelodyGenerator
    description: str = ""

    @classmethod
    def heroic(cls) -> MelodyStyle:
        """Bold, triumphant melody patterns."""
        gen = MarkovMelodyGenerator(order=2, temperature=0.8)

        # Heroic patterns: big leaps, strong rhythms
        patterns = [
            # Fanfare-like
            [60, 64, 67, 72, 67, 64, 60],
            [60, 67, 64, 72, 69, 72, 67],
            # Ascending triumph
            [60, 62, 64, 67, 69, 72, 74, 72],
            [55, 60, 62, 64, 67, 72, 67, 64],
            # Strong intervals (4ths, 5ths)
            [60, 65, 67, 72, 67, 60, 65, 67],
            [60, 67, 65, 60, 67, 72, 67, 60],
        ]

        rhythms = [
            [1.0, 0.5, 0.5, 2.0, 1.0, 0.5, 0.5],
            [0.5, 0.5, 1.0, 1.0, 0.5, 0.5, 1.0],
            [1.0, 1.0, 0.5, 0.5, 1.0, 2.0, 1.0, 1.0],
        ]

        for pitches in patterns:
            gen.train_from_midi_pitches(pitches)
        for rhythm in rhythms:
            gen.rhythm_chain.train(rhythm)

        return cls(
            name="heroic",
            generator=gen,
            description="Bold, triumphant patterns with strong intervals",
        )

    @classmethod
    def mysterious(cls) -> MelodyStyle:
        """Eerie, suspenseful melody patterns."""
        gen = MarkovMelodyGenerator(order=2, temperature=1.0)

        # Mysterious: chromatic movement, minor seconds, tritones
        patterns = [
            [60, 61, 63, 60, 66, 63, 61, 60],  # Chromatic creep
            [60, 63, 66, 69, 66, 63, 60],  # Diminished
            [60, 61, 60, 66, 67, 66, 61, 60],  # Tritone tension
            [60, 58, 61, 60, 63, 61, 58, 60],  # Minor 2nds
            [60, 63, 67, 66, 63, 60, 58, 60],  # Descending chromatic
        ]

        rhythms = [
            [2.0, 1.0, 1.0, 2.0, 1.0, 1.0, 2.0],
            [1.5, 0.5, 1.0, 2.0, 1.0, 0.5, 1.5],
        ]

        for pitches in patterns:
            gen.train_from_midi_pitches(pitches)
        for rhythm in rhythms:
            gen.rhythm_chain.train(rhythm)

        return cls(
            name="mysterious",
            generator=gen,
            description="Chromatic, suspenseful patterns",
        )

    @classmethod
    def playful(cls) -> MelodyStyle:
        """Light, bouncy melody patterns."""
        gen = MarkovMelodyGenerator(order=2, temperature=1.1)

        # Playful: quick intervals, scalar runs
        patterns = [
            [60, 62, 64, 62, 60, 62, 64, 67],
            [67, 65, 64, 62, 64, 65, 67, 69],
            [60, 64, 62, 65, 64, 67, 65, 69],
            [72, 69, 67, 64, 67, 69, 67, 64],
            [60, 62, 64, 67, 64, 62, 64, 60],
        ]

        rhythms = [
            [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 1.0],
            [0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.5],
            [0.5, 0.5, 1.0, 0.5, 0.5, 0.5, 0.5],
        ]

        for pitches in patterns:
            gen.train_from_midi_pitches(pitches)
        for rhythm in rhythms:
            gen.rhythm_chain.train(rhythm)

        return cls(
            name="playful",
            generator=gen,
            description="Light, bouncy scalar patterns",
        )

    @classmethod
    def melancholic(cls) -> MelodyStyle:
        """Sad, emotional melody patterns."""
        gen = MarkovMelodyGenerator(order=2, temperature=0.9)

        # Melancholic: descending lines, minor mode
        patterns = [
            [72, 71, 69, 67, 69, 67, 65, 64],
            [67, 65, 64, 62, 60, 62, 64, 62],
            [72, 69, 67, 64, 67, 65, 64, 60],
            [60, 63, 62, 60, 58, 60, 63, 60],
            [67, 64, 63, 60, 63, 64, 63, 60],
        ]

        rhythms = [
            [2.0, 1.0, 1.0, 2.0, 1.0, 1.0, 2.0, 2.0],
            [1.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0],
        ]

        for pitches in patterns:
            gen.train_from_midi_pitches(pitches)
        for rhythm in rhythms:
            gen.rhythm_chain.train(rhythm)

        return cls(
            name="melancholic",
            generator=gen,
            description="Descending, emotional patterns",
        )

    @classmethod
    def epic(cls) -> MelodyStyle:
        """Grand, sweeping melody patterns."""
        gen = MarkovMelodyGenerator(order=3, temperature=0.85)

        # Epic: wide intervals, dramatic contour
        patterns = [
            [48, 55, 60, 67, 72, 67, 60, 55, 48],
            [60, 67, 72, 79, 72, 67, 64, 60],
            [55, 60, 67, 72, 76, 72, 67, 60, 55],
            [48, 60, 55, 67, 60, 72, 67, 60],
            [60, 72, 67, 79, 72, 60, 67, 55],
        ]

        rhythms = [
            [1.0, 1.0, 1.0, 2.0, 2.0, 1.0, 1.0, 1.0, 2.0],
            [2.0, 1.0, 1.0, 4.0, 2.0, 1.0, 1.0, 2.0],
        ]

        for pitches in patterns:
            gen.train_from_midi_pitches(pitches)
        for rhythm in rhythms:
            gen.rhythm_chain.train(rhythm)

        return cls(
            name="epic",
            generator=gen,
            description="Grand, sweeping dramatic patterns",
        )

    @classmethod
    def chiptune(cls) -> MelodyStyle:
        """Classic 8-bit game melody patterns."""
        gen = MarkovMelodyGenerator(order=2, temperature=0.9)

        # Chiptune: arpeggios, octave jumps
        patterns = [
            [60, 64, 67, 72, 67, 64, 60, 64],
            [60, 67, 60, 72, 60, 67, 60, 64],
            [72, 60, 67, 64, 72, 67, 60, 64],
            [60, 62, 64, 67, 64, 62, 60, 55],
            [60, 72, 64, 76, 67, 79, 72, 60],
        ]

        rhythms = [
            [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
            [0.25, 0.25, 0.25, 0.25, 0.5, 0.5, 0.5, 0.5],
            [1.0, 0.5, 0.5, 1.0, 0.5, 0.5, 1.0],
        ]

        for pitches in patterns:
            gen.train_from_midi_pitches(pitches)
        for rhythm in rhythms:
            gen.rhythm_chain.train(rhythm)

        return cls(
            name="chiptune",
            generator=gen,
            description="Classic 8-bit arpeggio patterns",
        )
