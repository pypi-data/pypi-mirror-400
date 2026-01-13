"""NES 2A03 sound chip channel models and constraints.

The NES APU (Audio Processing Unit) has 5 channels:
- 2 Pulse wave channels (melody, harmony)
- 1 Triangle wave channel (bass)
- 1 Noise channel (percussion)
- 1 DPCM channel (samples - optional)

This module models these constraints for authentic chiptune composition.
"""

from __future__ import annotations

from enum import Enum, IntEnum
from typing import ClassVar

from pydantic import BaseModel, field_validator

from chiptune.theory.arpeggios import Note


class ChannelType(str, Enum):
    """Types of sound channels in classic sound chips."""

    PULSE = "pulse"  # Square wave, configurable duty cycle
    TRIANGLE = "triangle"  # Triangle wave, no volume control
    NOISE = "noise"  # Pseudo-random noise generator
    DPCM = "dpcm"  # Delta pulse-code modulation (samples)
    WAVE = "wave"  # Wavetable (Game Boy, etc.)


class DutyCycle(IntEnum):
    """Pulse wave duty cycle options.

    Duty cycle affects the timbre of the sound:
    - 12.5%: Thin, nasal (good for high harmonics)
    - 25%: Classic NES lead sound
    - 50%: Full, hollow square wave
    - 75%: Same as 25% but phase-inverted
    """

    DUTY_12_5 = 0  # 12.5% - thin, high overtones
    DUTY_25 = 1  # 25% - classic NES sound
    DUTY_50 = 2  # 50% - pure square wave
    DUTY_75 = 3  # 75% - same timbre as 25%


class Channel(BaseModel):
    """A single audio channel with hardware constraints.

    Models the capabilities and limitations of a sound chip channel.
    """

    channel_type: ChannelType
    channel_id: int
    notes: list[Note] = []
    duty_cycle: DutyCycle = DutyCycle.DUTY_50
    volume: int = 15  # 0-15 for NES (4-bit)

    # Channel-specific constraints
    min_pitch: int = 0
    max_pitch: int = 127
    has_volume_control: bool = True

    @field_validator("volume")
    @classmethod
    def validate_volume(cls, v: int) -> int:
        """Ensure volume is in valid range."""
        return max(0, min(15, v))

    def add_note(self, note: Note) -> None:
        """Add a note to this channel."""
        # Clamp pitch to channel range
        clamped_pitch = max(self.min_pitch, min(self.max_pitch, note.pitch))
        if clamped_pitch != note.pitch:
            note = Note(
                pitch=clamped_pitch,
                duration=note.duration,
                velocity=note.velocity,
            )
        self.notes.append(note)

    def add_notes(self, notes: list[Note]) -> None:
        """Add multiple notes to this channel."""
        for note in notes:
            self.add_note(note)

    def clear(self) -> None:
        """Clear all notes from this channel."""
        self.notes = []

    @property
    def duration_beats(self) -> float:
        """Total duration of notes in this channel."""
        return sum(note.duration for note in self.notes)

    @classmethod
    def pulse(cls, channel_id: int = 0, duty: DutyCycle = DutyCycle.DUTY_25) -> Channel:
        """Create a pulse channel (for melody/harmony)."""
        return cls(
            channel_type=ChannelType.PULSE,
            channel_id=channel_id,
            duty_cycle=duty,
            min_pitch=33,  # A1 - lowest stable NES pitch
            max_pitch=108,  # C8 - practical upper limit
        )

    @classmethod
    def triangle(cls, channel_id: int = 2) -> Channel:
        """Create a triangle channel (for bass).

        Note: Triangle channel has no volume control on NES!
        """
        return cls(
            channel_type=ChannelType.TRIANGLE,
            channel_id=channel_id,
            min_pitch=21,  # A0 - can go lower than pulse
            max_pitch=96,  # C7 - sounds best in bass range
            has_volume_control=False,
            volume=15,  # Always max
        )

    @classmethod
    def noise(cls, channel_id: int = 3) -> Channel:
        """Create a noise channel (for percussion).

        Noise channel uses pitch to control the noise period/timbre.
        Lower values = higher pitched noise.
        """
        return cls(
            channel_type=ChannelType.NOISE,
            channel_id=channel_id,
            min_pitch=0,
            max_pitch=15,  # Only 16 noise periods
        )


