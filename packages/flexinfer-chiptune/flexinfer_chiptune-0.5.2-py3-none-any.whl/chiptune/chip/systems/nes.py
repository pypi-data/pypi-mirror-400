"""NES 2A03 APU sound chip emulation.

The NES APU (Audio Processing Unit) has 5 channels:
- Channel 0: Pulse 1 (melody) - duty cycle control
- Channel 1: Pulse 2 (harmony) - duty cycle control
- Channel 2: Triangle (bass) - no volume control, 16-step
- Channel 3: Noise (drums) - LFSR-based
- Channel 4: DPCM (samples) - not implemented here

Key characteristics:
- 4-bit volume (0-15) for pulse/noise
- Triangle has no volume control
- Pulse waves have 4 duty cycle options
- Noise has 16 period settings
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


class NESDutyCycle(IntEnum):
    """NES pulse wave duty cycles.

    Duty cycle affects the timbre:
    - 12.5%: Thin, nasal (high overtones)
    - 25%: Classic NES lead sound
    - 50%: Pure square wave
    - 75%: Same timbre as 25% (phase inverted)
    """

    DUTY_12_5 = 0  # 12.5% duty
    DUTY_25 = 1  # 25% duty (classic)
    DUTY_50 = 2  # 50% duty (square)
    DUTY_75 = 3  # 75% duty


class NESPulseVoice(ChipVoice):
    """NES pulse wave channel voice.

    The NES has two pulse channels with configurable duty cycles.
    Pulse 1 (channel 0) and Pulse 2 (channel 1) are identical
    except Pulse 1 has hardware sweep capability (not modeled here
    as it's handled by effects).
    """

    voice_type: VoiceType = VoiceType.PULSE
    duty_cycle: NESDutyCycle = NESDutyCycle.DUTY_25

    # NES pulse constraints
    min_pitch: int = 33  # A1 - lowest stable pitch
    max_pitch: int = 108  # C8 - practical upper limit
    volume_bits: int = 4

    # Duty cycle to ratio mapping
    DUTY_RATIOS: ClassVar[dict[NESDutyCycle, float]] = {
        NESDutyCycle.DUTY_12_5: 0.125,
        NESDutyCycle.DUTY_25: 0.25,
        NESDutyCycle.DUTY_50: 0.5,
        NESDutyCycle.DUTY_75: 0.75,
    }

    def generate_samples(
        self,
        frequency: float,
        duration: float,
        amplitude: float,
        sample_rate: int,
    ) -> NDArray[np.float32]:
        """Generate NES-style pulse wave.

        Args:
            frequency: Note frequency in Hz
            duration: Duration in seconds
            amplitude: Peak amplitude (0.0-1.0)
            sample_rate: Audio sample rate

        Returns:
            Mono samples as float32 array
        """
        num_samples = int(duration * sample_rate)
        if num_samples == 0:
            return np.array([], dtype=np.float32)

        duty_ratio = self.DUTY_RATIOS[self.duty_cycle]

        t = np.linspace(0, duration, num_samples, endpoint=False)
        phase = (t * frequency) % 1.0
        samples = np.where(phase < duty_ratio, amplitude, -amplitude)

        return samples.astype(np.float32)


class NESTriangleVoice(ChipVoice):
    """NES triangle wave channel voice.

    The NES triangle is NOT a smooth triangle - it's a 16-step
    quantized approximation with 32 steps per cycle (16 up, 16 down).
    This creates the characteristic "gritty" bass sound.

    Important: The triangle channel has NO volume control on real hardware.
    """

    voice_type: VoiceType = VoiceType.TRIANGLE

    # NES triangle constraints
    min_pitch: int = 21  # A0 - can go lower than pulse
    max_pitch: int = 96  # C7 - sounds best in bass range
    volume_bits: int = 0  # No volume control!
    has_volume_control: bool = False

    # NES triangle lookup table (32 steps: 16 down, 16 up)
    # Values are 0-15 representing the 16 discrete amplitude levels
    NES_TRIANGLE_LUT: ClassVar[NDArray[np.float32]] = (
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
    )  # Normalized to 0..1

    def generate_samples(
        self,
        frequency: float,
        duration: float,
        amplitude: float,
        sample_rate: int,
    ) -> NDArray[np.float32]:
        """Generate NES-style stepped triangle wave.

        Args:
            frequency: Note frequency in Hz
            duration: Duration in seconds
            amplitude: Peak amplitude (ignored - triangle has no volume)
            sample_rate: Audio sample rate

        Returns:
            Mono samples as float32 array
        """
        num_samples = int(duration * sample_rate)
        if num_samples == 0:
            return np.array([], dtype=np.float32)

        t = np.linspace(0, duration, num_samples, endpoint=False)

        # Phase position in 32-step cycle
        phase = (t * frequency * 32) % 32
        indices = phase.astype(int) % 32

        # Map to bipolar (-1 to 1)
        # Note: amplitude is effectively ignored for authenticity
        samples: NDArray[np.float32] = (self.NES_TRIANGLE_LUT[indices] * 2 - 1).astype(np.float32)

        return samples


class NESNoiseVoice(ChipVoice):
    """NES noise channel voice.

    The NES noise uses a 15-bit linear feedback shift register (LFSR).
    The "pitch" parameter selects from 16 different clock dividers,
    creating different noise timbres from low rumble to high hiss.

    Mode affects the LFSR feedback tap:
    - Long mode (bit 1): 32767-step sequence (white noise)
    - Short mode (bit 6): 93-step sequence (more tonal/metallic)
    """

    voice_type: VoiceType = VoiceType.NOISE

    # NES noise constraints
    min_pitch: int = 0  # Period 0 (highest pitch)
    max_pitch: int = 15  # Period 15 (lowest pitch)
    volume_bits: int = 4

    # Noise mode: "long" (32767 steps) or "short" (93 steps, more tonal)
    mode: str = Field(default="long")

    # NES noise period table (CPU cycles between LFSR shifts)
    PERIOD_TABLE: ClassVar[list[int]] = [
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
    NES_CPU_RATE: ClassVar[int] = 1789773

    def generate_samples(
        self,
        frequency: float,
        duration: float,
        amplitude: float,
        sample_rate: int,
    ) -> NDArray[np.float32]:
        """Generate NES-style LFSR noise.

        Args:
            frequency: Used as period index (0-15), lower = higher pitch
            duration: Duration in seconds
            amplitude: Peak amplitude (0.0-1.0)
            sample_rate: Audio sample rate

        Returns:
            Mono samples as float32 array
        """
        num_samples = int(duration * sample_rate)
        if num_samples == 0:
            return np.array([], dtype=np.float32)

        # Treat frequency as period index
        period_index = int(frequency)
        period_index = max(0, min(15, period_index))

        # Calculate samples per LFSR shift
        period_cycles = self.PERIOD_TABLE[period_index]
        shifts_per_second = self.NES_CPU_RATE / period_cycles
        samples_per_shift = sample_rate / shifts_per_second

        # LFSR feedback tap position
        feedback_bit = 6 if self.mode == "short" else 1

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
                feedback = (lfsr & 1) ^ ((lfsr >> feedback_bit) & 1)
                lfsr = (lfsr >> 1) | (feedback << 14)

        return samples


class NES2A03(ChipSystem):
    """NES 2A03 APU sound chip system.

    Complete emulation of the NES audio processing unit with:
    - 2 pulse wave channels (melody, harmony)
    - 1 triangle wave channel (bass)
    - 1 noise channel (percussion)

    Example:
        nes = NES2A03.create()
        nes.pulse1.notes = [Note(60, 1.0), Note(64, 1.0)]
        nes.pulse1.duty_cycle = NESDutyCycle.DUTY_25
        audio = nes.render(tempo=120)
    """

    chip_type: ChipType = ChipType.NES
    name: str = "NES 2A03"
    description: str = "Nintendo Entertainment System APU"

    # Voice channels
    pulse1: NESPulseVoice = Field(default_factory=lambda: NESPulseVoice(voice_id=0))
    pulse2: NESPulseVoice = Field(default_factory=lambda: NESPulseVoice(voice_id=1))
    triangle: NESTriangleVoice = Field(default_factory=lambda: NESTriangleVoice(voice_id=2))
    noise: NESNoiseVoice = Field(default_factory=lambda: NESNoiseVoice(voice_id=3))

    # Hardware specs
    voice_count: ClassVar[int] = 4
    clock_rate: ClassVar[int] = 1789773  # NTSC CPU clock

    # Channel IDs for consistency with legacy code
    PULSE1_ID: ClassVar[int] = 0
    PULSE2_ID: ClassVar[int] = 1
    TRIANGLE_ID: ClassVar[int] = 2
    NOISE_ID: ClassVar[int] = 3

    @property
    def voices(self) -> list[ChipVoice]:
        """Get all voices in this chip."""
        return [self.pulse1, self.pulse2, self.triangle, self.noise]

    def get_voice(self, voice_id: int) -> ChipVoice | None:
        """Get a specific voice by ID."""
        voice_map: dict[int, ChipVoice] = {
            0: self.pulse1,
            1: self.pulse2,
            2: self.triangle,
            3: self.noise,
        }
        return voice_map.get(voice_id)

    def render(self, tempo: float = 120.0) -> NDArray[np.float32]:
        """Render all voices to a stereo mix.

        Uses NES-accurate panning:
        - Pulse 1: Slightly left
        - Pulse 2: Slightly right
        - Triangle: Center
        - Noise: Center

        Args:
            tempo: Tempo in BPM for timing calculations

        Returns:
            Stereo samples as (N, 2) float32 array
        """
        # Render each voice
        voice_samples = {
            0: self.render_voice(0, tempo),
            1: self.render_voice(1, tempo),
            2: self.render_voice(2, tempo),
            3: self.render_voice(3, tempo),
        }

        # Find max length
        max_length = max(
            (len(s) for s in voice_samples.values() if len(s) > 0),
            default=0,
        )

        if max_length == 0:
            return np.array([], dtype=np.float32).reshape(0, 2)

        # Create stereo output
        left = np.zeros(max_length, dtype=np.float32)
        right = np.zeros(max_length, dtype=np.float32)

        # Mix with NES-style panning
        # Pulse 1: 60% left, 40% right
        if len(voice_samples[0]) > 0:
            s = voice_samples[0]
            left[: len(s)] += s * 0.6
            right[: len(s)] += s * 0.4

        # Pulse 2: 40% left, 60% right
        if len(voice_samples[1]) > 0:
            s = voice_samples[1]
            left[: len(s)] += s * 0.4
            right[: len(s)] += s * 0.6

        # Triangle: Center
        if len(voice_samples[2]) > 0:
            s = voice_samples[2]
            left[: len(s)] += s * 0.5
            right[: len(s)] += s * 0.5

        # Noise: Center
        if len(voice_samples[3]) > 0:
            s = voice_samples[3]
            left[: len(s)] += s * 0.5
            right[: len(s)] += s * 0.5

        # Normalize to prevent clipping
        max_val = max(np.max(np.abs(left)), np.max(np.abs(right)))
        if max_val > 1.0:
            left /= max_val
            right /= max_val

        return np.column_stack([left, right]).astype(np.float32)

    @classmethod
    def create(cls, sample_rate: int = 44100) -> NES2A03:
        """Create a fresh NES 2A03 chip instance.

        Args:
            sample_rate: Audio sample rate (default 44100)

        Returns:
            New NES2A03 instance with default settings
        """
        return cls(
            sample_rate=sample_rate,
            pulse1=NESPulseVoice(voice_id=0, duty_cycle=NESDutyCycle.DUTY_25),
            pulse2=NESPulseVoice(voice_id=1, duty_cycle=NESDutyCycle.DUTY_50),
            triangle=NESTriangleVoice(voice_id=2),
            noise=NESNoiseVoice(voice_id=3),
        )

    @classmethod
    def famitracker_style(cls) -> NES2A03:
        """Create NES chip with FamiTracker-style defaults.

        Uses duty cycles common in FamiTracker compositions.
        """
        return cls(
            pulse1=NESPulseVoice(voice_id=0, duty_cycle=NESDutyCycle.DUTY_50),
            pulse2=NESPulseVoice(voice_id=1, duty_cycle=NESDutyCycle.DUTY_25),
            triangle=NESTriangleVoice(voice_id=2),
            noise=NESNoiseVoice(voice_id=3),
        )
