"""Game Boy DMG (DMG-01) sound chip emulation.

The Game Boy's sound chip has 4 channels:
- Channel 1: Pulse wave with frequency sweep
- Channel 2: Pulse wave (no sweep)
- Channel 3: 32-sample wavetable
- Channel 4: Noise (LFSR-based)

Key differences from NES:
- 4-bit volume with envelope
- Frequency sweep on pulse 1
- 32-sample programmable wave channel
- Different noise period values
"""

from __future__ import annotations

from enum import IntEnum
from typing import ClassVar

import numpy as np
from numpy.typing import NDArray
from pydantic import Field

from chiptune.chip.systems.base import (
    ChipSystem,
    ChipType,
    ChipVoice,
    VoiceType,
)


class GBDutyCycle(IntEnum):
    """Game Boy pulse wave duty cycles."""

    DUTY_12_5 = 0  # 12.5% - very thin
    DUTY_25 = 1  # 25% - classic GB sound
    DUTY_50 = 2  # 50% - square wave
    DUTY_75 = 3  # 75% - inverted 25%


class GBPulseVoice(ChipVoice):
    """Game Boy pulse channel voice.

    Channels 1 and 2 are pulse waves. Channel 1 has
    hardware frequency sweep capability.
    """

    voice_type: VoiceType = VoiceType.PULSE
    duty_cycle: GBDutyCycle = GBDutyCycle.DUTY_25

    # Frequency sweep (channel 1 only)
    has_sweep: bool = False
    sweep_time: float = 0.0  # Sweep period in seconds
    sweep_direction: int = 1  # 1 = increase, -1 = decrease
    sweep_shift: int = 0  # Frequency change magnitude

    # Channel constraints
    min_pitch: int = 33  # ~55 Hz
    max_pitch: int = 107  # ~3951 Hz
    volume_bits: int = 4

    DUTY_RATIOS: ClassVar[dict[GBDutyCycle, float]] = {
        GBDutyCycle.DUTY_12_5: 0.125,
        GBDutyCycle.DUTY_25: 0.25,
        GBDutyCycle.DUTY_50: 0.5,
        GBDutyCycle.DUTY_75: 0.75,
    }

    def generate_samples(
        self,
        frequency: float,
        duration: float,
        amplitude: float,
        sample_rate: int,
    ) -> NDArray[np.float32]:
        """Generate Game Boy pulse wave."""
        num_samples = int(duration * sample_rate)
        if num_samples == 0:
            return np.array([], dtype=np.float32)

        duty_ratio = self.DUTY_RATIOS[self.duty_cycle]

        if self.has_sweep and self.sweep_time > 0:
            # Apply frequency sweep
            return self._generate_with_sweep(
                frequency, duration, amplitude, sample_rate, duty_ratio
            )

        # Standard pulse wave
        t = np.linspace(0, duration, num_samples, endpoint=False)
        phase = (t * frequency) % 1.0
        samples = np.where(phase < duty_ratio, amplitude, -amplitude)

        return samples.astype(np.float32)

    def _generate_with_sweep(
        self,
        frequency: float,
        duration: float,
        amplitude: float,
        sample_rate: int,
        duty_ratio: float,
    ) -> NDArray[np.float32]:
        """Generate pulse wave with frequency sweep."""
        num_samples = int(duration * sample_rate)
        samples = np.zeros(num_samples, dtype=np.float32)

        sweep_samples = (
            int(self.sweep_time * sample_rate) if self.sweep_time > 0 else num_samples
        )
        current_freq = frequency
        phase = 0.0

        for i in range(num_samples):
            # Update frequency at sweep intervals
            if sweep_samples > 0 and i > 0 and i % sweep_samples == 0:
                delta = (
                    current_freq / (1 << self.sweep_shift)
                    if self.sweep_shift > 0
                    else 0
                )
                current_freq = current_freq + delta * self.sweep_direction
                current_freq = max(20.0, min(4000.0, current_freq))

            # Generate sample
            phase_position = phase % 1.0
            samples[i] = amplitude if phase_position < duty_ratio else -amplitude
            phase += current_freq / sample_rate

        return samples


