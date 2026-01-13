"""
Tests semantic correctness of Analyzer.
"""

from glyphcore.engine.analyzer import Analyzer


def test_direction_up():
    s = Analyzer.analyze([1, 2, 3, 4])
    assert s.direction == "UP"


def test_direction_flat_threshold():
    s = Analyzer.analyze([100, 101, 100.5])
    assert s.direction == "FLAT"


def test_strength_normalized():
    s = Analyzer.analyze([0, 50, 100])
    assert 0.9 <= s.strength <= 1.0


def test_momentum_accelerating():
    s = Analyzer.analyze([1, 2, 4, 8])
    assert s.momentum == "ACCELERATING"


def test_regime_volatile():
    s = Analyzer.analyze([1, 10, 2, 12, 1, 11])
    assert s.regime == "VOLATILE"
