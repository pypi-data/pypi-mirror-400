"""
Locks semantic meanings to prevent silent drift.
"""

from glyphcore.engine.analyzer import Analyzer


def test_known_semantic_output():
    values = [10, 20, 30, 40]
    s = Analyzer.analyze(values)

    assert s.direction == "UP"
    assert s.regime == "TREND"
    assert s.momentum in {"STABLE", "ACCELERATING"}
    assert 0.0 <= s.confidence <= 1.0


def test_span_sensitivity():
    short = Analyzer.analyze([1, 2, 3])
    long = Analyzer.analyze([1, 2, 3, 2, 1])

    assert short.direction != long.direction or short.regime != long.regime
