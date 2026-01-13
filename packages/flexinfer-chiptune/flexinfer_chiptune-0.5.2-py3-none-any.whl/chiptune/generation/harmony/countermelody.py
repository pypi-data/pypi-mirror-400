"""Countermelody generator using music theory rules.

Generates harmonically correct secondary melodies that complement
the main melody using various motion types.
"""

from __future__ import annotations

from enum import Enum
from typing import ClassVar

import numpy as np
from pydantic import BaseModel, Field

from chiptune.theory.arpeggios import Note
from chiptune.theory.scales import Scale


class MotionType(str, Enum):
    """Types of melodic motion relative to main melody."""

    CONTRARY = "contrary"  # Opposite direction
    PARALLEL = "parallel"  # Same direction, fixed interval
    OBLIQUE = "oblique"  # One voice holds
    SIMILAR = "similar"  # Same direction, varying intervals
    FREE = "free"  # Mix of all types


class HarmonyInterval(str, Enum):
    """Common harmony intervals for parallel motion."""

    THIRD = "third"  # 3 or 4 semitones
    SIXTH = "sixth"  # 8 or 9 semitones
    FIFTH = "fifth"  # 7 semitones (power chord feel)
    OCTAVE = "octave"  # 12 semitones


class CountermelodyRules(BaseModel):
    """Rules governing countermelody generation."""

    # Preferred intervals from melody (semitones -> weight)
    interval_weights: dict[int, float] = Field(
        default_factory=lambda: {
            3: 0.9,  # Minor 3rd (common harmony)
            4: 0.9,  # Major 3rd
            5: 0.5,  # Perfect 4th
            7: 0.7,  # Perfect 5th
            8: 0.8,  # Minor 6th
            9: 0.8,  # Major 6th
            12: 0.6,  # Octave
        }
    )

    # Motion type probabilities for FREE motion
    motion_weights: dict[MotionType, float] = Field(
        default_factory=lambda: {
            MotionType.CONTRARY: 0.4,
            MotionType.PARALLEL: 0.3,
            MotionType.OBLIQUE: 0.2,
            MotionType.SIMILAR: 0.1,
        }
    )

    # Range constraints relative to melody
    min_offset: int = Field(default=-12, ge=-24, le=0)  # Below melody
    max_offset: int = Field(default=12, ge=0, le=24)  # Above melody

    # Absolute range
    min_pitch: int = Field(default=48, ge=0, le=127)  # C3
    max_pitch: int = Field(default=84, ge=0, le=127)  # C6

    # Rhythm settings
    rhythmic_variation: float = Field(default=0.0, ge=0.0, le=1.0)


