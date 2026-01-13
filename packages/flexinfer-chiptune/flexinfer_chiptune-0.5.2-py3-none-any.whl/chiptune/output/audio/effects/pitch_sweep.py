"""Pitch sweep and portamento effects.

NES-style pitch sweeps and smooth glides between notes.
"""

from enum import Enum
from typing import Literal

import numpy as np
from numpy.typing import NDArray
from pydantic import Field

from chiptune.output.audio.effects.base import PitchEffect


class SweepDirection(str, Enum):
    """Pitch sweep direction."""

    UP = "up"
    DOWN = "down"


class PitchSweep(PitchEffect):
    """NES-style hardware pitch sweep.

    Emulates the 2A03's sweep unit which automatically shifts
    the pitch up or down over time. Used for characteristic
    NES sound effects like falling/rising tones.

    The NES sweep formula:
    - period = period +/- (period >> shift)
    - Applied every N frames

    Attributes:
        direction: Sweep up or down
        rate: How fast to sweep (1 = fast, 7 = slow)
        shift: Amount to shift per step (1-7, higher = smaller change)
        start_delay: Delay before sweep starts (seconds)
    """

    direction: SweepDirection = SweepDirection.DOWN
    rate: int = Field(default=3, ge=1, le=7)
    shift: int = Field(default=2, ge=1, le=7)
    start_delay: float = Field(default=0.0, ge=0.0, le=2.0)

    def modulate_frequency(
        self,
        base_frequency: float,
        time_array: NDArray[np.float32],
        sample_rate: int = 44100,
    ) -> NDArray[np.float32]:
        """Generate swept frequency values.

        Args:
            base_frequency: Starting frequency in Hz
            time_array: Time values for each sample
            sample_rate: Sample rate in Hz

        Returns:
            Array of frequency values with sweep applied
        """
        if len(time_array) == 0:
            return np.array([], dtype=np.float32)

        # NES sweeps update at ~120Hz (every other frame at 60fps)
        sweep_rate_hz = 120.0 / (self.rate + 1)
        samples_per_sweep = int(sample_rate / sweep_rate_hz)

        # Convert frequency to period (samples per cycle)
        period = sample_rate / base_frequency

        frequencies = np.zeros(len(time_array), dtype=np.float32)
        current_period = period

        delay_samples = int(self.start_delay * sample_rate)

        for i in range(len(time_array)):
            if i < delay_samples:
                frequencies[i] = base_frequency
            else:
                frequencies[i] = sample_rate / current_period

                # Apply sweep at intervals
                if (i - delay_samples) % samples_per_sweep == 0:
                    # NES-style bit shift on period (convert to int for shift)
                    delta = int(current_period) >> self.shift

                    if self.direction == SweepDirection.UP:
                        # Period decreases = frequency increases
                        current_period = max(8.0, current_period - delta)
                    else:
                        # Period increases = frequency decreases
                        current_period = min(current_period + delta, float(0x7FF))

        return frequencies

    @classmethod
    def nes_up(cls) -> "PitchSweep":
        """Classic NES rising sweep (laser sound)."""
        return cls(direction=SweepDirection.UP, rate=2, shift=3)

    @classmethod
    def nes_down(cls) -> "PitchSweep":
        """Classic NES falling sweep (explosion/hit)."""
        return cls(direction=SweepDirection.DOWN, rate=3, shift=2)

    @classmethod
    def slow_rise(cls) -> "PitchSweep":
        """Slow dramatic rise."""
        return cls(direction=SweepDirection.UP, rate=6, shift=4)

    @classmethod
    def fast_drop(cls) -> "PitchSweep":
        """Fast pitch drop."""
        return cls(direction=SweepDirection.DOWN, rate=1, shift=1)


