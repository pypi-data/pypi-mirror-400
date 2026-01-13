"""Adaptive intensity system for dynamic music generation."""

from __future__ import annotations

from enum import Enum

import numpy as np
from pydantic import BaseModel, Field


class IntensityCurve(str, Enum):
    """Intensity curve shapes over time."""

    CONSTANT = "constant"  # Stay at one level
    LINEAR_UP = "linear_up"  # Gradual increase
    LINEAR_DOWN = "linear_down"  # Gradual decrease
    ARCH = "arch"  # Rise then fall
    TROUGH = "trough"  # Fall then rise
    WAVE = "wave"  # Oscillating
    BATTLE = "battle"  # Fast buildup, sustain, dramatic end
    EXPLORATION = "exploration"  # Low with occasional peaks


class IntensityProfile(BaseModel):
    """Defines how intensity changes over time.

    Intensity is a 0.0-1.0 value that can drive:
    - Tempo changes
    - Note density
    - Layer count
    - Dynamics (velocity)
    - Effect parameters

    Attributes:
        base_intensity: Starting intensity level
        curve: Shape of intensity change over time
        variation: Random variation amount
        peak_positions: Positions (0-1) of intensity peaks
    """

    base_intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    curve: IntensityCurve = IntensityCurve.CONSTANT
    variation: float = Field(default=0.1, ge=0.0, le=0.5)
    peak_positions: list[float] = Field(default_factory=list)
    peak_width: float = Field(default=0.1, ge=0.01, le=0.5)

    def get_intensity(self, progress: float, seed: int | None = None) -> float:
        """Get intensity at a given progress point.

        Args:
            progress: Position in piece (0.0 to 1.0)
            seed: Random seed for variation

        Returns:
            Intensity value (0.0 to 1.0)
        """
        progress = max(0.0, min(1.0, progress))

        # Base curve
        if self.curve == IntensityCurve.CONSTANT:
            intensity = self.base_intensity

        elif self.curve == IntensityCurve.LINEAR_UP:
            intensity = progress

        elif self.curve == IntensityCurve.LINEAR_DOWN:
            intensity = 1.0 - progress

        elif self.curve == IntensityCurve.ARCH:
            # Parabola peaking at 0.5
            intensity = 4 * progress * (1 - progress)

        elif self.curve == IntensityCurve.TROUGH:
            # Inverted parabola
            intensity = 1 - 4 * progress * (1 - progress)

        elif self.curve == IntensityCurve.WAVE:
            # Sine wave
            intensity = 0.5 + 0.5 * np.sin(2 * np.pi * progress * 2)

        elif self.curve == IntensityCurve.BATTLE:
            # Fast rise, sustain high, dramatic finish
            if progress < 0.2:
                intensity = progress * 5 * 0.8  # Quick rise to 0.8
            elif progress < 0.85:
                intensity = 0.8 + (progress - 0.2) * 0.3  # Gradual to 1.0
            else:
                intensity = 1.0 - (progress - 0.85) * 6  # Quick drop

        elif self.curve == IntensityCurve.EXPLORATION:
            # Low base with occasional peaks
            intensity = 0.3 + 0.2 * np.sin(2 * np.pi * progress * 4)

        else:
            intensity = self.base_intensity

        # Add peaks at specified positions
        for peak_pos in self.peak_positions:
            distance = abs(progress - peak_pos)
            if distance < self.peak_width:
                peak_boost = (1 - distance / self.peak_width) * 0.5
                intensity = min(1.0, intensity + peak_boost)

        # Add variation
        if self.variation > 0 and seed is not None:
            rng = np.random.default_rng(seed + int(progress * 1000))
            noise = rng.normal(0, self.variation)
            intensity += noise

        return float(max(0.0, min(1.0, intensity)))

    def get_intensity_array(self, num_points: int, seed: int | None = None) -> list[float]:
        """Get array of intensity values.

        Args:
            num_points: Number of points to sample
            seed: Random seed

        Returns:
            List of intensity values
        """
        return [self.get_intensity(i / max(1, num_points - 1), seed) for i in range(num_points)]

    @classmethod
    def calm(cls) -> IntensityProfile:
        """Calm, steady intensity."""
        return cls(base_intensity=0.3, curve=IntensityCurve.CONSTANT, variation=0.05)

    @classmethod
    def building(cls) -> IntensityProfile:
        """Gradually building intensity."""
        return cls(base_intensity=0.2, curve=IntensityCurve.LINEAR_UP, variation=0.1)

    @classmethod
    def fading(cls) -> IntensityProfile:
        """Gradually fading intensity."""
        return cls(base_intensity=0.8, curve=IntensityCurve.LINEAR_DOWN, variation=0.1)

    @classmethod
    def dramatic(cls) -> IntensityProfile:
        """Dramatic arch shape."""
        return cls(base_intensity=0.5, curve=IntensityCurve.ARCH, variation=0.15)

    @classmethod
    def battle(cls) -> IntensityProfile:
        """Battle/action intensity curve."""
        return cls(
            base_intensity=0.7,
            curve=IntensityCurve.BATTLE,
            variation=0.1,
            peak_positions=[0.5, 0.75],
        )

    @classmethod
    def exploration(cls) -> IntensityProfile:
        """Exploration/ambient intensity."""
        return cls(
            base_intensity=0.3,
            curve=IntensityCurve.EXPLORATION,
            variation=0.15,
            peak_positions=[0.3, 0.7],
            peak_width=0.15,
        )

    @classmethod
    def boss_fight(cls) -> IntensityProfile:
        """Intense boss fight curve."""
        return cls(
            base_intensity=0.8,
            curve=IntensityCurve.WAVE,
            variation=0.1,
            peak_positions=[0.25, 0.5, 0.75, 0.95],
            peak_width=0.08,
        )


