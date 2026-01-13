"""Test that pytest output matches expected markdown files."""

import subprocess
import sys
from pathlib import Path


def run_pytest(*args: str) -> str:
    """Run pytest with given args and return output."""
    cmd = [sys.executable, "-m", "pytest", *list(args)]
    result = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent,
    )
    # Combine stdout and stderr as pytest outputs to both
    return result.stdout + result.stderr


def test_quiet_mode() -> None:
    """Test quiet mode output matches expected."""
    actual = run_pytest("examples.py", "-q")
    expected = (Path(__file__).parent / "expected" / "pytest-quiet.md").read_text()
    assert actual == expected, (
        f"Quiet mode output mismatch:\nExpected:\n{expected}\n\nActual:\n{actual}"
    )


def test_default_mode() -> None:
    """Test default mode output matches expected."""
    actual = run_pytest("examples.py")
    expected = (Path(__file__).parent / "expected" / "pytest-default.md").read_text()
    assert actual == expected, (
        f"Default mode output mismatch:\nExpected:\n{expected}\n\nActual:\n{actual}"
    )


def test_verbose_mode() -> None:
    """Test verbose mode output matches expected."""
    actual = run_pytest("examples.py", "-v")
    expected = (Path(__file__).parent / "expected" / "pytest-verbose.md").read_text()
    assert actual == expected, (
        f"Verbose mode output mismatch:\nExpected:\n{expected}\n\nActual:\n{actual}"
    )


def test_skipped_section_separate() -> None:
    """Test that skipped tests appear in separate section, not Failures."""
    actual = run_pytest("examples.py")

    # Should have both sections
    assert "## Failures" in actual, "Should have Failures section"
    assert "## Skipped" in actual, "Should have Skipped section"

    # Skipped section should come after Failures
    failures_idx = actual.index("## Failures")
    skipped_idx = actual.index("## Skipped")
    assert skipped_idx > failures_idx, "Skipped should come after Failures"

    # Skipped test should be in Skipped section, not Failures
    skipped_section_start = skipped_idx
    # Find the next section or end
    passes_idx = actual.index("## Passes") if "## Passes" in actual else len(actual)
    skipped_section = actual[skipped_section_start:passes_idx]

    assert "test_future_feature SKIPPED" in skipped_section, (
        "Skipped test should be in Skipped section"
    )

    # Failures section should NOT contain SKIPPED
    failures_section = actual[failures_idx:skipped_idx]
    assert "SKIPPED" not in failures_section, (
        "Failures section should not contain skipped tests"
    )


def test_collection_error() -> None:
    """Test collection error output format."""
    # Create a temporary file with syntax error
    syntax_error_file = Path(__file__).parent / "test_collection_error_temp.py"
    syntax_error_file.write_text("def test_bad(\n    pass\n")

    try:
        actual = run_pytest(str(syntax_error_file))

        # Check for expected structure (paths vary by environment)
        assert actual.startswith("# Collection Errors\n"), (
            "Missing collection errors header"
        )
        assert "**1 collection error**" in actual, "Missing error count"
        assert "### tests/test_collection_error_temp.py" in actual, "Missing file name"
        assert "```python" in actual, "Missing code block"
        assert "SyntaxError: '(' was never closed" in actual, "Missing error message"
        assert actual.endswith("```\n"), "Should end with code block"
    finally:
        # Clean up
        syntax_error_file.unlink(missing_ok=True)


def test_no_trailing_blank_lines() -> None:
    """Verify all outputs end with single newline, not double."""
    for mode, args in [
        ("quiet", ["-q"]),
        ("default", []),
        ("verbose", ["-v"]),
    ]:
        actual = run_pytest("examples.py", *args)
        assert not actual.endswith("\n\n"), f"{mode} mode has trailing blank line"
        assert actual.endswith("\n"), f"{mode} mode missing final newline"
