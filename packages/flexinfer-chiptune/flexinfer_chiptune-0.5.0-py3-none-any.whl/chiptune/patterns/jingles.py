"""Short musical jingles for game events."""

from __future__ import annotations

from enum import Enum
from typing import ClassVar

from pydantic import BaseModel

from chiptune.theory.arpeggios import Note
from chiptune.theory.keys import Key, Mode


class JingleType(str, Enum):
    """Common game event jingles."""

    VICTORY_FANFARE = "victory"
    ITEM_GET = "item"
    LEVEL_UP = "level_up"
    COIN_COLLECT = "coin"
    SECRET_FOUND = "secret"
    DANGER_WARNING = "danger"
    GAME_OVER = "game_over"
    MENU_SELECT = "menu_select"
    MENU_CONFIRM = "menu_confirm"
    QUEST_COMPLETE = "quest_complete"
    POWER_UP = "power_up"
    DAMAGE = "damage"


class Jingle(BaseModel):
    """A short musical phrase for game events.

    Jingles are typically 2-8 beats and designed to be
    instantly recognizable and emotionally resonant.
    """

    jingle_type: JingleType
    key: Key
    notes: list[Note]
    tempo: int = 120

    # Jingle templates: (scale_degrees, durations, velocities)
    # Scale degrees are 1-indexed (1 = root, 3 = third, 5 = fifth, 8 = octave)
    TEMPLATES: ClassVar[dict[JingleType, dict]] = {
        JingleType.VICTORY_FANFARE: {
            "degrees": [1, 3, 5, 8, 8, 5, 8],
            "durations": [0.25, 0.25, 0.25, 0.5, 0.25, 0.25, 1.0],
            "velocities": [100, 100, 110, 120, 100, 100, 127],
            "mode": Mode.IONIAN,
        },
        JingleType.ITEM_GET: {
            "degrees": [1, 3, 5, 8],
            "durations": [0.125, 0.125, 0.125, 0.5],
            "velocities": [90, 100, 110, 120],
            "mode": Mode.IONIAN,
        },
        JingleType.LEVEL_UP: {
            "degrees": [1, 2, 3, 4, 5, 6, 7, 8],
            "durations": [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.75],
            "velocities": [80, 85, 90, 95, 100, 105, 110, 127],
            "mode": Mode.LYDIAN,
        },
        JingleType.COIN_COLLECT: {
            "degrees": [5, 8],
            "durations": [0.0625, 0.25],
            "velocities": [100, 110],
            "mode": Mode.IONIAN,
        },
        JingleType.SECRET_FOUND: {
            "degrees": [1, 4, 1, 5, 1, 8],
            "durations": [0.25, 0.25, 0.25, 0.25, 0.25, 0.75],
            "velocities": [90, 95, 100, 105, 110, 120],
            "mode": Mode.LYDIAN,
        },
        JingleType.DANGER_WARNING: {
            "degrees": [5, 4, 3, 2, 1],
            "durations": [0.25, 0.25, 0.25, 0.25, 0.5],
            "velocities": [110, 105, 100, 95, 90],
            "mode": Mode.PHRYGIAN,
        },
        JingleType.GAME_OVER: {
            "degrees": [5, 4, 3, 2, 1],
            "durations": [0.5, 0.5, 0.5, 0.5, 1.5],
            "velocities": [100, 90, 80, 70, 60],
            "mode": Mode.AEOLIAN,
        },
        JingleType.MENU_SELECT: {
            "degrees": [5],
            "durations": [0.125],
            "velocities": [80],
            "mode": Mode.IONIAN,
        },
        JingleType.MENU_CONFIRM: {
            "degrees": [1, 5],
            "durations": [0.125, 0.25],
            "velocities": [90, 100],
            "mode": Mode.IONIAN,
        },
        JingleType.QUEST_COMPLETE: {
            "degrees": [1, 3, 5, 3, 5, 8, 5, 8],
            "durations": [0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.75],
            "velocities": [90, 95, 100, 95, 105, 110, 105, 127],
            "mode": Mode.IONIAN,
        },
        JingleType.POWER_UP: {
            "degrees": [1, 1, 3, 3, 5, 5, 8],
            "durations": [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.5],
            "velocities": [100, 100, 105, 105, 110, 110, 127],
            "mode": Mode.IONIAN,
        },
        JingleType.DAMAGE: {
            "degrees": [3, 1],
            "durations": [0.125, 0.25],
            "velocities": [120, 100],
            "mode": Mode.AEOLIAN,
        },
    }

    @classmethod
    def create(
        cls,
        jingle_type: JingleType,
        root: str = "C",
        octave: int = 5,
        tempo: int = 120,
    ) -> Jingle:
        """Create a jingle of the specified type.

        Args:
            jingle_type: The type of jingle to create
            root: Root note for the key
            octave: Base octave for the jingle
            tempo: Tempo in BPM

        Returns:
            Jingle instance with generated notes
        """
        template = cls.TEMPLATES[jingle_type]

        key = Key(root=root, mode=template["mode"])
        notes = cls._generate_notes(
            key=key,
            degrees=template["degrees"],
            durations=template["durations"],
            velocities=template["velocities"],
            octave=octave,
        )

        return cls(
            jingle_type=jingle_type,
            key=key,
            notes=notes,
            tempo=tempo,
        )

    @classmethod
    def _generate_notes(
        cls,
        key: Key,
        degrees: list[int],
        durations: list[float],
        velocities: list[int],
        octave: int,
    ) -> list[Note]:
        """Generate Note objects from scale degrees.

        Args:
            key: Musical key
            degrees: Scale degrees (1-indexed)
            durations: Note durations in beats
            velocities: MIDI velocities
            octave: Base octave

        Returns:
            List of Note objects
        """
        from chiptune.theory.scales import Scale

        scale = Scale.from_key(key)
        notes = []

        for degree, duration, velocity in zip(degrees, durations, velocities, strict=False):
            pitch = scale.degree_to_pitch(degree, octave=octave)
            notes.append(
                Note(
                    pitch=pitch,
                    duration=duration,
                    velocity=velocity,
                )
            )

        return notes

    @classmethod
    def victory_fanfare(cls, root: str = "C", tempo: int = 140) -> Jingle:
        """Create a victory fanfare jingle.

        Classic I-IV-V-I progression feel with ascending arpeggio.
        """
        return cls.create(JingleType.VICTORY_FANFARE, root=root, tempo=tempo)

    @classmethod
    def item_get(cls, root: str = "C", tempo: int = 160) -> Jingle:
        """Create an item pickup jingle.

        Quick ascending arpeggio, satisfying and short.
        """
        return cls.create(JingleType.ITEM_GET, root=root, tempo=tempo)

    @classmethod
    def level_up(cls, root: str = "C", tempo: int = 150) -> Jingle:
        """Create a level-up jingle.

        Full scale run with triumphant ending.
        """
        return cls.create(JingleType.LEVEL_UP, root=root, tempo=tempo)

    @classmethod
    def coin_collect(cls, root: str = "C", tempo: int = 180) -> Jingle:
        """Create a coin collection jingle.

        Two-note ascending blip, very short.
        """
        return cls.create(JingleType.COIN_COLLECT, root=root, tempo=tempo)

    @classmethod
    def danger_warning(cls, root: str = "C", tempo: int = 100) -> Jingle:
        """Create a danger warning jingle.

        Descending chromatic-feeling phrase in Phrygian mode.
        """
        return cls.create(JingleType.DANGER_WARNING, root=root, tempo=tempo)

    @classmethod
    def game_over(cls, root: str = "C", tempo: int = 70) -> Jingle:
        """Create a game over jingle.

        Slow, sad descending phrase.
        """
        return cls.create(JingleType.GAME_OVER, root=root, tempo=tempo)

    def transpose(self, semitones: int) -> Jingle:
        """Transpose the jingle to a different key.

        Args:
            semitones: Number of semitones to transpose

        Returns:
            New Jingle in transposed key
        """
        new_key = self.key.transpose(semitones)
        new_notes = [note.transpose(semitones) for note in self.notes]
        return Jingle(
            jingle_type=self.jingle_type,
            key=new_key,
            notes=new_notes,
            tempo=self.tempo,
        )

    def with_tempo(self, tempo: int) -> Jingle:
        """Create a copy with different tempo.

        Args:
            tempo: New tempo in BPM

        Returns:
            New Jingle with updated tempo
        """
        return self.model_copy(update={"tempo": tempo})

    @property
    def duration_beats(self) -> float:
        """Total duration of the jingle in beats."""
        return sum(note.duration for note in self.notes)

    @property
    def duration_seconds(self) -> float:
        """Total duration of the jingle in seconds."""
        beats_per_second = self.tempo / 60.0
        return self.duration_beats / beats_per_second


class JingleSequence(BaseModel):
    """A sequence of jingles for complex events."""

    jingles: list[Jingle]
    gap_beats: float = 0.25  # Gap between jingles

    def all_notes(self) -> list[Note]:
        """Flatten all jingles into a single note sequence.

        Includes rest notes for gaps.
        """
        all_notes: list[Note] = []

        for i, jingle in enumerate(self.jingles):
            all_notes.extend(jingle.notes)

            # Add gap (rest) between jingles
            if i < len(self.jingles) - 1 and self.gap_beats > 0:
                # Rest represented as velocity 0
                all_notes.append(Note(pitch=0, duration=self.gap_beats, velocity=0))

        return all_notes

    @property
    def total_duration_beats(self) -> float:
        """Total duration including gaps."""
        jingle_duration = sum(j.duration_beats for j in self.jingles)
        gap_duration = self.gap_beats * max(0, len(self.jingles) - 1)
        return jingle_duration + gap_duration
