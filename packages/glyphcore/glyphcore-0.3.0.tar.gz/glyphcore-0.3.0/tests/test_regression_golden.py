"""
Golden snapshot tests.
These should change VERY rarely.
"""

from glyphcore.renderers.signal_block import SignalBlockRenderer
from glyphcore.core.signal import Signal


def test_statusblock_snapshot():
    r = SignalBlockRenderer("api")

    s = Signal(
        direction="UP",
        strength=0.5,
        momentum="STABLE",
        regime="TREND",
        confidence=1.0,
        values=[10, 20, 30],
        labels=["a", "b", "c"]
    )

    out = r.render(s)

    expected = (
        "api             +50.0% ▲  TREND\n"
        "Span: a → c\n"
        "Last: 30\n"
        "Range: 10 ───── 30\n"
        "Wave: ▁▄█"
    )

    assert out == expected