class CountermelodyGenerator(BaseModel):
    """Generate countermelodies following music theory principles.

    Creates secondary melodies that harmonize with the main melody using:
    - Contrary motion (opposite direction)
    - Parallel motion (fixed intervals like 3rds/6ths)
    - Oblique motion (sustained notes)
    - Scale-aware note selection

    Example:
        gen = CountermelodyGenerator(motion=MotionType.CONTRARY)
        melody = [Note(60, 1.0), Note(62, 1.0), Note(64, 1.0)]
        counter = gen.generate(melody, scale=Scale.major("C"))
    """

    motion: MotionType = MotionType.CONTRARY
    harmony_interval: HarmonyInterval = HarmonyInterval.THIRD
    rules: CountermelodyRules = Field(default_factory=CountermelodyRules)
    velocity_offset: int = Field(default=-10, ge=-50, le=50)  # Quieter than melody
    seed: int | None = None

    # Interval mappings
    INTERVAL_SEMITONES: ClassVar[dict[HarmonyInterval, list[int]]] = {
        HarmonyInterval.THIRD: [3, 4],  # Minor/major 3rd
        HarmonyInterval.SIXTH: [8, 9],  # Minor/major 6th
        HarmonyInterval.FIFTH: [7],  # Perfect 5th
        HarmonyInterval.OCTAVE: [12],  # Octave
    }

    def _get_rng(self) -> np.random.Generator:
        """Get random number generator."""
        return np.random.default_rng(self.seed)

    def _is_in_scale(self, pitch: int, scale: Scale | None) -> bool:
        """Check if pitch is in scale."""
        if scale is None:
            return True
        scale_pitches = scale.get_pitches(octave=0)
        pitch_class = pitch % 12
        return pitch_class in [p % 12 for p in scale_pitches]

    def _nearest_scale_tone(self, pitch: int, scale: Scale | None) -> int:
        """Find nearest pitch in scale."""
        if scale is None:
            return pitch

        scale_pitches = scale.get_pitches(octave=0)
        scale_classes = [p % 12 for p in scale_pitches]
        pitch_class = pitch % 12

        if pitch_class in scale_classes:
            return pitch

        # Find nearest scale tone
        best_pitch = pitch
        best_distance = 12

        for sc in scale_classes:
            distance = min(abs(pitch_class - sc), 12 - abs(pitch_class - sc))
            if distance < best_distance:
                best_distance = distance
                # Adjust to nearest occurrence
                if pitch_class < sc or (pitch_class > sc + 6):
                    best_pitch = pitch + (sc - pitch_class)
                else:
                    best_pitch = pitch - (pitch_class - sc)

        return best_pitch

    def _clamp_pitch(self, pitch: int) -> int:
        """Clamp pitch to valid range."""
        return max(self.rules.min_pitch, min(self.rules.max_pitch, pitch))

    def _generate_contrary(
        self,
        melody: list[Note],
        scale: Scale | None = None,
    ) -> list[Note]:
        """Generate countermelody using contrary motion."""
        if len(melody) < 2:
            return self._generate_parallel(melody, scale)

        result: list[Note] = []
        rng = self._get_rng()

        # Start with harmony interval below/above melody
        intervals = self.INTERVAL_SEMITONES[self.harmony_interval]
        base_interval = rng.choice(intervals)

        # Determine if counter is above or below
        above = melody[0].pitch < (self.rules.max_pitch + self.rules.min_pitch) / 2

        prev_counter_pitch = (
            melody[0].pitch + base_interval if above else melody[0].pitch - base_interval
        )

        for i, note in enumerate(melody):
            if note.velocity == 0:
                # Rest
                result.append(Note(pitch=0, duration=note.duration, velocity=0))
                continue

            if i == 0:
                counter_pitch = prev_counter_pitch
            else:
                # Calculate melody direction
                prev_melody = melody[i - 1].pitch
                melody_direction = note.pitch - prev_melody

                # Move contrary direction
                if melody_direction > 0:
                    # Melody went up, counter goes down
                    step = -rng.integers(1, 4)
                elif melody_direction < 0:
                    # Melody went down, counter goes up
                    step = rng.integers(1, 4)
                else:
                    # Melody stayed, counter can move slightly
                    step = rng.integers(-2, 3)

                counter_pitch = prev_counter_pitch + step

            # Snap to scale
            counter_pitch = self._nearest_scale_tone(counter_pitch, scale)
            counter_pitch = self._clamp_pitch(counter_pitch)

            velocity = max(1, min(127, note.velocity + self.velocity_offset))
            result.append(Note(pitch=counter_pitch, duration=note.duration, velocity=velocity))
            prev_counter_pitch = counter_pitch

        return result

    def _generate_parallel(
        self,
        melody: list[Note],
        scale: Scale | None = None,
    ) -> list[Note]:
        """Generate countermelody using parallel motion."""
        result: list[Note] = []
        rng = self._get_rng()

        intervals = self.INTERVAL_SEMITONES[self.harmony_interval]

        # Decide above or below melody
        above = rng.random() > 0.5

        for note in melody:
            if note.velocity == 0:
                result.append(Note(pitch=0, duration=note.duration, velocity=0))
                continue

            # Pick interval for this note
            interval = rng.choice(intervals)
            counter_pitch = note.pitch + interval if above else note.pitch - interval

            # Snap to scale
            counter_pitch = self._nearest_scale_tone(counter_pitch, scale)
            counter_pitch = self._clamp_pitch(counter_pitch)

            velocity = max(1, min(127, note.velocity + self.velocity_offset))
            result.append(Note(pitch=counter_pitch, duration=note.duration, velocity=velocity))

        return result

    def _generate_oblique(
        self,
        melody: list[Note],
        scale: Scale | None = None,
    ) -> list[Note]:
        """Generate countermelody using oblique motion (sustained notes)."""
        if not melody:
            return []

        result: list[Note] = []
        rng = self._get_rng()

        intervals = self.INTERVAL_SEMITONES[self.harmony_interval]
        above = rng.random() > 0.5

        # Pick a held pitch based on first melody note
        interval = rng.choice(intervals)
        held_pitch = melody[0].pitch + interval if above else melody[0].pitch - interval
        held_pitch = self._nearest_scale_tone(held_pitch, scale)
        held_pitch = self._clamp_pitch(held_pitch)

        # Count notes before changing held pitch
        hold_count = 0
        hold_length = rng.integers(2, 5)

        for note in melody:
            if note.velocity == 0:
                result.append(Note(pitch=0, duration=note.duration, velocity=0))
                continue

            hold_count += 1

            # Occasionally change the held pitch
            if hold_count >= hold_length:
                hold_count = 0
                hold_length = rng.integers(2, 5)

                # Pick new held note
                interval = rng.choice(intervals)
                held_pitch = note.pitch + interval if above else note.pitch - interval
                held_pitch = self._nearest_scale_tone(held_pitch, scale)
                held_pitch = self._clamp_pitch(held_pitch)

            velocity = max(1, min(127, note.velocity + self.velocity_offset))
            result.append(Note(pitch=held_pitch, duration=note.duration, velocity=velocity))

        return result

    def _generate_similar(
        self,
        melody: list[Note],
        scale: Scale | None = None,
    ) -> list[Note]:
        """Generate countermelody using similar motion (same direction, different intervals)."""
        if len(melody) < 2:
            return self._generate_parallel(melody, scale)

        result: list[Note] = []
        rng = self._get_rng()

        intervals = self.INTERVAL_SEMITONES[self.harmony_interval]
        above = rng.random() > 0.5

        # Start with a harmony interval
        interval = rng.choice(intervals)
        prev_counter_pitch = melody[0].pitch + interval if above else melody[0].pitch - interval

        for i, note in enumerate(melody):
            if note.velocity == 0:
                result.append(Note(pitch=0, duration=note.duration, velocity=0))
                continue

            if i == 0:
                counter_pitch = prev_counter_pitch
            else:
                # Move in same direction as melody, but with varying step size
                prev_melody = melody[i - 1].pitch
                melody_direction = note.pitch - prev_melody

                # Same direction, but possibly different amount
                step: int
                if melody_direction > 0:
                    step = int(rng.integers(1, melody_direction + 2))
                elif melody_direction < 0:
                    step = -int(rng.integers(1, abs(melody_direction) + 2))
                else:
                    step = 0

                counter_pitch = prev_counter_pitch + step

            counter_pitch = self._nearest_scale_tone(counter_pitch, scale)
            counter_pitch = self._clamp_pitch(counter_pitch)

            velocity = max(1, min(127, note.velocity + self.velocity_offset))
            result.append(Note(pitch=counter_pitch, duration=note.duration, velocity=velocity))
            prev_counter_pitch = counter_pitch

        return result

    def _generate_free(
        self,
        melody: list[Note],
        scale: Scale | None = None,
    ) -> list[Note]:
        """Generate countermelody mixing all motion types."""
        if not melody:
            return []

        result: list[Note] = []
        rng = self._get_rng()

        # Split melody into segments and apply different motions
        segment_size = max(2, len(melody) // 4)
        motion_types = list(self.rules.motion_weights.keys())
        weights = list(self.rules.motion_weights.values())

        for i in range(0, len(melody), segment_size):
            segment = melody[i : i + segment_size]

            # Choose motion type for this segment
            motion = rng.choice(motion_types, p=np.array(weights) / sum(weights))

            if motion == MotionType.CONTRARY:
                segment_counter = self._generate_contrary(segment, scale)
            elif motion == MotionType.PARALLEL:
                segment_counter = self._generate_parallel(segment, scale)
            elif motion == MotionType.OBLIQUE:
                segment_counter = self._generate_oblique(segment, scale)
            else:
                segment_counter = self._generate_similar(segment, scale)

            result.extend(segment_counter)

        return result

    def generate(
        self,
        melody: list[Note],
        scale: Scale | None = None,
    ) -> list[Note]:
        """Generate countermelody for given melody.

        Args:
            melody: Main melody notes
            scale: Optional scale for note selection

        Returns:
            Countermelody notes
        """
        if not melody:
            return []

        if self.motion == MotionType.CONTRARY:
            return self._generate_contrary(melody, scale)
        elif self.motion == MotionType.PARALLEL:
            return self._generate_parallel(melody, scale)
        elif self.motion == MotionType.OBLIQUE:
            return self._generate_oblique(melody, scale)
        elif self.motion == MotionType.SIMILAR:
            return self._generate_similar(melody, scale)
        else:  # FREE
            return self._generate_free(melody, scale)

    @classmethod
    def thirds(cls, above: bool = True) -> CountermelodyGenerator:
        """Parallel thirds harmony."""
        rules = CountermelodyRules(
            min_offset=-12 if not above else 0,
            max_offset=0 if not above else 12,
        )
        return cls(
            motion=MotionType.PARALLEL,
            harmony_interval=HarmonyInterval.THIRD,
            rules=rules,
        )

    @classmethod
    def sixths(cls) -> CountermelodyGenerator:
        """Parallel sixths harmony."""
        return cls(
            motion=MotionType.PARALLEL,
            harmony_interval=HarmonyInterval.SIXTH,
        )

    @classmethod
    def contrary(cls) -> CountermelodyGenerator:
        """Classic contrary motion counterpoint."""
        return cls(motion=MotionType.CONTRARY)

    @classmethod
    def drone(cls) -> CountermelodyGenerator:
        """Drone/pedal tone style."""
        return cls(motion=MotionType.OBLIQUE, velocity_offset=-20)

    @classmethod
    def mixed(cls, seed: int | None = None) -> CountermelodyGenerator:
        """Mixed motion types for variety."""
        return cls(motion=MotionType.FREE, seed=seed)

    @classmethod
    def chiptune_harmony(cls) -> CountermelodyGenerator:
        """Chiptune-style harmony (tight intervals, high register)."""
        rules = CountermelodyRules(
            min_pitch=60,  # C4
            max_pitch=96,  # C7
            min_offset=0,
            max_offset=12,
        )
        return cls(
            motion=MotionType.PARALLEL,
            harmony_interval=HarmonyInterval.THIRD,
            rules=rules,
            velocity_offset=-5,
        )
