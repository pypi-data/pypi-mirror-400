"""py-chiptune: Retro game music generation library.

Generate 8-bit/16-bit style music and sound effects with a semantic API
that agents can use to programmatically compose music. Supports both
MIDI export and direct audio synthesis with authentic NES waveforms.
"""

from chiptune.composer.agent_api import MusicAgent
from chiptune.composer.composer import ChiptuneComposer
from chiptune.output.audio import AudioExporter, AudioPlayer
from chiptune.patterns.jingles import Jingle
from chiptune.sfx.effects import SFXGenerator
from chiptune.theory.chords import Chord, ChordProgression
from chiptune.theory.keys import Key
from chiptune.theory.scales import Scale

__version__ = "0.3.0"

__all__ = [
    "ChiptuneComposer",
    "MusicAgent",
    "Jingle",
    "SFXGenerator",
    "Scale",
    "Chord",
    "ChordProgression",
    "Key",
    "AudioExporter",
    "AudioPlayer",
]
