"""Core plugin implementation for pytest-markdown-report."""

import io
import re
import sys
from pathlib import Path

import pytest
from _pytest.config import Config
from _pytest.reports import TestReport


def escape_markdown(text: str) -> str:
    """Escape markdown special characters in user-provided text.

    Only escapes inline formatting characters that can have real impact:
    - [ ] : Link references
    - * : Bold/italic
    - _ : Italic (particularly important for code like variable_names)
    """
    special_chars = r"[]*_"
    return re.sub(f"([{re.escape(special_chars)}])", r"\\\1", text)


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(
    early_config: Config,  # noqa: ARG001 - Required by pytest hook spec
    parser: object,  # noqa: ARG001 - Required by pytest hook spec
    args: list[str],
) -> None:
    """Set traceback style before loading plugins."""
    # Set --tb=short as default if not specified
    if not any(arg.startswith("--tb") for arg in args):
        args.insert(0, "--tb=short")


def pytest_addoption(parser: object) -> None:
    """Add command-line options."""
    group = parser.getgroup("markdown-report")
    group.addoption(
        "--markdown-report",
        action="store",
        dest="markdown_report_path",
        metavar="path",
        default=None,
        help="Also save markdown test report to specified file",
    )
    group.addoption(
        "--markdown-rerun-cmd",
        action="store",
        dest="markdown_rerun_cmd",
        metavar="cmd",
        default="pytest --lf",
        help="Command to suggest for rerunning failed tests (empty to disable)",
    )


def pytest_configure(config: Config) -> None:
    """Register the plugin."""
    # Always register markdown reporter
    # Pytest-recommended pattern for storing plugin state on config object
    config._markdown_report = MarkdownReport(config)  # noqa: SLF001
    config.pluginmanager.register(config._markdown_report)  # noqa: SLF001

    # Redirect stdout/stderr to suppress pytest output
    config._markdown_report._redirect_output()  # noqa: SLF001


def pytest_unconfigure(config: Config) -> None:
    """Unregister the plugin."""
    markdown_report = getattr(config, "_markdown_report", None)
    if markdown_report:
        # Restore output before cleaning up (handles crashes/interrupts)
        markdown_report._restore_output()  # noqa: SLF001

        # Close buffer after all hooks complete
        markdown_report._close_buffer()  # noqa: SLF001

        # Clean up plugin state stored on config object
        del config._markdown_report  # noqa: SLF001
        config.pluginmanager.unregister(markdown_report)


