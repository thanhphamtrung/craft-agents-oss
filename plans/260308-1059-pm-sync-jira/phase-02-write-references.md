# Phase 2: Write Reference Files

## Context

Two reference files needed under `.claude/skills/pm-sync-jira/references/`.

## File 1: `jira-status-mapping.md`

Maps Jira workflow statuses to Kioku's three-value status enum: `open`, `in_progress`, `closed`.

### Content to Write

```markdown
# Jira Status Mapping

Maps Jira statuses to Kioku status values. Jira statuses vary by project workflow.

## Default Mapping

| Kioku Status | Jira Statuses |
|-------------|---------------|
| `open` | Open, To Do, Backlog, New, Reopened, Selected for Development |
| `in_progress` | In Progress, In Review, In QA, Code Review, Testing, Blocked |
| `closed` | Done, Closed, Resolved, Released, Cancelled, Won't Do, Declined |

## Rules

1. Match is **case-insensitive** (e.g., "IN PROGRESS" -> `in_progress`)
2. If status not in table, default to `open` and log warning
3. User can override by providing custom mapping at sync time

## Custom Mapping (User Override)

If user says "In our project, 'Waiting' means in_progress", apply that override for the session.

## Common Workflow Variants

### Simplified (3-column board)
To Do -> In Progress -> Done

### Software Development
Backlog -> Selected for Dev -> In Progress -> In Review -> Done

### Kanban
New -> Analysis -> Dev -> QA -> Release -> Closed

### Support/Service Desk
Open -> Waiting for Support -> Waiting for Customer -> Resolved -> Closed
```

## File 2: `example-output.md`

Shows what a complete sync session looks like for implementer reference.

### Content to Write

```markdown
# Example Sync Output

## User Request
"Sync all tickets from project ACME"

## Agent Execution Flow

### Step 1: Scope
```
Syncing project ACME — all tickets, no date filter.
JQL: project = ACME ORDER BY updated DESC
```

### Step 2: Fetch
```
Fetching tickets from Jira...
  Page 1: tickets 1-50 of 127
  Page 2: tickets 51-100 of 127
  Page 3: tickets 101-127 of 127
Fetched 127 tickets.
```

### Step 3: Enrich
```
Enriching tickets with full details and links...
  Processing 1/127: ACME-1 (Epic)
  Processing 2/127: ACME-2 (Story)
  ...
  Processing 127/127: ACME-127 (Task)
```

### Step 4: Store
```
Storing tickets in Kioku...
  ACME-1: created (Epic)
  ACME-2: updated (Story)
  ...
```

### Step 5: Relationships
```
Creating relationships...
  ACME-1 -> ACME-2: epic_to_story
  ACME-1 -> ACME-3: epic_to_story
  ACME-5 -> ACME-12: blocks
  ACME-8 -> ACME-9: related_to
Created 43 relationships.
```

### Step 6: Summary
```
## Sync Complete

**Scope:** project = ACME
**Total:** 127 tickets synced
**New:** 127 | **Updated:** 0
**Relationships:** 43

| Type | Count |
|------|-------|
| Epic | 3 |
| Story | 48 |
| Task | 52 |
| Bug | 19 |
| Sub-task | 5 |

### Warnings
- ACME-44: empty description
- ACME-99 -> EXT-5: link skipped (target not in scope)

### Next Steps
- Search: `kioku search --query "authentication"`
- Incremental: re-run with "ACME since 2026-03-08"
```
```

## Files to Create

| File | Path |
|------|------|
| Status mapping | `.claude/skills/pm-sync-jira/references/jira-status-mapping.md` |
| Example output | `.claude/skills/pm-sync-jira/references/example-output.md` |

## Success Criteria

- [ ] Status mapping covers common Jira workflows
- [ ] Default mapping handles 90%+ of standard statuses
- [ ] Example output matches SKILL.md workflow steps exactly
- [ ] Example shows pagination, enrichment, relationships, and summary
