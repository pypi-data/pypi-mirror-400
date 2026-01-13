"""Music theory primitives for chiptune composition."""

from chiptune.theory.arpeggios import Arpeggio
from chiptune.theory.chords import Chord, ChordProgression
from chiptune.theory.keys import Key
from chiptune.theory.scales import Scale

__all__ = ["Scale", "Chord", "ChordProgression", "Arpeggio", "Key"]
