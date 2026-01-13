"""
Signal: The semantic contract between renderers.

This is the shared truth. If something is not in Signal,
renderers are not allowed to invent it.
"""

from dataclasses import dataclass
from typing import Literal, Sequence, Optional

Direction = Literal["UP", "DOWN", "FLAT"]
Momentum = Literal["ACCELERATING", "DECELERATING", "STABLE"]
Regime = Literal["TREND", "RANGE", "VOLATILE"]

__all__ = ["Signal"]


@dataclass(frozen=True)
class Signal:
    """
    Semantic representation of system state (domain-agnostic).

    This is the immutable contract that all renderers consume.
    The framework never names the domain.
    """
    direction: Direction
    strength: float
    momentum: Momentum
    regime: Regime
    confidence: float

    values: Sequence[float]
    labels: Optional[Sequence[str]]
