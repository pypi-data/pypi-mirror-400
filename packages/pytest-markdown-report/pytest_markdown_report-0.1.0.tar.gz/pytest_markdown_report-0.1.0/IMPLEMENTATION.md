# Implementation Log: Suppressing pytest Console Output

- **Date**: 2026-01-02
- **Goal**: Modify pytest-markdown-report plugin to replace pytest's default console
  output with markdown-formatted results instead of writing to a file.

## Context

The original plugin design wrote markdown reports to a file specified by
`--markdown-report=path`. The goal was to make the plugin output markdown to console by
default, making it immediately useful for LLM-based TDD agents without requiring file
I/O.

## Approaches Attempted

### ❌ Approach 1: Early `pytest_cmdline_preparse` with `-p no:terminal`

**What we tried**: Added `-p no:terminal` flag in `pytest_cmdline_preparse` hook to
disable pytest's terminal reporter before registration.

```python
def pytest_cmdline_preparse(config, args):
    """Disable terminal reporter before it gets registered."""
    if "no:terminal" not in args:
        args.extend(["-p", "no:terminal"])
```

**Result**: Terminal reporter still showed output. The `-p no:terminal` flag didn't
completely suppress output - pytest still showed the session header, collected items,
and progress dots.

**Why it didn't work**: The terminal reporter had already been partially initialized
before this hook ran, and `-p no:terminal` only prevents some but not all terminal
output.

---

### ❌ Approach 2: Stream Redirection in `pytest_configure`

**What we tried**: Redirected `sys.stdout` and `sys.stderr` to a capture buffer
immediately in `pytest_configure`.

```python
def pytest_configure(config):
    config._markdown_report = MarkdownReport(config)
    config.pluginmanager.register(config._markdown_report)
    config._markdown_report._redirect_output()

def _redirect_output(self):
    sys.stdout = self._capture_buffer
    sys.stderr = self._capture_buffer
```

**Result**: This suppressed test execution output but broke `pytest --help` because the
redirection happened before help text could be printed.

**Why it didn't work**: Redirecting output in `pytest_configure` is too early - it
affects all pytest operations including help/version commands that should display
normally.

---

### ❌ Approach 3: Stream Redirection in `pytest_collection_finish`

**What we tried**: Delayed stream redirection until after collection completes.

```python
def pytest_collection_finish(self, session):
    """Redirect output after collection, before test execution."""
    self._redirect_output()
```

**Result**: Still showed pytest's session header and collection output, but broke the
display of pytest's standard summary. Output was duplicated (both pytest's format and
our markdown).

**Why it didn't work**: The terminal reporter was still active and produced output after
our markdown report. Stream redirection alone doesn't prevent the terminal reporter from
executing its hooks.

---

### ❌ Approach 4: Replacing TerminalWriter with NullWriter (v1)

**What we tried**: Replace the terminal reporter's `_tw` (TerminalWriter) object with a
NullWriter that has no-op methods.

```python
def pytest_configure(config):
    terminal_reporter = config.pluginmanager.get_plugin("terminalreporter")
    if terminal_reporter:
        class NullWriter:
            def write(self, msg, **kwargs):
                pass
            def line(self, msg="", **kwargs):
                pass
            # ... etc

        terminal_reporter._tw = NullWriter()
```

**Result**: Partially worked but pytest crashed with
`TypeError: object of type 'NoneType' has no len()` when the terminal reporter tried to
calculate string widths.

**Why it didn't work**: The TerminalWriter interface has complex return value
expectations. Methods like `markup()` need to return strings, properties need specific
types, and the NullWriter didn't match the full interface contract.

---

### ❌ Approach 5: NullWriter with `__getattr__` (v2)

**What we tried**: Made NullWriter smarter by using `__getattr__` to dynamically handle
all method calls.

```python
class NullWriter:
    def __getattr__(self, name):
        if name in ('markup', 'get_write_msg'):
            return lambda *args, **kwargs: ''
        return lambda *args, **kwargs: None
```

**Result**: Still crashed with
`TypeError: unsupported operand type(s) for +=: 'function' and 'int'` because properties
returned functions instead of values.

**Why it didn't work**: Python's `__getattr__` can't distinguish between method calls
and property accesses. The terminal reporter accessed properties like `fullwidth`
expecting integers, but got lambda functions instead.

---

### ❌ Approach 6: Unregister in `pytest_configure`

**What we tried**: Unregister the terminal reporter immediately in `pytest_configure`.

```python
def pytest_configure(config):
    terminal_reporter = config.pluginmanager.get_plugin("terminalreporter")
    if terminal_reporter:
        config.pluginmanager.unregister(terminal_reporter)
```

**Result**: Removed duplicate output at session end, but pytest still showed header and
progress during collection/execution because unregistering happened after the reporter
already initialized.

**Why it didn't work**: By the time `pytest_configure` runs, the terminal reporter has
already been registered and started its initialization. Unregistering it removes future
hooks but doesn't undo what's already displayed.

---

### ✅ Approach 7: Unregister in `pytest_runtest_logstart` (FINAL SOLUTION)

**What we tried**: Unregister the terminal reporter just before the first test runs,
using a flag to ensure it only happens once.

```python
def pytest_runtest_logstart(self, nodeid, location):
    """Unregister terminal reporter before first test runs."""
    if not self._tw_replaced:
        terminal_reporter = self.config.pluginmanager.get_plugin("terminalreporter")
        if terminal_reporter:
            self.config.pluginmanager.unregister(terminal_reporter)
            self._tw_replaced = True
```

**Result**: ✅ **Success!** This approach:

