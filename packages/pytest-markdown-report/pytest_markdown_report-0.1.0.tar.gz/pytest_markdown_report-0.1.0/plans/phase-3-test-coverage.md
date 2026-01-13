# Phase 3: Test Coverage & Verification

- **Focus:** Comprehensive test coverage + final verification
- **TDD Process:** RED test → GREEN implementation → Verify

---

## Part A: Comprehensive Test Coverage

### Context

From code review, we need tests for:

- Special characters in test names and error messages
- Unit tests for `escape_markdown()` function
- Unit tests for `_categorize_reports()` logic
- Integration test combining all outcome types

---

### TDD Step 5.1: Special Characters in Test Names

**File:** `tests/test_edge_cases.py` (append to existing file)

**Purpose:** Verify markdown special characters are handled correctly

**Add test:**

```python
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

        # Test names with special chars should appear
        # Note: pytest escapes [] in parametrize, shows as [*], [_], [[]], []]
        assert "test_with_special_chars" in actual
        assert "test_asterisk_in_name FAILED" in actual

        # Error message with asterisk should be escaped/handled
        assert "Failed with" in actual  # The error message appears

    finally:
        test_file.unlink(missing_ok=True)
```

**Run test:**

```bash
pytest tests/test_edge_cases.py::test_special_characters_in_test_names -v
```

**Expected result:** Should PASS (GREEN) - already handled by `escape_markdown()`

---

### TDD Step 5.2: Unit Tests for escape_markdown

**File:** `tests/test_edge_cases.py` (append)

**Purpose:** Direct unit tests for markdown escaping function

**Add test:**

```python
def test_escape_markdown() -> None:
    """Test markdown escaping function."""
    from pytest_markdown_report.plugin import escape_markdown

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
```

**Run test:**

```bash
pytest tests/test_edge_cases.py::test_escape_markdown -v
```

**Expected result:** Should PASS (GREEN) - function already exists

---

### TDD Step 5.3: Unit Tests for _categorize_reports

**File:** `tests/test_edge_cases.py` (append)

**Purpose:** Test categorization logic in isolation

**Add test:**

```python
def test_categorize_reports_unit() -> None:
    """Unit test for _categorize_reports method."""
    from pytest_markdown_report.plugin import MarkdownReport
    from unittest.mock import Mock

    # Create mock config
    config = Mock()
    config.getoption.side_effect = lambda x: None if x == "markdown_report_path" else "pytest --lf"
    config.option.verbose = 0

    reporter = MarkdownReport(config)

    # Create mock reports
    passed_report = Mock()
    passed_report.passed = True
    passed_report.failed = False
    passed_report.skipped = False

    failed_report = Mock()
    failed_report.passed = False
    failed_report.failed = True
    failed_report.skipped = False

    skipped_report = Mock()
    skipped_report.passed = False
    skipped_report.failed = False
    skipped_report.skipped = True

    xfailed_report = Mock()
    xfailed_report.passed = False
    xfailed_report.failed = False
    xfailed_report.skipped = True
    xfailed_report.wasxfail = "reason"
    xfailed_report.outcome = "skipped"

    xpassed_report = Mock()
    xpassed_report.passed = True
    xpassed_report.failed = False
    xpassed_report.skipped = False
    xpassed_report.wasxfail = "reason"
    xpassed_report.outcome = "passed"

    # Add reports
    reporter.reports = [
        passed_report,
        failed_report,
        skipped_report,
        xfailed_report,
        xpassed_report,
    ]

    # Categorize
    reporter._categorize_reports()

    # Verify categorization
    assert len(reporter.passed) == 1
    assert len(reporter.failed) == 1
    assert len(reporter.skipped) == 1
    assert len(reporter.xfailed) == 1
    assert len(reporter.xpassed) == 1
```

**Run test:**

```bash
pytest tests/test_edge_cases.py::test_categorize_reports_unit -v
```

**Expected result:** Should PASS (GREEN) - logic already exists

---

### TDD Step 5.4: Comprehensive Integration Test

**File:** `tests/test_edge_cases.py` (append)

**Purpose:** Test all outcome types in single test run

**Add test:**

```python
def test_comprehensive_report_all_outcomes() -> None:
    """Test report with all outcome types (pass, fail, skip, xfail, xpass, setup/teardown errors)."""
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
        # - 4 failed (test_normal_fail + test_xpass + test_setup_failure + test_teardown_failure)
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
```

**Run test:**

```bash
pytest tests/test_edge_cases.py::test_comprehensive_report_all_outcomes -v
```

**Expected result:** Should PASS (GREEN) after all previous phases complete

**Full verification:**

```bash
just test
```

**Expected result:** All tests pass

---

## Part B: Final Verification & Documentation

### Step 6.1: Run Full Test Suite

**Command:**

```bash
just test
```

**Expected output:**

- All tests pass
- No warnings or errors
- Clean output

**Success criteria:**

