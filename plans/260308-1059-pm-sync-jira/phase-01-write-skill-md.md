# Phase 1: Write SKILL.md

## Context

- Pattern: follow `pm-spec-to-tickets/SKILL.md` structure (frontmatter, prerequisites, workflow steps, error handling)
- Path: `.claude/skills/pm-sync-jira/SKILL.md`

## SKILL.md Frontmatter

```yaml
---
name: ck:pm-sync-jira
description: "Sync Jira tickets into Kioku knowledge base. Fetches by project or JQL, stores with relationships. Use for building local searchable index of Jira issues."
argument-hint: "[project key, JQL query, or 'incremental']"
---
```

## Workflow Steps to Implement

### Step 0: Kioku Setup Check

Same pattern as `pm-spec-to-tickets`:
- Check DB exists via `kioku.py search --query "test"`
- If not initialized, offer to run `init`
- Unlike spec-to-tickets, kioku is REQUIRED here (not optional) -- the whole point is storing data

### Step 1: Determine Sync Scope

Parse user input into one of:
1. **Project key** (e.g., "PROJ") -> JQL: `project = PROJ ORDER BY updated DESC`
2. **Custom JQL** (e.g., "project = PROJ AND type = Bug") -> use as-is
3. **Incremental** (e.g., "PROJ since last week") -> JQL: `project = PROJ AND updated >= "2026-03-01" ORDER BY updated DESC`

Ask user for:
- Project key OR JQL query
- Optional: date filter for incremental sync
- Optional: max tickets to sync (default: all)

### Step 2: Fetch Tickets (Paginated Loop)

Core pagination logic the agent must follow:

```
startAt = 0
maxResults = 50
allTickets = []

LOOP:
  result = call mcp__claude_ai_Atlassian__searchJiraIssuesUsingJql(
    jql = "<constructed JQL>",
    startAt = startAt,
    maxResults = maxResults
  )

  append result.issues to allTickets

  if startAt + maxResults >= result.total:
    BREAK
  else:
    startAt += maxResults
    CONTINUE
```

Report progress: "Fetched {len} of {total} tickets..."

### Step 3: Enrich Tickets (Selective)

For each ticket from search results, check if we need full details:
- Search results include: key, summary, status, issuetype, priority, assignee, labels, created, updated
- Search results MAY include: description, epic link, components
- If description or links are truncated/missing, call `getJiraIssue` for full data

**Optimization**: Only call `getJiraIssue` for tickets where:
- Description was truncated in search results
- We need issue links (not returned in search)

In practice: call `getJiraIssue` for EVERY ticket to get links. Batch awareness: report "Enriching ticket {n} of {total}..."

### Step 4: Map and Store Each Ticket

For each ticket, run kioku store:

```bash
KIOKU=".claude/skills/kioku-lite/scripts/kioku.py"
DB=".claude/kioku/pm.db"

python3 $KIOKU --db $DB store \
  --source jira \
  --source-id "PROJ-123" \
  --type ticket \
  --title "Fix login bug" \
  --content "Full description from Jira..." \
  --status open \
  --metadata '{"issue_type":"Story","priority":"High","labels":["auth","api"],"components":["Backend"],"assignee":"alice","project":"PROJ","created":"2026-01-15","updated":"2026-03-07"}'
```

**Status mapping** (see `references/jira-status-mapping.md`):
- Open/To Do/Backlog/New -> `open`
- In Progress/In Review/In QA/Selected for Development -> `in_progress`
- Done/Closed/Resolved/Released -> `closed`
- Unknown -> default to `open`, log warning

**Content construction**: Concatenate description + acceptance criteria if present. Truncate to reasonable length (kioku has no hard limit but keep under 10K chars).

**Metadata JSON fields**:
- `issue_type`: Epic/Story/Task/Bug/Sub-task
- `priority`: Highest/High/Medium/Low/Lowest
- `labels`: array of label strings
- `components`: array of component names
- `assignee`: display name or null
- `reporter`: display name
- `project`: project key
- `sprint`: active sprint name if any
- `created`: ISO date
- `updated`: ISO date
- `resolution`: resolution name if resolved

### Step 5: Create Relationships

After ALL tickets are stored, process relationships:

