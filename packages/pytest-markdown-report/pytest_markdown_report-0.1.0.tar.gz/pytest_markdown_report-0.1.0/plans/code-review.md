# Code Review: pytest-markdown-report

- **Date:** 2026-01-03
- **Commit:** 648d8e1a3db8dd56651028ab821f77ca97afba3c
- **Review Type:** Comprehensive project review (no PR available)

## Executive Summary

Comprehensive review of the pytest-markdown-report project identified **3
high-confidence issues** requiring fixes:

- 2 critical bugs affecting functionality
- 1 design principle violation (AGENTS.md compliance)

The project demonstrates strong code quality with excellent documentation. Issues found
are isolated and have clear fix paths.

---

## Implementation Status

- **Date Implemented:** 2026-01-04
- **Status:** ✅ ALL ISSUES FIXED

| Issue    | Description                 | Status   | Verification                        |
| -------- | --------------------------- | -------- | ----------------------------------- |
| #1       | XPASS not displayed         | ✅ Fixed | `tests/test_xpass.py`               |
| #2       | Setup/teardown not captured | ✅ Fixed | `tests/test_setup_teardown.py`      |
| #3       | Unicode in XPASS            | ✅ Fixed | `tests/test_xpass.py`               |
| #4       | StringIO not closed         | ✅ Fixed | Code review                         |
| #5       | No crash recovery           | ✅ Fixed | Manual Ctrl+C test                  |
| #6       | Skipped in failures         | ✅ Fixed | `tests/test_output_expectations.py` |
| Coverage | Missing tests               | ✅ Fixed | `tests/test_edge_cases.py`          |

**Test coverage added:**

- XPASS display and counting: 2 tests
- Setup/teardown failures: 3 tests
- Edge cases (special chars, resource cleanup): 5 tests
- Integration (all outcomes): 1 test
- Total new tests: 11

**Documentation updated:**

- `design-decisions.md`: Report organization section
- `AGENTS.md`: Report generation pipeline, categorization logic, resource management

---

## Critical Issues (Require Fixes)

### Issue #1: XPASS Tests Counted But Not Displayed

- **Severity:** HIGH
- **Confidence:** 90/100
- **Type:** Bug - Logic Error
- **File:** `src/pytest_markdown_report/plugin.py`

#### Problem Description

Tests marked with `@pytest.mark.xfail` that unexpectedly pass (XPASS) are counted as
failures in the summary but never displayed in the failures section. Users see a count
mismatch where the summary shows N failures but only N-X failures appear in the details.

#### Evidence

**Line 217, 241:** XPASS tests are counted as failures in summary

```python
total_failed = len(self.failed) + len(self.xpassed)
```

**Line 170:** Condition to show failures section includes xpassed

```python
if self.failed or self.xfailed or self.xpassed:
    lines.extend(self._generate_failures())
```

**Lines 262-275:** `_generate_failures()` method missing xpassed iteration

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

    # MISSING: iteration over self.xpassed
    return lines
```

**Lines 287-292:** `_format_xpass()` method exists but is never called

```python
def _format_xpass(self, report: TestReport) -> list[str]:
    """Format an unexpected pass."""
    lines = [f"### {report.nodeid} ⚠ XPASS"]
    lines.append("**Unexpected pass** (expected to fail)")
    lines.append("")
    return lines
```

#### How to Reproduce

1. Create a test file with an xfail test that passes:

```python
import pytest

@pytest.mark.xfail(strict=False)
def test_will_unexpectedly_pass():
    assert True  # Expected to fail but passes
```

2. Run pytest with the plugin:

```bash
pytest test_file.py
```

3. **Expected output:** Summary shows "0/1 passed, 1 failed" AND details of the xpass
   test
4. **Actual output:** Summary shows "0/1 passed, 1 failed" but NO test details in
   failures section

#### Impact

- **User Experience:** Confusing count mismatch between summary and details
- **Debugging:** Impossible to identify which tests unexpectedly passed
- **Severity:** High - XPASS is a critical signal that test expectations are wrong

#### Recommended Fix

Add xpassed iteration to `_generate_failures()` method at line 273 (after xfailed):

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

    # ADD THIS:
    for report in self.xpassed:
        lines.extend(self._format_xpass(report))

    return lines
```

**Note:** This will also surface Issue #3 (Unicode symbol violation), which should be
fixed at the same time.

#### Test Coverage Needed

Add test case in `tests/test_output_expectations.py`:

1. Create test fixture with xfail test that passes
2. Verify xpass appears in failures section
3. Verify count matches between summary and details
4. Add expected output file: `tests/expected/pytest-xpass.md`

---

### Issue #2: Setup and Teardown Failures Not Captured

