"""ADSR envelope generator for audio synthesis.

Provides sample-accurate amplitude envelopes that shape the
attack, decay, sustain, and release of each note.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel


class ADSREnvelope(BaseModel):
    """ADSR envelope generator for audio synthesis.

    Converts time-based envelope parameters to sample-accurate
    amplitude curves for authentic chiptune sounds.

    Attributes:
        attack_time: Time to reach peak amplitude (seconds)
        decay_time: Time to decay to sustain level (seconds)
        sustain_level: Amplitude during sustain phase (0.0-1.0)
        release_time: Time to fade to silence (seconds)
    """

    attack_time: float = 0.01
    decay_time: float = 0.1
    sustain_level: float = 0.7
    release_time: float = 0.1

    @classmethod
    def chip_lead(cls) -> ADSREnvelope:
        """Classic chiptune lead envelope - instant attack, quick decay."""
        return cls(
            attack_time=0.001,
            decay_time=0.05,
            sustain_level=0.7,
            release_time=0.1,
        )

    @classmethod
    def chip_bass(cls) -> ADSREnvelope:
        """Bass envelope - fuller sustain for low frequencies."""
        return cls(
            attack_time=0.001,
            decay_time=0.02,
            sustain_level=0.9,
            release_time=0.05,
        )

    @classmethod
    def pluck(cls) -> ADSREnvelope:
        """Pluck envelope - instant attack, fast decay to silence."""
        return cls(
            attack_time=0.001,
            decay_time=0.15,
            sustain_level=0.0,
            release_time=0.05,
        )

    @classmethod
    def pad(cls) -> ADSREnvelope:
        """Pad envelope - slow attack and release for ambient sounds."""
        return cls(
            attack_time=0.1,
            decay_time=0.1,
            sustain_level=0.8,
            release_time=0.3,
        )

    @classmethod
    def percussion(cls) -> ADSREnvelope:
        """Percussion envelope - instant attack, very fast decay."""
        return cls(
            attack_time=0.0,
            decay_time=0.08,
            sustain_level=0.0,
            release_time=0.02,
        )

    def generate(
        self,
        note_duration: float,
        sample_rate: int,
        velocity: float = 1.0,
    ) -> NDArray[np.float32]:
        """Generate envelope curve for a note.

        Args:
            note_duration: Total note duration in seconds
            sample_rate: Audio sample rate
            velocity: Velocity scaling (0.0-1.0)

        Returns:
            Amplitude envelope as float32 array
        """
        total_samples = int(note_duration * sample_rate)
        if total_samples <= 0:
            return np.array([], dtype=np.float32)

        envelope = np.zeros(total_samples, dtype=np.float32)

        attack_samples = int(self.attack_time * sample_rate)
        decay_samples = int(self.decay_time * sample_rate)
        release_samples = int(self.release_time * sample_rate)

        # Sustain fills the remainder
        sustain_samples = max(0, total_samples - attack_samples - decay_samples - release_samples)

        current_sample = 0

        # Attack: 0 -> 1
        if attack_samples > 0 and current_sample < total_samples:
            end = min(current_sample + attack_samples, total_samples)
            count = end - current_sample
            if count > 0:
                envelope[current_sample:end] = np.linspace(0, 1, count)
            current_sample = end

        # Decay: 1 -> sustain_level
        if decay_samples > 0 and current_sample < total_samples:
            end = min(current_sample + decay_samples, total_samples)
            count = end - current_sample
            if count > 0:
                envelope[current_sample:end] = np.linspace(1, self.sustain_level, count)
            current_sample = end

        # Sustain: hold at sustain_level
        if sustain_samples > 0 and current_sample < total_samples:
            end = min(current_sample + sustain_samples, total_samples)
            envelope[current_sample:end] = self.sustain_level
            current_sample = end

        # Release: sustain_level -> 0
        if current_sample < total_samples:
            end = total_samples
            count = end - current_sample
            if count > 0:
                start_level = (
                    envelope[current_sample - 1] if current_sample > 0 else self.sustain_level
                )
                envelope[current_sample:end] = np.linspace(start_level, 0, count)

        return (envelope * velocity).astype(np.float32)
