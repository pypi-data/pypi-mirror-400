"""
TUI Wave Renderer – legacy exploratory visualization.

This renderer is NOT a decision surface.
It renders raw wave shapes only.

StatusBlocks are the primary TUI interface.
"""

import shutil
from typing import Sequence, Optional

from glyphcore.core.signal import Signal
from glyphcore.engine.normalize import Normalizer

__all__ = ["TUIRenderer"]


class TUIRenderer:
    """
    Renders a glyph-based wave for inspection.

    This renderer:
    - has NO labels
    - has NO axes
    - has NO domain meaning
    - has NO decision semantics
    """

    MAX_POINTS_RATIO = 3  # refuse chart density

    def __init__(self, width: Optional[int] = None, height: Optional[int] = None):
        try:
            term = shutil.get_terminal_size()
            self.width = width or term.columns
            self.height = height or term.lines
        except Exception:
            self.width = width or 80
            self.height = height or 24

        self.width = max(20, self.width)
        self.height = max(8, self.height)

        self._canvas = [[" " for _ in range(self.width)] for _ in range(self.height)]

    # ------------------------------------------------------------

    def _clear(self) -> None:
        self._canvas = [[" " for _ in range(self.width)] for _ in range(self.height)]

    def _draw_wave(self, xs: Sequence[int], ys: Sequence[int]) -> None:
        for i in range(len(xs) - 1):
            x1, y1 = xs[i], ys[i]
            x2, y2 = xs[i + 1], ys[i + 1]

            mid_x = (x1 + x2) // 2

            for x in range(min(x1, mid_x), max(x1, mid_x) + 1):
                self._canvas[y1][x] = "─"

            for y in range(min(y1, y2), max(y1, y2) + 1):
                self._canvas[y][mid_x] = "│"

            for x in range(min(mid_x, x2), max(mid_x, x2) + 1):
                self._canvas[y2][x] = "─"

        self._canvas[ys[0]][xs[0]] = "●"
        self._canvas[ys[-1]][xs[-1]] = "●"

    # ------------------------------------------------------------

    def render(self, signal: Signal) -> str:
        if not signal.values:
            return ""

        self._clear()

        max_points = max(3, self.width // self.MAX_POINTS_RATIO)
        values = list(signal.values)

        if len(values) > max_points:
            step = len(values) / max_points
            values = [values[int(i * step)] for i in range(max_points)]

        plot_top = 1
        plot_bottom = self.height - 2

        ys = Normalizer.normalize_to_plot_area(values, plot_top, plot_bottom)

        xs = [
            int(i / (len(values) - 1) * (self.width - 2)) + 1
            if len(values) > 1 else self.width // 2
            for i in range(len(values))
        ]

        self._draw_wave(xs, ys)

        return "\n".join("".join(row).rstrip() for row in self._canvas)