- `tests/test_xpass.py`: 2 tests pass
- `tests/test_setup_teardown.py`: 3 tests pass
- `tests/test_edge_cases.py`: 5 tests pass (2 from Phase 2 + 3 from Phase 3)
- `tests/test_output_expectations.py`: 4 tests pass (3 original + 1 new)
- Total: ~14 tests pass

---

### Step 6.2: Verify Token Counts

**Purpose:** Ensure changes don't increase token usage (should decrease slightly)

**Commands:**

```bash
# Generate sample reports
pytest tests/test_example.py > /tmp/sample_default.md
pytest tests/test_example.py -v > /tmp/sample_verbose.md
pytest tests/test_example.py -q > /tmp/sample_quiet.md

# Check token counts
claudeutils tokens sonnet /tmp/sample_default.md
claudeutils tokens sonnet /tmp/sample_verbose.md
claudeutils tokens sonnet /tmp/sample_quiet.md
```

**Expected result:**

- Token counts similar or lower than before
- Unicode symbol removal saves 1 token per XPASS
- Separate skipped section adds ~2 tokens for "## Skipped\n\n" but improves clarity

**Document results:** Note token counts in session notes or commit message

---

### Step 6.3: Update AGENTS.md

**File:** `AGENTS.md`

**Update "Report Generation Pipeline" section (around line 89):**

**Before:**

```markdown
4. **Formatting** (`pytest_sessionfinish`): Generates markdown based on verbosity mode:
   - **Quiet mode**: Summary + optional rerun command
   - **Default mode**: Summary + failures section
   - **Verbose mode**: Summary + failures + passes list
```

**After:**

```markdown
4. **Formatting** (`pytest_sessionfinish`): Generates markdown based on verbosity mode:
   - **Quiet mode**: Summary + optional rerun command
   - **Default mode**: Summary + failures section + skipped section
   - **Verbose mode**: Summary + failures section + skipped section + passes list
```

**Update "Report Categorization Logic" section (around line 96):**

**Before:**

```markdown
### Report Categorization Logic

Test outcomes are categorized with specific handling:

- `skipped`: Tests marked with `@pytest.mark.skip` or conditional skips (displays
  reason)
- `xfailed`: Expected failures (`@pytest.mark.xfail` that fail as expected, displays
  reason from decorator)
- `xpassed`: Unexpected passes (xfail tests that pass, counted as failures in summary)
- `failed`: Regular test failures (displays full traceback in code block)
- `passed`: Successful tests (only shown in verbose mode)
```

**After:**

```markdown
### Report Categorization Logic

Test outcomes are categorized and displayed in separate sections:

- `failed`: Regular test failures → **## Failures** section (displays full traceback)
- `xfailed`: Expected failures (`@pytest.mark.xfail` that fail as expected) → **##
  Failures** section (displays reason from decorator)
- `xpassed`: Unexpected passes (xfail tests that pass) → **## Failures** section
  (counted as failures in summary)
- `skipped`: Tests marked with `@pytest.mark.skip` or conditional skips → **## Skipped**
  section (displays reason)
- `passed`: Successful tests → **## Passes** section (only shown in verbose mode)

**Section order:** Summary → Failures → Skipped → Passes

**Setup/teardown handling:** The plugin captures failures and errors from all test
phases (setup, call, teardown). Setup errors and teardown failures are reported in the
Failures section with full traceback.
```

**Add new subsection under "Architecture":**

**Insert after "Report Categorization Logic" section:**

```markdown
### Resource Management

The plugin manages output streams carefully to ensure clean operation:

- **Output redirection**: Redirects `sys.stdout` and `sys.stderr` to suppress pytest's
  default output during test execution
- **Idempotent restoration**: `_restore_output()` can be called multiple times safely,
  setting stream references to `None` after restoration
- **Crash recovery**: `pytest_unconfigure()` calls `_restore_output()` to handle Ctrl+C
  and crashes
- **Buffer cleanup**: StringIO buffer is explicitly closed to prevent memory leaks
- **Error handling**: File I/O errors (invalid `--markdown-report` path) are caught and
  logged without crashing
```

---

### Step 6.4: Update Code Review Status

**File:** `plans/code-review.md`

**Add at top after Executive Summary:**

**Insert after line 20 (after Executive Summary):**

```markdown
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
```

---

### Step 6.5: Create Implementation Summary

**File:** `plans/implementation-summary.md` (new)

**Purpose:** Quick reference for what was changed

**Content:**

````markdown
# Implementation Summary: Code Review Fixes

- **Implementation Date:** 2026-01-04
- **Plan Files:** `plans/phase-1-xpass-and-setup.md`,
  `plans/phase-2-skipped-and-resources.md`, `plans/phase-3-test-coverage.md`

---

## Changes Made

### Source Code: `src/pytest_markdown_report/plugin.py`

**Lines changed: ~40**