- **Severity:** HIGH
- **Confidence:** 88/100
- **Type:** Bug - Missing Test Phase Handling
- **File:** `src/pytest_markdown_report/plugin.py`

#### Problem Description

The plugin only captures test reports from the "call" phase (actual test execution) and
skipped tests from the setup phase. Setup failures and all teardown reports (both
failures and successes) are completely ignored, resulting in missing error information.

#### Evidence

**Lines 126-131:** `pytest_runtest_logreport()` hook with incomplete condition

```python
def pytest_runtest_logreport(self, report: TestReport) -> None:
    """Collect test reports."""
    if report.when == "call" or (
        report.when == "setup" and report.outcome == "skipped"
    ):
        self.reports.append(report)
    # MISSING: setup failures, teardown phase
```

**Missing cases:**

1. `report.when == "setup" and report.outcome == "failed"` - Setup failures (fixture
   errors)
2. `report.when == "setup" and report.outcome == "error"` - Setup errors
3. `report.when == "teardown"` - All teardown reports

#### How to Reproduce

**Test case 1: Setup failure**

```python
import pytest

@pytest.fixture
def broken_fixture():
    raise RuntimeError("Setup failed")

def test_uses_broken_fixture(broken_fixture):
    assert True
```

**Test case 2: Teardown failure**

```python
import pytest

@pytest.fixture
def fixture_with_bad_teardown():
    yield "value"
    raise RuntimeError("Teardown failed")

def test_uses_fixture(fixture_with_bad_teardown):
    assert True
```

**Expected:** Both errors shown in report **Actual:**

- Setup failure: "0/0 passed" with no error details
- Teardown failure: Test shown as passed, teardown error hidden

#### Impact

- **Critical Infrastructure Failures Invisible:** Database connections, file access,
  resource cleanup errors are hidden
- **Misleading Results:** Tests marked as passed when teardown failed
- **Common Scenario:** Fixture errors are frequent in real test suites

#### Recommended Fix

Update `pytest_runtest_logreport()` to capture all relevant phases:

```python
def pytest_runtest_logreport(self, report: TestReport) -> None:
    """Collect test reports."""
    # Capture call phase (actual test execution)
    if report.when == "call":
        self.reports.append(report)
    # Capture setup phase for skips and failures
    elif report.when == "setup":
        if report.outcome in ("skipped", "failed", "error"):
            self.reports.append(report)
    # Capture teardown phase for failures
    elif report.when == "teardown":
        if report.outcome in ("failed", "error"):
            self.reports.append(report)
```

**Alternative (simpler but may need more testing):**

```python
def pytest_runtest_logreport(self, report: TestReport) -> None:
    """Collect test reports."""
    # Capture all non-passing outcomes from any phase
    if report.when == "call" or report.outcome in ("skipped", "failed", "error"):
        self.reports.append(report)
```

#### Categorization Considerations

Setup/teardown failures may need special handling in `_categorize_reports()`. Current
categorization logic (lines 143-157) should work correctly because it checks
`report.failed`, `report.passed`, etc., which work regardless of `report.when` phase.

**Verify:** Test that setup/teardown failures are correctly categorized as failures and
displayed with appropriate tracebacks.

#### Test Coverage Needed

Add test cases in `tests/test_output_expectations.py`:

1. Test with fixture setup failure
2. Test with fixture teardown failure
3. Test with both setup and teardown failures
4. Verify error appears in failures section with traceback
5. Verify summary counts correctly

---

### Issue #3: Token Efficiency Violation - Unicode Symbol in XPASS

- **Severity:** MEDIUM
- **Confidence:** 90/100
- **Type:** AGENTS.md Design Principle Violation
- **File:** `src/pytest_markdown_report/plugin.py`

#### Problem Description

The `_format_xpass()` method uses a Unicode symbol `⚠` which directly violates the
documented token efficiency design principle. This inconsistency wastes tokens and
contradicts the project's core design goal.

#### Evidence

**AGENTS.md lines 113-114:**

```markdown
Using text labels (FAILED, SKIPPED, XFAIL) instead of Unicode symbols (saves 1 token per
status vs ✗, ⊘, ⚠)
```

**Line 289:** `_format_xpass()` uses Unicode symbol

```python
def _format_xpass(self, report: TestReport) -> list[str]:
    """Format an unexpected pass."""
    lines = [f"### {report.nodeid} ⚠ XPASS"]  # ⚠ symbol here
    lines.append("**Unexpected pass** (expected to fail)")
    lines.append("")
    return lines
```

**All other formatters use text-only:**

- Line 279: `_format_failure()` → `"FAILED"`
- Line 296: `_format_skip()` → `"SKIPPED"`
- Line 311: `_format_xfail()` → `"XFAIL"`