class NESChannels(BaseModel):
    """NES 2A03 APU channel configuration.

    Models the complete NES sound chip with its 5 channels.
    """

    pulse1: Channel
    pulse2: Channel
    triangle: Channel
    noise: Channel

    # Standard NES channel assignments
    PULSE1_ID: ClassVar[int] = 0
    PULSE2_ID: ClassVar[int] = 1
    TRIANGLE_ID: ClassVar[int] = 2
    NOISE_ID: ClassVar[int] = 3

    @classmethod
    def create(cls) -> NESChannels:
        """Create a standard NES channel configuration."""
        return cls(
            pulse1=Channel.pulse(cls.PULSE1_ID, DutyCycle.DUTY_25),
            pulse2=Channel.pulse(cls.PULSE2_ID, DutyCycle.DUTY_50),
            triangle=Channel.triangle(cls.TRIANGLE_ID),
            noise=Channel.noise(cls.NOISE_ID),
        )

    def get_channel(self, channel_id: int) -> Channel | None:
        """Get channel by ID."""
        channels = {
            self.PULSE1_ID: self.pulse1,
            self.PULSE2_ID: self.pulse2,
            self.TRIANGLE_ID: self.triangle,
            self.NOISE_ID: self.noise,
        }
        return channels.get(channel_id)

    def clear_all(self) -> None:
        """Clear all channels."""
        self.pulse1.clear()
        self.pulse2.clear()
        self.triangle.clear()
        self.noise.clear()

    @property
    def all_channels(self) -> list[Channel]:
        """Get all channels as a list."""
        return [self.pulse1, self.pulse2, self.triangle, self.noise]


class PartRole(str, Enum):
    """Musical roles for channel allocation."""

    MELODY = "melody"
    HARMONY = "harmony"
    BASS = "bass"
    PERCUSSION = "percussion"
    ARPEGGIO = "arpeggio"
    COUNTER_MELODY = "counter_melody"


class Part(BaseModel):
    """A musical part with a role and notes."""

    role: PartRole
    notes: list[Note]
    priority: int = 0  # Higher = more important


