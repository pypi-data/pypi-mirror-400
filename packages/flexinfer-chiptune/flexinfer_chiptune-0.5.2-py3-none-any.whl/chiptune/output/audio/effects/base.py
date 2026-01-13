"""Base classes for audio effects."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from chiptune.output.audio.effects.chain import EffectChain


class SampleEffect(BaseModel, ABC):
    """Base class for sample-based audio effects.

    Effects process numpy arrays of audio samples and return modified samples.
    All effects should be stateless - they don't maintain state between calls.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @abstractmethod
    def process(
        self,
        samples: NDArray[np.float32],
        sample_rate: int = 44100,
    ) -> NDArray[np.float32]:
        """Process audio samples through the effect.

        Args:
            samples: Input audio samples (1D array)
            sample_rate: Sample rate in Hz

        Returns:
            Processed audio samples (same length as input)
        """
        ...

    def __or__(self, other: "SampleEffect") -> "EffectChain":
        """Chain effects using the | operator.

        Example:
            vibrato | echo | tremolo
        """
        from chiptune.output.audio.effects.chain import EffectChain

        return EffectChain(effects=[self, other])


class PitchEffect(BaseModel, ABC):
    """Base class for pitch-modifying effects.

    Unlike SampleEffect, pitch effects modify the frequency of notes
    before waveform generation, not after.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @abstractmethod
    def modulate_frequency(
        self,
        base_frequency: float,
        time_array: NDArray[np.float32],
        sample_rate: int = 44100,
    ) -> NDArray[np.float32]:
        """Generate frequency values over time.

        Args:
            base_frequency: The base note frequency in Hz
            time_array: Time values for each sample
            sample_rate: Sample rate in Hz

        Returns:
            Array of frequency values (one per sample)
        """
        ...


class AmplitudeEffect(BaseModel, ABC):
    """Base class for amplitude-modifying effects.

    These effects generate amplitude envelopes that multiply
    with the audio signal.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @abstractmethod
    def generate_envelope(
        self,
        num_samples: int,
        sample_rate: int = 44100,
    ) -> NDArray[np.float32]:
        """Generate amplitude envelope.

        Args:
            num_samples: Number of samples to generate
            sample_rate: Sample rate in Hz

        Returns:
            Amplitude multipliers (one per sample, 0.0 to 1.0+)
        """
        ...
