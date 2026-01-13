"""pytest-markdown-report: Token-efficient markdown test reports for LLM agents."""

from importlib.metadata import PackageNotFoundError, version

from pytest_markdown_report.plugin import (
    pytest_addoption,
    pytest_configure,
    pytest_load_initial_conftests,
    pytest_unconfigure,
)

try:
    __version__ = version("pytest-markdown-report")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = [
    "pytest_addoption",
    "pytest_configure",
    "pytest_load_initial_conftests",
    "pytest_unconfigure",
]
