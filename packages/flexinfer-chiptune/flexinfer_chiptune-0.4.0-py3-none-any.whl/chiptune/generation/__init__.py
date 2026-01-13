"""Procedural music generation for chiptune compositions.

This module provides algorithmic composition tools:

Markov Chains:
- MarkovChain: N-gram sequence generator
- MarkovMelodyGenerator: Melody generation from learned patterns
- MelodyStyle: Pre-trained style presets (heroic, mysterious, etc.)

Harmony:
- BassGenerator: Rule-based bass line generation
- BassPattern: Bass line patterns (root, walking, arpeggiated)

Adaptive:
- IntensityProfile: Dynamic intensity curves
- IntensityController: Map intensity to musical parameters

Example:
    from chiptune.generation import MelodyStyle, BassGenerator, IntensityController

    # Generate melody in heroic style
    style = MelodyStyle.heroic()
    melody = style.generator.generate(length=16, start_pitch=60)

    # Generate walking bass
    bass_gen = BassGenerator.jazz()
    bass = bass_gen.generate(chords, beats_per_chord=4)

    # Use intensity for dynamic music
    controller = IntensityController.action()
    tempo = controller.get_tempo(progress=0.5)
"""

from chiptune.generation.adaptive.intensity import (
    IntensityController,
    IntensityCurve,
    IntensityProfile,
)
from chiptune.generation.harmony.bass import (
    BassGenerator,
    BassPattern,
    BassRules,
)
from chiptune.generation.markov.chain import (
    MarkovChain,
    WeightedMarkovChain,
)
from chiptune.generation.markov.melody import (
    MarkovMelodyGenerator,
    MelodyStyle,
)

__all__ = [
    # Markov
    "MarkovChain",
    "WeightedMarkovChain",
    "MarkovMelodyGenerator",
    "MelodyStyle",
    # Harmony
    "BassGenerator",
    "BassPattern",
    "BassRules",
    # Adaptive
    "IntensityProfile",
    "IntensityCurve",
    "IntensityController",
]
