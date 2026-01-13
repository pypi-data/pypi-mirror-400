"""
glyphcore - TUI-GUI Hybrid Charting Engine

A modular framework for semantic data visualization, optimized for traders
and data-intensive workflows. Merges low-latency TUI glyph rendering with
on-demand GUI escalation.
"""

from glyphcore.core.signal import Signal
from glyphcore.engine.engine import Engine

__all__ = ['Engine', 'Signal']
__version__ = '0.3.0'
