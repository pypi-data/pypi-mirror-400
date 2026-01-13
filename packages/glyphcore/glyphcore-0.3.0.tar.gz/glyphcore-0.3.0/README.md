# glyphcore

**glyphcore** is a **semantic state summarization framework** for terminal-native applications.

It answers one question: **"Is this system in a state that requires attention?"**

glyphcore renders **semantic signals** as **glyph-based views** for fast scanning, while allowing optional escalation to **high-fidelity GUI inspection** when deeper analysis is needed.

This is not a charting library.
This is not a finance tool.
This is a **domain-agnostic decision framework**.

---

## Why glyphcore exists

Most visualization tools assume pixels, mice, and dashboards.

But many serious workflows live in terminals:
- system operators
- DevOps engineers
- infrastructure monitors
- remote SSH environments
- keyboard-first users

Existing options force a bad trade-off:
- TUIs are fast but visually limited
- GUIs are rich but slow and workflow-breaking

**glyphcore removes that trade-off.**

It treats the terminal as a **semantic grid**, rendering meaning first, not geometry — and only uses GUI visuals when the user explicitly asks for them.

## Domain-Agnostic Design

glyphcore is **not** a finance framework. It is a **semantic state summarization framework**.

Finance is just one domain where:
- signals exist
- trends matter
- humans must decide fast

The framework does not know or care what the numbers represent. It models:

- **Direction** → Is the system moving?
- **Momentum** → Is change accelerating or slowing?
- **Regime** → What kind of environment is this?
- **Confidence** → How sure are we?
- **Span** → Over what window?

This applies to:
- **Finance**: values, volume
- **Infrastructure**: CPU usage, latency
- **AI/ML**: loss curves, accuracy
- **Security**: threat scores
- **Health**: vitals trends
- **Product**: DAU, churn
- **DevOps**: error rates
- **Games**: player activity

Same semantics. Different nouns.

---

## Core ideas

### 1. Semantic first, visuals second
Data is interpreted into **signals** (direction, momentum, regime) before anything is rendered.

If the meaning is unclear, nothing is drawn.

### 2. Terminal as a semantic grid
The terminal is treated as a 2D canvas of glyphs, not a stream of text.

Rendering is done in memory using a virtual framebuffer, then flushed atomically.

### 3. Layered fidelity
- **TUI (always-on):** fast, glyph-based, SSH-safe
- **GUI (summonable):** pixel-based inspection for detail

Both views are driven by the same semantic core.

---

## What glyphcore is (and is not)

### It **is**
- a framework / engine
- terminal-first
- keyboard-native
- field-agnostic
- dependency-light

### It **is not**
- a plotting library
- a finance-only tool
- an ASCII art generator
- a dashboard framework

---

## Typical use cases

- Infrastructure health dashboards
- System monitoring and alerting
- AI/ML training run status
- Security threat surface visualization
- Product metrics tracking
- Developer tooling with optional visual inspection
- Remote or cloud-native observability
- Any application where **"Is this system in a state that requires attention?"** matters more than raw detail

---

## Minimal example

```python
from glyphcore import Engine

# Create engine
engine = Engine(width=80, height=24)

# Analyze raw data to get semantic Signal
# (values could be CPU usage, latency, numeric metrics, loss curves, etc.)
signal = engine.analyze(
    values=[42.0, 43.0, 48.0, 45.5, 46.0],
    labels=['00:00', '01:00', '02:00', '03:00', '04:00']
)

# Render TUI (always-on, zero-lag)
tui_view = engine.render_tui(signal)
print(tui_view)

# Signal properties
print(f"Direction: {signal.direction}")      # UP | DOWN | FLAT
print(f"Strength: {signal.strength:.2f}")    # 0.0 - 1.0
print(f"Momentum: {signal.momentum}")        # ACCELERATING | DECELERATING | STABLE
print(f"Regime: {signal.regime}")            # TREND | RANGE | VOLATILE
print(f"Confidence: {signal.confidence:.2f}") # 0.0 - 1.0

# When deeper inspection is needed (optional)
engine.render_gui(signal)  # Opens interactive GUI window
```

## API Overview

### Signal (The Semantic Contract)

`Signal` is the shared truth between TUI and GUI renderers. If something is not in Signal, renderers are not allowed to invent it.

```python
@dataclass(frozen=True)
class Signal:
    direction: str        # "UP" | "DOWN" | "FLAT"
    strength: float       # normalized magnitude (0.0 - 1.0)
    momentum: str         # "ACCELERATING" | "DECELERATING" | "STABLE"
    regime: str           # "TREND" | "RANGE" | "VOLATILE"
    confidence: float     # 0.0 – 1.0
    values: list[float]   # raw series
    labels: list[str]     # optional x-axis labels
```

### Engine (The Orchestrator)

The `Engine` normalizes data, computes semantics, and chooses fidelity. It never draws directly.

```python
engine = Engine(width=80, height=24, locale='en_US.UTF-8')

# Analyze: convert raw data to semantic Signal
signal = engine.analyze(values=[...], labels=[...])

# Render TUI: glyph-based terminal view (returns string)
output = engine.render_tui(signal)

# Render GUI: high-fidelity inspection (optional, opens window)
engine.render_gui(signal)
```

## Architecture

```
glyphcore/
├── __init__.py        # exports Engine, Signal
├── core/
│   └── signal.py      # Signal dataclass (semantic contract)
├── engine/
│   ├── analyzer.py    # Semantic analysis (direction, momentum, regime)
│   ├── normalize.py   # Coordinate transformation
│   └── engine.py      # Main orchestrator
└── renderers/
    ├── tui.py         # TUI glyph renderer
    └── gui.py         # GUI pixel renderer (optional)
```

## Design Principles

- **Domain-agnostic**: glyphcore never names the domain; the host application provides meaning
- **Signal is the contract**: TUI and GUI both consume the same Signal
- **Engine never draws**: All rendering delegated to renderers
- **Internal details hidden**: Glyph selection, framebuffer, interpolation are implementation details
- **Zero-dependency core**: TUI uses only Python stdlib
- **Optional GUI**: Requires plotly or matplotlib for GUI escalation
- **Compliance guaranteed**: StatusBlock renderers are validated against framework invariants
- **Compliance guaranteed**: StatusBlock renderers are validated against framework invariants