class Portamento(PitchEffect):
    """Smooth pitch glide between notes.

    Creates a smooth transition from one pitch to another,
    also known as glide or legato. Essential for expressive
    melodies and bass lines.

    Attributes:
        start_frequency: Starting frequency (Hz)
        glide_time: Time to complete glide (seconds)
        curve: Glide curve type (linear, exponential, logarithmic)
    """

    start_frequency: float = Field(default=220.0, ge=20.0, le=20000.0)
    glide_time: float = Field(default=0.1, ge=0.01, le=2.0)
    curve: Literal["linear", "exponential", "logarithmic"] = "exponential"

    def modulate_frequency(
        self,
        base_frequency: float,
        time_array: NDArray[np.float32],
        sample_rate: int = 44100,
    ) -> NDArray[np.float32]:
        """Generate glided frequency values.

        Args:
            base_frequency: Target (ending) frequency in Hz
            time_array: Time values for each sample
            sample_rate: Sample rate in Hz

        Returns:
            Array of frequency values with glide applied
        """
        if len(time_array) == 0:
            return np.array([], dtype=np.float32)

        glide_samples = int(self.glide_time * sample_rate)
        total_samples = len(time_array)

        frequencies = np.zeros(total_samples, dtype=np.float32)

        if self.curve == "linear":
            # Linear interpolation in frequency
            for i in range(total_samples):
                if i < glide_samples:
                    t = i / glide_samples
                    frequencies[i] = (
                        self.start_frequency + (base_frequency - self.start_frequency) * t
                    )
                else:
                    frequencies[i] = base_frequency

        elif self.curve == "exponential":
            # Exponential interpolation (more musical)
            log_start = np.log2(self.start_frequency)
            log_end = np.log2(base_frequency)

            for i in range(total_samples):
                if i < glide_samples:
                    t = i / glide_samples
                    # Smooth exponential curve
                    t_smooth = t * t * (3 - 2 * t)  # smoothstep
                    log_freq = log_start + (log_end - log_start) * t_smooth
                    frequencies[i] = 2.0**log_freq
                else:
                    frequencies[i] = base_frequency

        elif self.curve == "logarithmic":
            # Logarithmic curve (fast start, slow end)
            log_start = np.log2(self.start_frequency)
            log_end = np.log2(base_frequency)

            for i in range(total_samples):
                if i < glide_samples:
                    t = i / glide_samples
                    t_log = np.sqrt(t)  # Fast start
                    log_freq = log_start + (log_end - log_start) * t_log
                    frequencies[i] = 2.0**log_freq
                else:
                    frequencies[i] = base_frequency

        return frequencies.astype(np.float32)

    @classmethod
    def fast(cls, start_freq: float = 220.0) -> "Portamento":
        """Fast glide (good for bass)."""
        return cls(start_frequency=start_freq, glide_time=0.05, curve="exponential")

    @classmethod
    def medium(cls, start_freq: float = 220.0) -> "Portamento":
        """Medium glide speed."""
        return cls(start_frequency=start_freq, glide_time=0.15, curve="exponential")

    @classmethod
    def slow(cls, start_freq: float = 220.0) -> "Portamento":
        """Slow expressive glide."""
        return cls(start_frequency=start_freq, glide_time=0.3, curve="exponential")

    @classmethod
    def octave_up(cls, base_freq: float = 220.0) -> "Portamento":
        """Glide up one octave."""
        return cls(start_frequency=base_freq / 2, glide_time=0.12, curve="exponential")

    @classmethod
    def octave_down(cls, base_freq: float = 440.0) -> "Portamento":
        """Glide down one octave."""
        return cls(start_frequency=base_freq * 2, glide_time=0.12, curve="exponential")


class PitchBend(PitchEffect):
    """Pitch bend over time with return.

    Creates a pitch bend that goes up/down and optionally returns,
    useful for expression and sound design.

    Attributes:
        bend_semitones: Amount to bend in semitones
        bend_time: Time to reach full bend
        hold_time: Time to hold at bent position
        return_time: Time to return to base pitch (0 = stay bent)
    """

    bend_semitones: float = Field(default=2.0, ge=-24.0, le=24.0)
    bend_time: float = Field(default=0.1, ge=0.01, le=2.0)
    hold_time: float = Field(default=0.0, ge=0.0, le=5.0)
    return_time: float = Field(default=0.1, ge=0.0, le=2.0)

    def modulate_frequency(
        self,
        base_frequency: float,
        time_array: NDArray[np.float32],
        sample_rate: int = 44100,
    ) -> NDArray[np.float32]:
        """Generate pitch-bent frequency values.

        Args:
            base_frequency: Base frequency in Hz
            time_array: Time values for each sample
            sample_rate: Sample rate in Hz

        Returns:
            Array of frequency values with bend applied
        """
        if len(time_array) == 0:
            return np.array([], dtype=np.float32)

        bend_samples = int(self.bend_time * sample_rate)
        hold_samples = int(self.hold_time * sample_rate)
        return_samples = int(self.return_time * sample_rate)

        frequencies = np.zeros(len(time_array), dtype=np.float32)

        for i in range(len(time_array)):
            if i < bend_samples:
                # Bending phase
                t = i / bend_samples
                semitones = self.bend_semitones * t
            elif i < bend_samples + hold_samples:
                # Hold phase
                semitones = self.bend_semitones
            elif self.return_time > 0 and i < bend_samples + hold_samples + return_samples:
                # Return phase
                t = (i - bend_samples - hold_samples) / return_samples
                semitones = self.bend_semitones * (1 - t)
            # After return or no return
            elif self.return_time > 0:
                semitones = 0.0
            else:
                semitones = self.bend_semitones

            frequencies[i] = base_frequency * (2.0 ** (semitones / 12.0))

        return frequencies.astype(np.float32)

    @classmethod
    def cry(cls) -> "PitchBend":
        """Crying/wailing bend up."""
        return cls(bend_semitones=2.0, bend_time=0.15, hold_time=0.1, return_time=0.2)

    @classmethod
    def dive(cls) -> "PitchBend":
        """Dive bomb down."""
        return cls(bend_semitones=-12.0, bend_time=0.3, hold_time=0.0, return_time=0.0)

    @classmethod
    def scoop(cls) -> "PitchBend":
        """Scoop up into note."""
        return cls(bend_semitones=-2.0, bend_time=0.0, hold_time=0.0, return_time=0.08)
