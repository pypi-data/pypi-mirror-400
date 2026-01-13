"""Command-line interface for py-chiptune.

Provides commands for generating chiptune music and sound effects
from the terminal.

Usage:
    chiptune generate --preset battle --output battle.wav
    chiptune sfx explosion --output explosion.wav
    chiptune list presets
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import Namespace


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="chiptune",
        description="Generate retro 8-bit/16-bit style music and sound effects.",
        epilog="Example: chiptune generate --preset battle --output music.wav",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.5.2",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate command
    gen_parser = subparsers.add_parser(
        "generate",
        help="Generate chiptune music",
        description="Generate music using genre presets or custom settings.",
    )
    gen_parser.add_argument(
        "--preset",
        "-p",
        choices=[
            "battle",
            "overworld",
            "dungeon",
            "victory",
            "title",
            "shop",
            "sad",
            "chase",
        ],
        default="overworld",
        help="Genre preset (default: overworld)",
    )
    gen_parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("output.wav"),
        help="Output file path (default: output.wav)",
    )
    gen_parser.add_argument(
        "--bars",
        "-b",
        type=int,
        default=8,
        help="Length in bars (default: 8)",
    )
    gen_parser.add_argument(
        "--root",
        "-r",
        default=None,
        help="Root note (e.g., C, A, F#). Overrides preset default.",
    )
    gen_parser.add_argument(
        "--bpm",
        type=int,
        default=None,
        help="Tempo in BPM. Overrides preset default.",
    )
    gen_parser.add_argument(
        "--effects",
        "-e",
        choices=[
            "clean",
            "retro",
            "space",
            "lofi",
            "arcade",
            "dreamy",
            "dungeon",
            "boss",
        ],
        default="retro",
        help="Effect preset (default: retro)",
    )
    gen_parser.add_argument(
        "--no-drums",
        action="store_true",
        help="Exclude drums from the track",
    )
    gen_parser.add_argument(
        "--no-bass",
        action="store_true",
        help="Exclude bass from the track",
    )
    gen_parser.add_argument(
        "--no-counter",
        action="store_true",
        help="Exclude countermelody from the track",
    )
    gen_parser.add_argument(
        "--seed",
        "-s",
        type=int,
        default=None,
        help="Random seed for reproducible output",
    )
    gen_parser.add_argument(
        "--format",
        "-f",
        choices=["wav", "midi"],
        default="wav",
        help="Output format (default: wav)",
    )

    # SFX command
    sfx_parser = subparsers.add_parser(
        "sfx",
        help="Generate sound effects",
        description="Generate retro game sound effects as MIDI.",
    )
    sfx_parser.add_argument(
        "type",
        choices=[
            "jump",
            "land",
            "coin",
            "powerup",
            "damage",
            "explosion",
            "laser",
            "shield",
            "teleport",
            "menu_select",
            "menu_confirm",
            "menu_back",
            "success",
            "error",
            "door_open",
            "door_close",
            "heartbeat",
            "countdown",
        ],
        help="Type of sound effect to generate",
    )
    sfx_parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("sfx.mid"),
        help="Output file path (default: sfx.mid)",
    )

    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List available presets and options",
        description="Display available presets, effects, and sound effect types.",
    )
    list_parser.add_argument(
        "category",
        nargs="?",
        choices=["presets", "effects", "sfx", "all"],
        default="all",
        help="Category to list (default: all)",
    )

    return parser


def cmd_generate(args: Namespace) -> int:
    """Execute the generate command."""
    import random

    from chiptune.output.audio import AudioExporter
    from chiptune.output.midi import MidiExporter
    from chiptune.presets import EffectPresets, GenrePresets

    # Set seed if provided
    if args.seed is not None:
        random.seed(args.seed)

    # Get genre preset
    preset_map = {
        "battle": GenrePresets.battle_theme,
        "overworld": GenrePresets.overworld,
        "dungeon": GenrePresets.dungeon,
        "victory": GenrePresets.victory_fanfare,
        "title": GenrePresets.title_screen,
        "shop": GenrePresets.shop_theme,
        "sad": GenrePresets.sad_scene,
        "chase": GenrePresets.chase_scene,
    }

    # Get root from args or use None for preset default
    root = args.root if args.root else None

    if root:
        composer = preset_map[args.preset](root=root)
    else:
        composer = preset_map[args.preset]()

    # Override BPM if specified
    if args.bpm:
        composer.bpm = args.bpm

    # Add tracks
    composer.add_melody(length_bars=args.bars)

    if not args.no_counter:
        composer.add_countermelody()

    if not args.no_bass:
        composer.add_bass()

    if not args.no_drums and args.preset not in ["sad", "victory"]:
        composer.add_drums()

    # Build track
    track = composer.build()

    # Get effect preset
    effect_map = {
        "clean": EffectPresets.clean,
        "retro": EffectPresets.retro_gaming,
        "space": EffectPresets.space_adventure,
        "lofi": EffectPresets.lo_fi_nostalgia,
        "arcade": EffectPresets.arcade_cabinet,
        "dreamy": EffectPresets.dreamy,
        "dungeon": EffectPresets.dungeon_reverb,
        "boss": EffectPresets.boss_battle,
    }
    effects = effect_map[args.effects]()

    # Export
    output_path = args.output

    if args.format == "midi" or str(output_path).endswith(".mid"):
        midi_exporter = MidiExporter()
        midi_exporter.export_file(track, str(output_path))
        print(f"Exported MIDI to: {output_path}")
    else:
        audio_exporter = AudioExporter()
        audio_exporter.export_wav(track, output_path, effects=effects)
        print(f"Exported WAV to: {output_path}")

    return 0


def cmd_sfx(args: Namespace) -> int:
    """Execute the sfx command."""
    from chiptune.sfx.effects import SFXGenerator

    sfx = SFXGenerator()

    # Map CLI names to method names
    method_map = {
        "jump": "jump",
        "land": "land",
        "coin": "coin_collect",
        "powerup": "powerup",
        "damage": "damage",
        "explosion": "explosion",
        "laser": "laser",
        "shield": "shield",
        "teleport": "teleport",
        "menu_select": "menu_select",
        "menu_confirm": "menu_confirm",
        "menu_back": "menu_back",
        "success": "success",
        "error": "error",
        "door_open": "door_open",
        "door_close": "door_close",
        "heartbeat": "heartbeat",
        "countdown": "countdown_tick",
    }

    method_name = method_map[args.type]
    generator_method = getattr(sfx, method_name)

    # Generate MIDI bytes
    midi_bytes = generator_method()

    # Save to file
    sfx.save(midi_bytes, str(args.output))

    print(f"Exported {args.type} SFX to: {args.output}")
    return 0


def cmd_list(args: Namespace) -> int:
    """Execute the list command."""
    category = args.category

    if category in ("presets", "all"):
        print("\nGenre Presets:")
        print("-" * 40)
        presets = [
            ("battle", "Intense battle/boss fight music (A minor, 165 BPM)"),
            ("overworld", "Adventurous exploration theme (C major, 120 BPM)"),
            ("dungeon", "Dark, mysterious atmosphere (E dorian, 85 BPM)"),
            ("victory", "Short victory fanfare (C lydian, 140 BPM)"),
            ("title", "Catchy title screen music (F major, 130 BPM)"),
            ("shop", "Cheerful shop/menu music (G mixolydian, 115 BPM)"),
            ("sad", "Emotional, melancholic scene (D minor, 70 BPM)"),
            ("chase", "Fast-paced action music (E phrygian, 185 BPM)"),
        ]
        for name, desc in presets:
            print(f"  {name:12} {desc}")

    if category in ("effects", "all"):
        print("\nEffect Presets:")
        print("-" * 40)
        effects = [
            ("clean", "No effects - dry signal"),
            ("retro", "Classic retro gaming (subtle chorus + echo)"),
            ("space", "Sci-fi atmosphere (lush chorus + space delay)"),
            ("lofi", "Lo-fi nostalgia (tape delay + tremolo)"),
            ("arcade", "Bright arcade sound (chorus + slapback)"),
            ("dreamy", "Ethereal floating feel (heavy effects)"),
            ("dungeon", "Cavernous reverb atmosphere"),
            ("boss", "Punchy minimal effects for clarity"),
        ]
        for name, desc in effects:
            print(f"  {name:12} {desc}")

    if category in ("sfx", "all"):
        print("\nSound Effects (outputs MIDI):")
        print("-" * 40)
        sfx_types = [
            ("jump", "Character jump sound"),
            ("land", "Landing thud"),
            ("coin", "Coin/pickup collect"),
            ("powerup", "Power-up acquisition"),
            ("damage", "Take damage/hit"),
            ("explosion", "Explosion effect"),
            ("laser", "Laser/projectile fire"),
            ("shield", "Shield activation"),
            ("teleport", "Teleport effect"),
            ("menu_select", "Menu selection"),
            ("menu_confirm", "Menu confirm action"),
            ("menu_back", "Menu back/cancel"),
            ("success", "Success/achievement"),
            ("error", "Error/invalid action"),
            ("door_open", "Door opening"),
            ("door_close", "Door closing"),
            ("heartbeat", "Heartbeat/tension"),
            ("countdown", "Countdown tick"),
        ]
        for name, desc in sfx_types:
            print(f"  {name:14} {desc}")

    print()
    return 0


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "generate":
        return cmd_generate(args)
    elif args.command == "sfx":
        return cmd_sfx(args)
    elif args.command == "list":
        return cmd_list(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
