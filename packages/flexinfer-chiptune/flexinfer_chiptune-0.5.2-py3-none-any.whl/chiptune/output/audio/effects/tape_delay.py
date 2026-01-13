"""Tape delay effect - analog-style delay with character.

Simulates vintage tape echo units like the Roland Space Echo or Echoplex,
with characteristics like:
- High-frequency rolloff on each repeat
- Subtle pitch warble (wow/flutter)
- Soft saturation
- Natural feedback decay
"""

import numpy as np
from numpy.typing import NDArray
from pydantic import Field
from scipy import signal as scipy_signal

from chiptune.output.audio.effects.base import SampleEffect
from chiptune.output.audio.effects.lfo import LFO, LFOShape


class TapeDelay(SampleEffect):
    """Tape-style delay with analog character.

    Attributes:
        delay_time: Delay time in seconds (tap tempo)
        feedback: Amount of signal fed back (0.0-0.95)
        mix: Wet/dry mix (0.0 = dry, 1.0 = wet only)
        tape_age: Simulated tape wear (0.0 = pristine, 1.0 = worn)
        wow_depth: Pitch wobble depth (tape speed variation)
        flutter_depth: Fast pitch variation depth
        saturation: Tape saturation amount (0.0-1.0)
        highcut: High frequency cutoff in Hz (tape loses treble)
    """

    delay_time: float = Field(default=0.3, ge=0.01, le=2.0)
    feedback: float = Field(default=0.5, ge=0.0, le=0.95)
    mix: float = Field(default=0.5, ge=0.0, le=1.0)
    tape_age: float = Field(default=0.3, ge=0.0, le=1.0)
    wow_depth: float = Field(default=0.002, ge=0.0, le=0.01)
    flutter_depth: float = Field(default=0.0005, ge=0.0, le=0.002)
    saturation: float = Field(default=0.3, ge=0.0, le=1.0)
    highcut: float = Field(default=4000.0, ge=500.0, le=20000.0)

    def _soft_clip(self, samples: NDArray[np.float32]) -> NDArray[np.float32]:
        """Apply soft saturation (tape compression)."""
        if self.saturation == 0:
            return samples

        # Blend between clean and saturated
        drive = 1.0 + self.saturation * 3.0
        saturated = np.tanh(samples * drive) / np.tanh(drive)
        result: NDArray[np.float32] = (
            samples * (1 - self.saturation) + saturated * self.saturation
        ).astype(np.float32)
        return result

    def _apply_lowpass(self, samples: NDArray[np.float32], sample_rate: int) -> NDArray[np.float32]:
        """Apply lowpass filter (tape loses high frequencies)."""
        nyquist = sample_rate / 2
        cutoff = min(self.highcut, nyquist * 0.95)
        normalized_cutoff = cutoff / nyquist

        # Simple 2nd order lowpass
        b, a = scipy_signal.butter(2, normalized_cutoff, btype="low")
        filtered: NDArray[np.float32] = scipy_signal.lfilter(b, a, samples).astype(np.float32)
        return filtered

    def _generate_wow_flutter(self, num_samples: int, sample_rate: int) -> NDArray[np.float32]:
        """Generate combined wow (slow) and flutter (fast) modulation."""
        if self.wow_depth == 0 and self.flutter_depth == 0:
            return np.zeros(num_samples, dtype=np.float32)

        modulation = np.zeros(num_samples, dtype=np.float32)

        # Wow: slow, random-ish pitch drift (0.5-2 Hz)
        if self.wow_depth > 0:
            wow_lfo = LFO(rate=0.8, depth=self.wow_depth, shape=LFOShape.SINE)
            modulation += wow_lfo.generate(num_samples, sample_rate)

            # Add slight randomness to wow
            wow_lfo2 = LFO(rate=1.3, depth=self.wow_depth * 0.5, shape=LFOShape.TRIANGLE)
            modulation += wow_lfo2.generate(num_samples, sample_rate)

        # Flutter: faster, mechanical variation (5-15 Hz)
        if self.flutter_depth > 0:
            flutter_lfo = LFO(rate=9.0, depth=self.flutter_depth, shape=LFOShape.TRIANGLE)
            modulation += flutter_lfo.generate(num_samples, sample_rate)

        return modulation

    def _modulated_delay_read(
        self,
        buffer: NDArray[np.float32],
        write_pos: int,
        delay_samples: int,
        modulation: float,
        sample_rate: int,
    ) -> float:
        """Read from delay buffer with pitch modulation."""
        # Modulation affects delay time
        mod_delay = delay_samples * (1.0 + modulation)
        read_pos = write_pos - int(mod_delay)

        # Wrap around buffer
        read_pos = read_pos % len(buffer)
        return float(buffer[read_pos])

    def process(
        self,
        samples: NDArray[np.float32],
        sample_rate: int = 44100,
    ) -> NDArray[np.float32]:
        """Apply tape delay effect.

        Args:
            samples: Input audio samples
            sample_rate: Sample rate in Hz

        Returns:
            Delayed audio with tape character
        """
        if len(samples) == 0:
            return samples

        delay_samples = int(self.delay_time * sample_rate)

        # Generate wow/flutter modulation
        wow_flutter = self._generate_wow_flutter(len(samples), sample_rate)

        # Delay buffer (extra space for modulation)
        buffer_size = delay_samples + int(0.02 * sample_rate) + len(samples)
        delay_buffer = np.zeros(buffer_size, dtype=np.float32)

        output = np.zeros_like(samples)

        for i in range(len(samples)):
            # Read from delay line with modulation
            mod = wow_flutter[i] if len(wow_flutter) > i else 0.0
            mod_delay = int(delay_samples * (1.0 + mod))
            read_pos = (i - mod_delay) % buffer_size

            if read_pos >= 0 and read_pos < buffer_size:
                delayed = delay_buffer[read_pos]
            else:
                delayed = 0.0

            # Write input + feedback to buffer
            feedback_signal = delayed * self.feedback
            delay_buffer[i % buffer_size] = samples[i] + feedback_signal

            # Store wet signal
            output[i] = delayed

        # Apply tape character to wet signal
        output = self._soft_clip(output)
        output = self._apply_lowpass(output, sample_rate)

        # Add subtle noise based on tape age
        if self.tape_age > 0:
            noise = np.random.default_rng(42).normal(0, 0.001 * self.tape_age, len(output))
            output = output + noise.astype(np.float32)

        # Mix dry and wet
        result = samples * (1 - self.mix) + output * self.mix

        return result.astype(np.float32)

    @classmethod
    def space_echo(cls) -> "TapeDelay":
        """Classic Roland Space Echo style."""
        return cls(
            delay_time=0.35,
            feedback=0.55,
            mix=0.4,
            tape_age=0.3,
            wow_depth=0.003,
            flutter_depth=0.0008,
            saturation=0.35,
            highcut=3500.0,
        )

    @classmethod
    def slapback(cls) -> "TapeDelay":
        """Rockabilly slapback echo."""
        return cls(
            delay_time=0.12,
            feedback=0.2,
            mix=0.5,
            tape_age=0.2,
            wow_depth=0.001,
            flutter_depth=0.0003,
            saturation=0.2,
            highcut=5000.0,
        )

    @classmethod
    def dub(cls) -> "TapeDelay":
        """Dub reggae style heavy delay."""
        return cls(
            delay_time=0.45,
            feedback=0.7,
            mix=0.6,
            tape_age=0.5,
            wow_depth=0.004,
            flutter_depth=0.001,
            saturation=0.5,
            highcut=2500.0,
        )

    @classmethod
    def lo_fi(cls) -> "TapeDelay":
        """Lo-fi worn tape character."""
        return cls(
            delay_time=0.3,
            feedback=0.4,
            mix=0.45,
            tape_age=0.8,
            wow_depth=0.006,
            flutter_depth=0.0015,
            saturation=0.6,
            highcut=2000.0,
        )

    @classmethod
    def pristine(cls) -> "TapeDelay":
        """Clean, new tape sound."""
        return cls(
            delay_time=0.25,
            feedback=0.45,
            mix=0.35,
            tape_age=0.0,
            wow_depth=0.0008,
            flutter_depth=0.0002,
            saturation=0.1,
            highcut=6000.0,
        )


