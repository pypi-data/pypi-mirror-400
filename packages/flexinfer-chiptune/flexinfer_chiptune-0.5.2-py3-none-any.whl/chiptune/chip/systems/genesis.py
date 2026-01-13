"""Sega Genesis/Mega Drive YM2612 FM synthesis chip emulation.

The YM2612 is a 6-channel FM synthesizer using 4-operator FM synthesis.
Each channel has 4 operators connected in one of 8 algorithms.

FM synthesis creates complex timbres by using one oscillator (modulator)
to modulate the frequency of another (carrier). The YM2612's 4 operators
and 8 algorithms allow for a wide range of sounds from bells and brass
to bass and pads.

Key features:
- 6 FM channels (channel 6 can be used for DAC/PCM)
- 4 operators per channel
- 8 connection algorithms
- Hardware LFO for vibrato/tremolo
- SSG-EG envelope mode for special effects
"""

from __future__ import annotations

from enum import IntEnum
from typing import ClassVar

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, Field

from chiptune.chip.systems.base import (
    ChipSystem,
    ChipType,
    ChipVoice,
    VoiceType,
)


class FMAlgorithm(IntEnum):
    """YM2612 FM algorithm configurations.

    Each algorithm defines how the 4 operators (OP1-OP4) connect.
    Operators can be modulators (M) or carriers (C).

    The number indicates how many carriers (sound-producing operators).
    More carriers = brighter, more harmonic sound.
    Fewer carriers = more complex modulation, metallic sounds.
    """

    ALG0 = 0  # Serial: 1→2→3→4  (1 carrier, most complex modulation)
    ALG1 = 1  # 1+2→3→4         (1 carrier)
    ALG2 = 2  # 2→3→4, 1→4      (1 carrier)
    ALG3 = 3  # 1→2→4, 3→4      (1 carrier)
    ALG4 = 4  # 1→2, 3→4        (2 carriers, balanced)
    ALG5 = 5  # 1→2, 1→3, 1→4   (3 carriers)
    ALG6 = 6  # 1→2, 3, 4       (3 carriers)
    ALG7 = 7  # 1, 2, 3, 4      (4 carriers, all parallel, organ-like)


class FMOperator(BaseModel):
    """Single FM operator with envelope and frequency settings."""

    # Frequency multiplier (ratio to base frequency)
    # 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
    multiple: float = 1.0

    # Detune for slight pitch variation (-3 to +3)
    detune: int = 0

    # Total level (attenuation) - 0 = loudest, 127 = silent
    total_level: int = 0

    # Envelope rates (0-31, higher = faster)
    attack_rate: int = 31
    decay_rate: int = 0
    sustain_rate: int = 0
    release_rate: int = 15
    sustain_level: int = 0  # 0-15

    # Feedback (only applies to OP1 in most algorithms)
    feedback: int = 0  # 0-7

    def generate_envelope(self, num_samples: int, sample_rate: int) -> NDArray[np.float32]:
        """Generate ADSR envelope for this operator."""
        # Convert YM2612 rates to times (simplified)
        attack_time = 0.002 + (31 - self.attack_rate) * 0.05
        decay_time = 0.01 + (31 - self.decay_rate) * 0.1
        sustain_level = 1.0 - (self.sustain_level / 15.0)
        release_time = 0.01 + (31 - self.release_rate) * 0.1

        attack_samples = int(attack_time * sample_rate)
        decay_samples = int(decay_time * sample_rate)
        release_samples = int(release_time * sample_rate)
        sustain_samples = max(0, num_samples - attack_samples - decay_samples - release_samples)

        envelope = np.zeros(num_samples, dtype=np.float32)
        pos = 0

        # Attack
        if attack_samples > 0 and pos < num_samples:
            end = min(pos + attack_samples, num_samples)
            envelope[pos:end] = np.linspace(0, 1, end - pos)
            pos = end

        # Decay
        if decay_samples > 0 and pos < num_samples:
            end = min(pos + decay_samples, num_samples)
            envelope[pos:end] = np.linspace(1, sustain_level, end - pos)
            pos = end

        # Sustain
        if sustain_samples > 0 and pos < num_samples:
            end = min(pos + sustain_samples, num_samples)
            envelope[pos:end] = sustain_level
            pos = end

        # Release
        if pos < num_samples:
            envelope[pos:] = np.linspace(sustain_level, 0, num_samples - pos)

        # Apply total level attenuation
        attenuation = 10 ** (-self.total_level / 20.0)  # dB to linear
        return envelope * attenuation


