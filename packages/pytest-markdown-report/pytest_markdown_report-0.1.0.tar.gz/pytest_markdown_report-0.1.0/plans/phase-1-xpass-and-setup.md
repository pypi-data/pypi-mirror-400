# Phase 1: XPASS Display & Setup/Teardown Fixes

- **Issues:** #1, #2, #3 from code review
- **TDD Process:** RED test → GREEN implementation → Verify

---

## Design Decisions (Finalized)

### XPASS Symbol

- **Decision:** Use "XPASS" text label without Unicode ⚠ symbol
- **Rationale:** Maintains token efficiency design principle (saves 1 token per xpass)

### Setup/Teardown Phase Handling

- **Decision:** Capture setup failures/errors and teardown failures/errors
- **Implementation:**
  `report.when == "call" or report.outcome in ("skipped", "failed", "error")`
- **Rationale:** Simpler condition, captures all non-passing outcomes from any phase

---

## Part A: Fix XPASS Display (Issues #1 + #3)

### Context

**Problem:** XPASS tests (unexpected passes) are categorized but never displayed in
output.

**Root cause:** `_generate_failures()` iterates over `self.xpassed` but there's no
iteration to display them.

**Impact:** Users can't see which xfail tests are now passing, missing important test
quality signals.

---

### TDD Step 1.1: Add RED Test for XPASS

**File:** `tests/test_xpass.py` (new)

**Purpose:** Verify XPASS tests appear in Failures section without Unicode symbols

**Implementation:**

```python
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
    test_file.write_text('''
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
''')

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
```

**Expected output file:** `tests/expected/pytest-xpass.md`

```markdown
# Test Report

**Summary:** 0/1 passed, 1 failed

## Failures

### tests/test_xpass_temp.py::test_will_unexpectedly_pass XPASS

**Unexpected pass** (expected to fail)
```

**Run test (should FAIL):**

```bash
pytest tests/test_xpass.py -v
```

**Expected result:** Tests FAIL (RED) because XPASS tests aren't displayed yet

---

### TDD Step 1.2: Implement GREEN Fix

**File:** `src/pytest_markdown_report/plugin.py`

**Change 1:** Add xpassed iteration at line 273 in `_generate_failures()`

**Location:** After `self.xfailed` iteration, before return

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

    return lines
```

**After:**

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

**Change 2:** Remove Unicode symbol at line 289 in `_format_xpass()`

**Before:**

```python
def _format_xpass(self, report: TestReport) -> list[str]:
    """Format an unexpected pass."""
    lines = [f"### {report.nodeid} ⚠ XPASS"]
    lines.append("**Unexpected pass** (expected to fail)")
    lines.append("")
    return lines
```

**After:**

```python
def _format_xpass(self, report: TestReport) -> list[str]:
    """Format an unexpected pass."""
    lines = [f"### {report.nodeid} XPASS"]
    lines.append("**Unexpected pass** (expected to fail)")
    lines.append("")
    return lines
```

**Run test (should PASS):**

```bash
pytest tests/test_xpass.py -v
```

**Expected result:** Tests PASS (GREEN)

**Full verification:**

```bash
just test
```

**Expected result:** All tests pass

---

## Part B: Fix Setup/Teardown Failures (Issue #2)

### Context

**Problem:** Tests that fail during fixture setup or teardown are not captured in the
report.

**Root cause:** `pytest_runtest_logreport()` only captures `when == "call"` or
`when == "setup" and outcome == "skipped"`, missing setup errors and teardown failures.

**Impact:** Critical errors in fixtures go unreported, making debugging difficult.

---

### TDD Step 2.1: Add RED Test for Setup/Teardown

**File:** `tests/test_setup_teardown.py` (new)

**Purpose:** Verify setup and teardown failures are captured and displayed

**Implementation:**

```python
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
    test_file.write_text('''
import pytest

@pytest.fixture
def broken_fixture():
    raise RuntimeError("Setup failed")

def test_uses_broken_fixture(broken_fixture):
    assert True
''')

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
    test_file.write_text('''
import pytest

@pytest.fixture
def fixture_with_bad_teardown():
    yield "value"
    raise RuntimeError("Teardown failed")

def test_uses_fixture(fixture_with_bad_teardown):
    assert True
''')

    try:
        actual = run_pytest(str(test_file))

        # Test passed but teardown failed - should show failure
        assert "0/1 passed, 1 failed" in actual, "Teardown failure should count as failed"

        # Should show teardown error in failures
        assert "## Failures" in actual
        assert "test_uses_fixture" in actual
        assert "RuntimeError: Teardown failed" in actual

    finally:
        test_file.unlink(missing_ok=True)


def test_setup_and_teardown_both_fail() -> None:
    """Test handling when both setup and teardown fail."""
    test_file = Path(__file__).parent / "test_both_fail_temp.py"
    test_file.write_text('''
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
''')

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
```

**Run test (should FAIL):**

```bash
pytest tests/test_setup_teardown.py -v
```

**Expected result:** Tests FAIL (RED) because setup/teardown errors aren't captured

---

### TDD Step 2.2: Implement GREEN Fix

**File:** `src/pytest_markdown_report/plugin.py`

**Change:** Update `pytest_runtest_logreport()` at line 126

**Before:**

```python
def pytest_runtest_logreport(self, report: TestReport) -> None:
    """Collect test reports."""
    if report.when == "call" or (
        report.when == "setup" and report.outcome == "skipped"
    ):
        self.reports.append(report)