#### Impact

- **Token Waste:** +1 token per xpass test (Unicode character vs text)
- **Design Inconsistency:** Violates documented design principle
- **Severity:** Medium - Functional but contradicts project goals

#### Recommended Fix

Remove Unicode symbol from line 289:

```python
def _format_xpass(self, report: TestReport) -> list[str]:
    """Format an unexpected pass."""
    lines = [f"### {report.nodeid} XPASS"]  # Remove ⚠ symbol
    lines.append("**Unexpected pass** (expected to fail)")
    lines.append("")
    return lines
```

**Note:** This fix should be applied when fixing Issue #1 (since that makes this method
callable).

#### Test Coverage Needed

When adding xpass test coverage for Issue #1, verify output uses `XPASS` without Unicode
symbol.

---

## Medium Priority Issues (Should Fix)

### Issue #4: Resource Leak - StringIO Buffer Not Closed

- **Severity:** MEDIUM
- **Confidence:** 75/100
- **Type:** Resource Management
- **File:** `src/pytest_markdown_report/plugin.py`

#### Problem Description

The `_capture_buffer` (StringIO object) created in `_redirect_output()` is never
explicitly closed, creating a resource leak. While Python's garbage collector will
eventually clean it up, explicit cleanup is the correct pattern.

#### Evidence

**Line 111:** Buffer created

```python
self._capture_buffer = io.StringIO()
```

**Lines 115-120:** `_restore_output()` doesn't close buffer

```python
def _restore_output(self) -> None:
    """Restore original stdout/stderr."""
    if self._original_stdout:
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
    # MISSING: self._capture_buffer.close()
```

#### Recommended Fix

Add buffer cleanup to `_restore_output()`:

```python
def _restore_output(self) -> None:
    """Restore original stdout/stderr."""
    if self._original_stdout:
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr

    # Close capture buffer to release resources
    if self._capture_buffer:
        self._capture_buffer.close()
        self._capture_buffer = None
```

---

### Issue #5: Output Not Restored on Pytest Crash

- **Severity:** MEDIUM
- **Confidence:** 75/100
- **Type:** Error Handling
- **File:** `src/pytest_markdown_report/plugin.py`

#### Problem Description

Output streams are redirected in `pytest_configure()` but only restored in
`pytest_sessionfinish()`. If pytest crashes, is interrupted (Ctrl+C), or encounters an
unhandled exception before session finish, stdout/stderr are never restored, potentially
leaving the terminal in a broken state.

#### Evidence

**Line 66:** Redirection in configure hook

```python
config._markdown_report._redirect_output()  # noqa: SLF001
```

**Line 138:** Restoration only in session finish

```python
def pytest_sessionfinish(self, session: object) -> None:
    """Generate markdown report at session end."""
    self._restore_output()  # Only called if session completes
```

**Lines 69-75:** `pytest_unconfigure()` exists but doesn't restore output

```python
def pytest_unconfigure(config: Config) -> None:
    """Unregister the plugin."""
    markdown_report = getattr(config, "_markdown_report", None)
    if markdown_report:
        del config._markdown_report
        config.pluginmanager.unregister(markdown_report)
    # MISSING: markdown_report._restore_output()
```

#### How to Reproduce

1. Add a test that hangs or encounters unhandled exception during collection
2. Press Ctrl+C during test run
3. **Expected:** Terminal works normally
4. **Actual:** Terminal output may be broken (output goes to dead buffer)

#### Impact

- **User Experience:** Terminal becomes unusable after pytest crash
- **Recovery:** User must restart terminal session
- **Likelihood:** Medium - crashes/interrupts happen in development

#### Recommended Fix

Add output restoration to `pytest_unconfigure()`:

```python
def pytest_unconfigure(config: Config) -> None:
    """Unregister the plugin."""
    markdown_report = getattr(config, "_markdown_report", None)
    if markdown_report:
        # Restore output before cleaning up
        markdown_report._restore_output()

        # Clean up plugin state stored on config object
        del config._markdown_report  # noqa: SLF001
        config.pluginmanager.unregister(markdown_report)
```

**Note:** This means `_restore_output()` might be called twice (once in unconfigure,
once in sessionfinish), so ensure the method is idempotent:

```python
def _restore_output(self) -> None:
    """Restore original stdout/stderr."""
    if self._original_stdout:
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
        self._original_stdout = None  # ADD: Prevent double-restore
        self._original_stderr = None  # ADD: Prevent double-restore

    if self._capture_buffer:
        self._capture_buffer.close()
        self._capture_buffer = None
```

---

## Low Priority Issues (Informational)

### Issue #6: Skipped Tests Under "Failures" Heading

