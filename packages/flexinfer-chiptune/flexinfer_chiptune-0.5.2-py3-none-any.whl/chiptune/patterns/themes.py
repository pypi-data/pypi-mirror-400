"""Game music theme templates and patterns."""

from __future__ import annotations

from enum import Enum
from typing import Any, ClassVar

from pydantic import BaseModel

from chiptune.theory.chords import ChordProgression
from chiptune.theory.keys import Key, Mode


class GameTheme(str, Enum):
    """Common game music contexts/themes."""

    TITLE_SCREEN = "title"
    OVERWORLD = "overworld"
    BATTLE = "battle"
    BOSS = "boss"
    VICTORY = "victory"
    GAME_OVER = "game_over"
    SHOP = "shop"
    DUNGEON = "dungeon"
    PUZZLE = "puzzle"
    CREDITS = "credits"
    MENU = "menu"
    CUTSCENE = "cutscene"


class MelodicContour(str, Enum):
    """Melodic shape patterns."""

    ARCH = "arch"  # Rise then fall
    DESCENDING = "descending"  # Generally falling
    ASCENDING = "ascending"  # Generally rising
    WAVE = "wave"  # Oscillating
    FLAT = "flat"  # Minimal movement
    PEAK = "peak"  # Quick rise to climax
    TROUGH = "trough"  # Dip then return


class ThemeTemplate(BaseModel):
    """Template for generating themed music.

    Encapsulates the musical characteristics appropriate
    for different game contexts.
    """

    theme: GameTheme
    tempo: int
    key: Key
    time_signature: tuple[int, int] = (4, 4)
    chord_progression: list[str]
    melodic_contour: MelodicContour
    intensity: float = 0.5  # 0.0 = calm, 1.0 = intense
    loop_friendly: bool = True

    # Theme-specific default configurations
    THEME_CONFIGS: ClassVar[dict[GameTheme, dict[str, Any]]] = {
        GameTheme.TITLE_SCREEN: {
            "tempo": 110,
            "mode": Mode.IONIAN,
            "progression": ["I", "V", "vi", "IV"],
            "contour": MelodicContour.ARCH,
            "intensity": 0.6,
        },
        GameTheme.OVERWORLD: {
            "tempo": 120,
            "mode": Mode.IONIAN,
            "progression": ["I", "IV", "V", "I"],
            "contour": MelodicContour.WAVE,
            "intensity": 0.5,
        },
        GameTheme.BATTLE: {
            "tempo": 150,
            "mode": Mode.AEOLIAN,
            "progression": ["i", "bVII", "bVI", "V"],
            "contour": MelodicContour.ASCENDING,
            "intensity": 0.8,
        },
        GameTheme.BOSS: {
            "tempo": 140,
            "mode": Mode.PHRYGIAN,
            "progression": ["i", "bII", "V", "i"],
            "contour": MelodicContour.PEAK,
            "intensity": 0.95,
        },
        GameTheme.VICTORY: {
            "tempo": 130,
            "mode": Mode.IONIAN,
            "progression": ["I", "IV", "V", "I"],
            "contour": MelodicContour.ASCENDING,
            "intensity": 0.9,
        },
        GameTheme.GAME_OVER: {
            "tempo": 70,
            "mode": Mode.AEOLIAN,
            "progression": ["i", "iv", "bVI", "V"],
            "contour": MelodicContour.DESCENDING,
            "intensity": 0.3,
        },
        GameTheme.SHOP: {
            "tempo": 100,
            "mode": Mode.IONIAN,
            "progression": ["I", "vi", "IV", "V"],
            "contour": MelodicContour.WAVE,
            "intensity": 0.4,
        },
        GameTheme.DUNGEON: {
            "tempo": 90,
            "mode": Mode.DORIAN,
            "progression": ["i", "bVII", "iv", "i"],
            "contour": MelodicContour.FLAT,
            "intensity": 0.5,
        },
        GameTheme.PUZZLE: {
            "tempo": 95,
            "mode": Mode.LYDIAN,
            "progression": ["I", "II", "IV", "I"],
            "contour": MelodicContour.WAVE,
            "intensity": 0.4,
        },
        GameTheme.CREDITS: {
            "tempo": 85,
            "mode": Mode.IONIAN,
            "progression": ["I", "vi", "ii", "V"],
            "contour": MelodicContour.ARCH,
            "intensity": 0.5,
        },
        GameTheme.MENU: {
            "tempo": 100,
            "mode": Mode.IONIAN,
            "progression": ["I", "IV", "I", "V"],
            "contour": MelodicContour.FLAT,
            "intensity": 0.3,
        },
        GameTheme.CUTSCENE: {
            "tempo": 80,
            "mode": Mode.DORIAN,
            "progression": ["i", "bVI", "bVII", "i"],
            "contour": MelodicContour.ARCH,
            "intensity": 0.5,
        },
    }

    @classmethod
    def for_theme(cls, theme: GameTheme, root: str = "C") -> ThemeTemplate:
        """Create a template for a specific game theme.

        Args:
            theme: The game context/theme
            root: Root note for the key

        Returns:
            ThemeTemplate configured for the theme
        """
        config = cls.THEME_CONFIGS.get(theme, cls.THEME_CONFIGS[GameTheme.OVERWORLD])

        key = Key(root=root, mode=config["mode"])

        return cls(
            theme=theme,
            tempo=config["tempo"],
            key=key,
            chord_progression=config["progression"],
            melodic_contour=config["contour"],
            intensity=config["intensity"],
        )

    def get_progression(self) -> ChordProgression:
        """Get the chord progression for this theme."""
        return ChordProgression(key=self.key, numerals=self.chord_progression)

    def with_intensity(self, intensity: float) -> ThemeTemplate:
        """Create a copy with adjusted intensity.

        Intensity affects tempo and other parameters.
        """
        # Scale tempo based on intensity difference
        base_tempo = self.THEME_CONFIGS[self.theme]["tempo"]
        tempo_range = 30  # +/- 15 bpm from base
        adjusted_tempo = int(base_tempo + (intensity - 0.5) * tempo_range)

        return self.model_copy(update={"intensity": intensity, "tempo": adjusted_tempo})

    def transpose(self, semitones: int) -> ThemeTemplate:
        """Transpose the template to a different key."""
        new_key = self.key.transpose(semitones)
        return self.model_copy(update={"key": new_key})
