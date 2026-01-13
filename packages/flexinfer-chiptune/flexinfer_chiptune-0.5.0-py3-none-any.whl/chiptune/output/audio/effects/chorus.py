"""Chorus and unison effects for depth and richness.

Chorus creates depth by layering multiple slightly-detuned copies
of the signal. This simulates the natural variation of multiple
instruments or voices playing together.
"""

import numpy as np
from numpy.typing import NDArray
from pydantic import Field
from scipy import signal as scipy_signal

from chiptune.output.audio.effects.base import SampleEffect
from chiptune.output.audio.effects.lfo import LFO, LFOShape


class Chorus(SampleEffect):
    """Classic chorus effect for depth and movement.

    Creates multiple delayed copies of the input, each with slightly
    varying delay times controlled by LFOs. This creates a shimmering,
    ensemble-like effect.

    Attributes:
        voices: Number of chorus voices (2-4 typical)
        depth: Delay modulation depth in ms
        rate: LFO modulation rate in Hz
        mix: Wet/dry mix (0.0 = dry, 1.0 = wet only)
        spread: Stereo spread of voices (0.0 = mono, 1.0 = wide)
        feedback: Subtle feedback for more movement
    """

    voices: int = Field(default=3, ge=2, le=8)
    depth: float = Field(default=3.0, ge=0.5, le=10.0)  # milliseconds
    rate: float = Field(default=0.8, ge=0.1, le=5.0)  # Hz
    mix: float = Field(default=0.5, ge=0.0, le=1.0)
    spread: float = Field(default=0.7, ge=0.0, le=1.0)
    feedback: float = Field(default=0.1, ge=0.0, le=0.5)

    def process(
        self,
        samples: NDArray[np.float32],
        sample_rate: int = 44100,
    ) -> NDArray[np.float32]:
        """Apply chorus effect.

        Args:
            samples: Input audio samples
            sample_rate: Sample rate in Hz

        Returns:
            Chorused audio samples
        """
        if len(samples) == 0:
            return samples

        # Base delay (center of modulation)
        base_delay_ms = 20.0
        base_delay_samples = int(base_delay_ms * sample_rate / 1000)
        depth_samples = int(self.depth * sample_rate / 1000)

        output = np.zeros_like(samples)

        for voice in range(self.voices):
            # Each voice has slightly different LFO rate and phase
            voice_rate = self.rate * (1.0 + voice * 0.1)
            voice_phase = voice / self.voices

            lfo = LFO(rate=voice_rate, depth=1.0, shape=LFOShape.SINE, phase=voice_phase)
            modulation = lfo.generate(len(samples), sample_rate)

            # Calculate delay for each sample
            delay_mod = (modulation * depth_samples).astype(np.int32)
            delays = base_delay_samples + delay_mod

            # Read from delayed positions
            voice_output = np.zeros_like(samples)
            for i in range(len(samples)):
                read_pos = i - delays[i]
                if read_pos >= 0:
                    voice_output[i] = samples[read_pos]

            # Apply subtle highpass to remove DC offset
            # and subtle lowpass for warmth
            nyquist = sample_rate / 2
            b_hp, a_hp = scipy_signal.butter(1, 80 / nyquist, btype="high")
            voice_output = scipy_signal.lfilter(b_hp, a_hp, voice_output)

            # Voice level (center voice slightly louder)
            center = self.voices // 2
            distance = abs(voice - center)
            level = 1.0 - distance * 0.15

            output += voice_output.astype(np.float32) * level

        # Normalize by number of voices
        output = output / self.voices

        # Mix dry and wet
        result = samples * (1 - self.mix) + output * self.mix

        return result.astype(np.float32)

    @classmethod
    def subtle(cls) -> "Chorus":
        """Subtle, transparent chorus."""
        return cls(voices=2, depth=2.0, rate=0.5, mix=0.3)

    @classmethod
    def classic(cls) -> "Chorus":
        """Classic 80s chorus sound."""
        return cls(voices=3, depth=3.5, rate=0.8, mix=0.5)

    @classmethod
    def lush(cls) -> "Chorus":
        """Rich, lush ensemble effect."""
        return cls(voices=4, depth=4.0, rate=0.6, mix=0.6, feedback=0.15)

    @classmethod
    def shimmer(cls) -> "Chorus":
        """Shimmering, ethereal effect."""
        return cls(voices=4, depth=5.0, rate=1.2, mix=0.55, spread=0.9)


