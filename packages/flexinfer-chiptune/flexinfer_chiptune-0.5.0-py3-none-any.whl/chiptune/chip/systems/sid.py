"""Commodore 64 SID (6581/8580) sound chip emulation.

The SID chip is legendary for its unique sound, featuring:
- 3 voices with multiple waveforms each (pulse, triangle, saw, noise)
- Multi-mode resonant filter (lowpass, bandpass, highpass)
- Ring modulation between voices
- Hard sync between voices
- ADSR envelope per voice

The 6581 (original) has a warmer, grittier sound.
The 8580 (later revision) is cleaner with better filters.
"""

from __future__ import annotations

from enum import IntEnum
from typing import ClassVar

import numpy as np
from numpy.typing import NDArray
from pydantic import Field
from scipy import signal as scipy_signal

from chiptune.chip.systems.base import (
    ChipSystem,
    ChipType,
    ChipVoice,
    VoiceType,
)


class SIDWaveform(IntEnum):
    """SID oscillator waveform selection."""

    TRIANGLE = 0
    SAWTOOTH = 1
    PULSE = 2
    NOISE = 3
    # Combined waveforms (SID can combine multiple)
    TRI_SAW = 4  # Triangle + Sawtooth
    TRI_PULSE = 5  # Triangle + Pulse
    SAW_PULSE = 6  # Sawtooth + Pulse


class SIDFilterMode(IntEnum):
    """SID filter modes."""

    OFF = 0
    LOWPASS = 1
    BANDPASS = 2
    HIGHPASS = 3
    LOWPASS_BANDPASS = 4
    LOWPASS_HIGHPASS = 5  # Notch
    BANDPASS_HIGHPASS = 6
    ALL = 7  # All three combined


class SIDRevision(IntEnum):
    """SID chip revision."""

    R6581 = 0  # Original - warmer, grittier
    R8580 = 1  # Later - cleaner filters


class SIDVoice(ChipVoice):
    """Single SID voice with full oscillator capabilities."""

    voice_type: VoiceType = VoiceType.PULSE
    waveform: SIDWaveform = SIDWaveform.PULSE
    pulse_width: float = 0.5  # 0.0-1.0 for pulse wave

    # Ring modulation with previous voice
    ring_mod: bool = False
    # Hard sync with previous voice
    hard_sync: bool = False

    # Voice constraints
    min_pitch: int = 0
    max_pitch: int = 127
    volume_bits: int = 4

    # LFSR state for noise
    _lfsr: int = 0x7FFFF8

    SID_CLOCK: ClassVar[int] = 1022727  # PAL SID clock

    def generate_samples(
        self,
        frequency: float,
        duration: float,
        amplitude: float,
        sample_rate: int,
    ) -> NDArray[np.float32]:
        """Generate SID voice waveform."""
        num_samples = int(duration * sample_rate)
        if num_samples == 0:
            return np.array([], dtype=np.float32)

        if self.waveform == SIDWaveform.NOISE:
            return self._generate_noise(num_samples, frequency, amplitude, sample_rate)

        t = np.linspace(0, duration, num_samples, endpoint=False)
        phase = (t * frequency) % 1.0

        if self.waveform == SIDWaveform.TRIANGLE:
            samples = self._triangle_wave(phase)
        elif self.waveform == SIDWaveform.SAWTOOTH:
            samples = self._sawtooth_wave(phase)
        elif self.waveform == SIDWaveform.PULSE:
            samples = self._pulse_wave(phase)
        elif self.waveform == SIDWaveform.TRI_SAW:
            # Combined waveforms AND together in SID
            tri = (self._triangle_wave(phase) + 1) / 2
            saw = (self._sawtooth_wave(phase) + 1) / 2
            samples = (tri * saw) * 2 - 1
        elif self.waveform == SIDWaveform.TRI_PULSE:
            tri = (self._triangle_wave(phase) + 1) / 2
            pul = (self._pulse_wave(phase) + 1) / 2
            samples = (tri * pul) * 2 - 1
        elif self.waveform == SIDWaveform.SAW_PULSE:
            saw = (self._sawtooth_wave(phase) + 1) / 2
            pul = (self._pulse_wave(phase) + 1) / 2
            samples = (saw * pul) * 2 - 1
        else:
            samples = self._pulse_wave(phase)

        return (samples * amplitude).astype(np.float32)

    def _triangle_wave(self, phase: NDArray[np.float64]) -> NDArray[np.float64]:
        """Generate triangle wave (SID uses XOR with MSB)."""
        return 2 * np.abs(2 * phase - 1) - 1

    def _sawtooth_wave(self, phase: NDArray[np.float64]) -> NDArray[np.float64]:
        """Generate sawtooth wave."""
        return 2 * phase - 1

    def _pulse_wave(self, phase: NDArray[np.float64]) -> NDArray[np.float64]:
        """Generate pulse wave with variable width."""
        return np.where(phase < self.pulse_width, 1.0, -1.0)

    def _generate_noise(
        self,
        num_samples: int,
        frequency: float,
        amplitude: float,
        sample_rate: int,
    ) -> NDArray[np.float32]:
        """Generate SID noise using 23-bit LFSR."""
        # SID noise shifts LFSR at oscillator frequency
        samples_per_shift = sample_rate / frequency if frequency > 0 else num_samples
        samples = np.zeros(num_samples, dtype=np.float32)
        lfsr = self._lfsr
        shift_counter = 0.0

        for i in range(num_samples):
            # Output is bits 20, 18, 14, 11, 9, 5, 2, 0
            output_bits = (
                ((lfsr >> 20) & 1)
                | ((lfsr >> 17) & 2)
                | ((lfsr >> 12) & 4)
                | ((lfsr >> 8) & 8)
                | ((lfsr >> 5) & 16)
                | ((lfsr >> 0) & 32)
                | ((lfsr << 3) & 64)
                | ((lfsr << 6) & 128)
            )
            samples[i] = (output_bits / 128.0 - 0.5) * 2 * amplitude

            shift_counter += 1
            while shift_counter >= samples_per_shift:
                shift_counter -= samples_per_shift
                # Feedback from bits 17 and 22
                feedback = ((lfsr >> 17) ^ (lfsr >> 22)) & 1
                lfsr = ((lfsr << 1) | feedback) & 0x7FFFFF

        self._lfsr = lfsr
        return samples


