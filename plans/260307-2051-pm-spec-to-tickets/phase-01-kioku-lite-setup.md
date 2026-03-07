---
phase: 1
title: Kioku Lite Setup
status: done
priority: P1
effort: 30m
---

# Phase 1: Kioku Lite Setup

## Context

- Brainstorm report: `plans/reports/brainstorm-260307-2021-pm-workflow-knowledge-base.md`
- Kioku Lite does NOT exist in the repo yet (confirmed via glob search)
- Needed as the unified knowledge base for all PM workflows (dedup, search, cross-tool correlation)

## Overview

Set up a `kioku-lite` skill that provides local SQLite-based knowledge storage with tri-hybrid search (BM25 + vector + knowledge graph). This is the foundation layer that all PM workflow skills depend on.

## Key Insights

- Kioku is a LOCAL persistence layer -- no external service needed
- SQLite is the storage backend -- zero infrastructure
- The skill needs to expose clear "API" instructions for other skills to call (store, search, delete)
- Tri-hybrid search (BM25 + vector + KG) is the ideal, but start with BM25 + basic search; vector/KG can be added later (YAGNI)

## Requirements

### Functional
- Store items with: source, source_id, type, title, content, status, metadata (JSON), relationships
- Upsert by source_id (idempotent)
- Search by keyword (BM25)
- Search by semantic similarity (vector -- stretch goal)
- Link items via relationships
- Delete/update items

### Non-Functional
- SQLite database stored at workspace level (e.g., `.claude/kioku/pm.db`)
- No external dependencies beyond Python stdlib + sqlite3
- Fast local queries

## Architecture

```
.claude/skills/kioku-lite/
  SKILL.md          -- Skill instructions for agents
  scripts/
    kioku.py        -- Python CLI: init, store, search, link, delete
  references/
    schema.md       -- Database schema docs
```

The skill works via CLI: agents call `kioku.py` commands from bash.

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,        -- jira | slack | notion
  source_id TEXT NOT NULL,     -- unique ID from source
  type TEXT NOT NULL,          -- ticket | message | doc | spec
  title TEXT NOT NULL,
  content TEXT,
  status TEXT DEFAULT 'open',  -- open | closed | in_progress
  metadata TEXT DEFAULT '{}',  -- JSON blob
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now')),
  UNIQUE(source, source_id)
);

CREATE TABLE IF NOT EXISTS relationships (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  from_source TEXT NOT NULL,
  from_source_id TEXT NOT NULL,
  to_source TEXT NOT NULL,
  to_source_id TEXT NOT NULL,
  rel_type TEXT NOT NULL,      -- spec_to_ticket | epic_to_story | thread_to_ticket
  UNIQUE(from_source, from_source_id, to_source, to_source_id, rel_type)
);

-- BM25 full-text search
CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
  title, content, source, type, status,
  content='items',
  content_rowid='id'
);
```

## CLI Interface

```bash
KIOKU=".claude/skills/kioku-lite/scripts/kioku.py"
DB=".claude/kioku/pm.db"

# Initialize database
python3 $KIOKU init --db $DB

# Store/upsert item
python3 $KIOKU store --db $DB \
  --source jira --source-id PROJ-123 --type ticket \
  --title "Fix login bug" --content "Full description..." \
  --status open --metadata '{"assignee":"alice","labels":["bug"]}'

# Search (BM25)
python3 $KIOKU search --db $DB --query "login authentication bug" --limit 10

# Link items
python3 $KIOKU link --db $DB \
  --from-source notion --from-id page-abc \
  --to-source jira --to-id PROJ-123 \
  --rel-type spec_to_ticket

# Get item
python3 $KIOKU get --db $DB --source jira --source-id PROJ-123

# Delete item
python3 $KIOKU delete --db $DB --source jira --source-id PROJ-123
```

## Implementation Steps

1. [x] Create directory: `.claude/skills/kioku-lite/`
2. [x] Write `scripts/kioku.py` -- Python CLI with subcommands: init, store, search, get, link, delete
3. [x] Write `references/schema.md` -- Document the schema for other skills
4. [x] Write `SKILL.md` -- Instructions for agents on how to use kioku-lite
5. [x] Test: init DB, store a sample item, search for it, verify upsert idempotency
6. [x] Add `.claude/kioku/` to `.gitignore` (database is local, not committed)

## Success Criteria

- [x] `kioku.py init` creates SQLite DB with correct schema
- [x] `kioku.py store` upserts items correctly (no duplicates on re-run)
- [x] `kioku.py search` returns relevant results via FTS5
- [x] `kioku.py link` creates relationships between items
- [x] SKILL.md is clear enough for another agent to use without guidance

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| FTS5 not available in system SQLite | Python's bundled sqlite3 includes FTS5 on modern systems; test during init |
| Vector search needed for dedup quality | Start with BM25; add vector later if keyword search proves insufficient |
| Database path conflicts across workspaces | Use relative path `.claude/kioku/pm.db` from project root |

## Next Steps

After this phase, Phase 2 (`pm-spec-to-tickets` SKILL.md) can reference kioku-lite commands directly.