class IntensityController(BaseModel):
    """Maps intensity to musical parameters.

    Translates abstract intensity values into concrete musical changes:
    - Tempo adjustments
    - Note density
    - Velocity scaling
    - Layer activation
    - Effect parameters
    """

    profile: IntensityProfile = Field(default_factory=IntensityProfile.dramatic)

    # Tempo range
    min_tempo: int = Field(default=80, ge=40, le=200)
    max_tempo: int = Field(default=160, ge=60, le=300)

    # Velocity range
    min_velocity: int = Field(default=60, ge=1, le=127)
    max_velocity: int = Field(default=120, ge=1, le=127)

    # Density multiplier range
    min_density: float = Field(default=0.5, ge=0.1, le=2.0)
    max_density: float = Field(default=2.0, ge=0.5, le=4.0)

    def get_tempo(self, progress: float) -> int:
        """Get tempo at progress point.

        Args:
            progress: Position (0-1)

        Returns:
            Tempo in BPM
        """
        intensity = self.profile.get_intensity(progress)
        tempo = self.min_tempo + intensity * (self.max_tempo - self.min_tempo)
        return int(tempo)

    def get_velocity(self, progress: float) -> int:
        """Get velocity at progress point.

        Args:
            progress: Position (0-1)

        Returns:
            MIDI velocity (1-127)
        """
        intensity = self.profile.get_intensity(progress)
        velocity = self.min_velocity + intensity * (self.max_velocity - self.min_velocity)
        return int(max(1, min(127, velocity)))

    def get_density(self, progress: float) -> float:
        """Get note density multiplier at progress point.

        Args:
            progress: Position (0-1)

        Returns:
            Density multiplier
        """
        intensity = self.profile.get_intensity(progress)
        return self.min_density + intensity * (self.max_density - self.min_density)

    def get_active_layers(self, progress: float, total_layers: int = 4) -> int:
        """Get number of active layers at progress point.

        Args:
            progress: Position (0-1)
            total_layers: Maximum number of layers

        Returns:
            Number of layers to activate
        """
        intensity = self.profile.get_intensity(progress)

        # At least 1 layer, scale with intensity
        layers = 1 + int(intensity * (total_layers - 1))
        return max(1, min(total_layers, layers))

    def should_add_drums(self, progress: float, threshold: float = 0.4) -> bool:
        """Whether drums should be active at this point.

        Args:
            progress: Position (0-1)
            threshold: Intensity threshold for drums

        Returns:
            True if drums should play
        """
        return self.profile.get_intensity(progress) >= threshold

    def get_effect_mix(self, progress: float) -> float:
        """Get effect wet/dry mix based on intensity.

        Lower intensity = more effects (reverb, delay)
        Higher intensity = cleaner sound

        Args:
            progress: Position (0-1)

        Returns:
            Effect mix (0-1, where 1 = more wet)
        """
        intensity = self.profile.get_intensity(progress)
        # Inverse relationship: calm = more effects
        return 0.2 + (1 - intensity) * 0.6

    @classmethod
    def action(cls) -> IntensityController:
        """Controller for action/battle music."""
        return cls(
            profile=IntensityProfile.battle(),
            min_tempo=120,
            max_tempo=180,
            min_velocity=80,
            max_velocity=127,
        )

    @classmethod
    def ambient(cls) -> IntensityController:
        """Controller for ambient/exploration music."""
        return cls(
            profile=IntensityProfile.exploration(),
            min_tempo=60,
            max_tempo=100,
            min_velocity=50,
            max_velocity=90,
            min_density=0.3,
            max_density=1.0,
        )

    @classmethod
    def cinematic(cls) -> IntensityController:
        """Controller for cinematic/dramatic music."""
        return cls(
            profile=IntensityProfile.dramatic(),
            min_tempo=80,
            max_tempo=140,
            min_velocity=60,
            max_velocity=120,
        )
