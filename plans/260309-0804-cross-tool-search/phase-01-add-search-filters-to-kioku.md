---
title: "Add Search Filters to kioku.py"
status: pending
priority: P2
effort: 45min
---

# Phase 1: Add Search Filters to kioku.py

## Context

- kioku.py `search` command only supports `--query` and `--limit`
- pm-search skill needs `--source`, `--type`, `--status` filters for filtered search
- File: `.claude/skills/kioku-lite/scripts/kioku.py`

## Key Insights

- FTS5 MATCH handles text search; filters need WHERE clauses on the `items` table
- Filters are AND-combined (e.g., `--source jira --status open` = jira AND open)
- Keep backward compatible — all filters optional

## Related Code

- `cmd_search()` function at line ~140 in kioku.py
- `p_search` argparse setup at line ~259
- Items table columns: `source`, `type`, `status` (from schema)

## Implementation Steps

### 1. Add CLI arguments to search subparser (~line 259-261)

After the existing `--limit` argument, add:

```python
p_search.add_argument("--source", help="Filter by source (jira|slack|notion)")
p_search.add_argument("--type", help="Filter by type (ticket|message|doc|spec)")
p_search.add_argument("--status", help="Filter by status (open|closed|in_progress)")
```

### 2. Update `cmd_search()` to apply filters (~line 140-166)

Modify the SQL query to add optional WHERE clauses:

```python
def cmd_search(args):
    """Search items using FTS5 BM25 ranking."""
    query = args.query.strip()
    if not query:
        print(json.dumps({"ok": True, "count": 0, "results": []}))
        return

    conn = get_db(args.db)
    fail_if_not_initialized(conn)
    limit = args.limit or 10

    # Build filter clauses
    filters = []
    params = [query]

    if args.source:
        filters.append("i.source = ?")
        params.append(args.source)
    if args.type:
        filters.append("i.type = ?")
        params.append(args.type)
    if args.status:
        filters.append("i.status = ?")
        params.append(args.status)

    where_extra = (" AND " + " AND ".join(filters)) if filters else ""
    params.append(limit)

    try:
        cursor = conn.execute(
            f"""SELECT i.*, bm25(items_fts) AS rank
               FROM items_fts fts
               JOIN items i ON i.id = fts.rowid
               WHERE items_fts MATCH ?{where_extra}
               ORDER BY rank
               LIMIT ?""",
            params,
        )
        results = [dict(row) for row in cursor.fetchall()]
        print(json.dumps({"ok": True, "count": len(results), "results": results}))
    except sqlite3.OperationalError as e:
        print(json.dumps({"ok": False, "error": f"Search failed: {e}"}))
    finally:
        conn.close()
```

### 3. Test

```bash
KIOKU=".claude/skills/kioku-lite/scripts/kioku.py"
DB=".claude/kioku/pm.db"
PYTHON=".claude/skills/.venv/bin/python3"

# All filters
$PYTHON $KIOKU --db $DB search --query "login" --source jira --type ticket --status open

# Single filter
$PYTHON $KIOKU --db $DB search --query "login" --source jira

# No filters (backward compat)
$PYTHON $KIOKU --db $DB search --query "login"
```

## Todo

- [ ] Add `--source`, `--type`, `--status` args to search subparser
- [ ] Update `cmd_search()` with filter WHERE clauses
- [ ] Test all filter combinations
- [ ] Verify backward compatibility (no filters = same behavior)

## Success Criteria

- `search --query "x" --source jira` returns only Jira items
- `search --query "x" --type ticket --status open` returns only open tickets
- `search --query "x"` (no filters) works exactly as before
- Output format unchanged (JSON with `ok`, `count`, `results`)

## Risk

- **Low:** Simple SQL WHERE additions, no schema changes needed
