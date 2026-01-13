"""Tremolo effect - amplitude modulation."""

import numpy as np
from numpy.typing import NDArray
from pydantic import Field

from chiptune.output.audio.effects.base import SampleEffect
from chiptune.output.audio.effects.lfo import LFO, LFOShape


class Tremolo(SampleEffect):
    """Tremolo effect using LFO amplitude modulation.

    Tremolo creates a "wobbling" volume effect by modulating
    the amplitude of the signal with an LFO.

    Attributes:
        rate: Tremolo speed in Hz (typical: 2-10 Hz)
        depth: Modulation depth (0.0 = no effect, 1.0 = full mute at troughs)
        shape: LFO waveform shape
    """

    rate: float = Field(default=5.0, ge=0.1, le=20.0)
    depth: float = Field(default=0.5, ge=0.0, le=1.0)
    shape: LFOShape = LFOShape.SINE

    def process(
        self,
        samples: NDArray[np.float32],
        sample_rate: int = 44100,
    ) -> NDArray[np.float32]:
        """Apply tremolo to audio samples.

        Args:
            samples: Input audio samples
            sample_rate: Sample rate in Hz

        Returns:
            Amplitude-modulated audio samples
        """
        if len(samples) == 0:
            return samples

        # Generate LFO
        lfo = LFO(rate=self.rate, depth=self.depth, shape=self.shape)
        modulation = lfo.generate(len(samples), sample_rate)

        # Convert bipolar LFO (-depth to +depth) to amplitude multiplier
        # When LFO is at -depth, amplitude = 1.0 - depth (quiet)
        # When LFO is at +depth, amplitude = 1.0 (full volume)
        amplitude = 1.0 - (self.depth - modulation) / 2

        return (samples * amplitude).astype(np.float32)

    @classmethod
    def subtle(cls) -> "Tremolo":
        """Subtle, slow tremolo."""
        return cls(rate=3.0, depth=0.2)

    @classmethod
    def classic(cls) -> "Tremolo":
        """Classic vintage tremolo."""
        return cls(rate=5.0, depth=0.5, shape=LFOShape.SINE)

    @classmethod
    def hard(cls) -> "Tremolo":
        """Hard, choppy tremolo."""
        return cls(rate=8.0, depth=0.8, shape=LFOShape.SQUARE)

    @classmethod
    def helicopter(cls) -> "Tremolo":
        """Fast helicopter-like tremolo."""
        return cls(rate=15.0, depth=0.9, shape=LFOShape.SQUARE)
