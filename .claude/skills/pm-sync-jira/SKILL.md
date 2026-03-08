---
name: ck:pm-sync-jira
description: "Sync Jira tickets into Kioku knowledge base. Fetches by project or JQL, stores with relationships. Use for building local searchable index of Jira issues."
argument-hint: "[project key, JQL query, or 'incremental']"
---

# pm-sync-jira

Fetches Jira tickets via MCP and upserts them into Kioku knowledge base with relationships (epic links, issue links).

## Prerequisites

- Atlassian MCP connected (tools: `searchJiraIssuesUsingJql`, `getJiraIssue`, `getVisibleJiraProjects`)
- Kioku Lite initialized (**required** — the whole point is storing data)

## Workflow

### Step 0: Kioku Setup Check

Check if kioku DB exists at `.claude/kioku/pm.db`:
```bash
python3 .claude/skills/kioku-lite/scripts/kioku.py --db .claude/kioku/pm.db search --query "test" 2>&1
```
- If **ok** -> kioku ready, proceed
- If **"not initialized"** -> run init automatically:
  ```bash
  python3 .claude/skills/kioku-lite/scripts/kioku.py --db .claude/kioku/pm.db init
  ```

Kioku is REQUIRED for this skill. If init fails, stop and report error.

### Step 1: Determine Sync Scope

Parse user input into one of:
1. **Project key** (e.g., "PROJ") -> JQL: `project = PROJ ORDER BY updated DESC`
2. **Custom JQL** (e.g., "project = PROJ AND type = Bug") -> use as-is
3. **Incremental** (e.g., "PROJ since last week") -> JQL: `project = PROJ AND updated >= "YYYY-MM-DD" ORDER BY updated DESC`

Ask user for:
- Project key OR JQL query
- Optional: date filter for incremental sync
- Optional: max tickets to sync (default: all)

### Step 2: Fetch Tickets (Paginated Loop)

Paginate through all results:

```
startAt = 0
maxResults = 50
allTickets = []

LOOP:
  result = call searchJiraIssuesUsingJql(
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

### Step 3: Enrich Tickets

For each ticket, call `getJiraIssue` to get:
- Full description (may be truncated in search results)
- Issue links (not returned in search)
- Epic/parent field

Report progress: "Enriching ticket {n} of {total}..."

**Optimization for large syncs (100+ tickets):** If user set a max limit, respect it. For very large projects, suggest incremental sync with date filter.

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
  --content "$(cat <<'CONTENT'
Full description from Jira...
CONTENT
)" \
  --status open \
  --metadata '{"issue_type":"Story","priority":"High","labels":["auth"],"components":["Backend"],"assignee":"alice","reporter":"bob","project":"PROJ","sprint":"Sprint 5","created":"2026-01-15","updated":"2026-03-07","resolution":null}'
```

**Status mapping** (see `references/jira-status-mapping.md`):
- Open / To Do / Backlog / New / Reopened / Selected for Development -> `open`
- In Progress / In Review / In QA / Code Review / Testing / Blocked -> `in_progress`
- Done / Closed / Resolved / Released / Cancelled / Won't Do / Declined -> `closed`
- Unknown status -> default to `open`, log warning

**Content construction:** Concatenate description + acceptance criteria if present. Use heredoc for multi-line content. Keep under 10K chars.

**Metadata JSON fields:**
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
- `resolution`: resolution name if resolved, else null

**JSON escaping:** Escape double quotes in titles/descriptions. Replace newlines with `\n` in metadata strings. Use heredoc for content argument.

### Step 5: Create Relationships

After ALL tickets are stored, process relationships:

**Epic-to-Story links:**
For tickets with `epic` or `parent` field, create:
```bash
python3 $KIOKU --db $DB link \
  --from-source jira --from-id "PROJ-10" \
  --to-source jira --to-id "PROJ-123" \
  --rel-type epic_to_story
```

**Issue links (blocks, relates to, duplicates):**
From `getJiraIssue` response, `issuelinks` field contains linked issues. Map link types:
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

**Important:** Only create links where BOTH tickets exist in Kioku (both synced in this run or previously). Skip links to tickets outside the sync scope and log them as warnings.

### Step 6: Summary Report

Present results to user:

```
## Sync Complete

**Scope:** [JQL used]
**Total:** [N] tickets synced
**Relationships:** [N] created

| Type | Count |
|------|-------|
| Epic | [n] |
| Story | [n] |
| Task | [n] |
| Bug | [n] |
| Sub-task | [n] |

### Warnings
- [ticket]: empty description
- [ticket] -> [ticket]: link skipped (target not in scope)

### Next Steps
- Search: `kioku search --query "your topic"` to query synced data
- Incremental: re-run with date filter for future updates
```

## Error Handling

| Error | Action |
|-------|--------|
| Jira MCP not connected | Tell user to configure Atlassian MCP |
| Project not found / no access | List available projects via `getVisibleJiraProjects` |
| Kioku not initialized | Run `init` automatically |
| JQL syntax error | Show Jira's error message, suggest corrections |
| Rate limit / timeout | Report progress so far, offer to resume from last `startAt` |
| Empty description | Store with empty content, log warning |
| Invalid JSON in metadata | Escape special chars before building JSON |

## References

- `references/jira-status-mapping.md` — Jira status to Kioku status mapping
- `references/example-output.md` — Example sync session output
