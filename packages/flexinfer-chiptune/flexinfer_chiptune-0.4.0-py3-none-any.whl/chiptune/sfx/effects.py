"""Game sound effect generators.

Provides quick methods for generating common game sound effects
as MIDI, designed for the characteristic 8-bit/16-bit aesthetic.
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel

from chiptune.output.midi import MidiExporter
from chiptune.theory.arpeggios import Note


class SFXGenerator(BaseModel):
    """Generate common game sound effects.

    All methods return MIDI bytes that can be played directly
    or saved to files.

    Example:
        ```python
        sfx = SFXGenerator()

        # Generate sounds
        coin = sfx.coin_collect()
        jump = sfx.jump()
        explosion = sfx.explosion()

        # Save to file
        sfx.save(coin, "coin.mid")
        ```
    """

    tempo: int = 180  # Fast tempo for quick effects
    base_octave: int = 5
    base_velocity: int = 100

    # Common pitch values for effects
    PITCHES: ClassVar[dict[str, int]] = {
        "low": 48,  # C3
        "mid": 60,  # C4
        "high": 72,  # C5
        "very_high": 84,  # C6
    }

    def _to_midi(self, notes: list[Note]) -> bytes:
        """Convert notes to MIDI bytes."""
        exporter = MidiExporter()
        return exporter.export_sfx_bytes(notes, self.tempo)

    def coin_collect(self) -> bytes:
        """Generate coin collection sound.

        Classic ascending two-note blip.
        """
        notes = [
            Note(pitch=67, duration=0.0625, velocity=110),  # G4
            Note(pitch=72, duration=0.125, velocity=120),  # C5
        ]
        return self._to_midi(notes)

    def jump(self) -> bytes:
        """Generate jump sound.

        Quick ascending pitch sweep.
        """
        notes = []
        start_pitch = 48
        for i in range(6):
            notes.append(
                Note(
                    pitch=start_pitch + i * 4,
                    duration=0.03125,
                    velocity=100 - i * 10,
                )
            )
        return self._to_midi(notes)

    def land(self) -> bytes:
        """Generate landing sound.

        Short low thud.
        """
        notes = [
            Note(pitch=36, duration=0.0625, velocity=110),  # C2
            Note(pitch=36, duration=0.0625, velocity=80),
        ]
        return self._to_midi(notes)

    def explosion(self) -> bytes:
        """Generate explosion sound.

        Descending noise sweep with decay.
        """
        notes = []
        for i in range(8):
            # Simulate noise with rapid low pitches
            pitch = 36 - i * 2
            notes.append(
                Note(
                    pitch=max(24, pitch),
                    duration=0.0625,
                    velocity=max(40, 120 - i * 10),
                )
            )
        return self._to_midi(notes)

    def damage(self) -> bytes:
        """Generate damage/hurt sound.

        Quick dissonant burst.
        """
        notes = [
            Note(pitch=64, duration=0.0625, velocity=120),  # E4
            Note(pitch=60, duration=0.125, velocity=90),  # C4
        ]
        return self._to_midi(notes)

    def powerup(self) -> bytes:
        """Generate power-up sound.

        Ascending chromatic run with triumphant ending.
        """
        notes = []
        # Chromatic ascent
        for i in range(8):
            notes.append(
                Note(
                    pitch=60 + i,
                    duration=0.0625,
                    velocity=80 + i * 5,
                )
            )
        # Hold final note
        notes.append(Note(pitch=72, duration=0.25, velocity=120))
        return self._to_midi(notes)

    def menu_select(self) -> bytes:
        """Generate menu selection blip.

        Single short tone.
        """
        notes = [
            Note(pitch=67, duration=0.0625, velocity=80),  # G4
        ]
        return self._to_midi(notes)

    def menu_confirm(self) -> bytes:
        """Generate menu confirmation sound.

        Two-note ascending confirmation.
        """
        notes = [
            Note(pitch=60, duration=0.0625, velocity=90),  # C4
            Note(pitch=72, duration=0.125, velocity=100),  # C5
        ]
        return self._to_midi(notes)

    def menu_back(self) -> bytes:
        """Generate menu back/cancel sound.

        Two-note descending.
        """
        notes = [
            Note(pitch=67, duration=0.0625, velocity=80),  # G4
            Note(pitch=60, duration=0.0625, velocity=70),  # C4
        ]
        return self._to_midi(notes)

    def error(self) -> bytes:
        """Generate error/invalid action sound.

        Low buzzer tone.
        """
        notes = [
            Note(pitch=36, duration=0.125, velocity=100),  # C2
            Note(pitch=35, duration=0.125, velocity=90),  # B1
        ]
        return self._to_midi(notes)

    def success(self) -> bytes:
        """Generate success sound.

        Quick major arpeggio.
        """
        notes = [
            Note(pitch=60, duration=0.0625, velocity=100),  # C4
            Note(pitch=64, duration=0.0625, velocity=105),  # E4
            Note(pitch=67, duration=0.0625, velocity=110),  # G4
            Note(pitch=72, duration=0.125, velocity=120),  # C5
        ]
        return self._to_midi(notes)

    def door_open(self) -> bytes:
        """Generate door opening sound.

        Ascending sweep.
        """
        notes = []
        for i in range(4):
            notes.append(
                Note(
                    pitch=48 + i * 5,
                    duration=0.125,
                    velocity=80 + i * 10,
                )
            )
        return self._to_midi(notes)

    def door_close(self) -> bytes:
        """Generate door closing sound.

        Descending sweep.
        """
        notes = []
        for i in range(4):
            notes.append(
                Note(
                    pitch=60 - i * 5,
                    duration=0.125,
                    velocity=100 - i * 10,
                )
            )
        return self._to_midi(notes)

    def laser(self) -> bytes:
        """Generate laser/projectile sound.

        Quick descending zap.
        """
        notes = []
        for i in range(5):
            notes.append(
                Note(
                    pitch=84 - i * 6,
                    duration=0.03125,
                    velocity=120 - i * 15,
                )
            )
        return self._to_midi(notes)

    def shield(self) -> bytes:
        """Generate shield activation sound.

        Warbling tone.
        """
        notes = []
        for i in range(6):
            pitch = 72 if i % 2 == 0 else 76
            notes.append(Note(pitch=pitch, duration=0.0625, velocity=90))
        return self._to_midi(notes)

    def teleport(self) -> bytes:
        """Generate teleport sound.

        Ascending then descending sweep.
        """
        notes = []
        # Ascending
        for i in range(6):
            notes.append(Note(pitch=48 + i * 6, duration=0.03125, velocity=100))
        # Descending
        for i in range(6):
            notes.append(Note(pitch=84 - i * 6, duration=0.03125, velocity=100))
        return self._to_midi(notes)

    def heartbeat(self) -> bytes:
        """Generate heartbeat/tension sound.

        Two low thumps.
        """
        notes = [
            Note(pitch=36, duration=0.125, velocity=100),
            Note(pitch=36, duration=0.0625, velocity=80),
            Note(pitch=0, duration=0.25, velocity=0),  # Rest
            Note(pitch=36, duration=0.125, velocity=90),
            Note(pitch=36, duration=0.0625, velocity=70),
        ]
        return self._to_midi(notes)

    def countdown_tick(self) -> bytes:
        """Generate countdown tick sound.

        Single percussive click.
        """
        notes = [
            Note(pitch=80, duration=0.03125, velocity=100),
        ]
        return self._to_midi(notes)

    def countdown_final(self) -> bytes:
        """Generate final countdown sound.

        Dramatic final tick.
        """
        notes = [
            Note(pitch=48, duration=0.125, velocity=120),
            Note(pitch=60, duration=0.25, velocity=127),
        ]
        return self._to_midi(notes)

    def save(self, midi_bytes: bytes, path: str) -> None:
        """Save MIDI bytes to a file.

        Args:
            midi_bytes: MIDI data from any generator method
            path: Output file path
        """
        with open(path, "wb") as f:
            f.write(midi_bytes)
