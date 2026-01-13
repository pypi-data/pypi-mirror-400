"""Rule-based bass line generator."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from chiptune.theory.arpeggios import Note
from chiptune.theory.chords import Chord


class BassPattern(str, Enum):
    """Bass line pattern types."""

    ROOT = "root"  # Just root notes
    ROOT_FIFTH = "root_fifth"  # Root and fifth
    OCTAVE = "octave"  # Root and octave
    WALKING = "walking"  # Walking bass line
    ARPEGGIATED = "arpeggiated"  # Chord arpeggios
    APPROACH = "approach"  # Approach notes to next root


class BassRules(BaseModel):
    """Rule set for bass line generation."""

    # Interval preferences (semitones -> weight)
    # Lower weight = less likely
    interval_weights: dict[int, float] = Field(
        default_factory=lambda: {
            0: 0.3,  # Unison (avoid)
            1: 0.4,  # Minor 2nd
            2: 0.7,  # Major 2nd (common)
            3: 0.6,  # Minor 3rd
            4: 0.6,  # Major 3rd
            5: 0.9,  # Perfect 4th (very common)
            7: 1.0,  # Perfect 5th (most common)
            12: 0.8,  # Octave
        }
    )

    # Prefer stepwise motion vs leaps
    stepwise_preference: float = Field(default=0.7, ge=0.0, le=1.0)

    # Prefer moving toward next chord root
    approach_preference: float = Field(default=0.6, ge=0.0, le=1.0)

    # Range constraints
    min_pitch: int = Field(default=28, ge=0, le=127)  # E1
    max_pitch: int = Field(default=55, ge=0, le=127)  # G3

    # Rhythm settings
    note_density: float = Field(default=1.0, ge=0.25, le=4.0)  # Notes per beat


class BassGenerator(BaseModel):
    """Generate bass lines following music theory rules.

    Creates bass lines that:
    - Follow chord changes
    - Use appropriate patterns (root, walking, etc.)
    - Stay within bass range
    - Approach target notes smoothly

    Example:
        gen = BassGenerator(pattern=BassPattern.WALKING)
        chords = [Chord.parse("C"), Chord.parse("Am"), Chord.parse("F"), Chord.parse("G")]
        bass = gen.generate(chords, beats_per_chord=4)
    """

    pattern: BassPattern = BassPattern.ROOT_FIFTH
    rules: BassRules = Field(default_factory=BassRules)
    velocity: int = Field(default=100, ge=1, le=127)
    octave: int = Field(default=2, ge=1, le=4)  # Bass octave (2 = C2-C3)

    def _get_chord_bass(self, chord: Chord) -> int:
        """Get bass note (root) for chord."""
        # Get root pitch at bass octave
        root_pitch = chord.root_midi + (self.octave - 4) * 12

        # Adjust to stay in range
        while root_pitch > self.rules.max_pitch:
            root_pitch -= 12
        while root_pitch < self.rules.min_pitch:
            root_pitch += 12

        return root_pitch

    def _generate_root(self, chord: Chord, beats: float, beat_duration: float = 1.0) -> list[Note]:
        """Generate simple root notes."""
        root = self._get_chord_bass(chord)
        notes_count = max(1, int(beats * self.rules.note_density))
        duration = beats / notes_count

        return [
            Note(pitch=root, duration=duration, velocity=self.velocity) for _ in range(notes_count)
        ]

    def _generate_root_fifth(
        self, chord: Chord, beats: float, beat_duration: float = 1.0
    ) -> list[Note]:
        """Generate root-fifth pattern."""
        root = self._get_chord_bass(chord)
        fifth = root + 7  # Perfect fifth

        # Ensure fifth is in range
        if fifth > self.rules.max_pitch:
            fifth -= 12

        notes = []
        half_beats = beats / 2
        duration = half_beats / max(1, int(half_beats * self.rules.note_density))

        # Alternate root and fifth
        count = max(2, int(beats * self.rules.note_density))
        for i in range(count):
            pitch = root if i % 2 == 0 else fifth
            notes.append(Note(pitch=pitch, duration=duration, velocity=self.velocity))

        return notes

    def _generate_octave(
        self, chord: Chord, beats: float, beat_duration: float = 1.0
    ) -> list[Note]:
        """Generate root-octave pattern."""
        root = self._get_chord_bass(chord)
        octave = root + 12

        # Ensure octave is in range
        if octave > self.rules.max_pitch:
            octave = root  # Just use root

        notes = []
        count = max(2, int(beats * self.rules.note_density))
        duration = beats / count

        for i in range(count):
            pitch = root if i % 2 == 0 else octave
            notes.append(Note(pitch=pitch, duration=duration, velocity=self.velocity))

        return notes

    def _generate_walking(
        self,
        chord: Chord,
        beats: float,
        next_chord: Chord | None = None,
        beat_duration: float = 1.0,
    ) -> list[Note]:
        """Generate walking bass line."""
        root = self._get_chord_bass(chord)
        notes = []
        count = max(1, int(beats * self.rules.note_density))
        duration = beats / count

        # Get target for approach (next chord root)
        if next_chord:
            target = self._get_chord_bass(next_chord)
        else:
            target = root

        # Build walking pattern
        current = root
        chord_tones = [root, root + 3, root + 5, root + 7]  # Simple chord outline

        for i in range(count):
            if i == 0:
                # Start on root
                pitch = root
            elif i == count - 1 and next_chord:
                # Approach note to next root
                if target > current:
                    pitch = target - 1  # Approach from below
                elif target < current:
                    pitch = target + 1  # Approach from above
                else:
                    pitch = current
            # Choose chord tone or passing tone
            elif i % 2 == 1:
                # Prefer chord tones on weak beats
                pitch = chord_tones[(i // 2) % len(chord_tones)]
            else:
                # Stepwise motion on strong beats
                step = 2 if current < target else -2
                pitch = current + step

            # Clamp to range
            pitch = max(self.rules.min_pitch, min(self.rules.max_pitch, pitch))

            notes.append(Note(pitch=pitch, duration=duration, velocity=self.velocity))
            current = pitch

        return notes

    def _generate_arpeggiated(
        self, chord: Chord, beats: float, beat_duration: float = 1.0
    ) -> list[Note]:
        """Generate arpeggiated bass."""
        root = self._get_chord_bass(chord)
        arp_notes = [root, root + 4, root + 7, root + 12]  # 1-3-5-8

        # Filter to range
        arp_notes = [p for p in arp_notes if self.rules.min_pitch <= p <= self.rules.max_pitch]
        if not arp_notes:
            arp_notes = [root]

        notes = []
        count = max(len(arp_notes), int(beats * self.rules.note_density))
        duration = beats / count

        for i in range(count):
            pitch = arp_notes[i % len(arp_notes)]
            notes.append(Note(pitch=pitch, duration=duration, velocity=self.velocity))

        return notes

    def _generate_approach(
        self,
        chord: Chord,
        beats: float,
        next_chord: Chord | None = None,
        beat_duration: float = 1.0,
    ) -> list[Note]:
        """Generate bass with chromatic approach to next chord."""
        root = self._get_chord_bass(chord)
        notes = []

        if beats <= 1:
            return [Note(pitch=root, duration=beats, velocity=self.velocity)]

        # Main note on root
        main_duration = beats - 0.5
        notes.append(Note(pitch=root, duration=main_duration, velocity=self.velocity))

        # Approach note
        if next_chord:
            target = self._get_chord_bass(next_chord)
            if target > root:
                approach = target - 1
            elif target < root:
                approach = target + 1
            else:
                approach = root + 7 if root + 7 <= self.rules.max_pitch else root - 5
        else:
            approach = root + 7 if root + 7 <= self.rules.max_pitch else root

        notes.append(Note(pitch=approach, duration=0.5, velocity=self.velocity))

        return notes

    def generate_for_chord(
        self,
        chord: Chord,
        beats: float,
        next_chord: Chord | None = None,
    ) -> list[Note]:
        """Generate bass for a single chord.

        Args:
            chord: Current chord
            beats: Duration in beats
            next_chord: Next chord (for approach notes)

        Returns:
            List of bass notes
        """
        if self.pattern == BassPattern.ROOT:
            return self._generate_root(chord, beats)
        elif self.pattern == BassPattern.ROOT_FIFTH:
            return self._generate_root_fifth(chord, beats)
        elif self.pattern == BassPattern.OCTAVE:
            return self._generate_octave(chord, beats)
        elif self.pattern == BassPattern.WALKING:
            return self._generate_walking(chord, beats, next_chord)
        elif self.pattern == BassPattern.ARPEGGIATED:
            return self._generate_arpeggiated(chord, beats)
        elif self.pattern == BassPattern.APPROACH:
            return self._generate_approach(chord, beats, next_chord)
        else:
            return self._generate_root(chord, beats)

    def generate(
        self,
        chords: list[Chord],
        beats_per_chord: float = 4.0,
    ) -> list[Note]:
        """Generate complete bass line for chord progression.

        Args:
            chords: List of chords in progression
            beats_per_chord: Duration of each chord in beats

        Returns:
            Complete bass line as list of notes
        """
        all_notes = []

        for i, chord in enumerate(chords):
            next_chord = chords[i + 1] if i + 1 < len(chords) else chords[0]
            notes = self.generate_for_chord(chord, beats_per_chord, next_chord)
            all_notes.extend(notes)

        return all_notes

    @classmethod
    def simple(cls) -> BassGenerator:
        """Simple root note bass."""
        return cls(pattern=BassPattern.ROOT)

    @classmethod
    def rock(cls) -> BassGenerator:
        """Rock-style root-fifth bass."""
        rules = BassRules(note_density=2.0)
        return cls(pattern=BassPattern.ROOT_FIFTH, rules=rules)

    @classmethod
    def jazz(cls) -> BassGenerator:
        """Jazz walking bass."""
        rules = BassRules(note_density=1.0, stepwise_preference=0.8)
        return cls(pattern=BassPattern.WALKING, rules=rules)

    @classmethod
    def funk(cls) -> BassGenerator:
        """Funky octave bass."""
        rules = BassRules(note_density=4.0)
        return cls(pattern=BassPattern.OCTAVE, rules=rules)

    @classmethod
    def chiptune(cls) -> BassGenerator:
        """8-bit arpeggiated bass."""
        rules = BassRules(note_density=4.0, min_pitch=36, max_pitch=60)
        return cls(pattern=BassPattern.ARPEGGIATED, rules=rules, octave=3)
