"""N-gram Markov chain for sequence generation."""

from __future__ import annotations

import random
from collections.abc import Hashable
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T", bound=Hashable)


class MarkovChain(BaseModel, Generic[T]):
    """N-gram Markov chain for probabilistic sequence generation.

    Learns transition probabilities from training sequences and generates
    new sequences that follow similar patterns.

    Attributes:
        order: Number of previous items to consider (N-gram size)
        transitions: Mapping from state tuples to next-item probabilities
        start_states: Valid starting states for generation
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    order: int = Field(default=2, ge=1, le=5)
    transitions: dict[tuple[Any, ...], dict[T, int]] = Field(default_factory=dict)
    start_states: list[tuple[Any, ...]] = Field(default_factory=list)

    def train(self, sequence: list[T]) -> None:
        """Train the chain on a sequence.

        Args:
            sequence: List of items to learn from
        """
        if len(sequence) <= self.order:
            return

        # Record starting state
        start = tuple(sequence[: self.order])
        if start not in self.start_states:
            self.start_states.append(start)

        # Build transition counts
        for i in range(len(sequence) - self.order):
            state = tuple(sequence[i : i + self.order])
            next_item = sequence[i + self.order]

            if state not in self.transitions:
                self.transitions[state] = {}

            if next_item not in self.transitions[state]:
                self.transitions[state][next_item] = 0

            self.transitions[state][next_item] += 1

    def train_multiple(self, sequences: list[list[T]]) -> None:
        """Train on multiple sequences.

        Args:
            sequences: List of sequences to learn from
        """
        for seq in sequences:
            self.train(seq)

    def _weighted_choice(self, choices: dict[T, int], rng: random.Random) -> T:
        """Select item based on weights."""
        total = sum(choices.values())
        r = rng.uniform(0, total)
        cumulative = 0

        for item, weight in choices.items():
            cumulative += weight
            if r <= cumulative:
                return item

        # Fallback (shouldn't happen)
        return list(choices.keys())[-1]

    def generate(
        self,
        length: int,
        seed: int | None = None,
        start: tuple[T, ...] | None = None,
    ) -> list[T]:
        """Generate a new sequence.

        Args:
            length: Desired sequence length
            seed: Random seed for reproducibility
            start: Starting state (uses random trained start if None)

        Returns:
            Generated sequence
        """
        if not self.transitions:
            return []

        rng = random.Random(seed)

        # Initialize with start state
        if start is not None:
            state = start
            result = list(start)
        elif self.start_states:
            state = rng.choice(self.start_states)
            result = list(state)
        else:
            state = rng.choice(list(self.transitions.keys()))
            result = list(state)

        # Generate remaining items
        while len(result) < length:
            if state not in self.transitions:
                # Dead end - try to find similar state or restart
                if self.start_states:
                    state = rng.choice(self.start_states)
                else:
                    break

            choices = self.transitions.get(state, {})
            if not choices:
                break

            next_item = self._weighted_choice(choices, rng)
            result.append(next_item)

            # Shift state window
            state = tuple(result[-self.order :])

        return result

    def get_probability(self, state: tuple[T, ...], next_item: T) -> float:
        """Get probability of next_item following state.

        Args:
            state: Current state tuple
            next_item: Item to check probability for

        Returns:
            Probability (0.0 to 1.0)
        """
        if state not in self.transitions:
            return 0.0

        choices = self.transitions[state]
        total = sum(choices.values())

        if next_item not in choices:
            return 0.0

        return choices[next_item] / total

    def get_next_options(self, state: tuple[T, ...]) -> dict[T, float]:
        """Get all possible next items with probabilities.

        Args:
            state: Current state tuple

        Returns:
            Dict mapping items to probabilities
        """
        if state not in self.transitions:
            return {}

        choices = self.transitions[state]
        total = sum(choices.values())

        return {item: count / total for item, count in choices.items()}

    def merge(self, other: MarkovChain[T]) -> MarkovChain[T]:
        """Merge another chain into this one.

        Args:
            other: Chain to merge

        Returns:
            New merged chain
        """
        merged = MarkovChain[T](order=self.order)
        merged.start_states = list(set(self.start_states + other.start_states))

        # Merge transitions
        all_states = set(self.transitions.keys()) | set(other.transitions.keys())

        for state in all_states:
            merged.transitions[state] = {}

            self_choices = self.transitions.get(state, {})
            other_choices = other.transitions.get(state, {})

            all_items = set(self_choices.keys()) | set(other_choices.keys())

            for item in all_items:
                count = self_choices.get(item, 0) + other_choices.get(item, 0)
                merged.transitions[state][item] = count

        return merged

    @property
    def num_states(self) -> int:
        """Number of unique states in the chain."""
        return len(self.transitions)

    @property
    def is_trained(self) -> bool:
        """Whether the chain has been trained."""
        return len(self.transitions) > 0


class WeightedMarkovChain(MarkovChain[T]):
    """Markov chain with adjustable randomness.

    Adds temperature parameter to control output randomness:
    - temperature=0.0: Always choose most likely
    - temperature=1.0: Normal probability distribution
    - temperature>1.0: More random, flatter distribution
    """

    temperature: float = Field(default=1.0, ge=0.0, le=3.0)

    def _weighted_choice(self, choices: dict[T, int], rng: random.Random) -> T:
        """Select with temperature-adjusted probabilities."""
        if self.temperature == 0.0:
            # Deterministic - pick highest
            return max(choices.keys(), key=lambda k: choices[k])

        # Apply temperature
        adjusted = {}
        for item, count in choices.items():
            adjusted[item] = count ** (1.0 / self.temperature)

        total = sum(adjusted.values())
        r = rng.uniform(0, total)
        cumulative = 0

        for item, weight in adjusted.items():
            cumulative += weight
            if r <= cumulative:
                return item

        return list(choices.keys())[-1]
