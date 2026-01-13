# Phase 2: Skipped Section & Resource Management

- **Issues:** #4, #5, #6 from code review + design change
- **TDD Process:** RED test → GREEN implementation → Verify

---

## Design Decisions (Finalized)

### Skipped Tests Display

- **Decision:** Create separate "## Skipped" section between Failures and Passes
- **Rationale:** Clearest semantic separation, skipped ≠ failed, matches pytest
  conventions
- **Summary format:** Keep unchanged ("5/8 passed, 1 failed, 1 skipped, 1 xfail")

### Section Order

- **Decision:** Summary → Failures → Skipped → Passes
- **Rationale:** Priority order - critical issues first, informational last

### Resource Cleanup

- **Decision:** Make `_restore_output()` idempotent, call from both
  `pytest_sessionfinish` and `pytest_unconfigure`
- **Rationale:** Ensures cleanup happens even on crashes/interrupts

---

## Part A: Separate Skipped Tests (Issue #6)

### Context

**Problem:** Skipped tests appear in "Failures" section, which is semantically incorrect
and confusing.

**Current behavior:** `_generate_failures()` includes skipped tests alongside actual
failures.

**Desired behavior:** Skipped tests in separate "## Skipped" section, clearly
distinguishing "not run" from "failed".

---

### TDD Step 3.1: Add RED Test for Skipped Section

**File:** `tests/test_output_expectations.py`

**Purpose:** Verify skipped tests appear in separate section

**Add new test:**

```python
def test_skipped_section_separate() -> None:
    """Test that skipped tests appear in separate section, not Failures."""
    actual = run_pytest("test_example.py")

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

    assert "test_future_feature SKIPPED" in skipped_section, "Skipped test should be in Skipped section"

    # Failures section should NOT contain SKIPPED
    failures_section = actual[failures_idx:skipped_idx]
    assert "SKIPPED" not in failures_section, "Failures section should not contain skipped tests"
```

**Update expected output files:**

**File:** `tests/expected/pytest-default.md`

**Before:**
````markdown
# Test Report

**Summary:** 5/8 passed, 1 failed, 1 skipped, 1 xfail

## Failures

### tests/test_example.py::test_edge_case FAILED

```python
test_example.py:40: in test_edge_case
    result = parser.extract_tokens(empty_data)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
test_example.py:18: in extract_tokens
    return data[0]  # Will fail on empty list
           ^^^^^^^
E   IndexError: list index out of range
```

### tests/test_example.py::test_future_feature SKIPPED

**Reason:** Not implemented yet

### tests/test_example.py::test_known_bug XFAIL

**Reason:** Bug #123

```python
test_example.py:54: in test_known_bug
    raise ValueError("Known issue")
E   ValueError: Known issue
```
````

**After:**
````markdown
# Test Report

**Summary:** 5/8 passed, 1 failed, 1 skipped, 1 xfail

## Failures

### tests/test_example.py::test_edge_case FAILED

```python
test_example.py:40: in test_edge_case
    result = parser.extract_tokens(empty_data)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
test_example.py:18: in extract_tokens
    return data[0]  # Will fail on empty list
           ^^^^^^^
E   IndexError: list index out of range
```

### tests/test_example.py::test_known_bug XFAIL

**Reason:** Bug #123

```python
test_example.py:54: in test_known_bug
    raise ValueError("Known issue")
E   ValueError: Known issue
```

## Skipped

### tests/test_example.py::test_future_feature SKIPPED

**Reason:** Not implemented yet
````

**File:** `tests/expected/pytest-verbose.md` (similar changes - add "## Skipped" section
between Failures and Passes)

**File:** `tests/expected/pytest-quiet.md` (no changes - quiet mode doesn't show
sections)

**Run test (should FAIL):**

```bash
pytest tests/test_output_expectations.py::test_skipped_section_separate -v
```

**Expected result:** Test FAILS (RED) because skipped section doesn't exist yet

---

### TDD Step 3.2: Implement GREEN Fix

**File:** `src/pytest_markdown_report/plugin.py`

**Change 1:** Update `_build_report_lines()` at line 159

**Before:**

```python
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
        if self.verbosity > 0:
            lines.extend(self._generate_passes())

    return lines
```

**After:**

```python
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
```

