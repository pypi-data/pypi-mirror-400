"""
Unit tests for StatusBlock compliance checker.
"""

from glyphcore.compliance import StatusBlockComplianceResult, validate_statusblock


def test_valid_block():
    """Test a valid StatusBlock passes all checks."""
    valid_block = """api-service      +8.3% ▲  TREND
Span: 1H · 5s
Last: 42.5ms
Range: 38.2ms ───── 42.5ms
Wave: ▁▂▃▄▅▆▇█"""
    
    result = validate_statusblock(valid_block)
    assert result.passed, f"Valid block failed: {result.violations}"
    print("✅ Valid block test passed")


def test_missing_span():
    """Test that missing Span is detected."""
    block_no_span = """api-service      +8.3% ▲  TREND
Last: 42.5ms
Range: 38.2ms ───── 42.5ms
Wave: ▁▂▃▄▅▆▇█"""
    
    result = validate_statusblock(block_no_span)
    assert not result.passed, "Missing span should fail"
    assert any("Span" in v for v in result.violations), "Should detect missing Span"
    print("✅ Missing span test passed")


def test_wave_height_violation():
    """Test that wave height exceeding 2 rows is detected."""
    block_high_wave = """api-service      +8.3% ▲  TREND
Span: 1H · 5s
Last: 42.5ms
Range: 38.2ms ───── 42.5ms
Wave: ▁▂▃▄▅▆▇█
      ▁▂▃▄▅▆▇█
      ▁▂▃▄▅▆▇█"""
    
    result = validate_statusblock(block_high_wave)
    assert not result.passed, "High wave should fail"
    assert any("height" in v.lower() or "rows" in v.lower() for v in result.violations), "Should detect wave height violation"
    print("✅ Wave height violation test passed")


def test_forbidden_glyph():
    """Test that forbidden glyphs are detected."""
    block_forbidden = """api-service      +8.3% ▲  TREND
Span: 1H · 5s
Last: 42.5ms
Range: 38.2ms ───── 42.5ms
Wave: ╭───────╮"""
    
    result = validate_statusblock(block_forbidden)
    assert not result.passed, "Forbidden glyph should fail"
    assert any("forbidden" in v.lower() for v in result.violations), "Should detect forbidden glyph"
    print("✅ Forbidden glyph test passed")


def test_density_limit():
    """Test that horizontal density limit is enforced."""
    # Create a wave that exceeds width // 3
    long_wave = "▁" * 30  # 30 chars, exceeds 80 // 3 = 26
    block_dense = f"""api-service      +8.3% ▲  TREND
Span: 1H · 5s
Last: 42.5ms
Range: 38.2ms ───── 42.5ms
Wave: {long_wave}"""
    
    result = validate_statusblock(block_dense, terminal_width=80)
    assert not result.passed, "Dense wave should fail"
    assert any("density" in v.lower() for v in result.violations), "Should detect density violation"
    print("✅ Density limit test passed")


def test_block_count():
    """Test that multiple █ blocks are detected."""
    block_multi = """api-service      +8.3% ▲  TREND
Span: 1H · 5s
Last: 42.5ms
Range: 38.2ms ───── 42.5ms
Wave: ████████
      ████████"""
    
    result = validate_statusblock(block_multi)
    assert not result.passed, "Multiple blocks should fail"
    assert any("block" in v.lower() and "█" in v for v in result.violations), "Should detect block count violation"
    print("✅ Block count test passed")


def test_ordering():
    """Test that section ordering is enforced."""
    block_wrong_order = """api-service      +8.3% ▲  TREND
Last: 42.5ms
Span: 1H · 5s
Range: 38.2ms ───── 42.5ms"""
    
    result = validate_statusblock(block_wrong_order)
    assert not result.passed, "Wrong order should fail"
    assert any("order" in v.lower() or "after" in v.lower() for v in result.violations), "Should detect ordering violation"
    print("✅ Ordering test passed")


def test_text_first():
    """Test that text-first invariant is enforced."""
    block_visual_first = """api-service      +8.3% ▲  TREND
▁▂▃▄▅▆▇█
Span: 1H · 5s
Last: 42.5ms
Range: 38.2ms ───── 42.5ms"""
    
    result = validate_statusblock(block_visual_first)
    assert not result.passed, "Visual before text should fail"
    assert any("text-first" in v.lower() for v in result.violations), "Should detect text-first violation"
    print("✅ Text-first test passed")


if __name__ == "__main__":
    print("=" * 60)
    print("StatusBlock Compliance Checker Tests")
    print("=" * 60)
    print()
    
    test_valid_block()
    test_missing_span()
    test_wave_height_violation()
    test_forbidden_glyph()
    test_density_limit()
    test_block_count()
    test_ordering()
    test_text_first()
    
    print()
    print("=" * 60)
    print("All tests passed!")
    print("=" * 60)

