# Code Review: kioku-lite + pm-spec-to-tickets Skills

## Scope
- Files: 6 (1 Python, 5 Markdown)
- LOC: ~400 total
- Focus: New skill files — security, correctness, edge cases, documentation clarity

## Overall Assessment

Solid implementation. Clean code, proper use of parameterized queries (no SQL injection risk), well-structured SKILL.md files. Two actionable bugs found, both in search error handling.

---

## Critical Issues

None.

## High Priority

### 1. FTS5 MATCH crashes on empty/malformed queries (kioku.py:137-145)

`cmd_search` passes user query directly to FTS5 MATCH. Empty strings and certain special characters (`*` alone, bare operators) cause `sqlite3.OperationalError` that is unhandled.

**Reproduction:**
```bash
python3 kioku.py --db test.db search --query ""
# → OperationalError: fts5: syntax error near ""

python3 kioku.py --db test.db search --query "*"
# → OperationalError: unknown special query
```

**Fix — wrap search in try/except:**
```python
def cmd_search(args):
    conn = get_db(args.db)
    limit = args.limit or 10
    query = args.query.strip()
    if not query:
        print(json.dumps({"ok": True, "count": 0, "results": []}))
        conn.close()
        return
    try:
        cursor = conn.execute(
            """SELECT i.*, bm25(items_fts) AS rank
               FROM items_fts fts JOIN items i ON i.id = fts.rowid
               WHERE items_fts MATCH ? ORDER BY rank LIMIT ?""",
            (query, limit),
        )
        results = [dict(row) for row in cursor.fetchall()]
        print(json.dumps({"ok": True, "count": len(results), "results": results}))
    except sqlite3.OperationalError as e:
        print(json.dumps({"ok": False, "error": f"Invalid search query: {e}"}))
    conn.close()
```

### 2. Commands crash on uninitialized DB (kioku.py:all cmd_* except cmd_init)

If any command runs before `init`, it hits `sqlite3.OperationalError: no such table`. No graceful error message.

**Fix — add table existence check in `get_db` or wrap each command:**
```python
def ensure_initialized(conn):
    try:
        conn.execute("SELECT 1 FROM items LIMIT 1")
        return True
    except sqlite3.OperationalError:
        print(json.dumps({"ok": False, "error": "DB not initialized. Run 'init' first."}))
        return False
```

## Medium Priority

### 3. Connection not closed on exceptions (kioku.py, multiple locations)

If an exception occurs before `conn.close()`, connections leak. Consider using context manager pattern:

```python
def get_db(db_path: str) -> sqlite3.Connection:
    # ... same setup ...
    return conn

# Usage in commands:
conn = get_db(args.db)
try:
    # ... operations ...
finally:
    conn.close()
```

Or simpler: make `get_db` return a context manager.

### 4. `cmd_store` uses manual upsert instead of SQLite UPSERT (kioku.py:101-124)

The SELECT-then-INSERT/UPDATE pattern has a race condition (two concurrent processes could both see "not existing" and try to insert). SQLite's `INSERT ... ON CONFLICT ... DO UPDATE` is atomic.

**Fix:**
```python
conn.execute(
    """INSERT INTO items (source, source_id, type, title, content, status, metadata, created_at, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
       ON CONFLICT(source, source_id) DO UPDATE SET
           type=excluded.type, title=excluded.title, content=excluded.content,
           status=excluded.status, metadata=excluded.metadata, updated_at=excluded.updated_at""",
    (args.source, args.source_id, args.type, args.title, args.content,
     args.status, metadata, now, now),
)
```

Note: this also simplifies the response — you lose the "created" vs "updated" distinction, but could check `changes()` or `last_insert_rowid()` if needed.

### 5. SKILL.md uses `python3` but project rule requires venv interpreter

SKILL.md says `python3 $KIOKU --db $DB init`, but `CLAUDE.md` mandates `.claude/skills/.venv/bin/python3` for skill scripts. This script uses only stdlib so it works either way, but for consistency and to follow project conventions, the docs should use the venv path.

**Fix:** Update SKILL.md setup section to use `.claude/skills/.venv/bin/python3`.

## Low Priority

### 6. Schema doc (references/schema.md) omits default values

Schema doc doesn't mention `status DEFAULT 'open'`, `metadata DEFAULT '{}'`, or `created_at`/`updated_at` defaults. Minor inconsistency with actual SQL.

---

## SKILL.md Clarity Assessment

### kioku-lite/SKILL.md — Good
- Clear setup, command examples, output format documented
- Agent can use without additional context
- Missing: what happens on errors (now partially addressed by bug #1 and #2)

### pm-spec-to-tickets/SKILL.md — Very Good
- Excellent step-by-step with explicit WAIT checkpoints
- Error handling table covers main failure modes
- Clear prerequisite list (Notion MCP, Atlassian MCP)
- One minor gap: doesn't specify which Jira issue type name to use for Epics (some projects use "Epic", others use custom names). Step 3 does reference `getJiraIssueTypeMetaWithFields` which handles this — acceptable.

### references/jira-field-mapping.md — Good
- Clean mapping, templates useful for agents
- Correctly advises not to set assignee/sprint

### references/example-output.md — Good
- Concrete examples help agents understand expected format

---

## Positive Observations

- All SQL uses parameterized queries — no injection risk
- FTS5 triggers correctly handle INSERT/UPDATE/DELETE sync
- Idempotent design (upsert, INSERT OR IGNORE) — safe for retries
- JSON output format consistent across all commands
- DB path gitignored — no accidental secret/data commits
- Two-checkpoint approval flow in pm-spec-to-tickets prevents runaway ticket creation
- Schema reference doc matches actual implementation (minus defaults noted above)

## Recommended Actions

1. **Fix #1** (search crash) — straightforward, high impact
2. **Fix #2** (uninitialized DB crash) — straightforward, improves DX
3. **Fix #4** (atomic upsert) — eliminates race condition, simplifies code
4. **Fix #3** (connection cleanup) — minor risk but good practice
5. **Fix #5** (venv path in docs) — consistency with project rules

## Unresolved Questions

- Should `cmd_link` validate that both referenced items exist before creating the relationship? Currently it allows dangling references.
- Should there be a `list` command (e.g., list all items by source or type)? Could be useful for agents exploring the knowledge base.