- Allows pytest's session header and collection info to display normally
- Removes the terminal reporter before test execution begins
- Prevents duplicate failure output
- Keeps `pytest --help` working correctly
- Shows clean markdown output at session end

**Why it worked**: The `pytest_runtest_logstart` hook runs:

1. **After** collection completes (so session header and "collected N items" appears)
2. **Before** test execution begins (so no progress dots or inline failures)
3. **Before** session finish (so no duplicate summary)

This timing allows pytest to handle CLI operations (help, version, collection) normally
while suppressing output only during test execution and reporting.

---

## Key Learnings

### 1. Hook Timing is Critical

Different hooks run at different stages:

- `pytest_cmdline_preparse`: Too early, affects CLI parsing
- `pytest_configure`: After basic setup, but before collection
- `pytest_collection_finish`: After collection, but terminal reporter already active
- `pytest_runtest_logstart`: **Perfect spot** - after collection, before test execution

### 2. Stream Redirection Isn't Enough

Simply redirecting `sys.stdout`/`sys.stderr` doesn't prevent plugin hooks from running.
The terminal reporter will still execute its `pytest_sessionfinish` hook and try to
generate summary output, leading to crashes or duplicate output.

### 3. Unregistering vs. Disabling

- **Disabling** (via `-p no:terminal`): Prevents initial registration but doesn't work
  reliably
- **Mocking** (via NullWriter): Fragile due to complex interface requirements
- **Unregistering** (via `pluginmanager.unregister()`): Clean removal that actually
  works

### 4. Terminal Reporter Lifecycle

The terminal reporter's lifecycle:

1. **Registration**: Happens very early in pytest startup
2. **Session start**: Prints header, Python version, plugin list
3. **Collection**: Shows "collecting..." and "collected N items"
4. **Test execution**: Shows progress dots (`.`, `F`, `s`, `x`)
5. **Session finish**: Prints failures, summary, and statistics

We needed to allow steps 1-3 for normal pytest experience, suppress step 4-5, then
inject our markdown report.

### 5. Live Progress Trade-off

Initial implementation included live test progress (numbered list with ✓/✗/⊘ symbols).
This was removed because:

- LLM agents process output synchronously (don't need live updates)
- Adds context bloat without value for the primary use case
- Background execution use case is better served by pytest's existing `-v` flag

---

## Final Implementation Details

### Plugin Architecture

```
pytest_addoption()
  ↓
pytest_configure()
  ↓ (registers MarkdownReport)
  ↓
[pytest shows header + collection normally]
  ↓
pytest_runtest_logstart() → Unregister terminal reporter (once)
  ↓
pytest_runtest_logreport() → Collect test reports
  ↓
pytest_sessionfinish() → Generate and print markdown report
```

### Output Behavior

**Default mode**:

```
============================= test session starts ==============================
platform darwin -- Python 3.14.1, pytest-9.0.2, pluggy-1.6.0
collected 8 items

examples.py # Test Report

**Summary**: 5/8 passed | 1 failed | 2 skipped

## Failures
[... detailed markdown ...]
```

**Quiet mode** (`-q`):

```
**Summary**: 5/8 passed | 1 failed | 2 skipped

Re-run failed: `pytest --lf`
```

**Verbose mode** (`-v`):

```
============================= test session starts ==============================
platform darwin -- Python 3.14.1, pytest-9.0.2, pluggy-1.6.0
collected 8 items

examples.py # Test Report

**Summary**: 5/8 passed | 1 failed | 2 skipped

## Failures
[... failures ...]

## Passes
- examples.py::test_simple ✓
[... all passed tests ...]
```

### Edge Cases Handled

1. **`pytest --help`**: Works correctly (terminal reporter needed for help text)
2. **`pytest --version`**: Works correctly (terminal reporter prints version)
3. **No tests collected**: Shows appropriate markdown summary with 0/0 results
4. **File output**: Optional `--markdown-report=file.md` saves copy to file
5. **Custom rerun commands**: `--markdown-rerun-cmd` configures rerun suggestion

---

## Performance Considerations

- No overhead during test execution (just collecting reports)
- Single markdown generation at session end
- File I/O only if `--markdown-report` specified
- Minimal memory usage (storing test reports)

---

## Future Considerations

### Not Implemented (By Design)

1. **Live progress output**: Removed for simplicity, agents don't need it
2. **Heartbeat for long tests**: Keeping it simple, use `-v` if needed for background
   execution
3. **Color support**: Markdown symbols (✓✗⊘⚠) are sufficient for console clarity

### Potential Enhancements

1. **Configurable markdown format**: Allow customizing report sections
2. **JSON output mode**: For machine parsing
3. **Integration with pytest-json-report**: Combine structured data with markdown
4. **Progress bar option**: For human-driven test runs (optional flag)

---

## Sources

- [Architecture Decision Records - GitHub](https://github.com/joelparkerhenderson/architecture-decision-record)
- [ADR - Microsoft Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record)
- [Development Logs - automoto/devlog](https://github.com/automoto/devlog)
- [All About DEVELOPMENT.md - Codementor](https://www.codementor.io/@mnyongrandkru/all-about-development-md-271v354saj)
- [Test Documentation Best Practices - testRigor](https://testrigor.com/blog/test-documentation-best-practices-with-examples/)

---

## Conclusion

The successful implementation required understanding pytest's plugin lifecycle deeply.
The key insight was finding the exact hook (`pytest_runtest_logstart`) that runs after
collection but before test execution, allowing us to cleanly unregister the terminal
reporter without breaking CLI commands or collection output.

This approach is simpler and more maintainable than stream redirection or writer
mocking, and it leverages pytest's own plugin architecture to achieve clean output
suppression.