- **Severity:** LOW
- **Confidence:** 75/100
- **Type:** Semantic/Documentation Issue
- **File:** `src/pytest_markdown_report/plugin.py`

#### Problem Description

The `_generate_failures()` method includes skipped tests under the "## Failures"
heading, which is semantically confusing. Skipped tests are not failures.

#### Evidence

**Lines 262-275:** Method includes skipped iteration

```python
def _generate_failures(self) -> list[str]:
    """Generate failures section."""
    lines = ["## Failures", ""]

    for report in self.failed:
        lines.extend(self._format_failure(report))

    for report in self.skipped:  # Skipped under "Failures"
        lines.extend(self._format_skip(report))

    for report in self.xfailed:
        lines.extend(self._format_xfail(report))

    return lines
```

#### Counter-Evidence (Why This May Be Intentional)

**From design-decisions.md line 125:**

> "Group all non-passing tests (failures, skips, xfails) in 'Failures' section"
>
> Rationale: "Focus on issues: What needs attention is all in one place"

This appears to be an intentional design decision to group all "non-passing" tests
together.

#### Recommendation

**Option 1 (Preferred):** Update method name and docstring to reflect actual behavior

```python
def _generate_failures(self) -> list[str]:
    """Generate failures section (includes failures, skips, xfails, xpasses)."""
```

**Option 2:** Rename section header to be more accurate

```python
lines = ["## Issues", ""]  # or "## Non-Passing Tests"
```

**Option 3:** Keep as-is if this design is intentional and acceptable

---

## Test Coverage Gaps

### Missing Test Scenarios

Based on review of `tests/test_output_expectations.py`, the following scenarios lack
test coverage:

1. **XPASS tests** - No tests for unexpected passes
2. **Setup failures** - No tests for fixture errors during setup
3. **Teardown failures** - No tests for fixture errors during teardown
4. **Special characters in test names** - No tests for markdown characters in node IDs
   (e.g., `test_name[param*with*asterisks]`)
5. **File I/O errors** - No tests for `--markdown-report` with invalid paths
6. **Captured output** - No tests verifying stdout/stderr capture (if intended)
7. **Warnings** - No tests for pytest warnings
8. **Unit tests** - No direct unit tests for helper functions:
   - `escape_markdown()`
   - `_categorize_reports()`
   - Individual `_format_*()` methods

### Recommended Test Additions

**High Priority:**

1. Add `test_xpass_mode()` covering Issue #1
2. Add `test_setup_failure()` covering Issue #2
3. Add `test_teardown_failure()` covering Issue #2

**Medium Priority:**

4. Add unit tests for `escape_markdown()` with edge cases
5. Add test for special characters in test names
6. Add test for file write errors

---

## Architecture & Design Context

### Output Suppression Mechanism

The output suppression mechanism (lines 107-120) went through **7 iterations** before
finding the current working solution (documented in IMPLEMENTATION.md). This suggests
fragility:

- Complex mechanism tightly coupled to pytest internals
- Relies on specific hook timing
- May break with future pytest versions

**Recommendation:** Document pytest version compatibility and consider pinning pytest
version range.

### Token Efficiency Trade-offs

From AGENTS.md and session.md documentation:

- Current markdown escaping adds ~11% token overhead
- Design uses text labels instead of Unicode symbols (saves 1 token each)
- Colons inside bold markers saves 1 token per label

**Observation:** Issue #3 (Unicode symbol) directly contradicts this careful
optimization work.

---

## Summary & Recommendations

### Fix Priority

**Must Fix (High Impact):**

1. Issue #1: XPASS tests not displayed - **Critical bug**
2. Issue #2: Setup/teardown failures not captured - **Critical bug**
3. Issue #3: Unicode symbol in xpass - **Fix with Issue #1**

**Should Fix (Medium Impact):**

4. Issue #4: Resource leak (StringIO not closed)
5. Issue #5: Output not restored on crash

**Consider:**

6. Issue #6: Skipped tests under "Failures" heading (may be intentional)

### Testing Requirements

Before merging fixes:

1. Add test coverage for xpass scenarios
2. Add test coverage for setup/teardown failures
3. Run full test suite: `just test`
4. Verify token counts haven't increased: `claudeutils tokens sonnet <file>`
5. Manually test crash scenarios (Ctrl+C during run)

### Code Quality Assessment

**Strengths:**

- Excellent documentation (AGENTS.md, IMPLEMENTATION.md, design-decisions.md)
- Clean architecture with well-separated concerns
- Comprehensive type annotations
- Good test coverage for main scenarios

**Areas for Improvement:**

- Missing test coverage for error scenarios
- Resource management could be more robust
- Output restoration needs better error handling

**Overall:** High quality codebase with isolated, fixable issues.
