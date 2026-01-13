"""Base classes for chip sound system emulation.

Provides abstract interfaces that all chip implementations
must follow, enabling a unified API across different retro
sound chips (NES, Game Boy, C64 SID, Genesis, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import ClassVar

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, Field

from chiptune.theory.arpeggios import Note


class ChipType(str, Enum):
    """Supported sound chip types."""

    NES = "nes"  # Nintendo 2A03
    GAMEBOY = "gameboy"  # Game Boy DMG
    SID = "sid"  # Commodore 64 SID
    GENESIS = "genesis"  # Sega Genesis YM2612
    CUSTOM = "custom"


class VoiceType(str, Enum):
    """Types of synthesis voices across chip systems."""

    PULSE = "pulse"  # Square/pulse wave
    TRIANGLE = "triangle"  # Triangle wave
    NOISE = "noise"  # Noise generator
    WAVETABLE = "wavetable"  # Custom waveform table
    FM = "fm"  # FM synthesis
    SAMPLE = "sample"  # PCM sample playback


class ChipVoice(BaseModel, ABC):
    """Abstract base for a single voice/channel in a chip.

    Each voice generates audio independently. Voices have
    chip-specific constraints on pitch, volume, and features.
    """

    voice_id: int
    voice_type: VoiceType
    notes: list[Note] = Field(default_factory=list)

    # Range constraints
    min_pitch: int = 0
    max_pitch: int = 127
    volume_bits: int = 4  # e.g., 4 bits = 0-15 volume levels
    has_volume_control: bool = True

    @property
    def max_volume(self) -> int:
        """Maximum volume value based on bit depth."""
        return (1 << self.volume_bits) - 1

    def add_note(self, note: Note) -> None:
        """Add a note, clamping pitch to valid range."""
        clamped_pitch = max(self.min_pitch, min(self.max_pitch, note.pitch))
        if clamped_pitch != note.pitch:
            note = Note(
                pitch=clamped_pitch,
                duration=note.duration,
                velocity=note.velocity,
            )
        self.notes.append(note)

    def clear(self) -> None:
        """Clear all notes from this voice."""
        self.notes = []

    @abstractmethod
    def generate_samples(
        self,
        frequency: float,
        duration: float,
        amplitude: float,
        sample_rate: int,
    ) -> NDArray[np.float32]:
        """Generate audio samples for this voice type.

        Args:
            frequency: Note frequency in Hz
            duration: Duration in seconds
            amplitude: Peak amplitude (0.0-1.0)
            sample_rate: Audio sample rate

        Returns:
            Mono samples as float32 array
        """


class ChipSystem(BaseModel, ABC):
    """Abstract base for a complete sound chip system.

    Represents an entire chip with all its voices and
    chip-specific features (filters, effects, etc.).
    """

    chip_type: ChipType
    sample_rate: int = 44100

    # Chip identification
    name: str = ""
    description: str = ""

    # Hardware specs
    voice_count: ClassVar[int] = 4
    clock_rate: ClassVar[int] = 0  # Chip clock in Hz

    @property
    @abstractmethod
    def voices(self) -> list[ChipVoice]:
        """Get all voices in this chip."""

    @abstractmethod
    def get_voice(self, voice_id: int) -> ChipVoice | None:
        """Get a specific voice by ID."""

    def clear_all(self) -> None:
        """Clear all voices."""
        for voice in self.voices:
            voice.clear()

    @abstractmethod
    def render(self, tempo: float = 120.0) -> NDArray[np.float32]:
        """Render all voices to a stereo mix.

        Args:
            tempo: Tempo in BPM for timing calculations

        Returns:
            Stereo samples as (N, 2) float32 array
        """

    def render_voice(
        self,
        voice_id: int,
        tempo: float = 120.0,
    ) -> NDArray[np.float32]:
        """Render a single voice to mono samples.

        Args:
            voice_id: Voice to render
            tempo: Tempo in BPM

        Returns:
            Mono samples as float32 array
        """
        voice = self.get_voice(voice_id)
        if voice is None or not voice.notes:
            return np.array([], dtype=np.float32)

        samples_list = []
        for note in voice.notes:
            freq = midi_to_frequency(note.pitch)
            duration_sec = (note.duration * 60.0) / tempo
            amplitude = note.velocity / 127.0

            note_samples = voice.generate_samples(freq, duration_sec, amplitude, self.sample_rate)
            samples_list.append(note_samples)

        if not samples_list:
            return np.array([], dtype=np.float32)

        return np.concatenate(samples_list).astype(np.float32)


class ChipPreset(BaseModel):
    """A preset configuration for a chip system."""

    name: str
    chip_type: ChipType
    description: str = ""
    parameters: dict[str, object] = Field(default_factory=dict)


def midi_to_frequency(midi_note: int) -> float:
    """Convert MIDI note number to frequency in Hz.

    Args:
        midi_note: MIDI note number (0-127, 69 = A4 = 440Hz)

    Returns:
        Frequency in Hz
    """
    return 440.0 * (2 ** ((midi_note - 69) / 12.0))


def frequency_to_midi(frequency: float) -> int:
    """Convert frequency in Hz to nearest MIDI note.

    Args:
        frequency: Frequency in Hz

    Returns:
        Nearest MIDI note number
    """
    if frequency <= 0:
        return 0
    return int(round(69 + 12 * np.log2(frequency / 440.0)))