class SIDFilter:
    """SID multi-mode resonant filter emulation."""

    def __init__(
        self,
        cutoff: float = 1000.0,
        resonance: float = 0.0,
        mode: SIDFilterMode = SIDFilterMode.LOWPASS,
        revision: SIDRevision = SIDRevision.R6581,
    ):
        self.cutoff = cutoff
        self.resonance = resonance  # 0.0-1.0
        self.mode = mode
        self.revision = revision

    def process(
        self,
        samples: NDArray[np.float32],
        sample_rate: int,
    ) -> NDArray[np.float32]:
        """Apply SID filter to samples."""
        if self.mode == SIDFilterMode.OFF or len(samples) == 0:
            return samples

        nyquist = sample_rate / 2
        cutoff = min(self.cutoff, nyquist * 0.95)
        normalized_cutoff = cutoff / nyquist

        # Calculate Q from resonance (SID has 4 bits = 16 levels)
        q = 0.707 + self.resonance * 15  # Q range roughly 0.7 to 16

        # 6581 has grittier, less accurate filter
        if self.revision == SIDRevision.R6581:
            # Add slight distortion characteristic of 6581
            q *= 0.85
            cutoff *= 0.9  # 6581 cutoff is slightly lower

        output = np.zeros_like(samples)

        try:
            if self.mode in (SIDFilterMode.LOWPASS, SIDFilterMode.LOWPASS_BANDPASS):
                b, a = scipy_signal.butter(2, normalized_cutoff, btype="low")
                output = scipy_signal.lfilter(b, a, samples)

            elif self.mode == SIDFilterMode.HIGHPASS:
                b, a = scipy_signal.butter(2, normalized_cutoff, btype="high")
                output = scipy_signal.lfilter(b, a, samples)

            elif self.mode == SIDFilterMode.BANDPASS:
                # Bandpass needs bandwidth parameter
                low = max(0.01, normalized_cutoff * 0.7)
                high = min(0.99, normalized_cutoff * 1.3)
                if low < high:
                    b, a = scipy_signal.butter(2, [low, high], btype="band")
                    output = scipy_signal.lfilter(b, a, samples)
                else:
                    output = samples

            elif self.mode == SIDFilterMode.LOWPASS_HIGHPASS:
                # Notch filter
                low = max(0.01, normalized_cutoff * 0.8)
                high = min(0.99, normalized_cutoff * 1.2)
                if low < high:
                    b, a = scipy_signal.butter(2, [low, high], btype="bandstop")
                    output = scipy_signal.lfilter(b, a, samples)
                else:
                    output = samples
            else:
                output = samples

        except ValueError:
            output = samples

        # Apply resonance boost
        if self.resonance > 0:
            output = output * (1.0 + self.resonance * 0.5)

        # 6581-style soft clipping
        if self.revision == SIDRevision.R6581:
            output = np.tanh(output * 1.2) / 1.2

        return output.astype(np.float32)


