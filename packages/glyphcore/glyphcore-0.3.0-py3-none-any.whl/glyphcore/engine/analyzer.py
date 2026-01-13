"""
Semantic analyzer - computes Direction, Strength, Momentum, Regime, Confidence.

This is the brain. It is domain-agnostic and renderer-agnostic.
"""

from typing import Sequence, Optional
from glyphcore.core.signal import Signal


class Analyzer:
    """Pure semantic analysis. No rendering. No domain meaning."""

    @staticmethod
    def analyze(
        values: Sequence[float],
        labels: Optional[Sequence[str]] = None
    ) -> Signal:
        if not values or len(values) < 2:
            return Signal(
                direction="UP / DOWN",
                strength=0.0,
                momentum="STABLE",
                regime="TREND",
                confidence=0.0,
                values=list(values),
                labels=list(labels) if labels else None,
            )

        first, last = values[0], values[-1]
        min_v, max_v = min(values), max(values)
        value_range = max_v - min_v

        # ------------------------------------------------------------
        # Direction & Strength
        # ------------------------------------------------------------
        if value_range == 0:
            direction = "FLAT"
            strength = 0.0
        else:
            net_change = last - first
            pct_change = abs(net_change) / max(abs(first), 1e-9)

            FLAT_THRESHOLD = 0.01  # 1%

            if pct_change < FLAT_THRESHOLD:
                direction = "FLAT"
            elif net_change > 0:
                direction = "UP"
            else:
                direction = "DOWN"

            strength = min(1.0, abs(net_change) / value_range)

        # ------------------------------------------------------------
        # Momentum
        # ------------------------------------------------------------
        momentum = Analyzer._compute_momentum(values)

        # ------------------------------------------------------------
        # Regime
        # ------------------------------------------------------------
        regime = Analyzer._compute_regime(values)

        # ------------------------------------------------------------
        # Confidence
        # ------------------------------------------------------------
        confidence = Analyzer._compute_confidence(values, direction)

        return Signal(
            direction=direction,
            strength=strength,
            momentum=momentum,
            regime=regime,
            confidence=confidence,
            values=list(values),
            labels=list(labels) if labels else None,
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _compute_momentum(values: Sequence[float]) -> str:
        if len(values) < 4:
            return "STABLE"

        mid = len(values) // 2

        def avg_abs_change(seq: Sequence[float]) -> float:
            changes = [abs(seq[i] - seq[i - 1]) for i in range(1, len(seq))]
            return sum(changes) / len(changes) if changes else 0.0

        first_rate = avg_abs_change(values[: mid + 1])
        second_rate = avg_abs_change(values[mid:])

        if first_rate == 0:
            return "STABLE"

        ratio = second_rate / first_rate

        if ratio > 1.2:
            return "ACCELERATING"
        if ratio < 0.8:
            return "DECELERATING"
        return "STABLE"

    # ------------------------------------------------------------------

    @staticmethod
    def _compute_regime(values: Sequence[float]) -> str:
        if len(values) < 3:
            return "RANGE"

        changes = [values[i] - values[i - 1] for i in range(1, len(values))]
        abs_changes = [abs(c) for c in changes]

        mean_change = sum(abs_changes) / len(abs_changes)
        if mean_change == 0:
            return "RANGE"

        variance = sum((c - mean_change) ** 2 for c in abs_changes) / len(abs_changes)
        coeff_var = (variance ** 0.5) / mean_change

        net_change = abs(values[-1] - values[0])
        value_range = max(values) - min(values)

        # Detect sign instability
        sign_flips = sum(
            1 for i in range(len(changes) - 1)
            if changes[i] * changes[i + 1] < 0
        )

        # ORDER MATTERS — volatility dominates trend
        if sign_flips >= len(changes) // 2 or coeff_var > 0.5:
            return "VOLATILE"

        if value_range > 0 and net_change / value_range > 0.5 and coeff_var < 0.3:
            return "TREND"

        return "RANGE"

    # ------------------------------------------------------------------

    @staticmethod
    def _compute_confidence(values: Sequence[float], direction: str) -> float:
        if len(values) < 3:
            return 0.0

        changes = [values[i] - values[i - 1] for i in range(1, len(values))]
        abs_changes = [abs(c) for c in changes]

        mean_change = sum(abs_changes) / len(abs_changes)
        if mean_change == 0:
            return 1.0 if direction == "FLAT" else 0.0

        variance = sum((c - mean_change) ** 2 for c in abs_changes) / len(abs_changes)
        coeff_var = (variance ** 0.5) / mean_change

        if direction == "FLAT":
            return max(0.0, min(1.0, 1.0 - coeff_var))

        aligned = sum(
            1 for c in changes
            if (c > 0 and direction == "UP") or (c < 0 and direction == "DOWN")
        )
        consistency = aligned / len(changes)

        value_range = max(values) - min(values)
        magnitude = abs(values[-1] - values[0]) / value_range if value_range else 0.0

        return max(0.0, min(1.0, consistency * 0.6 + magnitude * 0.4))
