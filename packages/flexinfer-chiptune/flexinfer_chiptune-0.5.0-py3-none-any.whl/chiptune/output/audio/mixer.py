"""Multi-channel stereo mixer for NES audio.

Combines multiple NES channels into stereo output with
authentic volume balance and subtle stereo positioning.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel

from chiptune.chip.channels import NESChannels


class ChannelMixer(BaseModel):
    """Mix multiple NES channels into stereo output.

    Uses NES-authentic mixing ratios where applicable, with subtle
    stereo panning for a wider soundstage while maintaining the
    classic chiptune character.
    """

    sample_rate: int = 44100
    master_volume: float = 0.8

    # Channel volume balance (normalized to prevent clipping)
    CHANNEL_VOLUMES: ClassVar[dict[int, float]] = {
        NESChannels.PULSE1_ID: 0.25,
        NESChannels.PULSE2_ID: 0.25,
        NESChannels.TRIANGLE_ID: 0.30,  # Slightly louder for bass presence
        NESChannels.NOISE_ID: 0.20,
    }

    # Stereo panning (-1.0 = left, 0.0 = center, 1.0 = right)
    CHANNEL_PAN: ClassVar[dict[int, float]] = {
        NESChannels.PULSE1_ID: -0.3,  # Slight left
        NESChannels.PULSE2_ID: 0.3,  # Slight right
        NESChannels.TRIANGLE_ID: 0.0,  # Center (bass)
        NESChannels.NOISE_ID: 0.0,  # Center (drums)
    }

    def mix(self, channel_samples: dict[int, NDArray[np.float32]]) -> NDArray[np.float32]:
        """Mix channel sample arrays into stereo output.

        Args:
            channel_samples: Dict mapping channel_id to mono samples

        Returns:
            Stereo samples as (N, 2) float32 array
        """
        if not channel_samples:
            return np.zeros((0, 2), dtype=np.float32)

        # Find the longest channel
        max_length = max(len(s) for s in channel_samples.values())

        # Initialize stereo output
        left = np.zeros(max_length, dtype=np.float32)
        right = np.zeros(max_length, dtype=np.float32)

        for channel_id, samples in channel_samples.items():
            if len(samples) == 0:
                continue

            volume = self.CHANNEL_VOLUMES.get(channel_id, 0.25)
            pan = self.CHANNEL_PAN.get(channel_id, 0.0)

            # Calculate left/right gains from pan using constant power panning
            # This maintains perceived loudness across the stereo field
            left_gain = np.sqrt(0.5 * (1 - pan)) * volume
            right_gain = np.sqrt(0.5 * (1 + pan)) * volume

            # Pad samples if needed
            padded = samples
            if len(samples) < max_length:
                padded = np.pad(samples, (0, max_length - len(samples)))

            left += padded * left_gain
            right += padded * right_gain

        # Apply master volume and soft clip to prevent harsh distortion
        stereo = np.column_stack([left, right]) * self.master_volume
        stereo = np.tanh(stereo)  # Soft limiting

        return stereo.astype(np.float32)

    def mix_mono(self, channel_samples: dict[int, NDArray[np.float32]]) -> NDArray[np.float32]:
        """Mix channel sample arrays into mono output.

        Args:
            channel_samples: Dict mapping channel_id to mono samples

        Returns:
            Mono samples as float32 array
        """
        stereo = self.mix(channel_samples)
        if len(stereo) == 0:
            return np.array([], dtype=np.float32)

        # Average left and right channels
        mono = (stereo[:, 0] + stereo[:, 1]) / 2
        return mono.astype(np.float32)
