# Code Review: Kioku Search Filters + pm-search SKILL.md

**Date:** 2026-03-09 | **Reviewer:** code-reviewer | **Scope:** 2 files, ~50 LOC changed

## Overall Assessment

Clean, well-structured changes. Search filters use parameterized queries correctly. SKILL.md follows established conventions. No critical issues.

## Change 1: kioku.py Search Filters

**File:** `.claude/skills/kioku-lite/scripts/kioku.py` (lines 140-182, 275-280)

### Security: PASS

- All filter values passed via `?` parameterized placeholders (lines 155, 158, 161) — no SQL injection risk
- FTS5 MATCH query also parameterized (line 153)
- f-string on line 172 only interpolates `where_extra` which is built from hardcoded column names, never user input

### Correctness: PASS (one minor note)

- Filter AND-combination logic is correct (line 164)
- Empty filter case handled — `where_extra` becomes empty string
- `params` list ordering matches placeholder positions: `[query, ...filters, limit]`
- BM25 ordering preserved with filters applied

**Minor note:** Line 149 `limit = args.limit or 10` is redundant since argparse already has `default=10`. The `or 10` would also convert `--limit 0` to 10, but 0 is not a useful limit so this is benign.

### Backward Compatibility: PASS

- All three new args (`--source`, `--type`, `--status`) are optional with no defaults
- Existing callers passing only `--query` and `--limit` are unaffected
- JSON output format unchanged

### Edge Cases

- **Empty filters:** Handled correctly — no WHERE extension added
- **All three filters + query:** AND-combined correctly
- **FTS5 special chars in query:** Caught by existing `sqlite3.OperationalError` handler (line 179)

## Change 2: pm-search SKILL.md

**File:** `.claude/skills/pm-search/SKILL.md` (98 lines)

### Clarity: GOOD

- Frontmatter matches pm-sync-jira convention (`ck:` prefix, description, argument-hint)
- NLP intent parsing table (lines 36-43) is practical and covers common patterns
- Extraction rules (lines 45-49) are clear
- Error handling table at bottom covers the three likely failure modes

### Issues

**Medium — Line 43, wildcard query:** `"in-progress tasks"` maps query to `*`. FTS5 `MATCH '*'` is a syntax error in SQLite. Should use a broad common term or document that filter-only searches (no text query) are not supported.

**Low — Step 0 DB check:** The check runs `search --query "test" --limit 1` which could match real items. A lighter check would be `get --source _ --source-id _` (returns "not found" but proves DB is initialized). Not a functional issue, just slightly noisy.

**Low — Missing `PYTHON`/`DB`/`KIOKU` path note:** Paths use relative format (`.claude/...`). Works fine when CWD is project root, which is standard for agent sessions. No action needed, but worth noting for awareness.

### Positive Observations

- Step-by-step workflow mirrors pm-sync-jira structure — consistent skill authoring
- Detail view (Step 4) and synthesis (Step 5) show good UX thinking
- Result table format is practical for agent consumption

## Recommended Actions

1. **Medium** — Document that pure filter-only searches (no text terms) are not supported, or change the `*` example in line 43 to use a real query term like `"tasks"`.
2. **Low** — Remove redundant `or 10` on line 149 of kioku.py (optional cleanup).

## Metrics

- Type Coverage: N/A (Python, no type annotations beyond argparse)
- Test Coverage: No tests observed for search filters
- Linting Issues: 0

## Unresolved Questions

1. Should filter-only search (no FTS query) be supported? Would require a separate SQL path that skips FTS MATCH entirely.
2. Are there plans to add tests for kioku.py? The search filter logic is simple but testable.
