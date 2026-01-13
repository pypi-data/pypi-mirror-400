"""Audio effects for chiptune synthesis.

This module provides a variety of effects for processing audio:

Sample Effects (process audio samples):
- Tremolo: Amplitude modulation
- VibratoSample: Pitch modulation via delay
- Echo: Simple clean digital delay
- TapeDelay: Analog-style delay with character
- MultiTapDelay: Rhythmic multi-tap delay
- Chorus: Multiple detuned voices for depth
- Unison: Static detuning for thickness
- Ensemble: Rich ensemble effect

Pitch Effects (modulate frequency):
- Vibrato: LFO pitch modulation
- PitchSweep: NES-style hardware sweep
- Portamento: Smooth pitch glides
- PitchBend: Bend and return

Effect Chaining:
- EffectChain: Serial effect processing
- ParallelChain: Parallel processing with mix
- EffectPresets: Pre-built effect combinations

LFO:
- LFO: Low frequency oscillator for modulation
- LFOShape: Waveform shapes (sine, triangle, square, etc.)

Example:
    from chiptune.output.audio.effects import (
        EffectChain, Chorus, TapeDelay, Tremolo
    )

    # Create effect chain
    chain = EffectChain(effects=[
        Chorus.lush(),
        TapeDelay.space_echo(),
        Tremolo.subtle(),
    ])

    # Or use | operator
    chain = Chorus.classic() | TapeDelay.slapback()

    # Process audio
    output = chain.process(samples, sample_rate=44100)
"""

from chiptune.output.audio.effects.base import (
    AmplitudeEffect,
    PitchEffect,
    SampleEffect,
)
from chiptune.output.audio.effects.chain import (
    EffectChain,
    EffectPresets,
    ParallelChain,
)
from chiptune.output.audio.effects.chorus import Chorus, Ensemble, Unison
from chiptune.output.audio.effects.echo import Echo
from chiptune.output.audio.effects.lfo import LFO, LFOShape
from chiptune.output.audio.effects.pitch_sweep import (
    PitchBend,
    PitchSweep,
    Portamento,
    SweepDirection,
)
from chiptune.output.audio.effects.tape_delay import MultiTapDelay, TapeDelay
from chiptune.output.audio.effects.tremolo import Tremolo
from chiptune.output.audio.effects.vibrato import Vibrato, VibratoSample

__all__ = [
    # Base classes
    "SampleEffect",
    "PitchEffect",
    "AmplitudeEffect",
    # LFO
    "LFO",
    "LFOShape",
    # Sample effects
    "Tremolo",
    "VibratoSample",
    "Echo",
    "TapeDelay",
    "MultiTapDelay",
    "Chorus",
    "Unison",
    "Ensemble",
    # Pitch effects
    "Vibrato",
    "PitchSweep",
    "SweepDirection",
    "Portamento",
    "PitchBend",
    # Chaining
    "EffectChain",
    "ParallelChain",
    "EffectPresets",
]
