"""MIDI file export for chiptune compositions.

Uses midiutil to generate standard MIDI files that can be
played in any DAW or synthesizer.
"""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING, ClassVar

from midiutil import MIDIFile
from pydantic import BaseModel

from chiptune.chip.channels import ChannelType, NESChannels

if TYPE_CHECKING:
    from chiptune.composer.composer import Track
    from chiptune.patterns.jingles import Jingle
    from chiptune.theory.arpeggios import Note


class MidiExporter(BaseModel):
    """Export tracks and jingles to MIDI format.

    Maps chiptune channels to appropriate MIDI channels and
    instruments for authentic retro sound.
    """

    # MIDI channel assignments (0-indexed)
    # Channel 9 is reserved for drums in General MIDI
    CHANNEL_MAP: ClassVar[dict[int, int]] = {
        NESChannels.PULSE1_ID: 0,  # Lead synth
        NESChannels.PULSE2_ID: 1,  # Harmony synth
        NESChannels.TRIANGLE_ID: 2,  # Bass
        NESChannels.NOISE_ID: 9,  # Drums (GM drum channel)
    }

    # General MIDI program numbers for chiptune sounds
    # These approximate 8-bit sounds on GM synths
    INSTRUMENT_MAP: ClassVar[dict[ChannelType, int]] = {
        ChannelType.PULSE: 80,  # Lead 1 (square)
        ChannelType.TRIANGLE: 38,  # Synth Bass 1
        ChannelType.NOISE: 0,  # Handled by drum channel
        ChannelType.WAVE: 81,  # Lead 2 (sawtooth)
    }

    # Alternative "authentic" instruments
    AUTHENTIC_INSTRUMENTS: ClassVar[dict[ChannelType, int]] = {
        ChannelType.PULSE: 80,  # Lead 1 (square)
        ChannelType.TRIANGLE: 80,  # Also square for authenticity
        ChannelType.NOISE: 0,
        ChannelType.WAVE: 81,
    }

    use_authentic_instruments: bool = False

    def _get_instrument(self, channel_type: ChannelType) -> int:
        """Get MIDI program number for channel type."""
        instruments = (
            self.AUTHENTIC_INSTRUMENTS if self.use_authentic_instruments else self.INSTRUMENT_MAP
        )
        return instruments.get(channel_type, 80)

    def export_bytes(self, track: Track) -> bytes:
        """Export a Track to MIDI bytes.

        Args:
            track: Composed Track object

        Returns:
            MIDI file as bytes
        """

        # Create MIDI file with 4 tracks (one per NES channel)
        midi = MIDIFile(4, deinterleave=False)

        # Set tempo on first track
        midi.addTempo(0, 0, track.bpm)

        # Add track names
        midi.addTrackName(0, 0, "Pulse 1 - Melody")
        midi.addTrackName(1, 0, "Pulse 2 - Harmony")
        midi.addTrackName(2, 0, "Triangle - Bass")
        midi.addTrackName(3, 0, "Noise - Drums")

        # Set instruments for each channel
        channels = track.channels.all_channels
        for i, channel in enumerate(channels):
            midi_channel = self.CHANNEL_MAP.get(channel.channel_id, i)

            # Don't set program change for drum channel
            if midi_channel != 9:
                program = self._get_instrument(channel.channel_type)
                midi.addProgramChange(i, midi_channel, 0, program)

            # Add notes
            current_time = 0.0
            for note in channel.notes:
                if note.velocity > 0:  # Skip rests
                    midi.addNote(
                        track=i,
                        channel=midi_channel,
                        pitch=note.pitch,
                        time=current_time,
                        duration=note.duration,
                        volume=note.velocity,
                    )
                current_time += note.duration

        # Write to bytes
        buffer = BytesIO()
        midi.writeFile(buffer)
        return buffer.getvalue()

    def export_file(self, track: Track, path: str) -> None:
        """Export a Track to a MIDI file.

        Args:
            track: Composed Track object
            path: Output file path
        """
        midi_bytes = self.export_bytes(track)
        with open(path, "wb") as f:
            f.write(midi_bytes)

    def export_jingle_bytes(self, jingle: Jingle) -> bytes:
        """Export a Jingle to MIDI bytes.

        Args:
            jingle: Jingle object

        Returns:
            MIDI file as bytes
        """

        # Create single-track MIDI
        midi = MIDIFile(1)

        midi.addTempo(0, 0, jingle.tempo)
        midi.addTrackName(0, 0, f"Jingle - {jingle.jingle_type.value}")

        # Use pulse wave sound
        midi.addProgramChange(0, 0, 0, 80)  # Lead 1 (square)

        # Add notes
        current_time = 0.0
        for note in jingle.notes:
            if note.velocity > 0:
                midi.addNote(
                    track=0,
                    channel=0,
                    pitch=note.pitch,
                    time=current_time,
                    duration=note.duration,
                    volume=note.velocity,
                )
            current_time += note.duration

        # Write to bytes
        buffer = BytesIO()
        midi.writeFile(buffer)
        return buffer.getvalue()

    def export_jingle_file(self, jingle: Jingle, path: str) -> None:
        """Export a Jingle to a MIDI file.

        Args:
            jingle: Jingle object
            path: Output file path
        """
        midi_bytes = self.export_jingle_bytes(jingle)
        with open(path, "wb") as f:
            f.write(midi_bytes)

    def export_sfx_bytes(self, notes: list[Note], tempo: int = 120) -> bytes:
        """Export a list of notes as a sound effect.

        Args:
            notes: List of Note objects
            tempo: Tempo in BPM

        Returns:
            MIDI file as bytes
        """

        midi = MIDIFile(1)
        midi.addTempo(0, 0, tempo)
        midi.addProgramChange(0, 0, 0, 80)  # Lead 1 (square)

        current_time = 0.0
        for note in notes:
            if note.velocity > 0:
                midi.addNote(
                    track=0,
                    channel=0,
                    pitch=note.pitch,
                    time=current_time,
                    duration=note.duration,
                    volume=note.velocity,
                )
            current_time += note.duration

        buffer = BytesIO()
        midi.writeFile(buffer)
        return buffer.getvalue()
