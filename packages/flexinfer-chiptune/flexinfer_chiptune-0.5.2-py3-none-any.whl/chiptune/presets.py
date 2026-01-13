"""Pre-built presets for quick chiptune composition.

This module provides ready-to-use configurations for common use cases:

- **Genre Presets**: Complete composer configurations for game genres
- **Effect Chains**: Pre-built effect combinations for common sounds
- **Chip Presets**: Sound chip configurations for different aesthetics
- **Quick Composers**: One-liner composition starters

Example:
    >>> from chiptune.presets import GenrePresets, EffectPresets
    >>>
    >>> # Create a battle theme in one line
    >>> composer = GenrePresets.battle_theme()
    >>> track = composer.add_melody(length_bars=8).add_bass().add_drums().build()
    >>>
    >>> # Get a ready-to-use effect chain
    >>> effects = EffectPresets.retro_gaming()
    >>> exporter.export_wav(track, "output.wav", effects=effects)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from chiptune.composer.composer import ChiptuneComposer
from chiptune.output.audio.effects import (
    Chorus,
    Echo,
    EffectChain,
    TapeDelay,
    Tremolo,
)

if TYPE_CHECKING:
    from chiptune.chip.systems import NES2A03


class GenrePresets:
    """Pre-configured composers for common game music genres."""

    @staticmethod
    def battle_theme(root: str = "A") -> ChiptuneComposer:
        """Intense battle/boss fight music.

        Features:
        - Fast tempo (160+ BPM)
        - Minor key with dramatic progressions
        - Driving drums

        Args:
            root: Root note (default A minor)

        Returns:
            Configured ChiptuneComposer
        """
        composer = ChiptuneComposer.create(bpm=165, root=root, mode="minor")
        composer.set_progression(["i", "VII", "VI", "V"])
        composer.set_intensity("battle")
        return composer

    @staticmethod
    def overworld(root: str = "C") -> ChiptuneComposer:
        """Adventurous overworld/exploration theme.

        Features:
        - Medium tempo (110-130 BPM)
        - Major key, optimistic feel
        - Moderate drums

        Args:
            root: Root note (default C major)

        Returns:
            Configured ChiptuneComposer
        """
        composer = ChiptuneComposer.create(bpm=120, root=root, mode="major")
        composer.set_progression(["I", "V", "vi", "IV"])
        composer.set_intensity("exploration")
        return composer

    @staticmethod
    def dungeon(root: str = "E") -> ChiptuneComposer:
        """Dark, mysterious dungeon music.

        Features:
        - Slow-medium tempo (80-100 BPM)
        - Dorian or Phrygian mode
        - Sparse drums or none

        Args:
            root: Root note (default E)

        Returns:
            Configured ChiptuneComposer
        """
        composer = ChiptuneComposer.create(bpm=85, root=root, mode="dorian")
        composer.set_progression(["i", "IV", "i", "VII"])
        composer.set_intensity("calm")
        return composer

    @staticmethod
    def victory_fanfare(root: str = "C") -> ChiptuneComposer:
        """Short victory jingle.

        Features:
        - Bright, triumphant
        - Major key with rising motion
        - Short duration

        Args:
            root: Root note (default C major)

        Returns:
            Configured ChiptuneComposer
        """
        composer = ChiptuneComposer.create(bpm=140, root=root, mode="lydian")
        composer.set_progression(["I", "V", "I"])
        return composer

    @staticmethod
    def title_screen(root: str = "F") -> ChiptuneComposer:
        """Memorable title screen music.

        Features:
        - Catchy, memorable melody
        - Major/Lydian mode
        - Loop-friendly

        Args:
            root: Root note (default F major)

        Returns:
            Configured ChiptuneComposer
        """
        composer = ChiptuneComposer.create(bpm=130, root=root, mode="major")
        composer.set_progression(["I", "IV", "vi", "V"])
        composer.set_intensity("dramatic")
        return composer

    @staticmethod
    def shop_theme(root: str = "G") -> ChiptuneComposer:
        """Cheerful shop/menu music.

        Features:
        - Upbeat, friendly
        - Major key
        - Light drums

        Args:
            root: Root note (default G major)

        Returns:
            Configured ChiptuneComposer
        """
        composer = ChiptuneComposer.create(bpm=115, root=root, mode="mixolydian")
        composer.set_progression(["I", "IV", "I", "V"])
        return composer

    @staticmethod
    def sad_scene(root: str = "D") -> ChiptuneComposer:
        """Emotional, sad scene music.

        Features:
        - Slow tempo
        - Minor key
        - No drums

        Args:
            root: Root note (default D minor)

        Returns:
            Configured ChiptuneComposer
        """
        composer = ChiptuneComposer.create(bpm=70, root=root, mode="minor")
        composer.set_progression(["i", "VI", "III", "VII"])
        composer.set_intensity("fading")
        return composer

    @staticmethod
    def chase_scene(root: str = "E") -> ChiptuneComposer:
        """Fast-paced chase/action music.

        Features:
        - Very fast tempo (180+ BPM)
        - Tense harmony
        - Driving rhythm

        Args:
            root: Root note (default E minor)

        Returns:
            Configured ChiptuneComposer
        """
        composer = ChiptuneComposer.create(bpm=185, root=root, mode="phrygian")
        composer.set_progression(["i", "bII", "i", "V"])
        composer.set_intensity("boss_fight")
        return composer


class EffectPresets:
    """Pre-built effect chains for common sounds."""

    @staticmethod
    def clean() -> EffectChain:
        """No effects - clean, dry signal."""
        return EffectChain(effects=[])

    @staticmethod
    def retro_gaming() -> EffectChain:
        """Classic retro gaming sound.

        Subtle chorus and short delay for depth
        without losing clarity.
        """
        return EffectChain(
            effects=[
                Chorus.subtle(),
                Echo.subtle(),
            ]
        )

    @staticmethod
    def space_adventure() -> EffectChain:
        """Sci-fi space game aesthetic.

        Lush chorus and longer delay with
        more feedback for spacious feel.
        """
        return EffectChain(
            effects=[
                Chorus.lush(),
                TapeDelay.space_echo(),
            ]
        )

    @staticmethod
    def lo_fi_nostalgia() -> EffectChain:
        """Lo-fi degraded sound.

        Tape-style delay with subtle tremolo
        for worn, nostalgic character.
        """
        return EffectChain(
            effects=[
                TapeDelay.lo_fi(),
                Tremolo.subtle(),
            ]
        )

    @staticmethod
    def arcade_cabinet() -> EffectChain:
        """Bright arcade machine sound.

        Slight chorus for stereo width,
        slapback for presence.
        """
        return EffectChain(
            effects=[
                Chorus.subtle(),
                TapeDelay.slapback(),
            ]
        )

    @staticmethod
    def dreamy() -> EffectChain:
        """Dreamy, ethereal sound.

        Heavy chorus and long delay with
        tremolo for floating feel.
        """
        return EffectChain(
            effects=[
                Chorus.lush(),
                TapeDelay(delay_time=0.5, feedback=0.55, mix=0.4),
                Tremolo(rate=1.5, depth=0.2),
            ]
        )

    @staticmethod
    def dungeon_reverb() -> EffectChain:
        """Cavernous dungeon atmosphere.

        Long echo with high feedback
        simulates stone chambers.
        """
        return EffectChain(
            effects=[
                Echo.cavernous(),
                Tremolo(rate=0.5, depth=0.1),
            ]
        )

    @staticmethod
    def boss_battle() -> EffectChain:
        """Intense boss battle sound.

        Minimal effects for clarity and punch,
        just slight depth enhancement.
        """
        return EffectChain(
            effects=[
                Echo.short(),
            ]
        )

    @staticmethod
    def underwater() -> EffectChain:
        """Underwater/aquatic atmosphere.

        Filtered delay and slow modulation
        for submerged feel.
        """
        return EffectChain(
            effects=[
                Chorus(rate=0.3, depth=3.0, mix=0.4),
                TapeDelay(delay_time=0.3, feedback=0.4, mix=0.35, highcut=2000),
            ]
        )


class ChipPresets:
    """Pre-configured chip system setups."""

    @staticmethod
    def nes_classic() -> NES2A03:
        """Classic NES sound configuration.

        Standard duty cycles as used in most
        NES games.
        """
        from chiptune.chip.systems import NES2A03

        return NES2A03.create()

    @staticmethod
    def nes_famitracker() -> NES2A03:
        """FamiTracker-style NES configuration.

        Slightly different duty cycle defaults
        popular in the chiptune community.
        """
        from chiptune.chip.systems import NES2A03

        return NES2A03.famitracker_style()


class QuickCompose:
    """One-liner composition helpers."""

    @staticmethod
    def random_melody(
        length_bars: int = 8,
        root: str = "C",
        mode: str = "major",
    ) -> ChiptuneComposer:
        """Generate a quick random melody.

        Args:
            length_bars: Length in bars
            root: Root note
            mode: Musical mode

        Returns:
            Composer with melody ready to build
        """
        return ChiptuneComposer.create(root=root, mode=mode).add_melody(length_bars=length_bars)

    @staticmethod
    def full_track(
        length_bars: int = 8,
        root: str = "C",
        mode: str = "major",
        drums: bool = True,
    ) -> ChiptuneComposer:
        """Generate a complete track with all parts.

        Args:
            length_bars: Length in bars
            root: Root note
            mode: Musical mode
            drums: Include drums

        Returns:
            Composer with full arrangement
        """
        composer = ChiptuneComposer.create(root=root, mode=mode)
        composer.add_melody(length_bars=length_bars)
        composer.add_countermelody()
        composer.add_bass()
        if drums:
            composer.add_drums()
        return composer

    @staticmethod
    def battle_track(length_bars: int = 16) -> ChiptuneComposer:
        """Quick battle music generation.

        Args:
            length_bars: Length in bars

        Returns:
            Battle-ready composer
        """
        composer = GenrePresets.battle_theme()
        composer.add_melody(length_bars=length_bars)
        composer.add_countermelody(motion="contrary")
        composer.add_bass(style="octave")
        composer.add_drums(pattern="driving")
        return composer

    @staticmethod
    def ambient_track(length_bars: int = 16) -> ChiptuneComposer:
        """Quick ambient/exploration music.

        Args:
            length_bars: Length in bars

        Returns:
            Ambient-ready composer
        """
        composer = GenrePresets.dungeon()
        composer.add_melody(length_bars=length_bars, contour="wave")
        composer.add_bass(style="root")
        return composer
