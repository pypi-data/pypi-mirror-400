"""Retro sound chip system emulators.

This module provides emulations of classic sound chips:
- NES 2A03 (via existing channels module)
- Game Boy DMG
- Commodore 64 SID
- Sega Genesis YM2612

Each chip system provides:
- Authentic voice/channel types
- Hardware-accurate waveform generation
- Chip-specific features (filters, FM, wavetables)
- Preset sounds for quick setup

Example:
    >>> from chiptune.chip.systems import GameBoyChip, SIDChip, GenesisChip
    >>> from chiptune.theory.arpeggios import Note
    >>>
    >>> # Game Boy with custom wavetable
    >>> gb = GameBoyChip.with_saw_wave()
    >>> gb.pulse1.add_note(Note(pitch=60, duration=1.0))
    >>> samples = gb.render(tempo=120)
    >>>
    >>> # C64 SID with filter
    >>> sid = SIDChip.lead_preset()
    >>> sid.voice1.add_note(Note(pitch=60, duration=1.0))
    >>> samples = sid.render(tempo=120)
    >>>
    >>> # Genesis FM synthesis
    >>> genesis = GenesisChip.brass_preset()
    >>> genesis.ch1.add_note(Note(pitch=60, duration=1.0))
    >>> samples = genesis.render(tempo=120)
"""

from chiptune.chip.systems.base import (
    ChipPreset,
    ChipSystem,
    ChipType,
    ChipVoice,
    VoiceType,
    frequency_to_midi,
    midi_to_frequency,
)
from chiptune.chip.systems.gameboy import (
    GameBoyChip,
    GBDutyCycle,
    GBNoiseVoice,
    GBPulseVoice,
    GBWaveVoice,
)
from chiptune.chip.systems.genesis import (
    FMAlgorithm,
    FMOperator,
    FMVoice,
    GenesisChip,
)
from chiptune.chip.systems.sid import (
    SIDChip,
    SIDFilter,
    SIDFilterMode,
    SIDRevision,
    SIDVoice,
    SIDWaveform,
)

__all__ = [
    # Base classes
    "ChipSystem",
    "ChipVoice",
    "ChipType",
    "VoiceType",
    "ChipPreset",
    "midi_to_frequency",
    "frequency_to_midi",
    # Game Boy
    "GameBoyChip",
    "GBPulseVoice",
    "GBWaveVoice",
    "GBNoiseVoice",
    "GBDutyCycle",
    # SID
    "SIDChip",
    "SIDVoice",
    "SIDFilter",
    "SIDWaveform",
    "SIDFilterMode",
    "SIDRevision",
    # Genesis
    "GenesisChip",
    "FMVoice",
    "FMOperator",
    "FMAlgorithm",
]
