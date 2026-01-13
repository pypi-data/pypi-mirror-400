# Design Decisions

This document records key design decisions made for pytest-markdown-report and their
rationale.

## Token Efficiency Over Visual Appeal

### Decision

Use text labels (FAILED, SKIPPED, XFAIL) instead of Unicode symbols (✗, ⊘, ⚠) for test
status.

### Rationale (verified with `claudeutils tokens sonnet`)

- **Token cost**: `PASSED\n` = 9 tokens, `✓\n` = 10 tokens
- **Token savings**: Text labels save 1 token per status marker
- **Readability**: Text is clearer for humans and more accessible
- **Consistency**: Aligns with pytest's own output conventions

### Decision

Use `**Label:**` format (with colon inside bold) for metadata fields.

### Rationale (verified with `claudeutils tokens sonnet`)

- **Token efficiency**: `**Label:**\n` = 10 tokens vs `**Label**:\n` = 11 tokens
- **Token savings**: Saves 1 token per label by placing colon inside bold
- **Consistency**: More correct markdown formatting
- **Readability**: Bold text with colon is visually distinct

### Decision

Summary separator uses `,` (comma-space) instead of `|` (space-pipe-space).

### Rationale (verified with `claudeutils tokens sonnet`)

- **Token efficiency**: `| \n` = 9 tokens, `, \n` = 9 tokens (same token count)
- **Readability**: Natural language separator, easier to parse
- **Consistency**: Matches common list formatting conventions

### Decision

Show xfail as separate count in summary, not grouped with skipped.

### Rationale

- **Semantic clarity**: xfail (expected failure) is different from skip (not run)
- **Actionability**: Developers care about different categories differently
- **Test quality**: Distinguishing xfail from skip provides better insight

## Traceback Format

### Decision

Use `--tb=short` as default traceback style.

### Rationale

- **Token efficiency**: Short format shows only relevant frames without fixture setup
  and separators
- **Agent-appropriate**: Provides enough context for LLMs to understand failures without
  overwhelming detail
- **Readability**: Clean output shows call chain from test to error point
- **Configurable**: Users can override with `--tb=line`, `--tb=long`, etc. if needed

## Markdown Escaping

### Decision

Escape user-provided text (reasons, error messages) for markdown special characters.

### Current Status: NEEDS RESEARCH

The current implementation escapes all ASCII punctuation characters, but this is likely
over-zealous:

- **Token cost** (verified): Escaping ADDS tokens, e.g., `Bug #123` = 10 tokens vs
  `Bug \#123` = 11 tokens
- **Context matters**: Many characters only trigger markdown formatting in specific
  contexts
  - `#` only creates headers at line start, not mid-text after `**Reason:**`
  - `*` and `_` only create emphasis when surrounding text
- **Over-escaping penalty**: Every escaped character costs an extra token

### Research Needed

- Determine minimal set of characters that actually need escaping in our contexts
- Consider: Do we need escaping at all if user text appears after `**Reason:**`?
- CommonMark spec: backslash escapes don't work in code blocks anyway
- May be better to let natural markdown formatting work (e.g., `*emphasis*` might be
  intentional)

## Output Suppression

### Decision

Completely suppress pytest's default terminal output using stdout/stderr redirection.

### Rationale

- **Clean output**: Only markdown report is shown, no pytest headers or progress
- **Token efficiency**: Eliminates redundant test name listings and progress indicators
- **Consistency**: Same output format regardless of verbosity level (-v, -q)
- **Control**: Plugin has full control over what information is displayed

## Verbosity Modes

### Decision

Support three modes: quiet (-q), default, verbose (-v)

### Rationale

- **Quiet mode**: For CI/automated testing - just summary and rerun command
- **Default mode**: For development - summary + failures
- **Verbose mode**: For review - summary + failures + passes

This matches pytest's own verbosity conventions while adapting output appropriately for
LLM consumption.

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