```

**After:**

```python
def pytest_runtest_logreport(self, report: TestReport) -> None:
    """Collect test reports."""
    # Capture call phase (actual test execution)
    # Also capture all non-passing outcomes from any phase (setup/teardown)
    if report.when == "call" or report.outcome in ("skipped", "failed", "error"):
        self.reports.append(report)
```

**Rationale:**

- `report.when == "call"`: Captures normal test execution
- `report.outcome in ("skipped", "failed", "error")`: Captures all problems regardless
  of phase
- Simpler than checking each phase individually
- Covers all edge cases: setup errors, teardown failures, skipped in setup, etc.

**Run test (should PASS):**

```bash
pytest tests/test_setup_teardown.py -v
```

**Expected result:** Tests PASS (GREEN)

**Full verification:**

```bash
just test
```

**Expected result:** All tests pass

---

## Phase 1 Completion Checklist

- [ ] `tests/test_xpass.py` created with 2 tests
- [ ] `tests/expected/pytest-xpass.md` created
- [ ] XPASS iteration added to `_generate_failures()`
- [ ] Unicode symbol removed from `_format_xpass()`
- [ ] `tests/test_setup_teardown.py` created with 3 tests
- [ ] `pytest_runtest_logreport()` updated to capture all non-passing outcomes
- [ ] All new tests pass: `pytest tests/test_xpass.py tests/test_setup_teardown.py -v`
- [ ] Full test suite passes: `just test`

---

## Next Steps

Proceed to `plans/phase-2-skipped-and-resources.md` for:

- Separating skipped tests into their own section
- Fixing resource management issues

---

## Appendix: Failure Phase Reporting Design Decision

**Status:** Design finalized, implementation in future phase

### Context

Phase 1 captures setup and teardown failures correctly and counts them as failures. However, the current implementation provides no semantic distinction between:

- Test assertion failure (call phase)
- Fixture setup failure (setup phase, test never ran)
- Fixture teardown failure (teardown phase, but test assertion passed)

### Design Decision: "FAILED in {phase}" Format

**Format:** `test_name FAILED in setup` or `test_name FAILED in teardown`

**Rationale:**
- ✅ Explicit and unambiguous (no markdown syntax conflicts with `[phase]` notation)
- ✅ More token-efficient than alternatives (+2 tokens vs +3 tokens for brackets)
- ✅ Provides semantic clarity for LLM agents about what broke
- ✅ Backward compatible (summary remains "X failed", details clarify why)

**Example output:**

```markdown
## Failures

### test_foo.py::test_needs_fixture FAILED in setup

```python
fixture_name setup failed: RuntimeError: Fixture broken
```

### test_bar.py::test_passes_but_cleanup_fails FAILED in teardown

**Test assertion passed. Teardown error:**

```python
fixture_name teardown failed: RuntimeError: Resource leak
```
```

### Alternative Formats Rejected

*Measured on base string "### test_foo FAILED"*

| Format | Delta Tokens | Issue |
|--------|-------------|-------|
| `FAILED [setup]` | +3 | Conflicts with markdown link syntax `[...]` |
| `SETUP FAILED` | (restructure) | Less discoverable - "FAILED" is the standard label |
| `FAILED (setup phase)` | +5 | More tokens than alternatives |
| `FAILED: setup` | +2 | Colon suggests error message intro, ambiguous with traceback |
| `FAILED in setup` | +2 | **CHOSEN** - clear, unambiguous, natural language, no syntax conflicts |

### Summary Behavior (Unchanged)

The summary count remains simple for token efficiency:

```markdown
**Summary:** 5/10 passed, 5 failed
```

Phase information only appears in the detailed Failures section, not in the summary. This keeps the summary compact while providing full context where needed.

### Three-Phase Semantic Model

When implemented, the plugin will distinguish:

1. **Test Failure** (implicit, no phase notation needed)
   - Report line: `### test_foo FAILED`
   - Meaning: Call phase (actual test) failed
   - Action: Fix test code

2. **Setup Failure** (explicit phase notation)
   - Report line: `### test_bar FAILED in setup`
   - Meaning: Fixture setup failed, test never ran
   - Action: Fix fixture or test environment

3. **Teardown Failure** (explicit phase notation)
   - Report line: `### test_baz FAILED in teardown`
   - Meaning: Test assertions passed, cleanup broke
   - Action: Fix fixture teardown, resource cleanup, or external service

### Implementation Approach (Future Phase)

1. Track failure phase in `_categorize_reports()` alongside worst outcome
2. Pass phase information to `_format_failure()` method
3. Conditionally add phase notation: `{symbol}` vs `{symbol} in {phase}`
4. Preserve all existing tests - this is purely additive

### Why This Matters

- **For LLM agents**: Different failure types need different fixes (code vs infrastructure vs cleanup)
- **For developers**: Instantly distinguishes "test is broken" from "test environment is broken"
- **Token efficient**: Only +2 tokens per failure for setup/teardown distinction, provides significant semantic clarity without markdown syntax conflicts
