"""NES 2A03-authentic waveform generators.

Generates sample-accurate pulse, triangle, and noise waveforms
matching the characteristics of the original NES sound chip.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from chiptune.chip.channels import DutyCycle


class WaveformGenerator:
    """Base class for NES-authentic waveform generation."""

    def __init__(self, sample_rate: int = 44100) -> None:
        self.sample_rate = sample_rate

    def generate(
        self, frequency: float, duration: float, amplitude: float = 1.0
    ) -> NDArray[np.float32]:
        """Generate samples for a single note.

        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            amplitude: Peak amplitude (0.0-1.0)

        Returns:
            Mono samples as float32 array
        """
        raise NotImplementedError


class PulseWaveGenerator(WaveformGenerator):
    """NES pulse wave with configurable duty cycle.

    Duty cycles affect timbre:
    - 12.5%: thin, nasal (8 samples high, 56 low at NES rate)
    - 25%: classic NES lead sound
    - 50%: hollow square wave
    - 75%: same as 25% inverted
    """

    DUTY_RATIOS: dict[DutyCycle, float] = {
        DutyCycle.DUTY_12_5: 0.125,
        DutyCycle.DUTY_25: 0.25,
        DutyCycle.DUTY_50: 0.5,
        DutyCycle.DUTY_75: 0.75,
    }

    def __init__(self, duty: DutyCycle = DutyCycle.DUTY_25, sample_rate: int = 44100) -> None:
        super().__init__(sample_rate)
        self.duty_ratio = self.DUTY_RATIOS[duty]

    def generate(
        self, frequency: float, duration: float, amplitude: float = 1.0
    ) -> NDArray[np.float32]:
        """Generate pulse wave with duty cycle."""
        num_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, num_samples, endpoint=False)

        # Create pulse wave: high when phase < duty_ratio
        phase = (t * frequency) % 1.0
        samples = np.where(phase < self.duty_ratio, amplitude, -amplitude)

        return samples.astype(np.float32)


class TriangleWaveGenerator(WaveformGenerator):
    """NES triangle wave - 16-step quantized.

    The NES triangle is NOT a smooth triangle wave; it's a
    4-bit stepped approximation with 16 discrete levels.
    This creates the characteristic "gritty" bass sound.
    """

    # NES triangle lookup table (32 steps in a cycle, 16 up + 16 down)
    # Values represent the 16 discrete amplitude levels
    NES_TRIANGLE_LUT: NDArray[np.float32] = (
        np.array(
            [
                15,
                14,
                13,
                12,
                11,
                10,
                9,
                8,
                7,
                6,
                5,
                4,
                3,
                2,
                1,
                0,
                0,
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
                15,
            ],
            dtype=np.float32,
        )
        / 15.0
    )  # Normalize to 0..1 range

    def generate(
        self, frequency: float, duration: float, amplitude: float = 1.0
    ) -> NDArray[np.float32]:
        """Generate NES-style stepped triangle wave."""
        num_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, num_samples, endpoint=False)

        # Phase position in 32-step cycle
        phase = (t * frequency * 32) % 32
        indices = phase.astype(int) % 32

        # Map to bipolar (-1 to 1) and apply amplitude
        samples = (self.NES_TRIANGLE_LUT[indices] * 2 - 1) * amplitude

        return samples.astype(np.float32)


class NoiseGenerator(WaveformGenerator):
    """NES noise channel - LFSR-based pseudo-random noise.

    The NES uses a 15-bit linear feedback shift register.
    'Period' (0-15) controls the clock rate, creating different
    pitched noise timbres from low rumble to high hiss.
    """

    # NES noise period table (CPU cycles between LFSR shifts)
    # Lower period = higher frequency noise
    PERIOD_TABLE: list[int] = [
        4,
        8,
        16,
        32,
        64,
        96,
        128,
        160,
        202,
        254,
        380,
        508,
        762,
        1016,
        2034,
        4068,
    ]

    # NTSC NES CPU clock rate
    NES_CPU_RATE: int = 1789773

    def __init__(self, mode: str = "long", sample_rate: int = 44100) -> None:
        """Initialize noise generator.

        Args:
            mode: "long" (32767 steps) or "short" (93 steps, more tonal)
            sample_rate: Audio sample rate
        """
        super().__init__(sample_rate)
        self.mode = mode
        # Feedback tap position: bit 6 for short mode, bit 1 for long mode
        self.feedback_bit = 6 if mode == "short" else 1

    def generate(self, period: int, duration: float, amplitude: float = 1.0) -> NDArray[np.float32]:
        """Generate NES-style noise.

        Args:
            period: NES noise period (0-15), lower = higher pitch
            duration: Duration in seconds
            amplitude: Peak amplitude (0.0-1.0)

        Returns:
            Mono samples as float32 array
        """
        num_samples = int(duration * self.sample_rate)

        # Clamp period to valid range
        period = max(0, min(15, period))

        # Calculate samples per LFSR shift
        period_cycles = self.PERIOD_TABLE[period]
        shifts_per_second = self.NES_CPU_RATE / period_cycles
        samples_per_shift = self.sample_rate / shifts_per_second

        # Initialize 15-bit LFSR
        lfsr = 1
        samples = np.zeros(num_samples, dtype=np.float32)
        shift_counter = 0.0

        for i in range(num_samples):
            # Output based on bit 0 of LFSR
            samples[i] = amplitude if (lfsr & 1) else -amplitude

            shift_counter += 1
            while shift_counter >= samples_per_shift:
                shift_counter -= samples_per_shift
                # XOR bits 0 and feedback_bit for new bit 14
                feedback = (lfsr & 1) ^ ((lfsr >> self.feedback_bit) & 1)
                lfsr = (lfsr >> 1) | (feedback << 14)

        return samples


def midi_to_frequency(midi_note: int) -> float:
    """Convert MIDI note number to frequency in Hz.

    Args:
        midi_note: MIDI note number (0-127, 69 = A4 = 440Hz)

    Returns:
        Frequency in Hz
    """
    return 440.0 * (2 ** ((midi_note - 69) / 12.0))
