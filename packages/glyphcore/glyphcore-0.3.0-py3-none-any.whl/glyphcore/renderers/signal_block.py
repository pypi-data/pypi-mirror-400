"""
StatusBlock Renderer - decision surface, not chart.

Renders Signal as a StatusBlock that answers:
"Is this system in a state that requires attention?"

Text-first. Wave-last. Domain-agnostic.
"""

from typing import Sequence, Optional

from glyphcore.core.signal import Signal
from glyphcore.compliance.statusblock import validate_statusblock


class SignalBlockRenderer:
    """
    Renders a Signal as a StatusBlock (domain-agnostic decision surface).

    Rules enforced by design:
    - Text first, wave last
    - Wave max height = 2 rows
    - No chart density
    - No semantic invention
    """

    BLOCK_CHARS = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']

    def __init__(self, title: str = ""):
        self.title = title

    # ---------- formatting helpers ----------

    def _direction_symbol(self, direction: str) -> str:
        return {
            "UP": "▲",
            "DOWN": "▼",
            "FLAT": "→",
        }.get(direction, "→")

    def _format_percentage(self, strength: float, direction: str) -> str:
        sign = "+" if direction == "UP" else "-" if direction == "DOWN" else ""
        return f"{sign}{strength * 100:.1f}%"

    def _format_value(self, value: float) -> str:
        if abs(value) >= 1000:
            return f"{value:,.0f}"
        return f"{value:.4f}".rstrip("0").rstrip(".")

    def _format_span(self, labels) -> Optional[str]:
        if not labels or len(labels) < 2:
            return None
        return f"Span: {labels[0]} → {labels[-1]}"

    # ---------- sparkline ----------

    def _sparkline(self, values: Sequence[float], max_width: int = 25) -> str:
        if not values:
            return ""

        if len(values) > max_width:
            step = len(values) / max_width
            values = (
                [values[int(i * step)] for i in range(max_width - 1)]
                + [values[-1]]
            )

        lo, hi = min(values), max(values)
        if lo == hi:
            return self.BLOCK_CHARS[3] * len(values)

        out = []
        for v in values:
            idx = int((v - lo) / (hi - lo) * (len(self.BLOCK_CHARS) - 1))
            out.append(self.BLOCK_CHARS[idx])
        return "".join(out)

    # ---------- renderer ----------

    def render(
        self,
        signal: Signal,
        title: Optional[str] = None,
        *,
        strict: bool = False,
        terminal_width: int = 80,
    ) -> str:
        """
        Render Signal as a StatusBlock.
        """
        if not signal.values:
            return f"{title or self.title or 'Signal'}\n(no data)"

        title_str = title or self.title or "Signal"

        # 1️⃣ Verdict line
        verdict = (
            f"{title_str:<15} "
            f"{self._format_percentage(signal.strength, signal.direction):>6} "
            f"{self._direction_symbol(signal.direction)}  "
            f"{signal.regime}"
        )

        # 2️⃣ Span (required for compliance)
        span_line = self._format_span(signal.labels)

        # 3️⃣ Context
        last = signal.values[-1]
        low, high = min(signal.values), max(signal.values)

        last_line = f"Last: {self._format_value(last)}"
        range_line = f"Range: {self._format_value(low)} ───── {self._format_value(high)}"

        # 4️⃣ Confirmation (visual, last)
        wave = self._sparkline(signal.values)
        wave_line = f"Wave: {wave}" if wave else None

        # ---------- assemble (ORDER MATTERS) ----------
        lines = [verdict]

        if span_line:
            lines.append(span_line)

        lines.extend([last_line, range_line])

        if wave_line:
            lines.append(wave_line)

        output = "\n".join(lines)

        # ---------- compliance enforcement ----------
        result = validate_statusblock(output, terminal_width=terminal_width)

        if strict and not result.passed:
            raise ValueError(
                "StatusBlock compliance violation:\n- "
                + "\n- ".join(result.violations)
            )

        return output
