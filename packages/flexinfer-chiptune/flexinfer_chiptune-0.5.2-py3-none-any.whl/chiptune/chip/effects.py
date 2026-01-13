"""Chiptune audio effects for authentic retro sound.

These effects model the capabilities of classic sound chips
like the NES 2A03, Game Boy DMG, and similar hardware.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, ClassVar

from pydantic import BaseModel

from chiptune.theory.arpeggios import Note


class EffectType(str, Enum):
    """Types of chiptune effects."""

    VIBRATO = "vibrato"
    PITCH_SLIDE = "pitch_slide"
    PITCH_BEND = "pitch_bend"
    VOLUME_ENVELOPE = "volume_envelope"
    DUTY_CYCLE_SWEEP = "duty_sweep"
    ECHO = "echo"
    ARPEGGIO_EFFECT = "arpeggio"
    TREMOLO = "tremolo"
    PORTAMENTO = "portamento"


class ChipEffect(BaseModel, ABC):
    """Base class for chiptune effects.

    Effects modify notes or add additional sonic character
    within the constraints of classic sound hardware.
    """

    effect_type: EffectType
    enabled: bool = True

    @abstractmethod
    def apply(self, notes: list[Note]) -> list[Note]:
        """Apply the effect to a list of notes.

        Args:
            notes: Input notes

        Returns:
            Modified notes
        """
        ...


class Vibrato(ChipEffect):
    """Pitch vibrato effect.

    Creates subtle pitch oscillation for a more expressive sound.
    On real hardware, this was often done via rapid pitch register writes.
    """

    effect_type: EffectType = EffectType.VIBRATO
    speed: float = 6.0  # Oscillations per beat
    depth: int = 1  # Semitone depth (usually very subtle)
    delay_beats: float = 0.25  # Delay before vibrato starts

    # Preset vibrato styles
    STYLES: ClassVar[dict[str, dict[str, Any]]] = {
        "subtle": {"speed": 4.0, "depth": 1, "delay_beats": 0.5},
        "expressive": {"speed": 6.0, "depth": 2, "delay_beats": 0.25},
        "fast": {"speed": 10.0, "depth": 1, "delay_beats": 0.125},
        "slow": {"speed": 3.0, "depth": 2, "delay_beats": 0.0},
    }

    @classmethod
    def from_style(cls, style: str) -> Vibrato:
        """Create vibrato from a preset style."""
        params = cls.STYLES.get(style, cls.STYLES["subtle"])
        return cls(**params)

    def apply(self, notes: list[Note]) -> list[Note]:
        """Apply vibrato by expanding notes into micro-pitch variations.

        For MIDI output, we'll represent this as pitch bend data,
        but for note representation we keep notes unchanged and
        mark them for vibrato processing during export.
        """
        if not self.enabled:
            return notes
        # Vibrato is typically applied at the MIDI export stage
        # Here we just pass through, but flag would be set on channel
        return notes


class PitchSlide(ChipEffect):
    """Pitch slide between notes (portamento/glide).

    Classic chiptune effect where pitch smoothly transitions
    between notes rather than jumping.
    """

    effect_type: EffectType = EffectType.PITCH_SLIDE
    slide_time: float = 0.1  # Time for slide in beats
    direction: str = "up"  # "up" or "down"

    def apply(self, notes: list[Note]) -> list[Note]:
        """Apply pitch slide effect.

        Inserts intermediate pitch values between notes.
        """
        if not self.enabled or len(notes) < 2:
            return notes

        result: list[Note] = []
        for i, note in enumerate(notes):
            if i > 0:
                prev_pitch = notes[i - 1].pitch
                curr_pitch = note.pitch
                steps = abs(curr_pitch - prev_pitch)

                if steps > 0 and self.slide_time > 0:
                    # Create intermediate notes for the slide
                    step_duration = self.slide_time / steps
                    direction = 1 if curr_pitch > prev_pitch else -1

                    for step in range(1, steps):
                        intermediate_pitch = prev_pitch + (step * direction)
                        result.append(
                            Note(
                                pitch=intermediate_pitch,
                                duration=step_duration,
                                velocity=note.velocity,
                            )
                        )

            result.append(note)

        return result


class VolumeEnvelope(ChipEffect):
    """Volume envelope (ADSR-style) for notes.

    Classic sound chips had simple volume control, often just
    attack and decay rather than full ADSR.
    """

    effect_type: EffectType = EffectType.VOLUME_ENVELOPE
    attack_time: float = 0.0  # Time to reach peak (beats)
    decay_time: float = 0.0  # Time to reach sustain level (beats)
    sustain_level: float = 1.0  # Sustain volume (0.0-1.0)
    release_time: float = 0.1  # Time to fade to zero (beats)

    # Preset envelopes
    PRESETS: ClassVar[dict[str, dict[str, Any]]] = {
        "pluck": {
            "attack_time": 0.0,
            "decay_time": 0.2,
            "sustain_level": 0.3,
            "release_time": 0.1,
        },
        "pad": {
            "attack_time": 0.3,
            "decay_time": 0.2,
            "sustain_level": 0.8,
            "release_time": 0.5,
        },
        "stab": {
            "attack_time": 0.0,
            "decay_time": 0.1,
            "sustain_level": 0.0,
            "release_time": 0.0,
        },
        "swell": {
            "attack_time": 0.5,
            "decay_time": 0.0,
            "sustain_level": 1.0,
            "release_time": 0.2,
        },
        "chip_lead": {
            "attack_time": 0.0,
            "decay_time": 0.05,
            "sustain_level": 0.7,
            "release_time": 0.1,
        },
    }

    @classmethod
    def from_preset(cls, preset: str) -> VolumeEnvelope:
        """Create envelope from preset name."""
        params = cls.PRESETS.get(preset, cls.PRESETS["chip_lead"])
        return cls(**params)

    def apply(self, notes: list[Note]) -> list[Note]:
        """Apply envelope shaping to velocities.

        For MIDI, this modifies velocities to approximate the envelope.
        Real envelope processing happens in the synth/output stage.
        """
        if not self.enabled:
            return notes

        result: list[Note] = []
        for note in notes:
            # Simple approximation: apply decay to velocity
            effective_velocity = int(note.velocity * self.sustain_level)
            if self.attack_time > 0:
                # Notes during attack have reduced velocity
                effective_velocity = int(effective_velocity * 0.8)

            result.append(
                Note(
                    pitch=note.pitch,
                    duration=note.duration,
                    velocity=max(1, effective_velocity),
                )
            )

        return result


class DutyCycleSweep(ChipEffect):
    """Sweep through duty cycles for timbral variation.

    On the NES, changing duty cycle mid-note creates
    interesting timbral effects.
    """

    effect_type: EffectType = EffectType.DUTY_CYCLE_SWEEP
    start_duty: int = 0  # Starting duty cycle (0-3)
    end_duty: int = 2  # Ending duty cycle (0-3)
    sweep_time: float = 0.5  # Time for sweep in beats

    def apply(self, notes: list[Note]) -> list[Note]:
        """Duty cycle sweeping is applied at export time.

        The effect is stored as metadata for the MIDI exporter.
        """
        return notes


class Echo(ChipEffect):
    """Simple echo/delay effect.

    Creates repeated notes at lower volumes to simulate echo.
    Classic technique used in many chiptune compositions.
    """

    effect_type: EffectType = EffectType.ECHO
    delay_beats: float = 0.5  # Delay between original and echo
    num_echoes: int = 2  # Number of echo repetitions
    decay: float = 0.5  # Volume decay per echo (0.0-1.0)

    def apply(self, notes: list[Note]) -> list[Note]:
        """Apply echo by duplicating notes at delay intervals."""
        if not self.enabled:
            return notes

        result: list[Note] = list(notes)

        for note in notes:
            current_velocity = note.velocity
            current_offset = 0.0

            for _ in range(self.num_echoes):
                current_offset += self.delay_beats
                current_velocity = int(current_velocity * self.decay)

                if current_velocity < 10:
                    break

                # Create echo note (would need timing info in real implementation)
                echo_note = Note(
                    pitch=note.pitch,
                    duration=note.duration,
                    velocity=current_velocity,
                )
                result.append(echo_note)

        return result


class ArpeggioEffect(ChipEffect):
    """Rapid arpeggio effect for chord simulation.

    The classic chiptune technique of rapidly cycling through
    chord tones to create the illusion of harmony.
    """

    effect_type: EffectType = EffectType.ARPEGGIO_EFFECT
    intervals: tuple[int, ...] = (0, 4, 7)  # Semitone offsets (major chord)
    speed: float = 0.0625  # Duration of each arpeggio step

    # Common arpeggio chord shapes
    CHORDS: ClassVar[dict[str, tuple[int, ...]]] = {
        "major": (0, 4, 7),
        "minor": (0, 3, 7),
        "dim": (0, 3, 6),
        "aug": (0, 4, 8),
        "sus4": (0, 5, 7),
        "sus2": (0, 2, 7),
        "7th": (0, 4, 7, 10),
        "power": (0, 7),
    }

    @classmethod
    def for_chord(cls, chord_type: str, speed: float = 0.0625) -> ArpeggioEffect:
        """Create arpeggio effect for a chord type."""
        intervals = cls.CHORDS.get(chord_type, cls.CHORDS["major"])
        return cls(intervals=intervals, speed=speed)

    def apply(self, notes: list[Note]) -> list[Note]:
        """Expand each note into a rapid arpeggio.

        Each input note becomes a series of rapid notes
        cycling through the arpeggio intervals.
        """
        if not self.enabled:
            return notes

        result: list[Note] = []

        for note in notes:
            # Calculate how many arpeggio cycles fit in the note duration
            num_steps = max(1, int(note.duration / self.speed))

            for i in range(num_steps):
                interval = self.intervals[i % len(self.intervals)]
                arp_note = Note(
                    pitch=note.pitch + interval,
                    duration=self.speed,
                    velocity=note.velocity,
                )
                result.append(arp_note)

        return result


class Tremolo(ChipEffect):
    """Volume tremolo (amplitude modulation).

    Rapid volume oscillation for a warbling effect.
    """

    effect_type: EffectType = EffectType.TREMOLO
    speed: float = 8.0  # Oscillations per beat
    depth: float = 0.3  # Depth of volume variation (0.0-1.0)

    def apply(self, notes: list[Note]) -> list[Note]:
        """Tremolo is applied at output stage.

        Returns notes unchanged; effect is processed during MIDI export.
        """
        return notes