class FMVoice(ChipVoice):
    """YM2612 FM channel voice with 4 operators."""

    voice_type: VoiceType = VoiceType.FM
    algorithm: FMAlgorithm = FMAlgorithm.ALG4

    op1: FMOperator = Field(default_factory=FMOperator)
    op2: FMOperator = Field(default_factory=FMOperator)
    op3: FMOperator = Field(default_factory=FMOperator)
    op4: FMOperator = Field(default_factory=FMOperator)

    # LFO settings (global but affects per-voice)
    lfo_enable: bool = False
    lfo_frequency: float = 5.0  # Hz
    amplitude_mod_sensitivity: int = 0  # 0-3
    frequency_mod_sensitivity: int = 0  # 0-7

    min_pitch: int = 0
    max_pitch: int = 127
    volume_bits: int = 7  # 128 levels

    def generate_samples(
        self,
        frequency: float,
        duration: float,
        amplitude: float,
        sample_rate: int,
    ) -> NDArray[np.float32]:
        """Generate FM synthesis output based on algorithm."""
        num_samples = int(duration * sample_rate)
        if num_samples == 0:
            return np.array([], dtype=np.float32)

        t = np.linspace(0, duration, num_samples, endpoint=False)

        # Generate each operator's base frequency
        freq1 = frequency * self.op1.multiple * (1 + self.op1.detune * 0.01)
        freq2 = frequency * self.op2.multiple * (1 + self.op2.detune * 0.01)
        freq3 = frequency * self.op3.multiple * (1 + self.op3.detune * 0.01)
        freq4 = frequency * self.op4.multiple * (1 + self.op4.detune * 0.01)

        # Phases
        phase1 = 2 * np.pi * freq1 * t
        phase2 = 2 * np.pi * freq2 * t
        phase3 = 2 * np.pi * freq3 * t
        phase4 = 2 * np.pi * freq4 * t

        # Envelopes
        env1 = self.op1.generate_envelope(num_samples, sample_rate)
        env2 = self.op2.generate_envelope(num_samples, sample_rate)
        env3 = self.op3.generate_envelope(num_samples, sample_rate)
        env4 = self.op4.generate_envelope(num_samples, sample_rate)

        # Feedback for OP1
        feedback_level = self.op1.feedback / 7.0 if self.op1.feedback > 0 else 0

        # Generate based on algorithm
        output = self._apply_algorithm(
            t,
            phase1,
            phase2,
            phase3,
            phase4,
            env1,
            env2,
            env3,
            env4,
            feedback_level,
        )

        # Apply LFO if enabled
        if self.lfo_enable:
            lfo = np.sin(2 * np.pi * self.lfo_frequency * t)
            # Amplitude modulation
            if self.amplitude_mod_sensitivity > 0:
                am_depth = self.amplitude_mod_sensitivity / 3.0 * 0.5
                output = output * (1 - am_depth + am_depth * (lfo + 1) / 2)

        return (output * amplitude).astype(np.float32)

    def _apply_algorithm(
        self,
        t: NDArray[np.float64],
        phase1: NDArray[np.float64],
        phase2: NDArray[np.float64],
        phase3: NDArray[np.float64],
        phase4: NDArray[np.float64],
        env1: NDArray[np.float32],
        env2: NDArray[np.float32],
        env3: NDArray[np.float32],
        env4: NDArray[np.float32],
        feedback: float,
    ) -> NDArray[np.floating]:
        """Apply FM algorithm to generate output."""
        # Simplified FM: modulation index based on envelope
        mod_index = 4.0  # Base modulation index

        if self.algorithm == FMAlgorithm.ALG0:
            # Serial: 1→2→3→4
            op1 = np.sin(phase1 + feedback * np.sin(phase1)) * env1
            op2 = np.sin(phase2 + mod_index * op1) * env2
            op3 = np.sin(phase3 + mod_index * op2) * env3
            op4 = np.sin(phase4 + mod_index * op3) * env4
            return op4

        elif self.algorithm == FMAlgorithm.ALG1:
            # (1+2)→3→4
            op1 = np.sin(phase1 + feedback * np.sin(phase1)) * env1
            op2 = np.sin(phase2) * env2
            op3 = np.sin(phase3 + mod_index * (op1 + op2) / 2) * env3
            op4 = np.sin(phase4 + mod_index * op3) * env4
            return op4

        elif self.algorithm == FMAlgorithm.ALG2:
            # 2→3→4, 1→4
            op1 = np.sin(phase1 + feedback * np.sin(phase1)) * env1
            op2 = np.sin(phase2) * env2
            op3 = np.sin(phase3 + mod_index * op2) * env3
            op4 = np.sin(phase4 + mod_index * (op3 + op1) / 2) * env4
            return op4

        elif self.algorithm == FMAlgorithm.ALG3:
            # 1→2→4, 3→4
            op1 = np.sin(phase1 + feedback * np.sin(phase1)) * env1
            op2 = np.sin(phase2 + mod_index * op1) * env2
            op3 = np.sin(phase3) * env3
            op4 = np.sin(phase4 + mod_index * (op2 + op3) / 2) * env4
            return op4

        elif self.algorithm == FMAlgorithm.ALG4:
            # 1→2, 3→4 (2 carriers)
            op1 = np.sin(phase1 + feedback * np.sin(phase1)) * env1
            op2 = np.sin(phase2 + mod_index * op1) * env2
            op3 = np.sin(phase3) * env3
            op4 = np.sin(phase4 + mod_index * op3) * env4
            return (op2 + op4) / 2

        elif self.algorithm == FMAlgorithm.ALG5:
            # 1→2, 1→3, 1→4 (3 carriers)
            op1 = np.sin(phase1 + feedback * np.sin(phase1)) * env1
            op2 = np.sin(phase2 + mod_index * op1) * env2
            op3 = np.sin(phase3 + mod_index * op1) * env3
            op4 = np.sin(phase4 + mod_index * op1) * env4
            return (op2 + op3 + op4) / 3

        elif self.algorithm == FMAlgorithm.ALG6:
            # 1→2, 3, 4 (3 carriers)
            op1 = np.sin(phase1 + feedback * np.sin(phase1)) * env1
            op2 = np.sin(phase2 + mod_index * op1) * env2
            op3 = np.sin(phase3) * env3
            op4 = np.sin(phase4) * env4
            return (op2 + op3 + op4) / 3

        else:  # ALG7
            # All parallel (4 carriers, organ-like)
            op1 = np.sin(phase1 + feedback * np.sin(phase1)) * env1
            op2 = np.sin(phase2) * env2
            op3 = np.sin(phase3) * env3
            op4 = np.sin(phase4) * env4
            return (op1 + op2 + op3 + op4) / 4


