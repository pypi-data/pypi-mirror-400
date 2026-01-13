"""
Tests formatting stability of SignalBlockRenderer.
These are NOT compliance tests.
"""

from glyphcore.core.signal import Signal
from glyphcore.renderers.signal_block import SignalBlockRenderer


def make_signal(direction="UP", strength=0.083):
    return Signal(
        direction=direction,
        strength=strength,
        momentum="STABLE",
        regime="TREND",
        confidence=0.9,
        values=[100, 105, 108],
        labels=["t1", "t2", "t3"]
    )


def test_percentage_formatting():
    r = SignalBlockRenderer("svc")
    s = make_signal("UP", 0.083)
    out = r.render(s)
    assert "+8.3%" in out


def test_negative_percentage():
    r = SignalBlockRenderer("svc")
    s = make_signal("DOWN", 0.125)
    out = r.render(s)
    assert "-12.5%" in out


def test_direction_symbols():
    r = SignalBlockRenderer("svc")

    up = r.render(make_signal("UP"))
    down = r.render(make_signal("DOWN"))
    flat = r.render(make_signal("FLAT"))

    assert "▲" in up
    assert "▼" in down
    assert "→" in flat


def test_value_formatting_commas():
    r = SignalBlockRenderer("svc")

    s = Signal(
        direction="UP",
        strength=0.5,
        momentum="STABLE",
        regime="TREND",
        confidence=1.0,
        values=[1000, 2500],
        labels=["a", "b"]
    )

    out = r.render(s)
    assert "2,500" in out
