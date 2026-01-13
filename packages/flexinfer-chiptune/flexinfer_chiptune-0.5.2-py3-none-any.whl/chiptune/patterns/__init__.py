"""Game music patterns and templates."""

from chiptune.patterns.jingles import Jingle, JingleSequence, JingleType
from chiptune.patterns.progressions import (
    ProgressionBuilder,
    ProgressionMood,
    ProgressionVariation,
)
from chiptune.patterns.themes import GameTheme, MelodicContour, ThemeTemplate

__all__ = [
    "GameTheme",
    "ThemeTemplate",
    "MelodicContour",
    "Jingle",
    "JingleType",
    "JingleSequence",
    "ProgressionBuilder",
    "ProgressionMood",
    "ProgressionVariation",
]
