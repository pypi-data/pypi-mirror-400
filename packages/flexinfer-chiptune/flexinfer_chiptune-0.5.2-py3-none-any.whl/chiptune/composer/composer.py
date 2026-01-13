"""Main chiptune composition API.

Provides a fluent interface for composing chiptune music
with authentic retro constraints and game-music patterns.
"""

from __future__ import annotations

import random
from enum import Enum
from typing import Any, ClassVar

from pydantic import BaseModel

from chiptune.chip.channels import (
    ChannelAllocator,
    DrumPattern,
    NESChannels,
    Part,
    PartRole,
)
from chiptune.patterns.themes import GameTheme, MelodicContour, ThemeTemplate
from chiptune.theory.arpeggios import Arpeggio, ArpeggioPattern, Note
from chiptune.theory.chords import Chord, ChordProgression
from chiptune.theory.keys import Key, Mode
from chiptune.theory.scales import Scale


class BassStyle(str, Enum):
    """Bass line styles."""

    ROOT = "root"  # Just root notes
    OCTAVE = "octave"  # Root and octave alternating
    WALKING = "walking"  # Moving bass line
    ARPEGGIATED = "arpeggiated"  # Arpeggiated bass


class DrumStyle(str, Enum):
    """Drum pattern styles."""

    BASIC = "basic"
    DRIVING = "driving"
    SPARSE = "sparse"
    NONE = "none"


class Track(BaseModel):
    """A composed track with multiple channels."""

    name: str
    bpm: int
    key: Key
    time_signature: tuple[int, int] = (4, 4)
    channels: NESChannels
    length_beats: float = 0.0

    def duration_seconds(self) -> float:
        """Get track duration in seconds."""
        beats_per_second = self.bpm / 60.0
        return self.length_beats / beats_per_second