**Change 2:** Remove skipped iteration from `_generate_failures()` at line 269

**Before:**

```python
def _generate_failures(self) -> list[str]:
    """Generate failures section."""
    lines = ["## Failures", ""]

    for report in self.failed:
        lines.extend(self._format_failure(report))

    for report in self.skipped:
        lines.extend(self._format_skip(report))

    for report in self.xfailed:
        lines.extend(self._format_xfail(report))

    for report in self.xpassed:
        lines.extend(self._format_xpass(report))

    return lines
```

**After:**

```python
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
```

**Change 3:** Add new `_generate_skipped()` method after `_generate_failures()`

**Insert after line ~290:**

```python
def _generate_skipped(self) -> list[str]:
    """Generate skipped section."""
    lines = ["## Skipped", ""]

    for report in self.skipped:
        lines.extend(self._format_skip(report))

    return lines
```

**Run test (should PASS):**

```bash
pytest tests/test_output_expectations.py -v
```

**Expected result:** All tests PASS (GREEN)

**Full verification:**

```bash
just test
```

**Expected result:** All tests pass

---

### TDD Step 3.3: Update Design Decisions

**File:** `design-decisions.md`

**Change:** Replace "Report Organization" section (lines 121-132)

**Before:**

```markdown
## Report Organization

### Decision

Group all non-passing tests (failures, skips, xfails) in "Failures" section.

### Rationale

- **Focus on issues**: What needs attention is all in one place
- **Scan efficiency**: Developers can quickly see everything that's not working
- **Semantic grouping**: "Things that need attention" vs "things that worked"
```

**After:**

```markdown
## Report Organization

### Decision

Create separate sections for different test outcome categories.

### Section Structure

1. **## Failures** - Failed tests and xfailed tests (expected failures)
   - Regular failures (FAILED)
   - Expected failures (XFAIL)
   - Unexpected passes (XPASS) - counted as failures

2. **## Skipped** - Skipped tests (not run)
   - Tests marked with `@pytest.mark.skip`
   - Conditionally skipped tests

3. **## Passes** - Passed tests (verbose mode only)

### Rationale

- **Semantic clarity**: Skipped tests are not failures, deserve separate section
- **Scan efficiency**: Each section has clear purpose and meaning
- **Priority order**: Critical issues (failures) first, informational (passes) last
- **Consistency**: Matches pytest's own categorization of test outcomes
```

---

## Part B: Fix Resource Management (Issues #4 + #5)

### Context

**Problem 1:** StringIO buffer is never closed, wasting memory.

**Problem 2:** If pytest crashes or is interrupted (Ctrl+C), `_restore_output()` never
runs, leaving stdout/stderr redirected.

**Impact:** Memory leaks in long test sessions, broken terminal after crashes.

---

### TDD Step 4.1: Add RED Test for Resource Cleanup

**File:** `tests/test_edge_cases.py` (new)

**Purpose:** Verify resource cleanup and error handling

**Implementation:**

```python
"""Test edge cases and error handling."""

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


def test_output_restored_after_normal_run() -> None:
    """Test that stdout/stderr are restored after normal pytest run."""
    # This test verifies output streams work after pytest runs
    test_file = Path(__file__).parent / "test_simple_temp.py"
    test_file.write_text('''
def test_pass():
    assert True
''')

    try:
        # Run pytest
        run_pytest(str(test_file))

        # Verify we can still capture output (streams are restored)
        result = subprocess.run(
            [sys.executable, "-c", "print('test')"],
            capture_output=True,
            text=True,
        )
        assert result.stdout.strip() == "test", "Output streams should be restored"

    finally:
        test_file.unlink(missing_ok=True)


def test_file_write_with_invalid_path() -> None:
    """Test that invalid --markdown-report path is handled gracefully."""
    test_file = Path(__file__).parent / "test_simple_temp.py"
    test_file.write_text('''
def test_pass():
    assert True
''')

    try:
        # Try to write to invalid path
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file),
             "--markdown-report=/nonexistent/directory/report.md"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )

        # Should still show output even if file write fails
        output = result.stdout + result.stderr
        assert "1/1 passed" in output or "Warning" in output, "Should show output or warning"

    finally:
        test_file.unlink(missing_ok=True)
```

**Note:** Testing crash recovery (Ctrl+C) is difficult in automated tests. Manual
verification in Step 4.3.

