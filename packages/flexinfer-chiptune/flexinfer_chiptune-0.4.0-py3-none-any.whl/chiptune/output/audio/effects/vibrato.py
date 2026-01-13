"""Vibrato effect - pitch modulation."""

import numpy as np
from numpy.typing import NDArray
from pydantic import Field

from chiptune.output.audio.effects.base import PitchEffect, SampleEffect
from chiptune.output.audio.effects.lfo import LFO, LFOShape


class Vibrato(PitchEffect):
    """Vibrato effect using LFO pitch modulation.

    Vibrato creates pitch variation by modulating frequency with an LFO.
    This version operates on frequency values before waveform generation.

    Attributes:
        rate: Vibrato speed in Hz (typical: 4-7 Hz)
        depth: Pitch deviation in semitones (typical: 0.1-0.5)
        delay: Time before vibrato starts (lets note attack be stable)
        shape: LFO waveform shape
    """

    rate: float = Field(default=5.0, ge=0.1, le=20.0)
    depth: float = Field(default=0.3, ge=0.0, le=2.0)  # semitones
    delay: float = Field(default=0.1, ge=0.0, le=2.0)  # seconds
    shape: LFOShape = LFOShape.SINE

    def modulate_frequency(
        self,
        base_frequency: float,
        time_array: NDArray[np.float32],
        sample_rate: int = 44100,
    ) -> NDArray[np.float32]:
        """Generate pitch-modulated frequency values.

        Args:
            base_frequency: Base note frequency in Hz
            time_array: Time values for each sample
            sample_rate: Sample rate in Hz

        Returns:
            Array of frequency values with vibrato applied
        """
        if len(time_array) == 0:
            return np.array([], dtype=np.float32)

        # Generate LFO for pitch modulation
        lfo = LFO(
            rate=self.rate,
            depth=1.0,  # Full swing, we scale by semitones
            shape=self.shape,
            delay=self.delay,
        )
        modulation = lfo.generate(len(time_array), sample_rate)

        # Convert semitone deviation to frequency multiplier
        # Each semitone is 2^(1/12) ratio
        semitone_mod = modulation * self.depth
        freq_multiplier = 2.0 ** (semitone_mod / 12.0)

        return (base_frequency * freq_multiplier).astype(np.float32)

    @classmethod
    def subtle(cls) -> "Vibrato":
        """Subtle, natural vibrato."""
        return cls(rate=5.0, depth=0.15, delay=0.15)

    @classmethod
    def classic(cls) -> "Vibrato":
        """Classic vocal/string vibrato."""
        return cls(rate=5.5, depth=0.3, delay=0.1)

    @classmethod
    def wide(cls) -> "Vibrato":
        """Wide, expressive vibrato."""
        return cls(rate=4.5, depth=0.5, delay=0.08)

    @classmethod
    def fast(cls) -> "Vibrato":
        """Fast, nervous vibrato."""
        return cls(rate=8.0, depth=0.2, delay=0.05)


class VibratoSample(SampleEffect):
    """Sample-based vibrato using variable delay modulation.

    This version operates on audio samples directly using a modulated
    delay line. It's useful for adding vibrato after waveform generation.

    Note: This uses resampling and may introduce slight artifacts.
    For cleaner results, use the Vibrato class with frequency modulation.
    """

    rate: float = Field(default=5.0, ge=0.1, le=20.0)
    depth: float = Field(default=0.003, ge=0.0, le=0.01)  # max delay in seconds
    shape: LFOShape = LFOShape.SINE

    def process(
        self,
        samples: NDArray[np.float32],
        sample_rate: int = 44100,
    ) -> NDArray[np.float32]:
        """Apply vibrato using modulated delay.

        Args:
            samples: Input audio samples
            sample_rate: Sample rate in Hz

        Returns:
            Pitch-modulated audio samples
        """
        if len(samples) == 0:
            return samples

        # Generate LFO for delay modulation
        lfo = LFO(rate=self.rate, depth=1.0, shape=self.shape)
        modulation = lfo.generate_unipolar(len(samples), sample_rate)

        # Convert to delay in samples
        max_delay_samples = int(self.depth * sample_rate)
        delay_samples = (modulation * max_delay_samples).astype(np.int32)

        # Create output with modulated delay (simplified approach)
        output = np.zeros_like(samples)
        indices = np.arange(len(samples))
        read_indices = indices - delay_samples

        # Clamp indices to valid range
        read_indices = np.clip(read_indices, 0, len(samples) - 1)
        output = samples[read_indices]

        return output.astype(np.float32)
