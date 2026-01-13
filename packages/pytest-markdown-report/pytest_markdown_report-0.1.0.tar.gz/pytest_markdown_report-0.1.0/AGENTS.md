# AGENTS.md

This file provides guidance to AI coding agents when working with code in this
repository.

## Project Overview

`pytest-markdown-report` is a pytest plugin that replaces pytest's default console
output with token-efficient markdown test reports optimized for LLM-based TDD agents.
The plugin completely suppresses pytest's standard terminal output and displays
markdown-formatted results instead, with live test progress during execution and
configurable verbosity levels.

## Commands

### Installation

```bash
pip install .
```

### Running Tests

```bash
# Verify output expectations (automated test suite) - recommended
just test

# Pass additional pytest args to just test
just test --lf          # Re-run only failed tests
just test -v            # Verbose output
just test --pdb         # Drop into debugger on failures

# Run example tests with markdown console output (default behavior)
pytest tests/examples.py

# Run tests verbosely (includes passed tests in report)
pytest tests/examples.py -v

# Run tests quietly (summary + rerun suggestion only, no live progress)
pytest tests/examples.py -q

# Run a single test
pytest tests/examples.py::test_simple

# Re-run only failed tests
pytest --lf

# Also save markdown report to a file
pytest --markdown-report=report.md

# Custom rerun command in report
pytest --markdown-rerun-cmd="just test --lf"
```

## Architecture

### Plugin Registration Flow

The plugin uses pytest's standard plugin registration mechanism and suppresses default
output:

1. `pytest_load_initial_conftests()` sets `--tb=short` as the default traceback style
2. `pytest_addoption()` registers CLI options (`--markdown-report`,
   `--markdown-rerun-cmd`)
3. `pytest_configure()` instantiates `MarkdownReport`, registers it with the plugin
   manager, and redirects stdout/stderr to suppress any remaining pytest output
4. `pytest_unconfigure()` cleans up the plugin registration

### Output Suppression Mechanism

The plugin completely suppresses pytest's console output using stream redirection:

1. **Stream Redirection**: Redirects `sys.stdout` and `sys.stderr` to a capture buffer
   in `_redirect_output()` (called from `pytest_configure()`) to suppress pytest's
   default output
2. **Output Restoration**: Restores the original streams in `_restore_output()` (called
   from `pytest_sessionfinish()`) before printing the markdown report

### Report Generation Pipeline

The `MarkdownReport` class orchestrates report generation:

1. **Output Redirection** (`_redirect_output`): Captures pytest's stdout/stderr to
   suppress default output
2. **Collection Phase** (`pytest_runtest_logreport`): Captures test reports from all
   phases (call, setup, teardown) when outcome is non-passing
3. **Categorization** (`pytest_sessionfinish`): Sorts reports into
   passed/failed/skipped/xfailed/xpassed buckets
4. **Formatting** (`pytest_sessionfinish`): Generates markdown based on verbosity mode:
   - **Quiet mode**: Summary + optional rerun command
   - **Default mode**: Summary + failures section + skipped section
   - **Verbose mode**: Summary + failures + skipped + passes list
5. **Output Restoration** (`pytest_sessionfinish`): Restores stdout/stderr and prints
   markdown report to console, optionally saves to file

### Report Categorization Logic

Test outcomes are categorized and displayed in separate sections:

- `failed`: Regular test failures → **## Failures** section (full traceback)
- `xfailed`: Expected failures (`@pytest.mark.xfail` that fail) → **## Failures**
  section
- `xpassed`: Unexpected passes (xfail tests that pass) → **## Failures** section
  (counted as failures)
- `skipped`: Tests marked skip or conditional skips → **## Skipped** section
- `passed`: Successful tests → **## Passes** section (verbose mode only)

**Section order:** Summary → Failures → Skipped → Passes

**Setup/teardown handling:** Captures failures and errors from all test phases (setup,
call, teardown). Setup errors and teardown failures appear in Failures section with full
traceback.

**Phase reporting:** Failures in setup or teardown phases display explicit phase notation
(e.g., "FAILED in setup", "FAILED in teardown") to distinguish them from call-phase test
failures. Call-phase failures show just "FAILED" since this is the implicit default. This
provides semantic clarity about whether the test assertion failed, fixture setup broke, or
cleanup failed.

### Resource Management

The plugin manages output streams to ensure clean operation:

