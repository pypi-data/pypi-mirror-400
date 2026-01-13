"""
Normalization and coordinate transformation.

Maps real-world values to terminal screen-space coordinates.
"""

from typing import Sequence, Tuple

__all__ = ["Normalizer"]


class Normalizer:
    """
    Handles vertical normalization only.

    This module:
    - knows NOTHING about glyphs
    - knows NOTHING about semantics
    - knows NOTHING about rendering
    """

    @staticmethod
    def get_bounds(values: Sequence[float]) -> Tuple[float, float]:
        """Return (min, max) bounds with safe defaults."""
        if not values:
            return 0.0, 1.0
        return min(values), max(values)

    @staticmethod
    def normalize_y(
        value: float,
        min_v: float,
        max_v: float,
        height: int,
    ) -> int:
        """
        Map a value into vertical screen coordinates.

        Coordinate system:
        - 0            → top
        - height - 1   → bottom

        Flat signals are centered (semantic neutrality).
        """
        if height <= 1:
            return 0

        if max_v == min_v:
            # Flatline → center vertically
            return height // 2

        norm = (value - min_v) / (max_v - min_v)
        y = height - 1 - int(norm * (height - 1))

        return max(0, min(height - 1, y))

    @staticmethod
    def normalize_to_plot_area(
        values: Sequence[float],
        plot_top: int,
        plot_bottom: int,
    ) -> list[int]:
        """
        Normalize values into a bounded vertical plot area.

        plot_top    → top row (inclusive)
        plot_bottom → bottom row (inclusive)
        """
        if not values:
            return []

        min_v, max_v = Normalizer.get_bounds(values)
        plot_height = plot_bottom - plot_top + 1

        coords: list[int] = []

        for v in values:
            local_y = Normalizer.normalize_y(
                value=v,
                min_v=min_v,
                max_v=max_v,
                height=plot_height,
            )
            coords.append(plot_top + local_y)

        return coords