class SIDChip(ChipSystem):
    """Complete Commodore 64 SID sound chip.

    3 voices with independent waveform selection,
    shared resonant multi-mode filter, and effects.
    """

    chip_type: ChipType = ChipType.SID
    name: str = "MOS 6581 SID"
    description: str = "Commodore 64 Sound Interface Device"

    voice1: SIDVoice = Field(default_factory=lambda: SIDVoice(voice_id=0))
    voice2: SIDVoice = Field(default_factory=lambda: SIDVoice(voice_id=1))
    voice3: SIDVoice = Field(default_factory=lambda: SIDVoice(voice_id=2))

    # Global filter settings
    filter_cutoff: float = 1000.0
    filter_resonance: float = 0.0
    filter_mode: SIDFilterMode = SIDFilterMode.LOWPASS
    filter_voice1: bool = True
    filter_voice2: bool = True
    filter_voice3: bool = False

    revision: SIDRevision = SIDRevision.R6581
    master_volume: float = 0.8

    voice_count: ClassVar[int] = 3
    clock_rate: ClassVar[int] = 1022727

    VOICE1_ID: ClassVar[int] = 0
    VOICE2_ID: ClassVar[int] = 1
    VOICE3_ID: ClassVar[int] = 2

    @property
    def voices(self) -> list[ChipVoice]:
        """Get all voices."""
        return [self.voice1, self.voice2, self.voice3]

    def get_voice(self, voice_id: int) -> ChipVoice | None:
        """Get voice by ID."""
        return {0: self.voice1, 1: self.voice2, 2: self.voice3}.get(voice_id)

    def render(self, tempo: float = 120.0) -> NDArray[np.float32]:
        """Render all voices with filter to stereo."""
        channel_samples = {}
        max_length = 0

        for voice in self.voices:
            if voice.notes:
                samples = self.render_voice(voice.voice_id, tempo)
                channel_samples[voice.voice_id] = samples
                max_length = max(max_length, len(samples))

        if max_length == 0:
            return np.zeros((0, 2), dtype=np.float32)

        # Create filter
        sid_filter = SIDFilter(
            cutoff=self.filter_cutoff,
            resonance=self.filter_resonance,
            mode=self.filter_mode,
            revision=self.revision,
        )

        # Mix voices
        filter_voices = {
            self.VOICE1_ID: self.filter_voice1,
            self.VOICE2_ID: self.filter_voice2,
            self.VOICE3_ID: self.filter_voice3,
        }

        filtered_mix = np.zeros(max_length, dtype=np.float32)
        unfiltered_mix = np.zeros(max_length, dtype=np.float32)

        for voice_id, samples in channel_samples.items():
            padded = (
                np.pad(samples, (0, max_length - len(samples)))
                if len(samples) < max_length
                else samples
            )

            if filter_voices.get(voice_id, False):
                filtered_mix += padded / 3
            else:
                unfiltered_mix += padded / 3

        # Apply filter to filtered voices
        if self.filter_mode != SIDFilterMode.OFF:
            filtered_mix = sid_filter.process(filtered_mix, self.sample_rate)

        # Combine
        mono = (filtered_mix + unfiltered_mix) * self.master_volume

        # Soft clip
        mono = np.tanh(mono)

        # Convert to stereo (SID is mono, slight widening)
        stereo = np.column_stack([mono, mono])

        return stereo.astype(np.float32)

    @classmethod
    def create(cls, revision: SIDRevision = SIDRevision.R6581) -> SIDChip:
        """Create a SID chip instance."""
        return cls(revision=revision)

    @classmethod
    def lead_preset(cls) -> SIDChip:
        """Classic SID lead sound."""
        chip = cls()
        chip.voice1.waveform = SIDWaveform.PULSE
        chip.voice1.pulse_width = 0.4
        chip.filter_mode = SIDFilterMode.LOWPASS
        chip.filter_cutoff = 2000.0
        chip.filter_resonance = 0.4
        return chip

    @classmethod
    def bass_preset(cls) -> SIDChip:
        """Classic SID bass sound."""
        chip = cls()
        chip.voice1.waveform = SIDWaveform.SAWTOOTH
        chip.filter_mode = SIDFilterMode.LOWPASS
        chip.filter_cutoff = 800.0
        chip.filter_resonance = 0.3
        return chip

    @classmethod
    def arpeggio_preset(cls) -> SIDChip:
        """Fast arpeggio lead preset."""
        chip = cls()
        chip.voice1.waveform = SIDWaveform.TRI_PULSE
        chip.voice1.pulse_width = 0.5
        chip.filter_mode = SIDFilterMode.BANDPASS
        chip.filter_cutoff = 1500.0
        chip.filter_resonance = 0.6
        return chip