class GBWaveVoice(ChipVoice):
    """Game Boy wave channel voice.

    Uses a 32-sample wavetable with 4-bit samples (0-15).
    This allows custom waveforms beyond the standard pulse/triangle.
    """

    voice_type: VoiceType = VoiceType.WAVETABLE
    wavetable: list[int] = Field(
        default_factory=lambda: [
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
        ]
    )

    min_pitch: int = 21  # Good for bass
    max_pitch: int = 96
    volume_bits: int = 2  # Only 4 volume levels on GB wave

    # Preset wavetables
    TRIANGLE: ClassVar[list[int]] = [
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
    ]
    SAW: ClassVar[list[int]] = [
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
    ]
    SINE_APPROX: ClassVar[list[int]] = [
        8,
        10,
        12,
        13,
        14,
        15,
        15,
        15,
        14,
        13,
        12,
        10,
        8,
        6,
        4,
        3,
        2,
        1,
        1,
        1,
        2,
        3,
        4,
        6,
        8,
        10,
        12,
        13,
        14,
        15,
        15,
        15,
    ]
    BASS: ClassVar[list[int]] = [
        15,
        15,
        15,
        15,
        15,
        15,
        15,
        15,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        15,
        15,
        15,
        15,
        15,
        15,
        15,
        15,
    ]

    def generate_samples(
        self,
        frequency: float,
        duration: float,
        amplitude: float,
        sample_rate: int,
    ) -> NDArray[np.float32]:
        """Generate wave channel output from wavetable."""
        num_samples = int(duration * sample_rate)
        if num_samples == 0:
            return np.array([], dtype=np.float32)

        t = np.linspace(0, duration, num_samples, endpoint=False)

        # Convert wavetable to numpy and normalize
        wt = np.array(self.wavetable, dtype=np.float32) / 15.0
        wt = wt * 2 - 1  # Convert to -1..1 range

        # Phase position in 32-sample table
        phase = (t * frequency * 32) % 32
        indices = phase.astype(int) % 32

        samples = wt[indices] * amplitude

        return samples.astype(np.float32)


class GBNoiseVoice(ChipVoice):
    """Game Boy noise channel voice.

    7-bit LFSR noise generator with width mode selection.
    """

    voice_type: VoiceType = VoiceType.NOISE
    width_mode: int = 0  # 0 = 15-bit (long), 1 = 7-bit (short/metallic)

    min_pitch: int = 0
    max_pitch: int = 7  # GB has 8 base divisor codes
    volume_bits: int = 4

    # Game Boy noise divisor ratios
    DIVISOR_TABLE: ClassVar[list[int]] = [8, 16, 32, 48, 64, 80, 96, 112]
    GB_CLOCK: ClassVar[int] = 4194304  # Game Boy CPU clock

    def generate_samples(
        self,
        frequency: float,
        duration: float,
        amplitude: float,
        sample_rate: int,
    ) -> NDArray[np.float32]:
        """Generate Game Boy noise.

        Note: 'frequency' here maps to divisor code (0-7).
        """
        num_samples = int(duration * sample_rate)
        if num_samples == 0:
            return np.array([], dtype=np.float32)

        # Use frequency as divisor code
        divisor_code = int(max(0, min(7, frequency / 100)))  # Map frequency to 0-7
        divisor = self.DIVISOR_TABLE[divisor_code]

        # Calculate shift frequency
        shift_freq = self.GB_CLOCK / (divisor * 8)
        samples_per_shift = sample_rate / shift_freq

        # Initialize LFSR
        lfsr_bits = 7 if self.width_mode == 1 else 15
        lfsr = (1 << lfsr_bits) - 1
        feedback_mask = (1 << lfsr_bits) - 1

        samples = np.zeros(num_samples, dtype=np.float32)
        shift_counter = 0.0

        for i in range(num_samples):
            samples[i] = amplitude if (lfsr & 1) else -amplitude

            shift_counter += 1
            while shift_counter >= samples_per_shift:
                shift_counter -= samples_per_shift
                # XOR bits 0 and 1 for feedback
                feedback = (lfsr ^ (lfsr >> 1)) & 1
                lfsr = ((lfsr >> 1) | (feedback << (lfsr_bits - 1))) & feedback_mask

        return samples


