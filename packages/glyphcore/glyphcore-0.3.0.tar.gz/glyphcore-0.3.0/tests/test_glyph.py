"""
Test script for GlyphEngine TUI rendering with new API.

Tests with sample BTC price data as specified in the requirements.
"""

import pandas as pd
from glyphcore import Engine

# Test data: Jan 3, 2026 BTC simulation ($42k trough → $48k spike)
data = {
    'time': pd.date_range('2026-01-03', periods=5, freq='h'),
    'price': [42000, 43000, 48000, 45500, 46000]
}
df = pd.DataFrame(data)

# Create engine
engine = Engine(width=80, height=24)

# Analyze data to get Signal
# Format labels for better display
labels = [t.strftime('%H:%M') if hasattr(t, 'strftime') else str(t) for t in df['time']]
signal = engine.analyze(
    values=df['price'].tolist(),
    labels=labels
)

# Render TUI
print("=" * 80)
print("GlyphEngine TUI Render Test (New API)")
print("=" * 80)
print()

output = engine.render_tui(signal)
print(output)

print()
print("=" * 80)
print("Signal Analysis:")
print(f"  Direction: {signal.direction}")
print(f"  Strength: {signal.strength:.2f}")
print(f"  Momentum: {signal.momentum}")
print(f"  Regime: {signal.regime}")
print(f"  Confidence: {signal.confidence:.2f}")
print("=" * 80)
