"""
Test SignalBlockRenderer - decision surface format.
"""

from glyphcore import Engine
from glyphcore.renderers.signal_block import SignalBlockRenderer

# Create engine
engine = Engine(width=80, height=24)

# Test data: Asia-Pacific region
values = [38190, 39200, 40500, 41200, 42234]
labels = ['00:00', '01:00', '02:00', '03:00', '04:00']

# Analyze
signal = engine.analyze(values, labels)

# Render as SignalBlock
renderer = SignalBlockRenderer(title="Asia-Pacific")
output = renderer.render(signal)

print("=" * 60)
print("SignalBlock Renderer Test")
print("=" * 60)
print()
print(output)
print()
print("=" * 60)
print("Signal Properties:")
print(f"  Direction: {signal.direction}")
print(f"  Strength: {signal.strength:.2f}")
print(f"  Momentum: {signal.momentum}")
print(f"  Regime: {signal.regime}")
print(f"  Confidence: {signal.confidence:.2f}")
print("=" * 60)

