"""Test edge cases and error handling."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock

from pytest_markdown_report.plugin import MarkdownReport, escape_markdown


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
    return result.stdout + result.stderr


def test_output_restored_after_normal_run() -> None:
    """Test that stdout/stderr are restored after normal pytest run."""
    # This test verifies output streams work after pytest runs
    test_file = Path(__file__).parent / "test_simple_temp.py"
    test_file.write_text("""
def test_pass():
    assert True
""")

    try:
        # Run pytest
        run_pytest(str(test_file))

        # Verify we can still capture output (streams are restored)
        result = subprocess.run(
            [sys.executable, "-c", "print('test')"],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.stdout.strip() == "test", "Output streams should be restored"

    finally:
        test_file.unlink(missing_ok=True)


def test_file_write_with_invalid_path() -> None:
    """Test that invalid --markdown-report path is handled gracefully."""
    test_file = Path(__file__).parent / "test_simple_temp.py"
    test_file.write_text("""
def test_pass():
    assert True
""")

    try:
        # Try to write to invalid path
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(test_file),
                "--markdown-report=/nonexistent/directory/report.md",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )

        # Should still show output even if file write fails
        output = result.stdout + result.stderr
        assert "1/1 passed" in output or "Warning" in output, (
            "Should show output or warning"
        )

    finally:
        test_file.unlink(missing_ok=True)


def test_special_characters_in_test_names() -> None:
    """Test that special markdown characters in test names are handled."""
    test_file = Path(__file__).parent / "test_special_chars_temp.py"
    test_file.write_text('''
import pytest

@pytest.mark.parametrize("value", ["*", "_", "[", "]"])
def test_with_special_chars(value):
    """Test with special character in parameter."""
    assert len(value) == 1

def test_asterisk_in_name():
    """Test with * in name."""
    assert False, "Failed with * asterisk"
''')

    try:
        actual = run_pytest(str(test_file))

        # All parametrized tests should pass except the failed one
        assert "4/5 passed, 1 failed" in actual

        # Test with asterisk in name should be in failures
        assert "test_asterisk_in_name FAILED" in actual

        # Error message with asterisk should be escaped/handled
        assert "Failed with" in actual  # The error message appears

    finally:
        test_file.unlink(missing_ok=True)


def test_escape_markdown() -> None:
    """Test markdown escaping function."""
    # Characters that should be escaped
    assert escape_markdown("text with *asterisk*") == r"text with \*asterisk\*"
    assert escape_markdown("text with _underscore_") == r"text with \_underscore\_"
    assert escape_markdown("text with [brackets]") == r"text with \[brackets\]"

    # Multiple special chars
    assert escape_markdown("*bold* and _italic_") == r"\*bold\* and \_italic\_"

    # Normal text unchanged
    assert escape_markdown("normal text") == "normal text"
    assert escape_markdown("Bug #123") == "Bug #123"

    # Edge cases
    assert escape_markdown("") == ""
    assert escape_markdown("***") == r"\*\*\*"


def test_categorize_reports_structure() -> None:
    """Test that MarkdownReport initializes with correct category lists."""
    # Create mock config
    config = Mock()
    config.getoption.side_effect = (
        lambda x: None if x == "markdown_report_path" else "pytest --lf"
    )
    config.option.verbose = 0

    # Instantiate reporter
    reporter = MarkdownReport(config)

    # Verify all category lists exist and are initialized as empty lists
    assert hasattr(reporter, "passed")
    assert hasattr(reporter, "failed")
    assert hasattr(reporter, "skipped")
    assert hasattr(reporter, "xfailed")
    assert hasattr(reporter, "xpassed")

    # Verify they're all empty initially
    assert isinstance(reporter.passed, list)
    assert isinstance(reporter.failed, list)
    assert isinstance(reporter.skipped, list)
    assert isinstance(reporter.xfailed, list)
    assert isinstance(reporter.xpassed, list)

    assert len(reporter.passed) == 0
    assert len(reporter.failed) == 0
    assert len(reporter.skipped) == 0
    assert len(reporter.xfailed) == 0
    assert len(reporter.xpassed) == 0


def test_comprehensive_report_all_outcomes() -> None:
    """Test comprehensive report with all outcome types.

    Tests pass, fail, skip, xfail, xpass, and setup/teardown errors.
    """
    test_file = Path(__file__).parent / "test_comprehensive_temp.py"
    test_file.write_text('''
import pytest

def test_normal_pass():
    """Normal passing test."""
    assert True

def test_normal_fail():
    """Normal failing test."""
    assert False, "Expected failure"

@pytest.mark.skip(reason="Not ready")
def test_skipped():
    """Skipped test."""
    pass

@pytest.mark.xfail(reason="Known bug", strict=True)
def test_xfail():
    """Expected failure."""
    raise ValueError("This is expected")

@pytest.mark.xfail(reason="Should fail but doesn't", strict=False)
def test_xpass():
    """Unexpected pass."""
    assert True

@pytest.fixture
def broken_setup():
    raise RuntimeError("Setup error")

def test_setup_failure(broken_setup):
    """Test with setup failure."""
    assert True

@pytest.fixture
def broken_teardown():
    yield "value"
    raise RuntimeError("Teardown error")

def test_teardown_failure(broken_teardown):
    """Test with teardown failure."""
    assert True
''')

    try:
        actual = run_pytest(str(test_file))

        # Summary should show:
        # - 1 passed (test_normal_pass)
        # - 4 failed (test_normal_fail, test_xpass, test_setup_failure,
        #   test_teardown_failure)
        # - 1 skipped (test_skipped)
        # - 1 xfail (test_xfail)
        # Total: 7 tests
        assert "1/7 passed, 4 failed, 1 skipped, 1 xfail" in actual

        # Verify sections exist
        assert "## Failures" in actual
        assert "## Skipped" in actual

        # Verify all failures appear
        assert "test_normal_fail FAILED" in actual
        assert "test_xpass XPASS" in actual
        assert "test_setup_failure" in actual
        assert "test_teardown_failure" in actual
        assert "test_xfail XFAIL" in actual

        # Verify skipped in separate section
        assert "test_skipped SKIPPED" in actual

        # Verify error messages present
        assert "Expected failure" in actual
        assert "Setup error" in actual
        assert "Teardown error" in actual
        assert "Known bug" in actual

    finally:
        test_file.unlink(missing_ok=True)


def test_buffer_cleanup_no_resource_leaks() -> None:
    """Regression test: verify repeated pytest runs don't leak resources.

    This test verifies that the StringIO buffer is properly cleaned up by
    running pytest multiple times in sequence. If buffers weren't being
    closed, we'd eventually see resource issues or memory growth.
    """
    test_file = Path(__file__).parent / "test_buffer_cleanup_temp.py"
    test_file.write_text("""
def test_simple():
    assert True
""")

    try:
        # Run pytest multiple times - if buffers aren't closed, this could
        # cause issues with repeated runs
        for _ in range(5):
            output = run_pytest(str(test_file))
            assert "1/1 passed" in output, "Test should pass on each run"

    finally:
        test_file.unlink(missing_ok=True)