class ChannelAllocator(BaseModel):
    """Allocates musical parts to NES channels.

    Handles the constraint of limited channels by intelligently
    assigning parts based on their roles.
    """

    channels: NESChannels

    # Default role-to-channel mapping
    DEFAULT_ALLOCATION: ClassVar[dict[PartRole, int]] = {
        PartRole.MELODY: NESChannels.PULSE1_ID,
        PartRole.HARMONY: NESChannels.PULSE2_ID,
        PartRole.COUNTER_MELODY: NESChannels.PULSE2_ID,
        PartRole.ARPEGGIO: NESChannels.PULSE2_ID,
        PartRole.BASS: NESChannels.TRIANGLE_ID,
        PartRole.PERCUSSION: NESChannels.NOISE_ID,
    }

    @classmethod
    def create(cls) -> ChannelAllocator:
        """Create an allocator with fresh NES channels."""
        return cls(channels=NESChannels.create())

    def allocate(self, parts: list[Part]) -> dict[int, list[Note]]:
        """Allocate parts to channels.

        Args:
            parts: List of musical parts to allocate

        Returns:
            Dict mapping channel IDs to their notes
        """
        # Sort by priority (higher first)
        sorted_parts = sorted(parts, key=lambda p: p.priority, reverse=True)

        allocation: dict[int, list[Note]] = {
            NESChannels.PULSE1_ID: [],
            NESChannels.PULSE2_ID: [],
            NESChannels.TRIANGLE_ID: [],
            NESChannels.NOISE_ID: [],
        }

        # Track which channels have been assigned high-priority parts
        assigned_priorities: dict[int, int] = {}

        for part in sorted_parts:
            target_channel = self.DEFAULT_ALLOCATION.get(part.role, NESChannels.PULSE1_ID)

            # Check if we need to bump a lower-priority part
            current_priority = assigned_priorities.get(target_channel, -1)
            if part.priority > current_priority:
                # This part takes precedence
                allocation[target_channel] = part.notes.copy()
                assigned_priorities[target_channel] = part.priority
            elif target_channel in (NESChannels.PULSE1_ID, NESChannels.PULSE2_ID):
                # Try the other pulse channel
                alt_channel = (
                    NESChannels.PULSE2_ID
                    if target_channel == NESChannels.PULSE1_ID
                    else NESChannels.PULSE1_ID
                )
                alt_priority = assigned_priorities.get(alt_channel, -1)
                if part.priority > alt_priority:
                    allocation[alt_channel] = part.notes.copy()
                    assigned_priorities[alt_channel] = part.priority

        return allocation

    def allocate_to_channels(self, parts: list[Part]) -> NESChannels:
        """Allocate parts and populate channel notes.

        Args:
            parts: List of musical parts

        Returns:
            NESChannels with notes populated
        """
        allocation = self.allocate(parts)

        self.channels.clear_all()
        self.channels.pulse1.add_notes(allocation[NESChannels.PULSE1_ID])
        self.channels.pulse2.add_notes(allocation[NESChannels.PULSE2_ID])
        self.channels.triangle.add_notes(allocation[NESChannels.TRIANGLE_ID])
        self.channels.noise.add_notes(allocation[NESChannels.NOISE_ID])

        return self.channels


class DrumPattern(BaseModel):
    """A pattern for the noise channel percussion.

    NES noise channel has 16 different "pitches" which are
    actually different noise periods/timbres.
    """

    # Common drum sounds mapped to noise periods
    KICK: ClassVar[int] = 10  # Lower, boomy noise
    SNARE: ClassVar[int] = 3  # Higher, snappy noise
    HIHAT_CLOSED: ClassVar[int] = 1  # High, short noise
    HIHAT_OPEN: ClassVar[int] = 0  # Highest noise period

    steps: list[tuple[int, float, int]]  # (pitch, duration, velocity)

    @classmethod
    def basic_4_4(cls) -> DrumPattern:
        """Basic 4/4 beat: kick-hihat-snare-hihat."""
        return cls(
            steps=[
                (cls.KICK, 0.5, 100),
                (cls.HIHAT_CLOSED, 0.5, 70),
                (cls.SNARE, 0.5, 90),
                (cls.HIHAT_CLOSED, 0.5, 70),
            ]
        )

    @classmethod
    def driving(cls) -> DrumPattern:
        """Driving beat with double-time hihat."""
        return cls(
            steps=[
                (cls.KICK, 0.25, 100),
                (cls.HIHAT_CLOSED, 0.25, 60),
                (cls.HIHAT_CLOSED, 0.25, 50),
                (cls.HIHAT_CLOSED, 0.25, 60),
                (cls.SNARE, 0.25, 90),
                (cls.HIHAT_CLOSED, 0.25, 60),
                (cls.HIHAT_CLOSED, 0.25, 50),
                (cls.HIHAT_CLOSED, 0.25, 60),
            ]
        )

    @classmethod
    def sparse(cls) -> DrumPattern:
        """Sparse pattern for calmer music."""
        return cls(
            steps=[
                (cls.KICK, 1.0, 80),
                (cls.SNARE, 1.0, 70),
            ]
        )

    def to_notes(self) -> list[Note]:
        """Convert pattern to Note objects."""
        return [
            Note(pitch=pitch, duration=duration, velocity=velocity)
            for pitch, duration, velocity in self.steps
        ]

    def repeat(self, times: int) -> list[Note]:
        """Repeat the pattern multiple times."""
        single = self.to_notes()
        return single * times
