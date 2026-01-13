"""Example test suite demonstrating pytest-markdown-report output."""

from typing import Never

import pytest


def validate(input_str: str) -> bool:
    """Validate input string."""
    return len(input_str) > 0


class Parser:
    """Example parser class."""

    def extract_tokens(self, data: list[str]) -> str:
        """Extract tokens from data."""
        return data[0]  # Will fail on empty list


parser = Parser()


# Parametrized test with failure
@pytest.mark.parametrize(("input_data", "expected"), [("", False), ("x", True)])
def test_invalid_input(input_data: str, expected: bool) -> None:  # noqa: FBT001
    """Test input validation."""
    assert validate(input_data) == expected


# Test with fixture and failure
@pytest.fixture
def empty_data() -> list[str]:
    """Provide empty data."""
    return []


def test_edge_case(empty_data: list[str]) -> None:
    """Test edge case with empty data."""
    result = parser.extract_tokens(empty_data)
    assert result is not None


# Skipped test
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature() -> None:
    """Test future feature."""


# xfail test
@pytest.mark.xfail(reason="Bug #123", strict=True)
def test_known_bug() -> Never:
    """Test known bug."""
    msg = "Known issue"
    raise ValueError(msg)


# Passing tests
def test_simple() -> None:
    """Simple passing test."""
    assert 1 + 1 == 2


def test_validation_pass() -> None:
    """Test validation with valid input."""
    assert validate("valid")


def test_critical_path() -> None:
    """Test critical functionality."""
    result = {"status": "success", "timestamp": 123456}
    assert result["status"] == "success"
    assert "timestamp" in result
