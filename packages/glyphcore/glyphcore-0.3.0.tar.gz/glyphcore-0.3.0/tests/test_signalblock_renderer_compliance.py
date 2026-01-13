"""
Tests that SignalBlockRenderer always produces compliant StatusBlocks.
This locks renderer → compliance coupling.
"""

import pytest

from glyphcore.core.signal import Signal
from glyphcore.renderers.signal_block import SignalBlockRenderer
from glyphcore.compliance import validate_statusblock


def make_signal(values):
    return Signal(
        direction="UP",
        strength=0.5,
        momentum="STABLE",
        regime="TREND",
        confidence=0.9,
        values=values,
        labels=[str(i) for i in range(len(values))]
    )


def test_renderer_output_is_compliant():
    renderer = SignalBlockRenderer(title="api-service")
    signal = make_signal([1, 2, 3, 4, 5])

    output = renderer.render(signal)

    result = validate_statusblock(output)
    assert result.passed, f"Renderer produced non-compliant block: {result.violations}"


def test_renderer_strict_mode_raises_on_violation(monkeypatch):
    renderer = SignalBlockRenderer(title="bad")

    signal = make_signal([1, 1, 1])

    # Force a violation by monkeypatching sparkline
    monkeypatch.setattr(
        renderer,
        "_sparkline",
        lambda *_: "█" * 100  # density violation
    )

    with pytest.raises(ValueError):
        renderer.render(signal, strict=True)


def test_renderer_non_strict_does_not_raise(monkeypatch):
    renderer = SignalBlockRenderer(title="bad")

    signal = make_signal([1, 1, 1])

    monkeypatch.setattr(
        renderer,
        "_sparkline",
        lambda *_: "█" * 100
    )

    output = renderer.render(signal, strict=False)
    assert isinstance(output, str)
