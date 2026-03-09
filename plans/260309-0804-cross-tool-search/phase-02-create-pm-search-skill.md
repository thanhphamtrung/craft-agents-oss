---
title: "Create pm-search SKILL.md"
status: pending
priority: P2
effort: 45min
---

# Phase 2: Create pm-search SKILL.md

## Context

- Pure SKILL.md — no scripts, just workflow instructions for the agent
- Uses kioku-lite CLI with filters added in Phase 1
- Follow pm-sync-jira SKILL.md style (YAML frontmatter, step-by-step workflow)

## Dependencies

- Phase 1 complete (search filters in kioku.py)

## Related Files

- Pattern to follow: `.claude/skills/pm-sync-jira/SKILL.md`
- CLI reference: `.claude/skills/kioku-lite/SKILL.md`
- Create: `.claude/skills/pm-search/SKILL.md`

## Implementation Steps

### 1. Create directory

```bash
mkdir -p .claude/skills/pm-search
```

### 2. Write SKILL.md

Target: ~100-130 lines. Structure:

```
---
name: ck:pm-search
description: "Search across all indexed PM sources (Jira, Slack, Notion) in Kioku. Returns unified ranked results with source links. Use for finding tickets, specs, threads across tools."
argument-hint: "[search query, optionally with filters like 'jira bugs about auth']"
---

# pm-search

Unified search across all PM sources indexed in Kioku knowledge base.
```

#### Key sections to include:

**Prerequisites**
- Kioku DB exists at `.claude/kioku/pm.db`
- At least one source synced (pm-sync-jira, etc.)

**Step 0: DB Check**
- Same pattern as pm-sync-jira: try search, init if needed
- If DB exists but empty, suggest running pm-sync-jira first

**Step 1: Parse User Intent**
Parse natural language into search params:
- Extract query terms
- Detect source filter: "in jira", "from slack", "notion docs"
- Detect type filter: "tickets", "messages", "docs", "specs"
- Detect status filter: "open", "closed", "in progress"

Examples:
| User says | Query | Source | Type | Status |
|-----------|-------|--------|------|--------|
| "find auth bugs" | auth bugs | - | - | - |
| "open jira tickets about login" | login | jira | ticket | open |
| "slack messages about deploy" | deploy | slack | message | - |
| "closed bugs in jira" | * | jira | ticket | closed |

**Step 2: Execute Search**
```bash
KIOKU=".claude/skills/kioku-lite/scripts/kioku.py"
DB=".claude/kioku/pm.db"
PYTHON=".claude/skills/.venv/bin/python3"

$PYTHON $KIOKU --db $DB search \
  --query "<terms>" \
  [--source jira|slack|notion] \
  [--type ticket|message|doc|spec] \
  [--status open|closed|in_progress] \
  --limit 15
```

**Step 3: Format Results**
Present as markdown table:

```markdown
## Search Results: "<query>"
Found N results [filtered by: source=jira, status=open]

| # | Source | ID | Title | Type | Status | Updated |
|---|--------|----|-------|------|--------|---------|
| 1 | Jira | PROJ-123 | Fix login bug | ticket | open | 2026-03-07 |
| 2 | Slack | thread-abc | Auth discussion | message | - | 2026-03-06 |
```

- Show source as badge: `Jira`, `Slack`, `Notion`
- Link source IDs when possible (Jira: `PROJ-123`)
- Show top 15 by default, mention if more available

**Step 4: Detail View (on request)**
If user asks for details on a specific result:

```bash
$PYTHON $KIOKU --db $DB get --source jira --source-id PROJ-123
```

Present full item:
```markdown
## PROJ-123: Fix login bug
**Source:** Jira | **Type:** ticket | **Status:** open
**Updated:** 2026-03-07

### Description
[full content]

### Metadata
- Assignee: alice
- Priority: High
- Labels: auth, bug

### Relationships
- Epic: PROJ-10 (Auth Epic)
- Blocks: PROJ-456
```

**Step 5: Synthesize Answer**
After showing results, provide a brief summary:
- How many results found, from which sources
- Key themes across results
- Suggest follow-up actions ("Want details on any item?" / "Try narrowing with --source jira")

**Error Handling Table**
| Error | Action |
|-------|--------|
| DB not found | Suggest running `pm-sync-jira` first |
| No results | Suggest broader query, different filters, or syncing more data |
| FTS syntax error | Simplify query (remove special chars) |

## Todo

- [ ] Create `.claude/skills/pm-search/` directory
- [ ] Write SKILL.md with all sections above
- [ ] Keep under 150 lines
- [ ] Verify CLI commands match Phase 1 implementation

## Success Criteria

- SKILL.md follows pm-sync-jira style (YAML frontmatter, step-by-step)
- Agent can parse "open jira bugs about auth" into correct CLI call
- Results displayed as clean markdown table with source links
- Detail view shows full item + relationships
- Under 150 lines

## Risk

- **Low:** Pure documentation, no runtime dependencies beyond kioku.py