class GameBoyChip(ChipSystem):
    """Complete Game Boy DMG sound chip.

    4 channels with mixing and stereo panning capabilities.
    """

    chip_type: ChipType = ChipType.GAMEBOY
    name: str = "Game Boy DMG"
    description: str = "Nintendo Game Boy original sound chip"

    pulse1: GBPulseVoice = Field(
        default_factory=lambda: GBPulseVoice(
            voice_id=0, has_sweep=True, sweep_time=0.0078
        )
    )
    pulse2: GBPulseVoice = Field(
        default_factory=lambda: GBPulseVoice(voice_id=1, has_sweep=False)
    )
    wave: GBWaveVoice = Field(default_factory=lambda: GBWaveVoice(voice_id=2))
    noise: GBNoiseVoice = Field(default_factory=lambda: GBNoiseVoice(voice_id=3))

    # Stereo panning (GB has L/R enable per channel)
    pan_pulse1: float = -0.25
    pan_pulse2: float = 0.25
    pan_wave: float = 0.0
    pan_noise: float = 0.0

    voice_count: ClassVar[int] = 4
    clock_rate: ClassVar[int] = 4194304

    # Channel IDs
    PULSE1_ID: ClassVar[int] = 0
    PULSE2_ID: ClassVar[int] = 1
    WAVE_ID: ClassVar[int] = 2
    NOISE_ID: ClassVar[int] = 3

    @property
    def voices(self) -> list[ChipVoice]:
        """Get all voices."""
        return [self.pulse1, self.pulse2, self.wave, self.noise]

    def get_voice(self, voice_id: int) -> ChipVoice | None:
        """Get voice by ID."""
        voice_map = {
            0: self.pulse1,
            1: self.pulse2,
            2: self.wave,
            3: self.noise,
        }
        return voice_map.get(voice_id)

    def render(self, tempo: float = 120.0) -> NDArray[np.float32]:
        """Render all channels to stereo."""
        # Render each voice
        channel_samples = {}
        max_length = 0

        for voice in self.voices:
            if voice.notes:
                samples = self.render_voice(voice.voice_id, tempo)
                channel_samples[voice.voice_id] = samples
                max_length = max(max_length, len(samples))

        if max_length == 0:
            return np.zeros((0, 2), dtype=np.float32)

        # Mix to stereo
        left = np.zeros(max_length, dtype=np.float32)
        right = np.zeros(max_length, dtype=np.float32)

        pans = {
            self.PULSE1_ID: self.pan_pulse1,
            self.PULSE2_ID: self.pan_pulse2,
            self.WAVE_ID: self.pan_wave,
            self.NOISE_ID: self.pan_noise,
        }

        volumes = {
            self.PULSE1_ID: 0.25,
            self.PULSE2_ID: 0.25,
            self.WAVE_ID: 0.30,
            self.NOISE_ID: 0.20,
        }

        for voice_id, samples in channel_samples.items():
            pan = pans.get(voice_id, 0.0)
            vol = volumes.get(voice_id, 0.25)

            # Constant power panning
            left_gain = np.sqrt(0.5 * (1 - pan)) * vol
            right_gain = np.sqrt(0.5 * (1 + pan)) * vol

            # Pad if needed
            padded = (
                np.pad(samples, (0, max_length - len(samples)))
                if len(samples) < max_length
                else samples
            )

            left += padded * left_gain
            right += padded * right_gain

        # Soft clip
        stereo = np.column_stack([left, right])
        stereo = np.tanh(stereo * 0.8)

        return stereo.astype(np.float32)

    def set_wavetable(self, wavetable: list[int]) -> None:
        """Set the wave channel wavetable."""
        if len(wavetable) != 32:
            raise ValueError("Wavetable must be exactly 32 samples")
        self.wave.wavetable = [max(0, min(15, v)) for v in wavetable]

    @classmethod
    def create(cls) -> GameBoyChip:
        """Create a fresh Game Boy chip instance."""
        return cls()

    @classmethod
    def with_sine_wave(cls) -> GameBoyChip:
        """Create chip with sine approximation wavetable."""
        chip = cls()
        chip.wave.wavetable = list(GBWaveVoice.SINE_APPROX)
        return chip

    @classmethod
    def with_saw_wave(cls) -> GameBoyChip:
        """Create chip with sawtooth wavetable."""
        chip = cls()
        chip.wave.wavetable = list(GBWaveVoice.SAW)
        return chip
