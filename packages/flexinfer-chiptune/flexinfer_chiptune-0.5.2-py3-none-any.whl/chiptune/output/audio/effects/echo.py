"""Simple digital echo/delay effect.

A clean, CPU-efficient delay effect without tape modeling.
For analog tape character, use TapeDelay instead.
"""

import numpy as np
from numpy.typing import NDArray
from pydantic import Field

from chiptune.output.audio.effects.base import SampleEffect


class Echo(SampleEffect):
    """Clean digital echo effect.

    Simple delay with feedback - no tape artifacts, filtering, or modulation.
    Uses vectorized numpy operations for efficiency.

    Attributes:
        delay_time: Delay time in seconds
        feedback: Amount fed back (0.0 = single echo, 0.9 = long decay)
        mix: Wet/dry mix (0.0 = dry only, 1.0 = wet only)
        num_repeats: Maximum number of echo repeats to compute

    Example:
        echo = Echo(delay_time=0.25, feedback=0.5, mix=0.4)
        output = echo.process(samples)

        # Or use presets
        output = Echo.short().process(samples)
    """

    delay_time: float = Field(default=0.25, ge=0.01, le=2.0)
    feedback: float = Field(default=0.5, ge=0.0, le=0.95)
    mix: float = Field(default=0.4, ge=0.0, le=1.0)
    num_repeats: int = Field(default=8, ge=1, le=32)

    def process(
        self,
        samples: NDArray[np.float32],
        sample_rate: int = 44100,
    ) -> NDArray[np.float32]:
        """Apply echo effect using vectorized operations.

        Args:
            samples: Input audio samples
            sample_rate: Sample rate in Hz

        Returns:
            Audio with echo applied
        """
        if len(samples) == 0:
            return samples

        delay_samples = int(self.delay_time * sample_rate)
        if delay_samples == 0:
            return samples

        # Pre-compute all echoes at once (vectorized)
        wet = np.zeros_like(samples)
        current_level = 1.0

        for i in range(self.num_repeats):
            offset = delay_samples * (i + 1)
            current_level *= self.feedback

            # Stop if level is negligible
            if current_level < 0.001:
                break

            # Add delayed signal
            if offset < len(samples):
                wet[offset:] += samples[:-offset] * current_level

        # Mix dry and wet
        result = samples * (1 - self.mix) + wet * self.mix
        return result.astype(np.float32)

    @classmethod
    def short(cls) -> "Echo":
        """Short slapback-style echo."""
        return cls(
            delay_time=0.1,
            feedback=0.3,
            mix=0.35,
            num_repeats=4,
        )

    @classmethod
    def medium(cls) -> "Echo":
        """Medium echo with moderate decay."""
        return cls(
            delay_time=0.25,
            feedback=0.5,
            mix=0.4,
            num_repeats=8,
        )

    @classmethod
    def long(cls) -> "Echo":
        """Long echo with extended decay."""
        return cls(
            delay_time=0.4,
            feedback=0.65,
            mix=0.45,
            num_repeats=12,
        )

    @classmethod
    def rhythmic(cls, bpm: int = 120, subdivision: float = 0.5) -> "Echo":
        """Tempo-synced echo.

        Args:
            bpm: Tempo in beats per minute
            subdivision: Note subdivision (1.0 = quarter, 0.5 = eighth, etc.)

        Returns:
            Echo timed to the beat
        """
        beat_duration = 60.0 / bpm
        delay = beat_duration * subdivision
        return cls(
            delay_time=min(delay, 2.0),  # Cap at max delay
            feedback=0.45,
            mix=0.4,
            num_repeats=8,
        )

    @classmethod
    def subtle(cls) -> "Echo":
        """Subtle depth-adding echo."""
        return cls(
            delay_time=0.15,
            feedback=0.25,
            mix=0.25,
            num_repeats=4,
        )

    @classmethod
    def cavernous(cls) -> "Echo":
        """Large space echo effect."""
        return cls(
            delay_time=0.6,
            feedback=0.7,
            mix=0.5,
            num_repeats=16,
        )