class ChiptuneComposer(BaseModel):
    """Main entry point for chiptune composition.

    Provides a fluent API for creating authentic chiptune music
    with game-appropriate patterns and constraints.

    Example:
        ```python
        composer = ChiptuneComposer(bpm=140, key="C", mode="major")
        composer.set_mood("heroic")
        composer.add_melody(contour="arch", length_bars=8)
        composer.add_bass(style="root")
        composer.add_drums(pattern="driving")
        midi_bytes = composer.to_midi_bytes()
        ```
    """

    bpm: int = 120
    key: Key
    time_signature: tuple[int, int] = (4, 4)
    channels: NESChannels
    parts: list[Part] = []
    length_bars: int = 0
    theme: GameTheme | None = None
    progression: ChordProgression | None = None

    # Mood to musical settings mapping
    MOOD_SETTINGS: ClassVar[dict[str, dict[str, Any]]] = {
        "heroic": {"mode": Mode.IONIAN, "tempo_mod": 1.1, "intensity": 0.8},
        "epic": {"mode": Mode.LYDIAN, "tempo_mod": 1.0, "intensity": 0.9},
        "mysterious": {"mode": Mode.DORIAN, "tempo_mod": 0.8, "intensity": 0.5},
        "danger": {"mode": Mode.PHRYGIAN, "tempo_mod": 1.2, "intensity": 0.85},
        "peaceful": {"mode": Mode.IONIAN, "tempo_mod": 0.7, "intensity": 0.3},
        "sad": {"mode": Mode.AEOLIAN, "tempo_mod": 0.6, "intensity": 0.4},
        "tense": {"mode": Mode.LOCRIAN, "tempo_mod": 0.9, "intensity": 0.7},
        "triumphant": {"mode": Mode.IONIAN, "tempo_mod": 1.15, "intensity": 0.95},
    }

    model_config = {"arbitrary_types_allowed": True}

    @classmethod
    def create(
        cls,
        bpm: int = 120,
        root: str = "C",
        mode: str | Mode = "major",
    ) -> ChiptuneComposer:
        """Create a new composer instance.

        Args:
            bpm: Tempo in beats per minute
            root: Root note of the key
            mode: Musical mode (string or Mode enum)

        Returns:
            Configured ChiptuneComposer
        """
        if isinstance(mode, str):
            mode_map = {
                "major": Mode.IONIAN,
                "minor": Mode.AEOLIAN,
                "ionian": Mode.IONIAN,
                "dorian": Mode.DORIAN,
                "phrygian": Mode.PHRYGIAN,
                "lydian": Mode.LYDIAN,
                "mixolydian": Mode.MIXOLYDIAN,
                "aeolian": Mode.AEOLIAN,
                "locrian": Mode.LOCRIAN,
            }
            mode = mode_map.get(mode.lower(), Mode.IONIAN)

        key = Key(root=root, mode=mode)
        channels = NESChannels.create()

        return cls(bpm=bpm, key=key, channels=channels)

    def set_mood(self, mood: str) -> ChiptuneComposer:
        """Configure the composer for a specific mood.

        Adjusts key, tempo, and other parameters to match
        the emotional character.

        Args:
            mood: Emotional descriptor (e.g., "heroic", "mysterious")

        Returns:
            Self for chaining
        """
        settings = self.MOOD_SETTINGS.get(mood.lower(), {})

        if "mode" in settings:
            self.key = Key(root=self.key.root, mode=settings["mode"])

        if "tempo_mod" in settings:
            self.bpm = int(self.bpm * settings["tempo_mod"])

        return self

    def set_theme(self, theme: GameTheme | str) -> ChiptuneComposer:
        """Configure for a specific game theme.

        Args:
            theme: GameTheme enum or string name

        Returns:
            Self for chaining
        """
        if isinstance(theme, str):
            theme = GameTheme(theme)

        self.theme = theme
        template = ThemeTemplate.for_theme(theme, root=self.key.root)

        self.key = template.key
        self.bpm = template.tempo
        self.progression = template.get_progression()

        return self

    def set_progression(
        self,
        progression: ChordProgression | list[str] | str,
    ) -> ChiptuneComposer:
        """Set the chord progression.

        Args:
            progression: ChordProgression, list of numerals, or preset name

        Returns:
            Self for chaining
        """
        if isinstance(progression, str):
            # Preset name
            self.progression = ChordProgression.from_preset(progression, self.key)
        elif isinstance(progression, list):
            # List of numerals
            self.progression = ChordProgression(key=self.key, numerals=progression)
        else:
            self.progression = progression

        return self

    def add_melody(
        self,
        contour: MelodicContour | str = MelodicContour.ARCH,
        length_bars: int = 4,
        register: str = "mid",
    ) -> ChiptuneComposer:
        """Generate and add a melody line.

        Args:
            contour: Melodic shape (arch, ascending, descending, wave)
            length_bars: Length in bars
            register: Pitch register (low, mid, high)

        Returns:
            Self for chaining
        """
        if isinstance(contour, str):
            contour = MelodicContour(contour)

        scale = Scale.from_key(self.key)
        beats_per_bar = self.time_signature[0]
        total_beats = length_bars * beats_per_bar

        # Register determines octave
        octave_map = {"low": 4, "mid": 5, "high": 6}
        base_octave = octave_map.get(register, 5)

        notes = self._generate_melody(
            scale=scale,
            contour=contour,
            total_beats=total_beats,
            octave=base_octave,
        )

        self.parts.append(Part(role=PartRole.MELODY, notes=notes, priority=10))
        self.length_bars = max(self.length_bars, length_bars)

        return self

    def _generate_melody(
        self,
        scale: Scale,
        contour: MelodicContour,
        total_beats: float,
        octave: int,
    ) -> list[Note]:
        """Generate melody notes following a contour."""
        notes: list[Note] = []
        current_beat = 0.0

        # Note duration patterns (in beats)
        rhythm_patterns = [
            [1.0, 0.5, 0.5],  # quarter, eighth, eighth
            [0.5, 0.5, 1.0],  # eighth, eighth, quarter
            [1.5, 0.5],  # dotted quarter, eighth
            [0.5, 0.5, 0.5, 0.5],  # four eighths
            [1.0, 1.0],  # two quarters
        ]

        # Get scale pitches
        scale_pitches = scale.get_pitches(octave=octave, num_octaves=2)

        while current_beat < total_beats:
            # Pick a rhythm pattern
            pattern = random.choice(rhythm_patterns)

            for duration in pattern:
                if current_beat >= total_beats:
                    break

                # Calculate pitch based on contour
                progress = current_beat / total_beats
                pitch_index = self._contour_to_index(contour, progress, len(scale_pitches))

                pitch = scale_pitches[pitch_index]
                velocity = random.randint(80, 110)

                notes.append(Note(pitch=pitch, duration=duration, velocity=velocity))
                current_beat += duration

        return notes

    def _contour_to_index(self, contour: MelodicContour, progress: float, max_index: int) -> int:
        """Convert contour and progress to scale index."""
        import math

        mid = max_index // 2

        match contour:
            case MelodicContour.ARCH:
                # Rise to middle, then fall
                if progress < 0.5:
                    t = progress * 2
                    return int(mid * t + mid * (1 - t) * 0.3)
                else:
                    t = (progress - 0.5) * 2
                    return int(mid * (1 - t) + mid * 0.3 * t)

            case MelodicContour.ASCENDING:
                return int(progress * (max_index - 1))

            case MelodicContour.DESCENDING:
                return int((1 - progress) * (max_index - 1))

            case MelodicContour.WAVE:
                # Sinusoidal movement
                wave = math.sin(progress * math.pi * 4) * 0.4 + 0.5
                return int(wave * (max_index - 1))

            case MelodicContour.FLAT:
                # Stay in middle register with slight variation
                return mid + random.randint(-1, 1)

            case MelodicContour.PEAK:
                # Quick rise to peak early, then gradual descent
                if progress < 0.3:
                    return int((progress / 0.3) * (max_index - 1))
                else:
                    return int((1 - (progress - 0.3) / 0.7) * (max_index - 1))

            case MelodicContour.TROUGH:
                # Dip down then return
                if progress < 0.5:
                    return int((0.5 - progress) * max_index)
                else:
                    return int((progress - 0.5) * max_index)

            case _:
                return mid

    def add_bass(self, style: BassStyle | str = BassStyle.ROOT) -> ChiptuneComposer:
        """Add a bass line.

        Args:
            style: Bass style (root, octave, walking, arpeggiated)

        Returns:
            Self for chaining
        """
        if isinstance(style, str):
            style = BassStyle(style)

        if not self.progression:
            # Default to a simple I-IV-V-I
            self.set_progression(["I", "IV", "V", "I"])

        assert self.progression is not None  # Set above if None
        chords = self.progression.get_chords()
        beats_per_chord = 4  # One bar per chord
        notes: list[Note] = []

        for chord in chords:
            bass_notes = self._generate_bass_for_chord(chord, style, beats_per_chord, octave=3)
            notes.extend(bass_notes)

        self.parts.append(Part(role=PartRole.BASS, notes=notes, priority=8))

        # Update length if bass is longer
        bass_bars = len(chords)
        self.length_bars = max(self.length_bars, bass_bars)

        return self

    def _generate_bass_for_chord(
        self,
        chord: Chord,
        style: BassStyle,
        beats: float,
        octave: int,
    ) -> list[Note]:
        """Generate bass notes for a single chord."""

        root_pitch = chord.root_midi + (octave - 4) * 12
        notes: list[Note] = []

        match style:
            case BassStyle.ROOT:
                # Just hold the root
                notes.append(Note(pitch=root_pitch, duration=beats, velocity=100))

            case BassStyle.OCTAVE:
                # Alternate root and octave
                half = beats / 2
                notes.append(Note(pitch=root_pitch, duration=half, velocity=100))
                notes.append(Note(pitch=root_pitch + 12, duration=half, velocity=90))

            case BassStyle.WALKING:
                # Walk through chord tones
                pitches = chord.get_pitches(octave=octave)
                note_duration = beats / len(pitches)
                for i, pitch in enumerate(pitches):
                    vel = 100 if i == 0 else 85
                    notes.append(Note(pitch=pitch, duration=note_duration, velocity=vel))

            case BassStyle.ARPEGGIATED:
                # Quick arpeggio on bass
                arp = Arpeggio.from_chord(chord, octave=octave, note_duration=0.5)
                notes.extend(arp.fill_duration(beats, velocity=95))

        return notes

    def add_arpeggio_layer(
        self,
        pattern: ArpeggioPattern = ArpeggioPattern.UP,
    ) -> ChiptuneComposer:
        """Add an arpeggio harmony layer.

        Uses rapid arpeggios to fill out the harmony on pulse2.

        Args:
            pattern: Arpeggio pattern (up, down, up_down, etc.)

        Returns:
            Self for chaining
        """
        if not self.progression:
            self.set_progression(["I", "IV", "V", "I"])

        assert self.progression is not None  # Set above if None
        chords = self.progression.get_chords()
        beats_per_chord = 4
        notes: list[Note] = []

        for chord in chords:
            arp = Arpeggio.from_chord(
                chord,
                octave=5,
                pattern=pattern,
                note_duration=0.125,
            )
            arp_notes = arp.fill_duration(beats_per_chord, velocity=70)
            notes.extend(arp_notes)

        self.parts.append(Part(role=PartRole.ARPEGGIO, notes=notes, priority=5))
        return self

    def add_drums(self, pattern: DrumStyle | str = DrumStyle.BASIC) -> ChiptuneComposer:
        """Add a drum pattern.

        Args:
            pattern: Drum style (basic, driving, sparse, none)

        Returns:
            Self for chaining
        """
        if isinstance(pattern, str):
            pattern = DrumStyle(pattern)

        if pattern == DrumStyle.NONE:
            return self

        # Get drum pattern
        drum_patterns = {
            DrumStyle.BASIC: DrumPattern.basic_4_4,
            DrumStyle.DRIVING: DrumPattern.driving,
            DrumStyle.SPARSE: DrumPattern.sparse,
        }

        drum_pattern = drum_patterns.get(pattern, DrumPattern.basic_4_4)()
        bars = max(1, self.length_bars)
        beats_per_bar = self.time_signature[0]
        total_beats = bars * beats_per_bar

        # Calculate repetitions needed
        pattern_beats = sum(n.duration for n in drum_pattern.to_notes())
        reps = max(1, int(total_beats / pattern_beats))

        notes = drum_pattern.repeat(reps)
        self.parts.append(Part(role=PartRole.PERCUSSION, notes=notes, priority=7))

        return self

    def add_countermelody(
        self,
        motion: str = "contrary",
        interval: str = "third",
    ) -> ChiptuneComposer:
        """Add a countermelody based on the existing melody.

        Uses music theory rules to generate a harmonically correct
        secondary melody that complements the main melody.

        Args:
            motion: Motion type ("contrary", "parallel", "oblique", "similar", "free")
            interval: Harmony interval ("third", "sixth", "fifth", "octave")

        Returns:
            Self for chaining
        """
        from chiptune.generation.harmony.countermelody import (
            CountermelodyGenerator,
            HarmonyInterval,
            MotionType,
        )

        # Find the melody part
        melody_part = next((p for p in self.parts if p.role == PartRole.MELODY), None)
        if not melody_part or not melody_part.notes:
            return self  # No melody to harmonize

        # Map strings to enums
        motion_map = {
            "contrary": MotionType.CONTRARY,
            "parallel": MotionType.PARALLEL,
            "oblique": MotionType.OBLIQUE,
            "similar": MotionType.SIMILAR,
            "free": MotionType.FREE,
        }
        interval_map = {
            "third": HarmonyInterval.THIRD,
            "sixth": HarmonyInterval.SIXTH,
            "fifth": HarmonyInterval.FIFTH,
            "octave": HarmonyInterval.OCTAVE,
        }

        motion_type = motion_map.get(motion.lower(), MotionType.CONTRARY)
        harmony_interval = interval_map.get(interval.lower(), HarmonyInterval.THIRD)

        # Generate countermelody
        scale = Scale.from_key(self.key)
        generator = CountermelodyGenerator(
            motion=motion_type,
            harmony_interval=harmony_interval,
        )
        counter_notes = generator.generate(melody_part.notes, scale=scale)

        self.parts.append(Part(role=PartRole.COUNTER_MELODY, notes=counter_notes, priority=6))
        return self

    def set_intensity(
        self,
        profile: str = "dramatic",
    ) -> ChiptuneComposer:
        """Configure intensity profile for dynamic composition.

        The intensity profile affects how musical parameters change
        over the course of the piece (tempo feel, density, dynamics).

        Args:
            profile: Profile preset ("calm", "building", "dramatic", "battle",
                     "exploration", "boss_fight")

        Returns:
            Self for chaining
        """
        from chiptune.generation.adaptive.intensity import IntensityProfile

        # Get the profile
        profile_map = {
            "calm": IntensityProfile.calm,
            "building": IntensityProfile.building,
            "fading": IntensityProfile.fading,
            "dramatic": IntensityProfile.dramatic,
            "battle": IntensityProfile.battle,
            "exploration": IntensityProfile.exploration,
            "boss_fight": IntensityProfile.boss_fight,
        }

        profile_factory = profile_map.get(profile.lower(), IntensityProfile.dramatic)
        intensity = profile_factory()

        # Adjust BPM based on intensity curve start
        start_intensity = intensity.get_intensity(0.0)
        self.bpm = int(self.bpm * (0.8 + start_intensity * 0.4))

        return self

    def with_effect(
        self,
        effect_name: str,
        **kwargs: Any,
    ) -> tuple[ChiptuneComposer, Any]:
        """Get an effect instance for use during audio export.

        Returns the composer and effect for chaining. Use the effect
        when calling export methods.

        Args:
            effect_name: Effect preset ("echo", "chorus", "delay", "tremolo")
            **kwargs: Additional effect parameters

        Returns:
            Tuple of (self, effect) for use in export

        Example:
            composer, echo = composer.with_effect("echo", delay_time=0.3)
            exporter.export_wav(track, "out.wav", effects=echo)
        """
        from chiptune.output.audio.effects import (
            Chorus,
            Echo,
            TapeDelay,
            Tremolo,
        )

        effect_map = {
            "echo": Echo.medium,
            "echo_short": Echo.short,
            "echo_long": Echo.long,
            "chorus": Chorus.classic,
            "chorus_lush": Chorus.lush,
            "delay": TapeDelay.space_echo,
            "delay_slapback": TapeDelay.slapback,
            "tremolo": Tremolo.classic,
            "tremolo_subtle": Tremolo.subtle,
        }

        factory = effect_map.get(effect_name.lower())
        if factory:
            effect = factory()
            # Apply any custom kwargs
            for key, value in kwargs.items():
                if hasattr(effect, key):
                    setattr(effect, key, value)
            return self, effect

        # Return no effect if not found
        return self, None

    def build(self) -> Track:
        """Build the final track.

        Allocates parts to channels and returns the complete Track.

        Returns:
            Composed Track ready for export
        """
        allocator = ChannelAllocator.create()
        channels = allocator.allocate_to_channels(self.parts)

        beats_per_bar = self.time_signature[0]
        total_beats = self.length_bars * beats_per_bar

        return Track(
            name=f"{self.theme.value if self.theme else 'composition'}_{self.key.root}",
            bpm=self.bpm,
            key=self.key,
            time_signature=self.time_signature,
            channels=channels,
            length_beats=total_beats,
        )

    def to_midi_bytes(self) -> bytes:
        """Export composition as MIDI bytes.

        Returns:
            MIDI file as bytes
        """
        from chiptune.output.midi import MidiExporter

        track = self.build()
        exporter = MidiExporter()
        return exporter.export_bytes(track)

    def export_midi(self, path: str) -> None:
        """Export composition to a MIDI file.

        Args:
            path: Output file path
        """
        from chiptune.output.midi import MidiExporter

        track = self.build()
        exporter = MidiExporter()
        exporter.export_file(track, path)

    def to_audio_bytes(self, format: str = "wav") -> bytes:
        """Export composition as audio bytes.

        Args:
            format: Audio format ("wav" or "ogg")

        Returns:
            Audio file as bytes
        """
        from chiptune.output.audio import AudioExporter

        track = self.build()
        exporter = AudioExporter()
        return exporter.export_bytes(track, format=format)

    def export_wav(self, path: str) -> None:
        """Export composition to a WAV file.

        Args:
            path: Output file path
        """
        from chiptune.output.audio import AudioExporter

        track = self.build()
        exporter = AudioExporter()
        exporter.export_wav(track, path)

    def export_ogg(self, path: str) -> None:
        """Export composition to an OGG file.

        Args:
            path: Output file path
        """
        from chiptune.output.audio import AudioExporter

        track = self.build()
        exporter = AudioExporter()
        exporter.export_ogg(track, path)

    def preview(self) -> None:
        """Play the composition (requires sounddevice).

        Renders and plays the audio. Blocks until complete.
        Requires: pip install py-chiptune[audio]
        """
        from chiptune.output.audio import AudioExporter, AudioPlayer

        track = self.build()
        exporter = AudioExporter()
        audio = exporter.render_track(track)

        player = AudioPlayer()
        player.play(audio)