**Epic-to-Story links:**
- From enriched ticket data, if ticket has `epic` field or `parent` field
- Extract epic key
- Create relationship:

```bash
python3 $KIOKU --db $DB link \
  --from-source jira --from-id "PROJ-10" \
  --to-source jira --to-id "PROJ-123" \
  --rel-type epic_to_story
```

**Issue links (blocks, relates to, duplicates):**
- From `getJiraIssue` response, `issuelinks` field contains linked issues
- For each link, create relationship. Use `rel_type` based on link type:
  - "blocks" / "is blocked by" -> `blocks`
  - "relates to" -> `related_to`
  - "duplicates" / "is duplicated by" -> `duplicates`
  - "clones" / "is cloned by" -> `clones`

```bash
python3 $KIOKU --db $DB link \
  --from-source jira --from-id "PROJ-123" \
  --to-source jira --to-id "PROJ-456" \
  --rel-type related_to
```

**Note:** Only create links where BOTH tickets are in Kioku (both synced in this run or previously). Skip links to tickets outside the sync scope -- they can be picked up on future syncs.

### Step 6: Summary Report

Present table to user:

```
## Sync Complete

**Scope:** project = PROJ (all tickets)
**Total fetched:** 142
**New:** 38
**Updated:** 104
**Relationships created:** 67

| Stat | Count |
|------|-------|
| Epics | 5 |
| Stories | 52 |
| Tasks | 61 |
| Bugs | 24 |

### Warnings
- 3 tickets had empty descriptions
- 2 issue links skipped (target not in sync scope)

### Next Steps
- Run `kioku search --query "your topic"` to query synced data
- Re-run with date filter for incremental updates
```

**Tracking new vs updated**: Check kioku store response. If `created` field in response differs from `updated`, it was an update. Alternatively, track by checking if item existed before store call (via `get` first) -- but this doubles calls. Simpler: count all as "synced" and note total.

**Tracking new vs updated**: kioku `store` returns `{"ok": true, "action": "upserted"}` -- it does NOT distinguish create from update. Two options:
1. **Simple**: Report total synced count only (recommended for v1)
2. **Precise**: Call `get` before each `store`; if item exists -> update, else -> new. Adds N extra calls.

Recommend option 1 for v1. The summary reports "N tickets synced" without new/updated breakdown. Can enhance later if needed.

## Error Handling

| Error | Action |
|-------|--------|
| Jira MCP not connected | Tell user to configure Atlassian MCP |
| Project not found / no access | List available projects via `getVisibleJiraProjects` |
| Kioku not initialized | Run `init` automatically (this skill requires it) |
| JQL syntax error | Show Jira's error message, suggest corrections |
| Pagination timeout / rate limit | Report progress so far, offer to resume from last `startAt` |
| Empty description | Store with empty content, log warning |
| Invalid JSON in metadata | Escape special chars in title/content before building JSON |

## Implementation Notes

### JSON Escaping
Ticket titles and descriptions may contain quotes, newlines, special chars. When building the `--metadata` JSON string and `--content` argument:
- Escape double quotes in strings
- Replace newlines with `\n` or strip them
- Consider using heredoc or temp file for long descriptions

Recommended approach: Use bash heredoc for content:
```bash
python3 $KIOKU --db $DB store \
  --source jira --source-id "PROJ-123" \
  --type ticket \
  --title "Fix \"login\" bug" \
  --content "$(cat <<'CONTENT'
Full description here with "quotes" and
multiple lines...
CONTENT
)" \
  --status open \
  --metadata '{"issue_type":"Story"}'
```

### Relationship Type Registry
Current kioku supports: `spec_to_ticket`, `epic_to_story`, `thread_to_ticket`
This skill adds: `blocks`, `related_to`, `duplicates`, `clones`
Kioku `link` command accepts any string for `rel_type` -- no schema change needed.

## Files to Create

- `.claude/skills/pm-sync-jira/SKILL.md`

## Success Criteria

- [ ] SKILL.md follows same structure as pm-spec-to-tickets/SKILL.md
- [ ] Handles pagination correctly
- [ ] Maps all key Jira fields to kioku store params
- [ ] Creates epic_to_story and issue link relationships
- [ ] Reports summary with new/updated counts
- [ ] Handles errors gracefully with actionable messages
- [ ] Idempotent -- re-running produces same result
