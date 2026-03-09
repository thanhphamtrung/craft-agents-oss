---
name: ck:pm-search
description: "Search across all indexed PM sources (Jira, Slack, Notion) in Kioku. Returns unified ranked results with source links. Use for finding tickets, specs, threads across tools."
argument-hint: "[search query, optionally with filters like 'jira bugs about auth']"
---

# pm-search

Unified search across all PM sources indexed in Kioku knowledge base.

## Prerequisites

- Kioku DB exists at `.claude/kioku/pm.db`
- At least one source synced (run `pm-sync-jira` first if empty)

## Workflow

### Step 0: DB Check

```bash
KIOKU=".claude/skills/kioku-lite/scripts/kioku.py"
DB=".claude/kioku/pm.db"
PYTHON=".claude/skills/.venv/bin/python3"

$PYTHON $KIOKU --db $DB search --query "test" --limit 1 2>&1
```

- If **ok** -> proceed
- If **"not initialized"** -> run `$PYTHON $KIOKU --db $DB init`
- If DB exists but 0 results for broad query -> suggest running `pm-sync-jira` first

### Step 1: Parse User Intent

Parse natural language into search params:

| User says | Query | Source | Type | Status |
|-----------|-------|--------|------|--------|
| "find auth bugs" | auth bugs | - | - | - |
| "open jira tickets about login" | login | jira | ticket | open |
| "slack messages about deploy" | deploy | slack | message | - |
| "closed bugs in jira" | bugs | jira | ticket | closed |
| "notion docs about onboarding" | onboarding | notion | doc | - |
| "in-progress tasks" | tasks | - | - | in_progress |

**Extraction rules:**
- **Source:** "in jira", "from slack", "notion docs" -> `--source jira|slack|notion`
- **Type:** "tickets/bugs/stories" -> `ticket`, "messages/threads" -> `message`, "docs/pages" -> `doc`, "specs" -> `spec`
- **Status:** "open/new" -> `open`, "closed/done/resolved" -> `closed`, "in progress/in review" -> `in_progress`
- **Query:** remaining terms after extracting filters

### Step 2: Execute Search

```bash
$PYTHON $KIOKU --db $DB search \
  --query "<terms>" \
  [--source jira|slack|notion] \
  [--type ticket|message|doc|spec] \
  [--status open|closed|in_progress] \
  --limit 15
```

All filter flags are optional. Omit any not detected in user intent.

### Step 3: Format Results

Present as markdown table:

```markdown
## Search Results: "<query>"
Found N results [filtered by: source=jira, status=open]

| # | Source | ID | Title | Type | Status | Updated |
|---|--------|----|-------|------|--------|---------|
| 1 | Jira | PROJ-123 | Fix login bug | ticket | open | 2026-03-07 |
| 2 | Slack | thread-abc | Auth discussion | message | - | 2026-03-06 |
```

- Show top 15 by default, mention if more available
- If 0 results: suggest broader query, different filters, or syncing more data

### Step 4: Detail View (on request)

If user asks for details on a specific result:

```bash
$PYTHON $KIOKU --db $DB get --source jira --source-id PROJ-123
```

Present full item with metadata and relationships:

```markdown
## PROJ-123: Fix login bug
**Source:** Jira | **Type:** ticket | **Status:** open | **Updated:** 2026-03-07

### Description
[full content]

### Metadata
- Assignee: alice | Priority: High | Labels: auth, bug

### Relationships
- Epic: PROJ-10 (Auth Epic)
- Blocks: PROJ-456
```

### Step 5: Synthesize

After showing results:
- Summarize key themes across results
- Suggest follow-up: "Want details on any item?" / "Try narrowing with `--source jira`"

## Error Handling

| Error | Action |
|-------|--------|
| DB not found | Suggest running `pm-sync-jira` first |
| No results | Suggest broader query, different filters, or syncing more data |
| FTS syntax error | Simplify query (remove special chars) |
