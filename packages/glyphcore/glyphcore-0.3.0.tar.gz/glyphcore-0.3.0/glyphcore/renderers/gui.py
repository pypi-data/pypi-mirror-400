"""
GUI Renderer – high-fidelity inspection view.

This renderer is:
- OPTIONAL
- READ-ONLY
- SEMANTICALLY PASSIVE

It exists only to inspect the raw values
that produced a Signal.
"""

from typing import Sequence
from glyphcore.core.signal import Signal

__all__ = ["GUIRenderer"]


class GUIRenderer:
    """
    High-fidelity visual inspection renderer.

    The GUI:
    - never computes semantics
    - never labels meaning
    - never narrates conclusions
    """

    def __init__(self) -> None:
        self._backend = None

        try:
            import plotly.graph_objects as _  # noqa
            self._backend = "plotly"
        except Exception:
            try:
                import matplotlib.pyplot as _  # noqa
                self._backend = "matplotlib"
            except Exception:
                self._backend = None

    def render(self, signal: Signal) -> None:
        """
        Render raw values for inspection.

        Raises:
            RuntimeError if no GUI backend is available.
        """
        if self._backend is None:
            raise RuntimeError(
                "GUI rendering unavailable. Install plotly or matplotlib."
            )

        if not signal.values:
            return  # silent no-op

        if self._backend == "plotly":
            self._render_plotly(signal.values)
        else:
            self._render_matplotlib(signal.values)

    # ------------------------------------------------------------
    # Backends
    # ------------------------------------------------------------

    def _render_plotly(self, values: Sequence[float]) -> None:
        import plotly.graph_objects as go

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                y=list(values),
                mode="lines",
            )
        )

        fig.update_layout(
            title=None,
            xaxis_title=None,
            yaxis_title=None,
            showlegend=False,
        )

        fig.show()

    def _render_matplotlib(self, values: Sequence[float]) -> None:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.plot(values)

        ax.set_title(None)
        ax.set_xlabel(None)
        ax.set_ylabel(None)
        ax.grid(False)

        plt.tight_layout()
        plt.show()
