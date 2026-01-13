"""Test failure phase reporting (setup/teardown vs call)."""

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


def test_setup_failure_shows_phase() -> None:
    """Test that setup failures show 'FAILED in setup'."""
    test_file = Path(__file__).parent / "test_phase_setup_temp.py"
    test_file.write_text("""
import pytest

@pytest.fixture
def broken_fixture():
    raise RuntimeError("Setup failed")

def test_uses_broken_fixture(broken_fixture):
    assert True
""")

    try:
        actual = run_pytest(str(test_file))
        assert "test_uses_broken_fixture FAILED in setup" in actual
        assert "RuntimeError: Setup failed" in actual
    finally:
        test_file.unlink(missing_ok=True)


def test_teardown_failure_shows_phase() -> None:
    """Test that teardown failures show 'FAILED in teardown'."""
    test_file = Path(__file__).parent / "test_phase_teardown_temp.py"
    test_file.write_text("""
import pytest

@pytest.fixture
def fixture_with_bad_teardown():
    yield "value"
    raise RuntimeError("Teardown failed")

def test_uses_fixture(fixture_with_bad_teardown):
    assert True
""")

    try:
        actual = run_pytest(str(test_file))
        assert "test_uses_fixture FAILED in teardown" in actual
        assert "RuntimeError: Teardown failed" in actual
    finally:
        test_file.unlink(missing_ok=True)


def test_call_failure_no_phase() -> None:
    """Test that call phase failures show just 'FAILED' (no phase notation)."""
    test_file = Path(__file__).parent / "test_phase_call_temp.py"
    test_file.write_text("""
def test_normal_failure():
    assert False, "This is a normal failure"
""")

    try:
        actual = run_pytest(str(test_file))
        # Should show FAILED followed by newline or end (no phase)
        assert (
            "test_normal_failure FAILED\n" in actual
            or "test_normal_failure FAILED\r\n" in actual
        )
        assert "FAILED in call" not in actual
    finally:
        test_file.unlink(missing_ok=True)


def test_mixed_phases_in_report() -> None:
    """Test report with failures in different phases."""
    test_file = Path(__file__).parent / "test_phase_mixed_temp.py"
    test_file.write_text("""
import pytest

@pytest.fixture
def broken_setup():
    raise RuntimeError("Setup error")

@pytest.fixture
def broken_teardown():
    yield "value"
    raise RuntimeError("Teardown error")

def test_call_fails():
    assert False, "Call phase failure"

def test_setup_fails(broken_setup):
    assert True

def test_teardown_fails(broken_teardown):
    assert True
""")

    try:
        actual = run_pytest(str(test_file))
        # Verify all three failures with correct phase notation
        assert (
            "test_call_fails FAILED\n" in actual
            or "test_call_fails FAILED\r\n" in actual
        )
        assert "test_setup_fails FAILED in setup" in actual
        assert "test_teardown_fails FAILED in teardown" in actual
        assert "0/3 passed, 3 failed" in actual
    finally:
        test_file.unlink(missing_ok=True)
