"""Chord progression builder for game music contexts."""

from __future__ import annotations

from enum import Enum
from typing import ClassVar

from pydantic import BaseModel

from chiptune.theory.chords import Chord, ChordProgression
from chiptune.theory.keys import Key, Mode


class ProgressionMood(str, Enum):
    """Emotional character of a progression."""

    TRIUMPHANT = "triumphant"
    HEROIC = "heroic"
    ADVENTUROUS = "adventurous"
    MYSTERIOUS = "mysterious"
    TENSE = "tense"
    PEACEFUL = "peaceful"
    MELANCHOLY = "melancholy"
    EPIC = "epic"
    DANGER = "danger"
    RESOLUTION = "resolution"


class ProgressionBuilder(BaseModel):
    """Fluent builder for creating chord progressions.

    Allows building progressions step-by-step with game-music
    specific vocabulary.
    """

    key: Key
    numerals: list[str] = []
    beats_per_chord: list[int] = []

    # Mood to progression mapping
    MOOD_PROGRESSIONS: ClassVar[dict[ProgressionMood, list[str]]] = {
        ProgressionMood.TRIUMPHANT: ["I", "IV", "V", "I"],
        ProgressionMood.HEROIC: ["I", "V", "vi", "IV"],
        ProgressionMood.ADVENTUROUS: ["I", "V", "vi", "iii", "IV", "I", "IV", "V"],
        ProgressionMood.MYSTERIOUS: ["i", "bVII", "bVI", "V"],
        ProgressionMood.TENSE: ["i", "bII", "V", "i"],
        ProgressionMood.PEACEFUL: ["I", "vi", "IV", "V"],
        ProgressionMood.MELANCHOLY: ["vi", "IV", "I", "V"],
        ProgressionMood.EPIC: ["I", "IV", "I", "V", "I", "IV", "V", "I"],
        ProgressionMood.DANGER: ["i", "bVI", "bVII", "i"],
        ProgressionMood.RESOLUTION: ["V", "I"],
    }

    # Game context progressions
    GAME_PROGRESSIONS: ClassVar[dict[str, list[str]]] = {
        "title_screen": ["I", "V", "vi", "IV"],
        "overworld": ["I", "IV", "V", "I"],
        "battle": ["i", "bVII", "bVI", "V"],
        "boss": ["i", "iv", "V", "i"],
        "victory": ["I", "IV", "V", "I"],
        "game_over": ["i", "iv", "bVI", "V"],
        "shop": ["I", "vi", "IV", "V"],
        "dungeon": ["i", "bVII", "iv", "i"],
        "puzzle": ["I", "II", "IV", "I"],
        "cutscene": ["i", "bVI", "bVII", "i"],
        "credits": ["I", "vi", "ii", "V"],
    }

    @classmethod
    def in_key(cls, root: str = "C", mode: Mode = Mode.IONIAN) -> ProgressionBuilder:
        """Start building a progression in the specified key.

        Args:
            root: Root note
            mode: Musical mode

        Returns:
            New ProgressionBuilder instance
        """
        return cls(key=Key(root=root, mode=mode))

    @classmethod
    def from_mood(
        cls,
        mood: ProgressionMood,
        root: str = "C",
    ) -> ProgressionBuilder:
        """Create a progression from an emotional mood.

        Args:
            mood: The emotional character
            root: Root note

        Returns:
            ProgressionBuilder with preset progression
        """
        numerals = cls.MOOD_PROGRESSIONS.get(mood, ["I", "IV", "V", "I"])

        # Determine mode from progression
        is_minor = any(n.islower() for n in numerals if n.replace("b", "").isalpha())
        mode = Mode.AEOLIAN if is_minor else Mode.IONIAN

        return cls(
            key=Key(root=root, mode=mode),
            numerals=numerals,
            beats_per_chord=[4] * len(numerals),
        )

    @classmethod
    def for_context(
        cls,
        context: str,
        root: str = "C",
    ) -> ProgressionBuilder:
        """Create a progression for a game context.

        Args:
            context: Game context (e.g., "battle", "shop")
            root: Root note

        Returns:
            ProgressionBuilder with context-appropriate progression
        """
        numerals = cls.GAME_PROGRESSIONS.get(
            context.lower().replace(" ", "_"),
            ["I", "IV", "V", "I"],
        )

        is_minor = any(n.islower() for n in numerals if n.replace("b", "").isalpha())
        mode = Mode.AEOLIAN if is_minor else Mode.IONIAN

        return cls(
            key=Key(root=root, mode=mode),
            numerals=numerals,
            beats_per_chord=[4] * len(numerals),
        )

    def add(self, numeral: str, beats: int = 4) -> ProgressionBuilder:
        """Add a chord to the progression.

        Args:
            numeral: Roman numeral (e.g., "I", "iv", "bVII")
            beats: Duration in beats

        Returns:
            Self for chaining
        """
        new_numerals = self.numerals + [numeral]
        new_beats = self.beats_per_chord + [beats]
        return self.model_copy(update={"numerals": new_numerals, "beats_per_chord": new_beats})

    def add_tonic(self, beats: int = 4) -> ProgressionBuilder:
        """Add tonic chord (I or i)."""
        numeral = "i" if self.key.mode in (Mode.AEOLIAN, Mode.DORIAN, Mode.PHRYGIAN) else "I"
        return self.add(numeral, beats)

    def add_subdominant(self, beats: int = 4) -> ProgressionBuilder:
        """Add subdominant chord (IV or iv)."""
        numeral = "iv" if self.key.mode in (Mode.AEOLIAN, Mode.DORIAN, Mode.PHRYGIAN) else "IV"
        return self.add(numeral, beats)

    def add_dominant(self, beats: int = 4) -> ProgressionBuilder:
        """Add dominant chord (V)."""
        return self.add("V", beats)

    def add_relative_minor(self, beats: int = 4) -> ProgressionBuilder:
        """Add relative minor chord (vi)."""
        return self.add("vi", beats)

    def add_tension(self, beats: int = 4) -> ProgressionBuilder:
        """Add a tension chord (bVII or bII)."""
        return self.add("bVII", beats)

    def resolve(self, beats: int = 4) -> ProgressionBuilder:
        """Add V-I resolution."""
        return self.add("V", beats // 2).add_tonic(beats - beats // 2)

    def turnaround(self) -> ProgressionBuilder:
        """Add a classic turnaround (I-vi-IV-V or i-bVI-iv-V)."""
        if self.key.mode in (Mode.AEOLIAN, Mode.DORIAN, Mode.PHRYGIAN):
            return self.add("i", 4).add("bVI", 4).add("iv", 4).add("V", 4)
        else:
            return self.add("I", 4).add("vi", 4).add("IV", 4).add("V", 4)

    def repeat(self, times: int = 2) -> ProgressionBuilder:
        """Repeat the current progression.

        Args:
            times: Number of total repetitions (including original)

        Returns:
            ProgressionBuilder with repeated progression
        """
        return self.model_copy(
            update={
                "numerals": self.numerals * times,
                "beats_per_chord": self.beats_per_chord * times,
            }
        )

    def transpose(self, semitones: int) -> ProgressionBuilder:
        """Transpose to a different key.

        Args:
            semitones: Number of semitones to transpose

        Returns:
            ProgressionBuilder in new key
        """
        new_key = self.key.transpose(semitones)
        return self.model_copy(update={"key": new_key})

    def build(self) -> ChordProgression:
        """Build the final ChordProgression.

        Returns:
            ChordProgression instance
        """
        return ChordProgression(key=self.key, numerals=self.numerals)

    def get_chords(self) -> list[Chord]:
        """Get the chord objects for this progression.

        Returns:
            List of Chord instances
        """
        return self.build().get_chords()

    @property
    def total_beats(self) -> int:
        """Total duration in beats."""
        return sum(self.beats_per_chord) if self.beats_per_chord else 0


class ProgressionVariation(BaseModel):
    """Applies variations to chord progressions for interest."""

    base: ProgressionBuilder

    def with_substitution(self, original: str, substitute: str) -> ProgressionBuilder:
        """Replace a chord with a substitute.

        Common substitutions:
        - IV → ii (subdominant)
        - V → vii° (dominant)
        - I → vi (tonic)
        """
        new_numerals = [substitute if n == original else n for n in self.base.numerals]
        return self.base.model_copy(update={"numerals": new_numerals})

    def with_borrowed_chord(self, position: int, numeral: str) -> ProgressionBuilder:
        """Insert a borrowed chord (modal interchange).

        Args:
            position: Index in progression
            numeral: Borrowed chord numeral (e.g., "bVI" in major)
        """
        new_numerals = self.base.numerals.copy()
        if 0 <= position < len(new_numerals):
            new_numerals[position] = numeral
        return self.base.model_copy(update={"numerals": new_numerals})

    def with_passing_chord(self, position: int, passing: str) -> ProgressionBuilder:
        """Insert a passing chord between two chords.

        Args:
            position: Insert after this index
            passing: The passing chord numeral
        """
        new_numerals = self.base.numerals.copy()
        new_beats = self.base.beats_per_chord.copy()

        if 0 <= position < len(new_numerals):
            # Split the beats
            original_beats = new_beats[position]
            new_beats[position] = original_beats // 2
            new_numerals.insert(position + 1, passing)
            new_beats.insert(position + 1, original_beats - original_beats // 2)

        return self.base.model_copy(update={"numerals": new_numerals, "beats_per_chord": new_beats})