1. **Line 126: `pytest_runtest_logreport()`**
   - Changed condition to capture all non-passing outcomes from any phase
   - `if report.when == "call" or report.outcome in ("skipped", "failed", "error")`

2. **Line 115: `_restore_output()`**
   - Made idempotent by setting stream references to `None`
   - Added StringIO buffer cleanup

3. **Line 69: `pytest_unconfigure()`**
   - Added call to `_restore_output()` for crash recovery

4. **Line 159: `_build_report_lines()`**
   - Added call to `_generate_skipped()` for separate skipped section

5. **Line ~269: `_generate_failures()`**
   - Removed skipped iteration
   - Added xpassed iteration

6. **Line ~290: `_generate_skipped()` (new method)**
   - Creates separate "## Skipped" section

7. **Line 289: `_format_xpass()`**
   - Removed Unicode ⚠ symbol

8. **Line 177: `_write_report()`**
   - Added try/except for file I/O errors

### Tests Created

**New test files:**

1. `tests/test_xpass.py` - 2 tests for XPASS display
2. `tests/test_setup_teardown.py` - 3 tests for fixture errors
3. `tests/test_edge_cases.py` - 5 tests for edge cases

**Modified test files:**

1. `tests/test_output_expectations.py` - Added skipped section test

**Expected output updated:**

1. `tests/expected/pytest-default.md` - Separate skipped section
2. `tests/expected/pytest-verbose.md` - Separate skipped section

**Total new test lines:** ~350

### Documentation Updated

1. `design-decisions.md`
   - Updated "Report Organization" section with new structure

2. `AGENTS.md`
   - Updated "Report Generation Pipeline"
   - Updated "Report Categorization Logic"
   - Added "Resource Management" section

3. `plans/code-review.md`
   - Added "Implementation Status" table

**Total documentation lines updated:** ~100

---

## Test Results

**Before implementation:**

- Tests: ~5 integration tests
- Coverage: Basic happy path only

**After implementation:**

- Tests: ~16 tests (5 original + 11 new)
- Coverage: All critical paths + error scenarios + edge cases

**All tests pass:** ✅

```bash
just test
```

---

## Token Efficiency Impact

**Changes that save tokens:**

- Removed Unicode ⚠ from XPASS: -1 token per xpass

**Changes that add tokens:**

- Separate skipped section header: +2 tokens ("## Skipped\n\n")

**Net impact:** Minimal (±2 tokens), improved semantic clarity

---

## Issues Resolved

- ✅ Issue #1: XPASS tests now visible in Failures section
- ✅ Issue #2: Setup/teardown failures captured and displayed
- ✅ Issue #3: Unicode symbol removed (token efficiency maintained)
- ✅ Issue #4: StringIO buffer properly closed
- ✅ Issue #5: Terminal restored on crash (pytest_unconfigure)
- ✅ Issue #6: Skipped tests in separate semantic section
- ✅ Test coverage gaps filled with 11 new tests

---

## Verification Checklist

- [x] All tests pass: `just test`
- [x] XPASS tests pass: `pytest tests/test_xpass.py -v`
- [x] Setup/teardown tests pass: `pytest tests/test_setup_teardown.py -v`
- [x] Edge case tests pass: `pytest tests/test_edge_cases.py -v`
- [x] Integration tests pass: `pytest tests/test_output_expectations.py -v`
- [x] Manual Ctrl+C recovery test passed
- [x] Token counts verified (minimal change)
- [x] Documentation updated (design-decisions.md, AGENTS.md)
- [x] Code review status updated (plans/code-review.md)
````

---

## Phase 3 Completion Checklist

- [ ] `test_special_characters_in_test_names()` added to `tests/test_edge_cases.py`
- [ ] `test_escape_markdown()` added to `tests/test_edge_cases.py`
- [ ] `test_categorize_reports_unit()` added to `tests/test_edge_cases.py`
- [ ] `test_comprehensive_report_all_outcomes()` added to `tests/test_edge_cases.py`
- [ ] All edge case tests pass: `pytest tests/test_edge_cases.py -v`
- [ ] Full test suite passes: `just test`
- [ ] Token counts verified and documented
- [ ] AGENTS.md updated with new sections
- [ ] `plans/code-review.md` updated with implementation status
- [ ] `plans/implementation-summary.md` created

---

## Final Success Criteria

**All must be complete:**

1. ✅ All code changes implemented per plans
2. ✅ All 11 new tests created and passing
3. ✅ Full test suite passes: `just test`
4. ✅ Manual Ctrl+C test completed
5. ✅ Token counts verified (no significant increase)
6. ✅ All documentation updated:
   - `design-decisions.md`
   - `AGENTS.md`
   - `plans/code-review.md`
   - `plans/implementation-summary.md`

---

## Implementation Complete! 🎉

All issues from code review have been fixed with:
- Comprehensive test coverage
- Maintained token efficiency
- Improved semantic clarity
- Robust error handling
- Complete documentation