class GenesisChip(ChipSystem):
    """Sega Genesis/Mega Drive YM2612 FM synthesizer.

    6 FM channels, each with 4 operators.
    Channel 6 can optionally be used for 8-bit DAC output.
    """

    chip_type: ChipType = ChipType.GENESIS
    name: str = "Yamaha YM2612"
    description: str = "Sega Genesis FM synthesizer"

    ch1: FMVoice = Field(default_factory=lambda: FMVoice(voice_id=0))
    ch2: FMVoice = Field(default_factory=lambda: FMVoice(voice_id=1))
    ch3: FMVoice = Field(default_factory=lambda: FMVoice(voice_id=2))
    ch4: FMVoice = Field(default_factory=lambda: FMVoice(voice_id=3))
    ch5: FMVoice = Field(default_factory=lambda: FMVoice(voice_id=4))
    ch6: FMVoice = Field(default_factory=lambda: FMVoice(voice_id=5))

    # Global LFO
    lfo_enable: bool = False
    lfo_frequency: float = 5.0

    # Panning for each channel (-1 to 1)
    pan: list[float] = Field(default_factory=lambda: [0.0] * 6)

    master_volume: float = 0.8

    voice_count: ClassVar[int] = 6
    clock_rate: ClassVar[int] = 7670453

    @property
    def voices(self) -> list[ChipVoice]:
        """Get all FM channels."""
        return [self.ch1, self.ch2, self.ch3, self.ch4, self.ch5, self.ch6]

    def get_voice(self, voice_id: int) -> ChipVoice | None:
        """Get channel by ID (0-5)."""
        channels = [self.ch1, self.ch2, self.ch3, self.ch4, self.ch5, self.ch6]
        if 0 <= voice_id < 6:
            return channels[voice_id]
        return None

    def render(self, tempo: float = 120.0) -> NDArray[np.float32]:
        """Render all channels to stereo."""
        channel_samples = {}
        max_length = 0

        for i, voice in enumerate(self.voices):
            if voice.notes:
                # Apply global LFO settings (voices are FMVoice instances)
                fm_voice = voice if isinstance(voice, FMVoice) else None
                if fm_voice:
                    fm_voice.lfo_enable = self.lfo_enable
                    fm_voice.lfo_frequency = self.lfo_frequency

                samples = self.render_voice(voice.voice_id, tempo)
                channel_samples[i] = samples
                max_length = max(max_length, len(samples))

        if max_length == 0:
            return np.zeros((0, 2), dtype=np.float32)

        left = np.zeros(max_length, dtype=np.float32)
        right = np.zeros(max_length, dtype=np.float32)

        for channel_id, samples in channel_samples.items():
            padded = (
                np.pad(samples, (0, max_length - len(samples)))
                if len(samples) < max_length
                else samples
            )

            pan_value = self.pan[channel_id] if channel_id < len(self.pan) else 0.0

            # Constant power panning
            left_gain = np.sqrt(0.5 * (1 - pan_value))
            right_gain = np.sqrt(0.5 * (1 + pan_value))

            left += padded * left_gain / 6
            right += padded * right_gain / 6

        stereo = np.column_stack([left, right]) * self.master_volume
        stereo = np.tanh(stereo)

        return stereo.astype(np.float32)

    @classmethod
    def create(cls) -> GenesisChip:
        """Create a fresh Genesis chip."""
        return cls()

    @classmethod
    def brass_preset(cls) -> GenesisChip:
        """Classic Genesis brass sound."""
        chip = cls()
        voice = chip.ch1
        voice.algorithm = FMAlgorithm.ALG4

        # OP1 - modulator
        voice.op1.multiple = 1.0
        voice.op1.total_level = 30
        voice.op1.attack_rate = 31
        voice.op1.decay_rate = 10
        voice.op1.sustain_level = 3

        # OP2 - carrier
        voice.op2.multiple = 1.0
        voice.op2.total_level = 0
        voice.op2.attack_rate = 28
        voice.op2.decay_rate = 8

        # OP3 - modulator
        voice.op3.multiple = 1.0
        voice.op3.total_level = 35

        # OP4 - carrier
        voice.op4.multiple = 2.0
        voice.op4.total_level = 10

        return chip

    @classmethod
    def bass_preset(cls) -> GenesisChip:
        """Punchy FM bass."""
        chip = cls()
        voice = chip.ch1
        voice.algorithm = FMAlgorithm.ALG0  # Serial for complex modulation

        voice.op1.multiple = 0.5
        voice.op1.total_level = 20
        voice.op1.feedback = 3
        voice.op1.attack_rate = 31
        voice.op1.decay_rate = 15

        voice.op2.multiple = 1.0
        voice.op2.total_level = 15

        voice.op3.multiple = 1.0
        voice.op3.total_level = 10

        voice.op4.multiple = 1.0
        voice.op4.total_level = 0
        voice.op4.attack_rate = 31
        voice.op4.decay_rate = 12
        voice.op4.sustain_level = 5

        return chip

    @classmethod
    def bell_preset(cls) -> GenesisChip:
        """Metallic bell sound."""
        chip = cls()
        voice = chip.ch1
        voice.algorithm = FMAlgorithm.ALG4

        # Non-harmonic ratios for bell-like inharmonicity
        voice.op1.multiple = 1.0
        voice.op1.total_level = 25
        voice.op1.attack_rate = 31
        voice.op1.decay_rate = 5
        voice.op1.sustain_level = 0

        voice.op2.multiple = 3.5  # Inharmonic ratio
        voice.op2.total_level = 0
        voice.op2.decay_rate = 3

        voice.op3.multiple = 1.0
        voice.op3.total_level = 30

        voice.op4.multiple = 7.0  # High harmonic
        voice.op4.total_level = 10
        voice.op4.decay_rate = 2

        return chip

    @classmethod
    def strings_preset(cls) -> GenesisChip:
        """Warm string pad."""
        chip = cls()
        voice = chip.ch1
        voice.algorithm = FMAlgorithm.ALG7  # All carriers for organ-like blend

        voice.op1.multiple = 1.0
        voice.op1.total_level = 10
        voice.op1.attack_rate = 20
        voice.op1.decay_rate = 0
        voice.op1.sustain_level = 0
        voice.op1.feedback = 2

        voice.op2.multiple = 2.0
        voice.op2.total_level = 15
        voice.op2.attack_rate = 18

        voice.op3.multiple = 3.0
        voice.op3.total_level = 20
        voice.op3.attack_rate = 22

        voice.op4.multiple = 4.0
        voice.op4.total_level = 25
        voice.op4.attack_rate = 24

        # Enable LFO for slight vibrato
        chip.lfo_enable = True
        chip.lfo_frequency = 4.5
        voice.frequency_mod_sensitivity = 2

        return chip
