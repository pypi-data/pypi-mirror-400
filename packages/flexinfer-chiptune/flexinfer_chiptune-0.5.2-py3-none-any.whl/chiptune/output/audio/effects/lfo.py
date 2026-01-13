"""Low Frequency Oscillator for modulation effects."""

from enum import Enum

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, Field


class LFOShape(str, Enum):
    """LFO waveform shapes."""

    SINE = "sine"
    TRIANGLE = "triangle"
    SQUARE = "square"
    SAW_UP = "saw_up"
    SAW_DOWN = "saw_down"
    SAMPLE_HOLD = "sample_hold"


class LFO(BaseModel):
    """Low Frequency Oscillator for modulation.

    LFOs generate slow oscillations used to modulate other parameters
    like pitch (vibrato), amplitude (tremolo), or filter cutoff.

    Attributes:
        rate: Oscillation frequency in Hz (typically 0.1 to 20 Hz)
        depth: Modulation depth (0.0 to 1.0)
        shape: Waveform shape
        phase: Initial phase offset (0.0 to 1.0)
        delay: Delay before LFO starts in seconds
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    rate: float = Field(default=5.0, ge=0.01, le=50.0)
    depth: float = Field(default=1.0, ge=0.0, le=1.0)
    shape: LFOShape = LFOShape.SINE
    phase: float = Field(default=0.0, ge=0.0, le=1.0)
    delay: float = Field(default=0.0, ge=0.0)

    def generate(
        self,
        num_samples: int,
        sample_rate: int = 44100,
    ) -> NDArray[np.float32]:
        """Generate LFO waveform.

        Args:
            num_samples: Number of samples to generate
            sample_rate: Sample rate in Hz

        Returns:
            LFO values ranging from -depth to +depth
        """
        if num_samples == 0:
            return np.array([], dtype=np.float32)

        # Time array
        t = np.arange(num_samples, dtype=np.float32) / sample_rate

        # Calculate phase with initial offset
        phase = (t * self.rate + self.phase) % 1.0

        # Generate waveform based on shape
        if self.shape == LFOShape.SINE:
            wave = np.sin(2 * np.pi * phase)
        elif self.shape == LFOShape.TRIANGLE:
            # Triangle: 0->1->0->-1->0
            wave = 2 * np.abs(2 * phase - 1) - 1
        elif self.shape == LFOShape.SQUARE:
            wave = np.where(phase < 0.5, 1.0, -1.0)
        elif self.shape == LFOShape.SAW_UP:
            wave = 2 * phase - 1
        elif self.shape == LFOShape.SAW_DOWN:
            wave = 1 - 2 * phase
        elif self.shape == LFOShape.SAMPLE_HOLD:
            # Sample and hold: random value held for each cycle
            cycle_idx = (t * self.rate).astype(np.int32)
            unique_cycles = np.unique(cycle_idx)
            random_values = np.random.default_rng(42).uniform(-1, 1, len(unique_cycles))
            wave = random_values[np.searchsorted(unique_cycles, cycle_idx)]
        else:
            wave = np.sin(2 * np.pi * phase)

        # Apply depth
        output = wave.astype(np.float32) * self.depth

        # Apply delay (fade in from 0)
        if self.delay > 0:
            delay_samples = int(self.delay * sample_rate)
            if delay_samples < num_samples:
                # Linear fade-in over delay period
                fade_in = np.minimum(np.arange(num_samples) / delay_samples, 1.0)
                output = output * fade_in.astype(np.float32)
            else:
                # Entire output is within delay period
                fade_in = np.arange(num_samples) / delay_samples
                output = output * fade_in.astype(np.float32)

        return output

    def generate_unipolar(
        self,
        num_samples: int,
        sample_rate: int = 44100,
    ) -> NDArray[np.float32]:
        """Generate unipolar LFO (0 to depth instead of -depth to +depth).

        Useful for effects that only modulate in one direction.

        Args:
            num_samples: Number of samples to generate
            sample_rate: Sample rate in Hz

        Returns:
            LFO values ranging from 0 to depth
        """
        bipolar = self.generate(num_samples, sample_rate)
        return ((bipolar + self.depth) / 2).astype(np.float32)

    @classmethod
    def vibrato(cls, rate: float = 5.0, depth: float = 0.5) -> "LFO":
        """Create LFO preset for vibrato effect."""
        return cls(rate=rate, depth=depth, shape=LFOShape.SINE, delay=0.1)

    @classmethod
    def tremolo(cls, rate: float = 4.0, depth: float = 0.3) -> "LFO":
        """Create LFO preset for tremolo effect."""
        return cls(rate=rate, depth=depth, shape=LFOShape.SINE)

    @classmethod
    def wobble(cls, rate: float = 2.0, depth: float = 0.8) -> "LFO":
        """Create LFO preset for wobble bass effect."""
        return cls(rate=rate, depth=depth, shape=LFOShape.TRIANGLE)

    @classmethod
    def chiptune(cls, rate: float = 8.0, depth: float = 0.4) -> "LFO":
        """Create LFO preset with fast, retro-style modulation."""
        return cls(rate=rate, depth=depth, shape=LFOShape.SQUARE)