- **Output redirection**: Redirects `sys.stdout` and `sys.stderr` during test execution
- **Idempotent restoration**: `_restore_output()` can be called multiple times safely
- **Crash recovery**: `pytest_unconfigure()` calls `_restore_output()` to handle
  interrupts (Ctrl+C)
- **Buffer cleanup**: StringIO buffer explicitly closed to prevent memory leaks
- **Error handling**: File I/O errors handled gracefully without crashing

## Key Design Decisions

**Token Efficiency**: The plugin minimizes token usage by:

- Showing only failures by default (not passed tests)
- Using text labels (FAILED, SKIPPED, XFAIL) instead of Unicode symbols (saves 1 token
  per status vs ✗, ⊘, ⚠)
- Condensing summary to single line format with comma separators
- Using `--tb=short` by default for concise tracebacks
- Placing colons inside bold markers (`**Label:**` vs `**Label**:` saves 1 token per
  label)
- Note: Current implementation escapes markdown special characters in reasons, which
  adds ~11% token overhead (see session.md for analysis)

**Verbosity Modes**: Three modes controlled by pytest's `-v`/`-q` flags allow adaptation
to different agent workflows (implementation vs. review).

**Rerun Integration**: The `--markdown-rerun-cmd` option enables custom workflow
integration (e.g., `just` recipes) while defaulting to `pytest --lf`.

## Agent Guidelines

### Persistent vs Temporary Information

**CRITICAL**: AGENTS.md is for persistent, long-lived information only.

- **Do put in AGENTS.md**: Architecture, commands, design principles, testing guidelines
- **Do NOT put in AGENTS.md**: Current plans, active tasks, session-specific context,
  implementation details

**Current plans and tasks belong in:**

- `plans/` directory - Implementation plans, code reviews, specifications
- `session.md` - Current session context, handoff notes, temporary analysis

**REMEMBER Directive**: When you see "REMEMBER:" in user messages, add the content to
this AGENTS.md file ONLY if it's persistent information (architecture, commands,
guidelines). If it's about current work or plans, put it in `session.md` or `plans/`
instead.

### Context Management

**For small projects like this one:**

1. **session.md** is the primary context file for:
   - Current work state (what's in progress)
   - Handoff notes for next agent
   - Recent decisions with rationale
   - Known blockers

2. **Size discipline**: Keep session.md under ~100 lines
   - When it grows beyond this, archive completed work to `plans/archive/` or delete
   - Preserve only: current state, next actions, recent decisions, blockers

3. **Flushing strategy**:
   - After completing a feature/fix: summarize outcome in 1-2 lines, delete details
   - After multi-day work: archive full context to `plans/archive/{date}-session.md`
   - Keep session.md focused on "what does the next agent need to know?"

4. **When to create agents/ directory**: Not needed until project has:
   - Multiple specialized agent roles
   - Sustained multi-week development
   - Context files exceeding 200+ lines regularly
   - Reference: `claudeutils/agents/` for full architecture example

**Handoff Protocol**: When asked to handoff to another agent, update `session.md` with:
- Current state (1-2 sentences)
- Immediate next action
- Any blockers or gotchas

### Testing Guidelines

**Output Verification**: Always run `pytest tests/test_output_expectations.py -v` after
making changes to verify output format matches expectations. This automated test suite
validates quiet/default/verbose modes and collection error handling.

**Token Count Verification**: Do not guess token counts. Always use
`claudeutils tokens sonnet <file>` to verify actual token usage.

## Documentation Organization

**File naming conventions:**

**Conventional files** (UPPERCASE.md):

- `AGENTS.md` - Persistent agent guidance (this file)
- `README.md` - Project overview and user documentation
- `START.md` - Getting started guide (if exists)

**Project documentation** (lowercase-dash.md):

- `design-decisions.md` - Design decisions and rationale
- `session.md` - Current session notes and handoff context

**Plans directory** (`plans/` with lowercase-dash.md):

- Implementation plans (phase-N-*.md)
- Code reviews (code-review.md, code-review-YYYY-MM-DD.md)
- Specifications and design documents
- Implementation summaries

**Directory structure:**

```
pytest-markdown-report/
├── AGENTS.md              # Persistent agent guidance
├── README.md              # User documentation
├── design-decisions.md    # Persistent design rationale
├── session.md             # Current session context
├── plans/                 # Implementation plans and reviews
│   ├── *.md               # All plan files
└── src/                   # Source code
```
