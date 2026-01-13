"""
Engine - orchestrates semantic analysis and rendering.

Never draws. Never mutates semantics.
"""

from typing import Sequence, Optional

from glyphcore.core.signal import Signal
from glyphcore.engine.analyzer import Analyzer
from glyphcore.renderers.tui import TUIRenderer


class Engine:
    """Framework orchestrator. No rendering logic lives here."""

    def __init__(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ):
        self._tui_renderer = TUIRenderer(width=width, height=height)
        self._gui_renderer = None  # Lazy init

    # ------------------------------------------------------------

    def analyze(
        self,
        values: Sequence[float],
        labels: Optional[Sequence[str]] = None,
    ) -> Signal:
        return Analyzer.analyze(values, labels)

    # ------------------------------------------------------------

    def render_tui(self, signal: Signal) -> str:
        return self._tui_renderer.render(signal)

    # ------------------------------------------------------------

    def render_gui(self, signal: Signal) -> None:
        if self._gui_renderer is None:
            from glyphcore.renderers.gui import GUIRenderer
            self._gui_renderer = GUIRenderer()

        self._gui_renderer.render(signal)
