"""Effect chain for combining multiple effects."""

from collections.abc import Iterator
from typing import Union

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, Field

from chiptune.output.audio.effects.base import SampleEffect


class EffectChain(BaseModel):
    """Chain multiple effects together.

    Effects are processed in order, with each effect's output
    becoming the next effect's input.

    Example:
        chain = EffectChain(effects=[
            Tremolo(rate=4.0, depth=0.3),
            TapeDelay.space_echo(),
            Chorus.subtle(),
        ])
        output = chain.process(samples)

    Or using the | operator:
        chain = Tremolo() | TapeDelay() | Chorus()
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    effects: list[SampleEffect] = Field(default_factory=list)

    def process(
        self,
        samples: NDArray[np.float32],
        sample_rate: int = 44100,
    ) -> NDArray[np.float32]:
        """Process samples through all effects in chain.

        Args:
            samples: Input audio samples
            sample_rate: Sample rate in Hz

        Returns:
            Processed audio samples
        """
        result = samples
        for effect in self.effects:
            result = effect.process(result, sample_rate)
        return result

    def __or__(self, other: Union[SampleEffect, "EffectChain"]) -> "EffectChain":
        """Chain effects using the | operator."""
        if isinstance(other, EffectChain):
            return EffectChain(effects=self.effects + other.effects)
        return EffectChain(effects=self.effects + [other])

    def __ror__(self, other: SampleEffect) -> "EffectChain":
        """Support effect | chain syntax."""
        return EffectChain(effects=[other] + self.effects)

    def add(self, effect: SampleEffect) -> "EffectChain":
        """Add an effect to the chain (returns new chain)."""
        return EffectChain(effects=self.effects + [effect])

    def __len__(self) -> int:
        return len(self.effects)

    def iter_effects(self) -> Iterator[SampleEffect]:
        """Iterate over effects in the chain."""
        return iter(self.effects)


class ParallelChain(BaseModel):
    """Process effects in parallel and mix results.

    Unlike EffectChain which processes serially, ParallelChain
    runs all effects on the original input and mixes the outputs.

    Useful for:
    - Layered effects (e.g., chorus + delay simultaneously)
    - Wet/dry blending
    - Creating complex textures

    Example:
        parallel = ParallelChain(
            chains=[
                EffectChain([Chorus.lush()]),
                EffectChain([TapeDelay.dub()]),
            ],
            levels=[0.5, 0.5],
            dry_level=0.3,
        )
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    chains: list[SampleEffect | EffectChain] = Field(default_factory=list)
    levels: list[float] = Field(default_factory=list)
    dry_level: float = Field(default=0.0, ge=0.0, le=1.0)

    def process(
        self,
        samples: NDArray[np.float32],
        sample_rate: int = 44100,
    ) -> NDArray[np.float32]:
        """Process samples through parallel chains and mix.

        Args:
            samples: Input audio samples
            sample_rate: Sample rate in Hz

        Returns:
            Mixed output from all parallel chains
        """
        if len(self.chains) == 0:
            return samples

        # Normalize levels
        levels = self.levels + [1.0] * (len(self.chains) - len(self.levels))
        total_level = sum(levels) + self.dry_level

        # Start with dry signal
        result = samples * (self.dry_level / total_level)

        # Add each chain's output
        for chain, level in zip(self.chains, levels, strict=False):
            if isinstance(chain, EffectChain):
                processed = chain.process(samples, sample_rate)
            else:
                processed = chain.process(samples, sample_rate)
            result = result + processed * (level / total_level)

        return result.astype(np.float32)


class EffectPresets:
    """Pre-built effect chains for common use cases."""

    @staticmethod
    def ambient() -> EffectChain:
        """Lush ambient effect chain."""
        from chiptune.output.audio.effects.chorus import Chorus
        from chiptune.output.audio.effects.tape_delay import TapeDelay
        from chiptune.output.audio.effects.tremolo import Tremolo

        return EffectChain(
            effects=[
                Chorus.lush(),
                TapeDelay(delay_time=0.4, feedback=0.45, mix=0.35, highcut=3500),
                Tremolo.subtle(),
            ]
        )

    @staticmethod
    def retro() -> EffectChain:
        """Retro 80s effect chain."""
        from chiptune.output.audio.effects.chorus import Chorus
        from chiptune.output.audio.effects.tape_delay import TapeDelay

        return EffectChain(
            effects=[
                Chorus.classic(),
                TapeDelay.space_echo(),
            ]
        )

    @staticmethod
    def lo_fi() -> EffectChain:
        """Lo-fi degradation chain."""
        from chiptune.output.audio.effects.chorus import Unison
        from chiptune.output.audio.effects.tape_delay import TapeDelay
        from chiptune.output.audio.effects.tremolo import Tremolo

        return EffectChain(
            effects=[
                TapeDelay.lo_fi(),
                Unison.subtle(),
                Tremolo(rate=2.0, depth=0.15),
            ]
        )

    @staticmethod
    def thick_lead() -> EffectChain:
        """Thick lead sound with chorus and delay."""
        from chiptune.output.audio.effects.chorus import Chorus, Unison
        from chiptune.output.audio.effects.tape_delay import TapeDelay

        return EffectChain(
            effects=[
                Unison(voices=3, detune=8.0, mix=0.6),
                Chorus.subtle(),
                TapeDelay(delay_time=0.25, feedback=0.25, mix=0.2),
            ]
        )

    @staticmethod
    def dreamy() -> EffectChain:
        """Dreamy, ethereal effect chain."""
        from chiptune.output.audio.effects.chorus import Ensemble
        from chiptune.output.audio.effects.tape_delay import TapeDelay
        from chiptune.output.audio.effects.tremolo import Tremolo

        return EffectChain(
            effects=[
                Ensemble.synth_pad(),
                TapeDelay(delay_time=0.5, feedback=0.55, mix=0.4, tape_age=0.3, highcut=3000),
                Tremolo(rate=1.5, depth=0.2),
            ]
        )

    @staticmethod
    def clean_chorus() -> EffectChain:
        """Clean chorus only."""
        from chiptune.output.audio.effects.chorus import Chorus

        return EffectChain(effects=[Chorus.classic()])

    @staticmethod
    def slapback() -> EffectChain:
        """Rockabilly slapback delay."""
        from chiptune.output.audio.effects.tape_delay import TapeDelay

        return EffectChain(effects=[TapeDelay.slapback()])
