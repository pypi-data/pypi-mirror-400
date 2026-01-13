"""Markov chain based music generation."""

from chiptune.generation.markov.chain import MarkovChain, WeightedMarkovChain
from chiptune.generation.markov.melody import MarkovMelodyGenerator, MelodyStyle

__all__ = [
    "MarkovChain",
    "WeightedMarkovChain",
    "MarkovMelodyGenerator",
    "MelodyStyle",
]