class MultiTapDelay(SampleEffect):
    """Multi-tap tape delay for rhythmic patterns.

    Creates multiple delay taps at different times, like a multi-head
    tape delay unit.
    """

    taps: list[float] = Field(default=[0.25, 0.5, 0.75])  # delay times in seconds
    tap_levels: list[float] = Field(default=[0.8, 0.5, 0.3])  # level per tap
    feedback: float = Field(default=0.3, ge=0.0, le=0.9)
    mix: float = Field(default=0.5, ge=0.0, le=1.0)
    highcut: float = Field(default=4000.0, ge=500.0, le=20000.0)

    def process(
        self,
        samples: NDArray[np.float32],
        sample_rate: int = 44100,
    ) -> NDArray[np.float32]:
        """Apply multi-tap delay.

        Args:
            samples: Input audio samples
            sample_rate: Sample rate in Hz

        Returns:
            Multi-tap delayed audio
        """
        if len(samples) == 0:
            return samples

        output = np.zeros_like(samples)

        # Ensure we have levels for all taps
        levels = self.tap_levels + [0.3] * (len(self.taps) - len(self.tap_levels))

        for tap_time, level in zip(self.taps, levels, strict=False):
            delay_samples = int(tap_time * sample_rate)
            if delay_samples < len(samples):
                # Simple delay (no modulation for multi-tap)
                delayed = np.zeros_like(samples)
                delayed[delay_samples:] = samples[:-delay_samples] * level
                output += delayed

        # Apply lowpass to wet signal
        nyquist = sample_rate / 2
        cutoff = min(self.highcut, nyquist * 0.95)
        b, a = scipy_signal.butter(2, cutoff / nyquist, btype="low")
        output = scipy_signal.lfilter(b, a, output).astype(np.float32)

        # Mix
        result = samples * (1 - self.mix) + output * self.mix
        return result.astype(np.float32)

    @classmethod
    def triplet(cls) -> "MultiTapDelay":
        """Triplet rhythm pattern."""
        return cls(
            taps=[0.167, 0.333, 0.5],
            tap_levels=[0.7, 0.5, 0.35],
            feedback=0.25,
            mix=0.45,
        )

    @classmethod
    def dotted_eighth(cls) -> "MultiTapDelay":
        """Dotted eighth note pattern (U2 style)."""
        return cls(
            taps=[0.375, 0.75],
            tap_levels=[0.6, 0.4],
            feedback=0.35,
            mix=0.5,
        )
