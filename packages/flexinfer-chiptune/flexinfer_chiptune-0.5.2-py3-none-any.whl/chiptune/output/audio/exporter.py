"""Audio file export for chiptune compositions.

Renders tracks to WAV/OGG files with authentic NES-style
waveforms and envelopes. Supports effects processing.
"""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING, ClassVar

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel

from chiptune.chip.channels import Channel, ChannelType, DutyCycle
from chiptune.output.audio.envelope import ADSREnvelope
from chiptune.output.audio.mixer import ChannelMixer
from chiptune.output.audio.waveforms import (
    NoiseGenerator,
    PulseWaveGenerator,
    TriangleWaveGenerator,
    midi_to_frequency,
)

if TYPE_CHECKING:
    from chiptune.composer.composer import Track
    from chiptune.output.audio.effects import EffectChain, SampleEffect
    from chiptune.theory.arpeggios import Note


class AudioExporter(BaseModel):
    """Export tracks to audio files (WAV/OGG).

    Generates authentic NES-style audio from composition data using
    proper pulse, triangle, and noise waveforms with ADSR envelopes.

    Example:
        ```python
        from chiptune import ChiptuneComposer
        from chiptune.output.audio import AudioExporter

        composer = ChiptuneComposer.create(bpm=140, root="C")
        composer.add_melody(length_bars=8)
        composer.add_bass()
        track = composer.build()

        exporter = AudioExporter()
        exporter.export_wav(track, "output.wav")
        ```
    """

    sample_rate: int = 44100
    bit_depth: int = 16

    # Envelope presets per channel type
    CHANNEL_ENVELOPES: ClassVar[dict[ChannelType, str]] = {
        ChannelType.PULSE: "chip_lead",
        ChannelType.TRIANGLE: "chip_bass",
        ChannelType.NOISE: "percussion",
    }

    def _get_envelope(self, channel_type: ChannelType) -> ADSREnvelope:
        """Get appropriate envelope for channel type."""
        envelope_name = self.CHANNEL_ENVELOPES.get(channel_type, "chip_lead")
        envelope_factory = getattr(ADSREnvelope, envelope_name)
        result: ADSREnvelope = envelope_factory()
        return result

    def render_channel(
        self,
        channel: Channel,
        bpm: int,
        effects: EffectChain | SampleEffect | None = None,
    ) -> NDArray[np.float32]:
        """Render a single channel to audio samples.

        Args:
            channel: Channel with notes
            bpm: Tempo in BPM
            effects: Optional effect chain to apply

        Returns:
            Mono samples as float32 array
        """
        beats_per_second = bpm / 60.0

        # Select waveform generator based on channel type
        from chiptune.output.audio.waveforms import WaveformGenerator

        generator: WaveformGenerator
        if channel.channel_type == ChannelType.PULSE:
            generator = PulseWaveGenerator(
                duty=channel.duty_cycle,
                sample_rate=self.sample_rate,
            )
        elif channel.channel_type == ChannelType.TRIANGLE:
            generator = TriangleWaveGenerator(sample_rate=self.sample_rate)
        elif channel.channel_type == ChannelType.NOISE:
            generator = NoiseGenerator(sample_rate=self.sample_rate)
        else:
            # Default to pulse for unknown types
            generator = PulseWaveGenerator(sample_rate=self.sample_rate)

        # Get envelope for this channel type
        envelope = self._get_envelope(channel.channel_type)

        # Calculate total duration
        total_beats = channel.duration_beats
        total_seconds = total_beats / beats_per_second
        total_samples = int(total_seconds * self.sample_rate)

        if total_samples <= 0:
            return np.array([], dtype=np.float32)

        # Render each note
        output = np.zeros(total_samples, dtype=np.float32)
        current_sample = 0

        for note in channel.notes:
            duration_seconds = note.duration / beats_per_second
            num_samples = int(duration_seconds * self.sample_rate)

            if note.velocity == 0 or num_samples <= 0:
                # Rest - just advance position
                current_sample += num_samples
                continue

            # Generate waveform
            if channel.channel_type == ChannelType.NOISE:
                # Noise uses pitch as period index (0-15)
                samples = generator.generate(
                    frequency=float(note.pitch),
                    duration=duration_seconds,
                )
            else:
                frequency = midi_to_frequency(note.pitch)
                samples = generator.generate(
                    frequency=frequency,
                    duration=duration_seconds,
                )

            # Apply envelope
            velocity = note.velocity / 127.0
            env = envelope.generate(duration_seconds, self.sample_rate, velocity)

            # Ensure same length (take minimum)
            min_len = min(len(samples), len(env))
            samples = samples[:min_len] * env[:min_len]

            # Add to output (handle boundary)
            end_sample = min(current_sample + len(samples), total_samples)
            actual_len = end_sample - current_sample
            if actual_len > 0:
                output[current_sample:end_sample] += samples[:actual_len]

            current_sample += num_samples

        # Apply effects if provided
        if effects is not None:
            from chiptune.output.audio.effects import SampleEffect

            if isinstance(effects, SampleEffect):
                output = effects.process(output, self.sample_rate)
            else:
                output = effects.process(output, self.sample_rate)

        return output

    def render_track(
        self,
        track: Track,
        effects: EffectChain | SampleEffect | None = None,
        channel_effects: dict[int, EffectChain | SampleEffect] | None = None,
    ) -> NDArray[np.float32]:
        """Render a complete Track to stereo audio.

        Args:
            track: Composed Track object
            effects: Master effects applied after mixing
            channel_effects: Per-channel effects (keyed by channel_id)

        Returns:
            Stereo samples as (N, 2) float32 array
        """
        channel_samples: dict[int, NDArray[np.float32]] = {}

        for channel in track.channels.all_channels:
            if channel.notes:
                # Get channel-specific effects if provided
                ch_effects = None
                if channel_effects and channel.channel_id in channel_effects:
                    ch_effects = channel_effects[channel.channel_id]

                samples = self.render_channel(channel, track.bpm, effects=ch_effects)
                if len(samples) > 0:
                    channel_samples[channel.channel_id] = samples

        mixer = ChannelMixer(sample_rate=self.sample_rate)
        stereo = mixer.mix(channel_samples)

        # Apply master effects to mixed stereo output
        if effects is not None:
            from chiptune.output.audio.effects import EffectChain, SampleEffect

            # Apply effects to each channel of stereo
            left = stereo[:, 0]
            right = stereo[:, 1]

            if isinstance(effects, (SampleEffect, EffectChain)):
                left = effects.process(left, self.sample_rate)
                right = effects.process(right, self.sample_rate)

            stereo = np.column_stack([left, right])

        return stereo

    def export_wav(
        self,
        track: Track,
        path: str,
        effects: EffectChain | SampleEffect | None = None,
    ) -> None:
        """Export Track to WAV file.

        Args:
            track: Composed Track object
            path: Output file path
            effects: Optional master effects to apply
        """
        try:
            import soundfile as sf
        except ImportError as e:
            raise ImportError("soundfile not installed. Install with: pip install soundfile") from e

        stereo = self.render_track(track, effects=effects)
        sf.write(path, stereo, self.sample_rate, subtype="PCM_16")

    def export_ogg(
        self,
        track: Track,
        path: str,
        effects: EffectChain | SampleEffect | None = None,
    ) -> None:
        """Export Track to OGG Vorbis file.

        Args:
            track: Composed Track object
            path: Output file path
            effects: Optional master effects to apply
        """
        try:
            import soundfile as sf
        except ImportError as e:
            raise ImportError("soundfile not installed. Install with: pip install soundfile") from e

        stereo = self.render_track(track, effects=effects)
        sf.write(path, stereo, self.sample_rate, format="OGG", subtype="VORBIS")

    def export_bytes(
        self,
        track: Track,
        format: str = "wav",
        effects: EffectChain | SampleEffect | None = None,
    ) -> bytes:
        """Export Track to audio bytes.

        Args:
            track: Composed Track object
            format: "wav" or "ogg"
            effects: Optional master effects to apply

        Returns:
            Audio file as bytes
        """
        try:
            import soundfile as sf
        except ImportError as e:
            raise ImportError("soundfile not installed. Install with: pip install soundfile") from e

        stereo = self.render_track(track, effects=effects)
        buffer = BytesIO()

        if format == "ogg":
            sf.write(buffer, stereo, self.sample_rate, format="OGG", subtype="VORBIS")
        else:
            sf.write(buffer, stereo, self.sample_rate, format="WAV", subtype="PCM_16")

        buffer.seek(0)
        return buffer.getvalue()

    def export_sfx(
        self,
        notes: list[Note],
        tempo: int = 120,
        duty: DutyCycle = DutyCycle.DUTY_25,
    ) -> bytes:
        """Export a list of notes as audio bytes (for SFX).

        Args:
            notes: List of Note objects
            tempo: Tempo in BPM
            duty: Pulse wave duty cycle

        Returns:
            WAV file as bytes
        """
        # Create a temporary channel
        channel = Channel.pulse(channel_id=0, duty=duty)
        channel.add_notes(notes)

        samples = self.render_channel(channel, tempo)

        # Convert mono to stereo (centered)
        stereo = np.column_stack([samples, samples])

        try:
            import soundfile as sf
        except ImportError as e:
            raise ImportError("soundfile not installed. Install with: pip install soundfile") from e

        buffer = BytesIO()
        sf.write(buffer, stereo, self.sample_rate, format="WAV", subtype="PCM_16")
        buffer.seek(0)
        return buffer.getvalue()
