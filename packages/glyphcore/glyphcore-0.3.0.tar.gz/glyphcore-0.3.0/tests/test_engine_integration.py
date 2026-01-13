"""
Integration tests for Engine.
"""

from glyphcore import Engine
from glyphcore.core.signal import Signal


def test_engine_analyze_returns_signal():
    e = Engine()
    s = e.analyze([1, 2, 3])
    assert isinstance(s, Signal)


def test_engine_render_tui_returns_string():
    e = Engine(width=80, height=20)
    s = e.analyze([1, 2, 3, 4, 5])
    out = e.render_tui(s)
    assert isinstance(out, str)


def test_engine_does_not_mutate_signal():
    e = Engine()
    s = e.analyze([1, 2, 3])
    before = s.values[:]
    e.render_tui(s)
    assert s.values == before
