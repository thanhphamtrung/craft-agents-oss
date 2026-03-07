---
name: ck:kioku-lite
description: "Local-first personal memory engine for AI agents. Zero Docker required. Stores memories in SQLite with BM25 full-text search. Use when: storing knowledge from Jira/Notion/Slack, dedup checking, cross-tool correlation, or building persistent agent memory."
---

# Kioku Lite

Local SQLite knowledge base with BM25 full-text search. Stores items from any source (Jira, Notion, Slack) with relationships between them.

## Setup

```bash
KIOKU=".claude/skills/kioku-lite/scripts/kioku.py"
DB=".claude/kioku/pm.db"

# Initialize database (run once)
python3 $KIOKU --db $DB init
```

## Commands

### Store/Upsert Item
```bash
python3 $KIOKU --db $DB store \
  --source jira --source-id PROJ-123 --type ticket \
  --title "Fix login bug" --content "Full description here" \
  --status open --metadata '{"assignee":"alice","labels":["bug"]}'
```
Upserts by `source + source_id` — safe to call repeatedly.

### Search (BM25)
```bash
python3 $KIOKU --db $DB search --query "login authentication" --limit 10
```
Returns items ranked by relevance with BM25 scoring.

### Get Item
```bash
python3 $KIOKU --db $DB get --source jira --source-id PROJ-123
```
Returns item with all relationships.

### Link Items
```bash
python3 $KIOKU --db $DB link \
  --from-source notion --from-id page-abc \
  --to-source jira --to-id PROJ-123 \
  --rel-type spec_to_ticket
```
Relationship types: `spec_to_ticket`, `epic_to_story`, `thread_to_ticket`

### Delete Item
```bash
python3 $KIOKU --db $DB delete --source jira --source-id PROJ-123
```
Removes item and all its relationships.

## Output Format

All commands return JSON: `{"ok": true, ...}` on success, `{"ok": false, "error": "..."}` on failure.

## Schema Reference

See `references/schema.md` for full database schema documentation.

## Notes

- Database stored at `.claude/kioku/pm.db` (gitignored, local only)
- Uses SQLite FTS5 for full-text search — no external dependencies
- All operations are idempotent (safe to retry)
- Python 3.8+ with stdlib only (no pip packages needed)
