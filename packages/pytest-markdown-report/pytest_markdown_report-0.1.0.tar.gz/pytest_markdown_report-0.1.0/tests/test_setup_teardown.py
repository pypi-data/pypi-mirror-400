"""Test setup and teardown failure handling."""

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


def test_setup_failure_appears() -> None:
    """Test that fixture setup failures appear in report."""
    test_file = Path(__file__).parent / "test_setup_fail_temp.py"
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

        # Should show 1 failure in summary
        assert "0/1 passed, 1 failed" in actual, "Summary should show setup failure"

        # Should show in failures section with error details
        assert "## Failures" in actual
        assert "test_uses_broken_fixture" in actual
        assert "RuntimeError: Setup failed" in actual

    finally:
        test_file.unlink(missing_ok=True)


def test_teardown_failure_appears() -> None:
    """Test that fixture teardown failures appear in report."""
    test_file = Path(__file__).parent / "test_teardown_fail_temp.py"
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

        # Test passed but teardown failed - should show failure
        assert "0/1 passed, 1 failed" in actual, (
            "Teardown failure should count as failed"
        )

        # Should show teardown error in failures
        assert "## Failures" in actual
        assert "test_uses_fixture" in actual
        assert "RuntimeError: Teardown failed" in actual

    finally:
        test_file.unlink(missing_ok=True)


def test_setup_and_teardown_both_fail() -> None:
    """Test handling when both setup and teardown fail."""
    test_file = Path(__file__).parent / "test_both_fail_temp.py"
    test_file.write_text("""
import pytest

@pytest.fixture
def broken_fixture():
    raise RuntimeError("Setup failed")
    yield
    raise RuntimeError("Teardown failed")

@pytest.fixture
def teardown_broken():
    yield "value"
    raise RuntimeError("Teardown failed")

def test_setup_fails(broken_fixture):
    assert True

def test_teardown_fails(teardown_broken):
    assert True
""")

    try:
        actual = run_pytest(str(test_file))

        # Both tests should show as failed
        assert "0/2 passed, 2 failed" in actual

        # Both errors should appear
        assert actual.count("## Failures") == 1
        assert "test_setup_fails" in actual
        assert "test_teardown_fails" in actual

    finally:
        test_file.unlink(missing_ok=True)
