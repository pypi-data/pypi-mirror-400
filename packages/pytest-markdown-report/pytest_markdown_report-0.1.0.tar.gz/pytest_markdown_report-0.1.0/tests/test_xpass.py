"""Test XPASS (unexpected pass) handling."""

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
    return result.stdout + result.stderr


def test_xpass_appears_in_failures() -> None:
    """Test that XPASS tests appear in failures section."""
    # Create temp test file
    test_file = Path(__file__).parent / "test_xpass_temp.py"
    test_file.write_text('''
import pytest

@pytest.mark.xfail(strict=False, reason="Expected to fail")
def test_will_unexpectedly_pass():
    """This test will pass but is marked xfail."""
    assert True
''')

    try:
        actual = run_pytest(str(test_file))

        # Verify summary shows 1 failure (xpass counts as failure)
        assert "0/1 passed, 1 failed" in actual, "Summary should show xpass as failed"

        # Verify xpass appears in failures section
        assert "## Failures" in actual, "Should have Failures section"
        assert "test_will_unexpectedly_pass XPASS" in actual, "Should show XPASS label"
        assert "**Unexpected pass**" in actual, "Should show xpass message"

        # Verify NO Unicode symbol
        assert "⚠" not in actual, "Should not contain Unicode warning symbol"

    finally:
        test_file.unlink(missing_ok=True)


def test_xpass_count_matches_display() -> None:
    """Test that xpass count in summary matches failures shown."""
    test_file = Path(__file__).parent / "test_xpass_multi_temp.py"
    test_file.write_text("""
import pytest

def test_normal_pass():
    assert True

@pytest.mark.xfail(strict=False, reason="Reason 1")
def test_xpass_1():
    assert True

@pytest.mark.xfail(strict=False, reason="Reason 2")
def test_xpass_2():
    assert True

def test_normal_fail():
    assert False
""")

    try:
        actual = run_pytest(str(test_file))

        # Summary: 1 passed, 3 failed (1 normal + 2 xpass)
        assert "1/4 passed, 3 failed" in actual

        # Should show 3 items in failures: 1 FAILED + 2 XPASS
        assert actual.count("### tests/test_xpass_multi_temp.py::") == 3
        assert actual.count("FAILED") == 1
        assert actual.count("XPASS") == 2

    finally:
        test_file.unlink(missing_ok=True)
