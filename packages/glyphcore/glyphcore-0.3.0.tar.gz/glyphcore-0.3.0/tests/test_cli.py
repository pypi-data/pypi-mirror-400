import subprocess
import sys
from pathlib import Path


def run_cli(args):
    return subprocess.run(
        [sys.executable, "-m", "glyphcore.cli", *args],
        capture_output=True,
        text=True,
    )


def test_cli_lint_valid(tmp_path: Path):
    valid = tmp_path / "valid.txt"
    valid.write_text(
        """api-service      +8.3% ▲  TREND
Span: 1H · 5s
Last: 42.5ms
Range: 38.2ms ───── 42.5ms
Wave: ▁▂▃▄▅▆▇█"""
    )

    result = run_cli(["lint", str(valid)])
    assert result.returncode == 0
    assert "compliant" in result.stdout.lower()


def test_cli_lint_invalid(tmp_path: Path):
    invalid = tmp_path / "invalid.txt"
    invalid.write_text(
        """api-service      +8.3% ▲  TREND
Last: 42.5ms
Range: 38.2ms ───── 42.5ms"""
    )

    result = run_cli(["lint", str(invalid)])
    assert result.returncode == 1
    assert "violation" in result.stdout.lower()
