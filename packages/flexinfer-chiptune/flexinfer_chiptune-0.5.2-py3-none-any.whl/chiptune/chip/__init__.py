"""Chiptune hardware constraints and channel models."""

from chiptune.chip.channels import (
    Channel,
    ChannelAllocator,
    ChannelType,
    DutyCycle,
    NESChannels,
)
from chiptune.chip.effects import (
    ChipEffect,
    DutyCycleSweep,
    EffectType,
    PitchSlide,
    Vibrato,
    VolumeEnvelope,
)

__all__ = [
    "Channel",
    "ChannelType",
    "DutyCycle",
    "NESChannels",
    "ChannelAllocator",
    "ChipEffect",
    "EffectType",
    "Vibrato",
    "PitchSlide",
    "VolumeEnvelope",
    "DutyCycleSweep",
]
