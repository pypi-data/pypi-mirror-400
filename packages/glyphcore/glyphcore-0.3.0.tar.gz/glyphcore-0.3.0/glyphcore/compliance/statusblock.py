"""
StatusBlock Compliance Checker

Executable law for StatusBlock invariants.
Prevents chart creep, visual dominance, and semantic dilution.

This module VALIDATES ONLY.
It never mutates output, never recomputes semantics.
"""

from dataclasses import dataclass
from typing import List


# -------------------- public API --------------------

@dataclass(frozen=True)
class StatusBlockComplianceResult:
    passed: bool
    violations: List[str]


__all__ = [
    "StatusBlockComplianceResult",
    "validate_statusblock",
]


# -------------------- glyph definitions --------------------

# Visual glyphs indicating confirmation waves
VISUAL_GLYPHS = set("▁▂▃▄▅▆▇█░━┃│")

# Separators allowed in text context
SEPARATOR_GLYPHS = set("─")

# Forbidden glyphs (diagonals & chart corners)
FORBIDDEN_GLYPHS = set("╭╮╯╰/\\")

# Direction symbols
DIRECTION_SYMBOLS = {"▲", "▼", "→"}

# Regime values
REGIME_VALUES = {"TREND", "RANGE", "VOLATILE"}


# -------------------- helpers --------------------

def _is_visual_line(line: str) -> bool:
    has_visual = any(c in VISUAL_GLYPHS for c in line)
    only_separators_or_text = all(
        c in SEPARATOR_GLYPHS or c.isalnum() or c in " :.,-%→▲▼"
        for c in line
    )
    return has_visual and not only_separators_or_text


def _is_text_line(line: str) -> bool:
    return bool(line.strip()) and not _is_visual_line(line)


def _count_visual_glyphs(line: str) -> int:
    return sum(1 for c in line if c in VISUAL_GLYPHS)


def _find_forbidden_glyphs(line: str) -> List[str]:
    return [g for g in FORBIDDEN_GLYPHS if g in line]


# -------------------- validator --------------------

def validate_statusblock(
    rendered: str,
    terminal_width: int = 80,
) -> StatusBlockComplianceResult:
    violations: List[str] = []

    lines = [
        line.rstrip()
        for line in rendered.splitlines()
        if line.strip()
    ]

    if not lines:
        return StatusBlockComplianceResult(
            passed=False,
            violations=["Empty StatusBlock"],
        )

    # ---------- section detection ----------

    title_idx = 0
    verdict_idx = -1
    span_idx = -1
    last_idx = -1
    range_idx = -1
    first_visual_idx = -1

    for i, line in enumerate(lines):
        if verdict_idx == -1:
            if any(sym in line for sym in DIRECTION_SYMBOLS) and \
               any(r in line for r in REGIME_VALUES):
                verdict_idx = i

        if span_idx == -1 and line.lower().startswith("span:"):
            span_idx = i

        if last_idx == -1 and line.lower().startswith("last:"):
            last_idx = i

        if range_idx == -1 and line.lower().startswith("range:"):
            range_idx = i

        if first_visual_idx == -1 and _is_visual_line(line):
            first_visual_idx = i

    # ---------- rule 1: required sections ----------

    if verdict_idx == -1:
        violations.append("Missing Verdict Line")

    if span_idx == -1:
        violations.append("Missing Span declaration")

    if last_idx == -1:
        violations.append("Missing Context: Last")

    if range_idx == -1:
        violations.append("Missing Context: Range")

# ---------- rule 2: ordering ----------

    if verdict_idx != -1 and verdict_idx < title_idx:
        violations.append("Ordering violation: Verdict must come after Title")

    if span_idx != -1 and verdict_idx != -1 and span_idx <= verdict_idx:
        violations.append("Ordering violation: Span must come after Verdict")

    if last_idx != -1 and span_idx != -1 and last_idx <= span_idx:
        violations.append("Ordering violation: Context must come after Span")


    # ---------- rule 3: text-first invariant ----------

    required_text_lines = 4  # Title, Verdict, Span, Context
    text_before_visual = 0

    for i, line in enumerate(lines):
        if first_visual_idx != -1 and i >= first_visual_idx:
            break
        if _is_text_line(line):
            text_before_visual += 1

    if first_visual_idx != -1 and text_before_visual < required_text_lines:
        violations.append(
            f"Text-first invariant violated: "
            f"{text_before_visual} text lines before visual "
            f"(minimum {required_text_lines})"
        )

    # ---------- rule 4: wave height ----------

    if first_visual_idx != -1:
        max_consecutive = 0
        current = 0

        for line in lines[first_visual_idx:]:
            if _is_visual_line(line):
                current += 1
                max_consecutive = max(max_consecutive, current)
            else:
                current = 0

        if max_consecutive > 2:
            violations.append(
                f"Wave height exceeds 2 rows ({max_consecutive})"
            )

    # ---------- rule 5: horizontal density ----------

    max_density = terminal_width // 3
    for i, line in enumerate(lines):
        if _is_visual_line(line):
            count = _count_visual_glyphs(line)
            if count > max_density:
                violations.append(
                    f"Horizontal density exceeded on line {i+1}: "
                    f"{count} glyphs (limit {max_density})"
                )

    # ---------- rule 6: forbidden glyphs ----------

    for i, line in enumerate(lines):
        found = _find_forbidden_glyphs(line)
        if found:
            violations.append(
                f"Forbidden glyph(s) on line {i+1}: {', '.join(found)}"
            )

    # ---------- rule 7: full block rule ----------

    block_lines = [
        i for i, line in enumerate(lines)
        if "█" in line
    ]

    if len(block_lines) > 1:
        violations.append(
            f"Full-height block (█) appears {len(block_lines)} times (max 1)"
        )

    if block_lines and first_visual_idx != -1:
        if block_lines[0] < first_visual_idx:
            violations.append(
                "Full-height block (█) used outside confirmation section"
            )

    # ---------- rule 8: single wave ----------

    if first_visual_idx != -1:
        visual_sections = 0
        in_section = False

        for line in lines[first_visual_idx:]:
            if _is_visual_line(line):
                if not in_section:
                    visual_sections += 1
                    in_section = True
            else:
                in_section = False

        if visual_sections > 1:
            violations.append(
                f"Multiple wave sections detected ({visual_sections})"
            )

    return StatusBlockComplianceResult(
        passed=len(violations) == 0,
        violations=violations,
    )
