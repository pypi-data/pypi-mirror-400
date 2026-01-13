"""Semantic API for AI agents to compose music.

Provides a high-level, natural language-inspired interface
for music generation without requiring music theory knowledge.
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel

from chiptune.composer.composer import BassStyle, ChiptuneComposer, DrumStyle
from chiptune.patterns.jingles import Jingle, JingleType
from chiptune.patterns.themes import GameTheme, MelodicContour
from chiptune.theory.keys import Mode


class MusicAgent(BaseModel):
    """Semantic interface for AI agents to generate music.

    Designed for agents that don't have music theory knowledge
    but need to generate context-appropriate game music.

    Example:
        ```python
        agent = MusicAgent()

        # Generate music from context description
        music = agent.compose_for_context(
            context="player enters the final boss arena",
            duration_seconds=60.0,
            intensity=0.9,
        )

        # Generate a quick sound effect
        sfx = agent.generate_sfx("coin_collect")
        ```
    """

    default_key: str = "C"

    # Context keywords to theme mapping
    CONTEXT_THEMES: ClassVar[dict[str, GameTheme]] = {
        # Battle/Combat
        "battle": GameTheme.BATTLE,
        "fight": GameTheme.BATTLE,
        "combat": GameTheme.BATTLE,
        "enemy": GameTheme.BATTLE,
        # Boss
        "boss": GameTheme.BOSS,
        "final boss": GameTheme.BOSS,
        "villain": GameTheme.BOSS,
        "showdown": GameTheme.BOSS,
        # Victory
        "victory": GameTheme.VICTORY,
        "win": GameTheme.VICTORY,
        "triumph": GameTheme.VICTORY,
        "success": GameTheme.VICTORY,
        "won": GameTheme.VICTORY,
        # Game Over
        "game over": GameTheme.GAME_OVER,
        "death": GameTheme.GAME_OVER,
        "defeat": GameTheme.GAME_OVER,
        "lost": GameTheme.GAME_OVER,
        # Overworld/Exploration
        "explore": GameTheme.OVERWORLD,
        "travel": GameTheme.OVERWORLD,
        "journey": GameTheme.OVERWORLD,
        "adventure": GameTheme.OVERWORLD,
        "overworld": GameTheme.OVERWORLD,
        "map": GameTheme.OVERWORLD,
        # Dungeon
        "dungeon": GameTheme.DUNGEON,
        "cave": GameTheme.DUNGEON,
        "dark": GameTheme.DUNGEON,
        "underground": GameTheme.DUNGEON,
        "maze": GameTheme.DUNGEON,
        # Shop
        "shop": GameTheme.SHOP,
        "store": GameTheme.SHOP,
        "merchant": GameTheme.SHOP,
        "buy": GameTheme.SHOP,
        "sell": GameTheme.SHOP,
        # Puzzle
        "puzzle": GameTheme.PUZZLE,
        "think": GameTheme.PUZZLE,
        "riddle": GameTheme.PUZZLE,
        # Menu/Title
        "menu": GameTheme.MENU,
        "title": GameTheme.TITLE_SCREEN,
        "main menu": GameTheme.MENU,
        "start screen": GameTheme.TITLE_SCREEN,
        # Cutscene
        "cutscene": GameTheme.CUTSCENE,
        "story": GameTheme.CUTSCENE,
        "dialogue": GameTheme.CUTSCENE,
        "conversation": GameTheme.CUTSCENE,
        # Credits
        "credits": GameTheme.CREDITS,
        "ending": GameTheme.CREDITS,
        "finale": GameTheme.CREDITS,
    }

    # SFX event mappings
    SFX_EVENTS: ClassVar[dict[str, JingleType]] = {
        "coin": JingleType.COIN_COLLECT,
        "coin_collect": JingleType.COIN_COLLECT,
        "pickup": JingleType.ITEM_GET,
        "item": JingleType.ITEM_GET,
        "item_get": JingleType.ITEM_GET,
        "collect": JingleType.ITEM_GET,
        "level_up": JingleType.LEVEL_UP,
        "levelup": JingleType.LEVEL_UP,
        "power_up": JingleType.POWER_UP,
        "powerup": JingleType.POWER_UP,
        "victory": JingleType.VICTORY_FANFARE,
        "win": JingleType.VICTORY_FANFARE,
        "fanfare": JingleType.VICTORY_FANFARE,
        "secret": JingleType.SECRET_FOUND,
        "discovery": JingleType.SECRET_FOUND,
        "danger": JingleType.DANGER_WARNING,
        "warning": JingleType.DANGER_WARNING,
        "alert": JingleType.DANGER_WARNING,
        "game_over": JingleType.GAME_OVER,
        "death": JingleType.GAME_OVER,
        "fail": JingleType.GAME_OVER,
        "menu_select": JingleType.MENU_SELECT,
        "select": JingleType.MENU_SELECT,
        "cursor": JingleType.MENU_SELECT,
        "menu_confirm": JingleType.MENU_CONFIRM,
        "confirm": JingleType.MENU_CONFIRM,
        "ok": JingleType.MENU_CONFIRM,
        "quest_complete": JingleType.QUEST_COMPLETE,
        "quest": JingleType.QUEST_COMPLETE,
        "mission": JingleType.QUEST_COMPLETE,
        "damage": JingleType.DAMAGE,
        "hurt": JingleType.DAMAGE,
        "hit": JingleType.DAMAGE,
    }

    def compose_for_context(
        self,
        context: str,
        duration_seconds: float = 30.0,
        intensity: float = 0.5,
        key: str | None = None,
    ) -> bytes:
        """Generate music appropriate for a game context.

        Parses the context description to determine appropriate
        theme, tempo, and mood, then generates music.

        Args:
            context: Natural language description of the game context
                (e.g., "player entered boss room", "exploring the forest")
            duration_seconds: Approximate duration in seconds
            intensity: Emotional intensity (0.0 = calm, 1.0 = intense)
            key: Optional key override (e.g., "C", "Dm", "F#")

        Returns:
            MIDI file as bytes
        """
        # Analyze context to determine theme
        theme = self._analyze_context(context)

        # Determine key
        root = key if key else self.default_key
        if key and len(key) > 1 and key[-1] == "m":
            root = key[:-1]
            # Minor key requested
            mode = Mode.AEOLIAN
        else:
            mode = Mode.IONIAN

        # Create composer with theme
        composer = ChiptuneComposer.create(bpm=120, root=root, mode=mode)
        composer.set_theme(theme)

        # Adjust for intensity
        if intensity > 0.7:
            composer.bpm = int(composer.bpm * 1.15)
            drum_style = DrumStyle.DRIVING
            melody_contour = MelodicContour.ASCENDING
        elif intensity < 0.3:
            composer.bpm = int(composer.bpm * 0.85)
            drum_style = DrumStyle.SPARSE
            melody_contour = MelodicContour.FLAT
        else:
            drum_style = DrumStyle.BASIC
            melody_contour = MelodicContour.WAVE

        # Calculate bars from duration
        beats_per_second = composer.bpm / 60.0
        total_beats = duration_seconds * beats_per_second
        bars = max(4, int(total_beats / 4))  # Assuming 4/4 time

        # Build composition
        composer.add_melody(contour=melody_contour, length_bars=bars)
        composer.add_bass(style=BassStyle.ROOT if intensity < 0.5 else BassStyle.OCTAVE)
        composer.add_arpeggio_layer()
        composer.add_drums(pattern=drum_style)

        return composer.to_midi_bytes()

    def _analyze_context(self, context: str) -> GameTheme:
        """Analyze context string to determine appropriate theme."""
        context_lower = context.lower()

        # Check for keyword matches
        for keyword, theme in self.CONTEXT_THEMES.items():
            if keyword in context_lower:
                return theme

        # Default to overworld for unknown contexts
        return GameTheme.OVERWORLD

    def generate_sfx(
        self,
        event: str,
        key: str | None = None,
    ) -> bytes:
        """Generate a sound effect for a game event.

        Args:
            event: Event type (e.g., "coin_collect", "level_up", "damage")
            key: Optional key for the sound (defaults to C)

        Returns:
            MIDI file as bytes
        """
        from chiptune.output.midi import MidiExporter

        # Determine jingle type
        event_lower = event.lower().replace(" ", "_")
        jingle_type = self.SFX_EVENTS.get(event_lower, JingleType.MENU_SELECT)

        # Create jingle
        root = key if key else self.default_key
        jingle = Jingle.create(jingle_type, root=root)

        # Export to MIDI
        exporter = MidiExporter()
        return exporter.export_jingle_bytes(jingle)

    def compose_loop(
        self,
        mood: str,
        bars: int = 8,
        key: str | None = None,
    ) -> bytes:
        """Generate a loopable music segment.

        Args:
            mood: Emotional mood (heroic, mysterious, peaceful, etc.)
            bars: Number of bars (should be power of 2 for clean loops)
            key: Optional key

        Returns:
            MIDI file as bytes
        """
        root = key if key else self.default_key

        composer = ChiptuneComposer.create(bpm=120, root=root)
        composer.set_mood(mood)

        # Ensure loop-friendly bar count
        bars = max(4, bars)
        if bars not in (4, 8, 16, 32):
            # Round to nearest power of 2
            import math

            bars = 2 ** round(math.log2(bars))

        composer.add_melody(contour=MelodicContour.ARCH, length_bars=bars)
        composer.add_bass(style=BassStyle.ROOT)
        composer.add_arpeggio_layer()
        composer.add_drums(pattern=DrumStyle.BASIC)

        return composer.to_midi_bytes()

    def compose_transition(
        self,
        from_mood: str,
        to_mood: str,
        duration_seconds: float = 4.0,
    ) -> bytes:
        """Generate a musical transition between moods.

        Useful for transitioning between game states
        (e.g., exploration to battle).

        Args:
            from_mood: Starting mood
            to_mood: Ending mood
            duration_seconds: Transition duration

        Returns:
            MIDI file as bytes
        """
        # For now, generate a short piece in the target mood
        # Future: implement actual crossfade/modulation
        return self.compose_loop(mood=to_mood, bars=4, key=self.default_key)

    @classmethod
    def list_themes(cls) -> list[str]:
        """List available game themes."""
        return [theme.value for theme in GameTheme]

    @classmethod
    def list_sfx_events(cls) -> list[str]:
        """List available SFX event types."""
        return list(set(cls.SFX_EVENTS.keys()))

    @classmethod
    def list_moods(cls) -> list[str]:
        """List available moods."""
        return list(ChiptuneComposer.MOOD_SETTINGS.keys())
