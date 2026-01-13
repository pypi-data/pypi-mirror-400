"""Rule-based harmony and bass generation."""

from chiptune.generation.harmony.bass import BassGenerator, BassPattern, BassRules
from chiptune.generation.harmony.countermelody import (
    CountermelodyGenerator,
    CountermelodyRules,
    HarmonyInterval,
    MotionType,
)

__all__ = [
    "BassGenerator",
    "BassPattern",
    "BassRules",
    "CountermelodyGenerator",
    "CountermelodyRules",
    "HarmonyInterval",
    "MotionType",
]