class Unison(SampleEffect):
    """Unison detuning for thickness without movement.

    Unlike chorus which uses modulated delays, unison creates
    static detuned copies for a thick, "stacked" sound.
    This is great for leads and bass.

    Attributes:
        voices: Number of voices (including center)
        detune: Detuning amount in cents (100 cents = 1 semitone)
        mix: Blend between original and detuned voices
        spread: Stereo spread
    """

    voices: int = Field(default=3, ge=2, le=7)
    detune: float = Field(default=10.0, ge=1.0, le=50.0)  # cents
    mix: float = Field(default=0.7, ge=0.0, le=1.0)
    spread: float = Field(default=0.5, ge=0.0, le=1.0)

    def process(
        self,
        samples: NDArray[np.float32],
        sample_rate: int = 44100,
    ) -> NDArray[np.float32]:
        """Apply unison detuning.

        Note: True unison requires pitch shifting, which is complex.
        This uses a simplified approach with variable delay for
        slight pitch variation.

        Args:
            samples: Input audio samples
            sample_rate: Sample rate in Hz

        Returns:
            Thickened audio samples
        """
        if len(samples) == 0:
            return samples

        output = samples.copy()

        for voice in range(1, self.voices):
            # Alternate detuning up and down
            direction = 1 if voice % 2 == 1 else -1
            voice_detune = self.detune * ((voice + 1) // 2) * direction

            # Convert cents to pitch ratio
            ratio = 2.0 ** (voice_detune / 1200.0)

            # Simple resampling for pitch shift
            original_len = len(samples)
            resampled_len = int(original_len / ratio)

            if resampled_len > 0:
                # Resample
                indices = np.linspace(0, original_len - 1, resampled_len)
                resampled = np.interp(indices, np.arange(original_len), samples)

                # Pad or trim to match original length
                if len(resampled) < original_len:
                    padded = np.zeros(original_len, dtype=np.float32)
                    padded[: len(resampled)] = resampled
                    resampled = padded
                else:
                    resampled = resampled[:original_len]

                # Voice level decreases with distance from center
                level = 1.0 / (voice + 1)
                output += resampled.astype(np.float32) * level

        # Normalize
        output = output / (1 + sum(1.0 / (v + 1) for v in range(1, self.voices)))

        # Mix
        result = samples * (1 - self.mix) + output * self.mix

        return result.astype(np.float32)

    @classmethod
    def supersaw(cls) -> "Unison":
        """Classic supersaw detuning."""
        return cls(voices=7, detune=15.0, mix=0.8)

    @classmethod
    def thick_bass(cls) -> "Unison":
        """Thick bass unison."""
        return cls(voices=3, detune=8.0, mix=0.6)

    @classmethod
    def subtle(cls) -> "Unison":
        """Subtle thickness."""
        return cls(voices=2, detune=5.0, mix=0.4)


class Ensemble(SampleEffect):
    """Combines chorus and slight pitch modulation for rich ensemble sound.

    This creates the effect of multiple instruments playing together,
    with natural variations in pitch and timing.
    """

    size: int = Field(default=4, ge=2, le=8)  # ensemble size
    detune: float = Field(default=5.0, ge=1.0, le=20.0)  # cents
    drift: float = Field(default=0.3, ge=0.0, le=1.0)  # random drift amount
    warmth: float = Field(default=0.5, ge=0.0, le=1.0)  # lowpass amount
    mix: float = Field(default=0.6, ge=0.0, le=1.0)

    def process(
        self,
        samples: NDArray[np.float32],
        sample_rate: int = 44100,
    ) -> NDArray[np.float32]:
        """Apply ensemble effect.

        Args:
            samples: Input audio samples
            sample_rate: Sample rate in Hz

        Returns:
            Ensemble-processed audio
        """
        if len(samples) == 0:
            return samples

        output = np.zeros_like(samples)
        rng = np.random.default_rng(42)

        for _voice in range(self.size):
            # Random but consistent detuning per voice
            voice_detune = rng.uniform(-self.detune, self.detune)
            ratio = 2.0 ** (voice_detune / 1200.0)

            # Random timing offset (slight delay variation)
            delay_samples = int(rng.uniform(0, 0.005 * sample_rate))

            # Apply pitch shift via resampling
            original_len = len(samples)
            resampled_len = int(original_len / ratio)

            if resampled_len > 0:
                indices = np.linspace(0, original_len - 1, resampled_len)
                resampled = np.interp(indices, np.arange(original_len), samples)

                # Pad to original length
                if len(resampled) < original_len:
                    padded = np.zeros(original_len, dtype=np.float32)
                    padded[: len(resampled)] = resampled
                    resampled = padded
                else:
                    resampled = resampled[:original_len]

                # Apply delay
                if delay_samples > 0:
                    delayed = np.zeros_like(resampled)
                    delayed[delay_samples:] = resampled[:-delay_samples]
                    resampled = delayed

                # Add slow random drift (simulates human/analog variation)
                if self.drift > 0:
                    drift_lfo = LFO(
                        rate=rng.uniform(0.2, 0.8),
                        depth=self.drift * 0.003,
                        shape=LFOShape.SINE,
                        phase=rng.uniform(0, 1),
                    )
                    drift = drift_lfo.generate(len(resampled), sample_rate)
                    # Apply as subtle amplitude variation
                    resampled = resampled * (1 + drift)

                output += resampled.astype(np.float32)

        # Normalize by ensemble size
        output = output / self.size

        # Apply warmth (subtle lowpass)
        if self.warmth > 0:
            cutoff = 8000 - self.warmth * 4000  # 8kHz to 4kHz
            nyquist = sample_rate / 2
            b, a = scipy_signal.butter(1, min(cutoff, nyquist * 0.95) / nyquist)
            output = scipy_signal.lfilter(b, a, output).astype(np.float32)

        # Mix
        result = samples * (1 - self.mix) + output * self.mix

        return result.astype(np.float32)

    @classmethod
    def strings(cls) -> "Ensemble":
        """String ensemble sound."""
        return cls(size=6, detune=8.0, drift=0.4, warmth=0.6, mix=0.7)

    @classmethod
    def synth_pad(cls) -> "Ensemble":
        """Synth pad ensemble."""
        return cls(size=4, detune=12.0, drift=0.3, warmth=0.4, mix=0.65)

    @classmethod
    def choir(cls) -> "Ensemble":
        """Choir-like ensemble."""
        return cls(size=5, detune=6.0, drift=0.5, warmth=0.5, mix=0.6)
