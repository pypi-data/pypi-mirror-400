"""
Test momentum-based stroke weight.

ACCELERATING should use heavy strokes (━, ┃)
STABLE/DECELERATING should use normal strokes (─, │)
"""

from glyphcore import Engine

# Create data with accelerating trend
values = [100, 110, 125, 145, 170, 200]  # Accelerating upward
labels = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00']

engine = Engine(width=70, height=18)
signal = engine.analyze(values, labels)

print("=" * 70)
print("Momentum Test - ACCELERATING (should use heavy strokes: ━, ┃)")
print("=" * 70)
print(f"Direction: {signal.direction}")
print(f"Momentum: {signal.momentum}")
print(f"Regime: {signal.regime}")
print()
print(engine.render_tui(signal))
print()

# Create data with decelerating trend
values2 = [200, 180, 165, 155, 150, 148]  # Decelerating downward
signal2 = engine.analyze(values2, labels)

print("=" * 70)
print("Momentum Test - DECELERATING (should use normal strokes: ─, │)")
print("=" * 70)
print(f"Direction: {signal2.direction}")
print(f"Momentum: {signal2.momentum}")
print(f"Regime: {signal2.regime}")
print()
print(engine.render_tui(signal2))