class MarkdownReport:
    """Generate token-efficient markdown test reports."""

    def __init__(self, config: Config) -> None:
        """Initialize markdown report generator.

        Args:
            config: pytest Config object with markdown report options
        """
        self.config = config
        markdown_path = config.getoption("markdown_report_path")
        self.markdown_path = Path(markdown_path) if markdown_path else None
        self.rerun_cmd = config.getoption("markdown_rerun_cmd")
        self.verbosity = config.option.verbose
        self.quiet = config.option.verbose < 0

        self.reports = []
        self.passed = []
        self.failed = []
        self.skipped = []
        self.xfailed = []
        self.xpassed = []
        self.collection_errors = []

        # For output redirection
        self._original_stdout = None
        self._original_stderr = None
        self._capture_buffer = None

    def _redirect_output(self) -> None:
        """Redirect stdout/stderr to suppress pytest output."""
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        self._capture_buffer = io.StringIO()
        sys.stdout = self._capture_buffer
        sys.stderr = self._capture_buffer

    def _restore_output(self) -> None:
        """Restore original stdout/stderr."""
        if self._original_stdout:
            sys.stdout = self._original_stdout
            sys.stderr = self._original_stderr
            self._original_stdout = None  # Prevent double-restore
            self._original_stderr = None

    def _close_buffer(self) -> None:
        """Close capture buffer to release resources."""
        if self._capture_buffer:
            self._capture_buffer.close()
            self._capture_buffer = None

    def pytest_collectreport(self, report: TestReport) -> None:
        """Capture collection errors."""
        if report.failed:
            self.collection_errors.append(report)

    def pytest_runtest_logreport(self, report: TestReport) -> None:
        """Collect test reports."""
        # Capture call phase (actual test execution)
        # Also capture all non-passing outcomes from any phase (setup/teardown)
        if report.when == "call" or report.outcome in ("skipped", "failed", "error"):
            self.reports.append(report)

    def pytest_sessionfinish(
        self,
        session: object,  # noqa: ARG002 - Required by pytest hook spec
    ) -> None:
        """Generate markdown report at session end."""
        self._restore_output()
        self._categorize_reports()
        lines = self._build_report_lines()
        self._write_report(lines)

    def _categorize_reports(self) -> None:
        """Categorize test reports by outcome."""
        reports_by_nodeid = self._group_reports_by_nodeid()

        for reports_for_test in reports_by_nodeid.values():
            worst_report = self._find_worst_report(reports_for_test)
            self._categorize_single_report(worst_report)

    def _group_reports_by_nodeid(self) -> dict[str, list[TestReport]]:
        """Group reports by nodeid to handle multiple phases."""
        reports_by_nodeid: dict[str, list[TestReport]] = {}
        for report in self.reports:
            nodeid = report.nodeid
            if nodeid not in reports_by_nodeid:
                reports_by_nodeid[nodeid] = []
            reports_by_nodeid[nodeid].append(report)
        return reports_by_nodeid

    def _find_worst_report(self, reports: list[TestReport]) -> TestReport:
        """Find the report with the worst outcome from a list.

        Priority: failed/error > skipped > passed
        """
        worst_report = reports[0]
        for report in reports[1:]:
            if worst_report.outcome not in ("failed", "error") and (
                report.outcome in ("failed", "error")
                or (worst_report.outcome != "skipped" and report.outcome == "skipped")
            ):
                worst_report = report
        return worst_report

    def _categorize_single_report(self, report: TestReport) -> None:
        """Categorize a single report by outcome."""
        # Check wasxfail first, as xfail tests also have skipped=True
        if hasattr(report, "wasxfail"):
            if report.outcome == "passed":
                self.xpassed.append(report)
            else:
                self.xfailed.append(report)
        elif report.skipped:
            self.skipped.append(report)
        elif report.passed:
            self.passed.append(report)
        elif report.failed:
            self.failed.append(report)

    def _build_report_lines(self) -> list[str]:
        """Build report lines based on test results and verbosity mode."""
        lines = []

        # Collection errors take priority
        if self.collection_errors:
            lines.extend(self._generate_collection_errors())
        elif self.quiet:
            lines.extend(self._generate_quiet())
        else:
            lines.extend(self._generate_summary())
            if self.failed or self.xfailed or self.xpassed:
                lines.extend(self._generate_failures())
            if self.skipped:
                lines.extend(self._generate_skipped())
            if self.verbosity > 0:
                lines.extend(self._generate_passes())

        return lines

    def _write_report(self, lines: list[str]) -> None:
        """Write report to stdout and optionally to file."""
        # Remove trailing empty line if present
        if lines and lines[-1] == "":
            lines = lines[:-1]
        report_text = "\n".join(lines) + "\n"
        sys.stdout.write(report_text)

        # Also write to file if specified
        if self.markdown_path:
            try:
                self.markdown_path.write_text(report_text)
            except OSError as e:
                # Print error but don't crash - console output is more important
                sys.stderr.write(
                    f"\nWarning: Could not write to {self.markdown_path}: {e}\n"
                )

    def _generate_collection_errors(self) -> list[str]:
        """Generate collection errors report."""
        lines = ["# Collection Errors", ""]

        error_count = len(self.collection_errors)
        plural = "error" if error_count == 1 else "errors"
        lines.append(f"**{error_count} collection {plural}**")
        lines.append("")

        for report in self.collection_errors:
            # Get the file path from the report
            if hasattr(report, "nodeid") and report.nodeid:
                lines.append(f"### {report.nodeid}")
            elif hasattr(report, "fspath"):
                lines.append(f"### {report.fspath}")
            else:
                lines.append("### Collection Error")
            lines.append("")

            # Add error details
            if report.longreprtext:
                lines.extend(["```python", report.longreprtext.strip(), "```", ""])

        return lines

    def _generate_summary(self) -> list[str]:
        """Generate summary line."""
        total_passed = len(self.passed)
        total_failed = len(self.failed) + len(self.xpassed)
        total_skipped = len(self.skipped)
        total_xfailed = len(self.xfailed)
        total = total_passed + total_failed + total_skipped + total_xfailed

        # Build summary parts
        parts = [f"{total_passed}/{total} passed"]
        if total_failed > 0:
            parts.append(f"{total_failed} failed")
        if total_skipped > 0:
            parts.append(f"{total_skipped} skipped")
        if total_xfailed > 0:
            parts.append(f"{total_xfailed} xfail")

        return [
            "# Test Report",
            "",
            f"**Summary:** {', '.join(parts)}",
            "",
        ]

    def _generate_quiet(self) -> list[str]:
        """Generate quiet mode output."""
        total_passed = len(self.passed)
        total_failed = len(self.failed) + len(self.xpassed)
        total_skipped = len(self.skipped)
        total_xfailed = len(self.xfailed)
        total = total_passed + total_failed + total_skipped + total_xfailed

        # Build summary parts
        parts = [f"{total_passed}/{total} passed"]
        if total_failed > 0:
            parts.append(f"{total_failed} failed")
        if total_skipped > 0:
            parts.append(f"{total_skipped} skipped")
        if total_xfailed > 0:
            parts.append(f"{total_xfailed} xfail")

        lines = [f"**Summary:** {', '.join(parts)}"]

        if self.rerun_cmd and total_failed > 0:
            lines.extend(["", f"Re-run failed: `{self.rerun_cmd}`"])

        return lines

    def _generate_failures(self) -> list[str]:
        """Generate failures section."""
        lines = ["## Failures", ""]

        for report in self.failed:
            lines.extend(self._format_failure(report))

        for report in self.xfailed:
            lines.extend(self._format_xfail(report))

        for report in self.xpassed:
            lines.extend(self._format_xpass(report))

        return lines

    def _generate_skipped(self) -> list[str]:
        """Generate skipped section."""
        lines = ["## Skipped", ""]

        for report in self.skipped:
            lines.extend(self._format_skip(report))

        return lines

    def _format_failure(self, report: TestReport, symbol: str = "FAILED") -> list[str]:
        """Format a failed test."""
        # Add phase notation for non-call failures
        phase_suffix = ""
        if hasattr(report, "when") and report.when != "call":
            phase_suffix = f" in {report.when}"

        lines = [f"### {report.nodeid} {symbol}{phase_suffix}", ""]

        # Add traceback
        if report.longreprtext:
            lines.extend(["```python", report.longreprtext.strip(), "```", ""])

        return lines

    def _format_xpass(self, report: TestReport) -> list[str]:
        """Format an unexpected pass."""
        lines = [f"### {report.nodeid} XPASS"]
        lines.append("**Unexpected pass** (expected to fail)")
        lines.append("")
        return lines

    def _format_skip(self, report: TestReport) -> list[str]:
        """Format a skipped test."""
        lines = [f"### {report.nodeid} SKIPPED", ""]
        if hasattr(report, "longrepr") and report.longrepr:
            reason = (
                str(report.longrepr[2])
                if isinstance(report.longrepr, tuple)
                else str(report.longrepr)
            )
            # Remove "Skipped: " prefix if present
            reason = reason.removeprefix("Skipped: ")
            lines.append(f"**Reason:** {escape_markdown(reason)}")
            lines.append("")
        return lines

    def _format_xfail(self, report: TestReport) -> list[str]:
        """Format an expected failure."""
        lines = [f"### {report.nodeid} XFAIL", ""]

        # Extract xfail reason from wasxfail attribute
        if hasattr(report, "wasxfail") and report.wasxfail:
            # wasxfail contains the reason string
            reason = str(report.wasxfail)
            if reason:
                lines.append(f"**Reason:** {escape_markdown(reason)}")
                lines.append("")

        if report.longreprtext:
            lines.extend(["```python", report.longreprtext.strip(), "```", ""])

        return lines

    def _generate_passes(self) -> list[str]:
        """Generate passes section (verbose mode only)."""
        if not self.passed:
            return []

        lines = ["## Passes", ""]
        lines.extend(f"- {report.nodeid}" for report in self.passed)
        lines.append("")

        return lines