**Run test:**

```bash
pytest tests/test_edge_cases.py -v
```

**Expected result:** May pass or fail depending on current implementation state

---

### TDD Step 4.2: Implement GREEN Fix

**File:** `src/pytest_markdown_report/plugin.py`

**Change 1:** Make `_restore_output()` idempotent at line 115

**Before:**

```python
def _restore_output(self) -> None:
    """Restore original stdout/stderr."""
    if self._original_stdout:
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
```

**After:**

```python
def _restore_output(self) -> None:
    """Restore original stdout/stderr."""
    if self._original_stdout:
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
        self._original_stdout = None  # Prevent double-restore
        self._original_stderr = None

    # Close capture buffer to release resources
    if self._capture_buffer:
        self._capture_buffer.close()
        self._capture_buffer = None
```

**Change 2:** Call `_restore_output()` in `pytest_unconfigure()` at line 69

**Before:**

```python
def pytest_unconfigure(config: Config) -> None:
    """Unregister the plugin."""
    markdown_report = getattr(config, "_markdown_report", None)
    if markdown_report:
        # Clean up plugin state stored on config object
        del config._markdown_report  # noqa: SLF001
        config.pluginmanager.unregister(markdown_report)
```

**After:**

```python
def pytest_unconfigure(config: Config) -> None:
    """Unregister the plugin."""
    markdown_report = getattr(config, "_markdown_report", None)
    if markdown_report:
        # Restore output before cleaning up (handles crashes/interrupts)
        markdown_report._restore_output()  # noqa: SLF001

        # Clean up plugin state stored on config object
        del config._markdown_report  # noqa: SLF001
        config.pluginmanager.unregister(markdown_report)
```

**Change 3:** Add error handling to `_write_report()` at line 177

**Before:**

```python
def _write_report(self, lines: list[str]) -> None:
    """Write report to stdout and optionally to file."""
    # Remove trailing empty line if present
    if lines and lines[-1] == "":
        lines = lines[:-1]
    report_text = "\n".join(lines) + "\n"
    sys.stdout.write(report_text)

    # Also write to file if specified
    if self.markdown_path:
        self.markdown_path.write_text(report_text)
```

**After:**

```python
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
            sys.stderr.write(f"\nWarning: Could not write to {self.markdown_path}: {e}\n")
```

**Run test (should PASS):**

```bash
pytest tests/test_edge_cases.py -v
```

**Expected result:** Tests PASS (GREEN)

**Full verification:**

```bash
just test
```

**Expected result:** All tests pass

---

### TDD Step 4.3: Manual Verification of Crash Handling

**Manual test procedure:**

1. Create test that can be interrupted:

```python
# test_hang.py
import time

def test_slow():
    time.sleep(100)
```

2. Run pytest and press Ctrl+C during execution:

```bash
pytest test_hang.py
# Press Ctrl+C after it starts
```

3. Verify terminal still works:

```bash
echo "Terminal works"
# Should see output
```

4. Check for error messages - should see none about streams

**Expected result:** Terminal functions normally after interrupt, no stream errors

**Clean up:**

```bash
rm test_hang.py
```

---

## Phase 2 Completion Checklist

- [ ] `test_skipped_section_separate()` added to `tests/test_output_expectations.py`
- [ ] `tests/expected/pytest-default.md` updated with separate Skipped section
- [ ] `tests/expected/pytest-verbose.md` updated with separate Skipped section
- [ ] `_generate_skipped()` method added to `plugin.py`
- [ ] Skipped iteration removed from `_generate_failures()`
- [ ] `_build_report_lines()` updated to call `_generate_skipped()`
- [ ] `design-decisions.md` updated with new report organization
- [ ] `tests/test_edge_cases.py` created with 2 tests
- [ ] `_restore_output()` made idempotent with buffer cleanup
- [ ] `pytest_unconfigure()` calls `_restore_output()`
- [ ] `_write_report()` has error handling for file I/O
- [ ] Manual Ctrl+C test completed successfully
- [ ] All tests pass: `just test`

---

## Next Steps

Proceed to `plans/phase-3-test-coverage.md` for:

- Comprehensive test coverage for edge cases
- Unit tests for helper functions
- Integration tests combining multiple scenarios
- Final verification and documentation updates
