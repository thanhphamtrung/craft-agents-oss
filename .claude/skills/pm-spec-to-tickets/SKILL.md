---
name: ck:pm-spec-to-tickets
description: "Read Notion specs and create Jira epics + stories with two-checkpoint approval flow. Use for converting PRDs, feature specs, or requirements docs into actionable Jira tickets."
argument-hint: "[Notion URL, page name, or search query]"
---

# pm-spec-to-tickets

Converts Notion specs/PRDs into Jira epics + stories via a two-checkpoint human-in-the-loop flow.

## Prerequisites

- Notion MCP connected (tools: `notion-fetch`, `notion-search`)
- Atlassian MCP connected (tools: `createJiraIssue`, `getVisibleJiraProjects`)
- Kioku Lite initialized (optional — enables dedup)

## Workflow

### Step 0: Kioku Setup Check

Check if kioku DB exists at `.claude/kioku/pm.db`:
```bash
python3 .claude/skills/kioku-lite/scripts/kioku.py --db .claude/kioku/pm.db search --query "test" 2>&1
```
- If **ok** → kioku ready, proceed
- If **"not initialized"** → ask user: "Kioku knowledge base is not set up yet. Want me to initialize it? (enables duplicate detection across runs)"
  - **Yes** → run `python3 .claude/skills/kioku-lite/scripts/kioku.py --db .claude/kioku/pm.db init`
  - **No** → skip kioku features, continue without dedup

### Step 1: Resolve Notion Page

Parse user input to find the spec:
- **URL provided** → call `notion-fetch` with the URL
- **Page name** → call `notion-search` with query, confirm if multiple results
- **Ambiguous** → present matches, ask user to pick

Extract full page content (title, body, sub-pages if needed).

### Step 2: Checkpoint 1 — Spec Review

Present structured summary to user:

```
## Spec Review

**Title:** [from page]
**Features/Requirements:**
1. [requirement]
2. [requirement]
...

**Scope:** [included vs excluded]
**Ambiguities:** [unclear items, missing acceptance criteria]
**Dependencies:** [external systems, APIs, other features]
```

Ask: **"Is this interpretation correct? Anything to add, remove, or clarify?"**

**WAIT for user response.** Do NOT proceed without approval.
If user adjusts: incorporate changes into working interpretation.

### Step 3: Discover Jira Context

- Ask user for **Jira project key** (no hardcoded default)
- Call `getVisibleJiraProjects` to list available projects for reference
- Call `getJiraProjectIssueTypesMetadata` to get issue types
- Call `getJiraIssueTypeMetaWithFields` for Epic and Story field schemas
- See `references/jira-field-mapping.md` for field mapping guidance

### Step 4: Dedup Check (if Kioku available)

```bash
KIOKU=".claude/skills/kioku-lite/scripts/kioku.py"
DB=".claude/kioku/pm.db"
python3 $KIOKU --db $DB search --query "[feature title]" --limit 5
```

- Flag matches: "Similar ticket exists: PROJ-123 — [title]"
- If Kioku DB missing, skip dedup and warn user once

### Step 5: Checkpoint 2 — Ticket Proposal

Present proposed tickets:

```
## Ticket Proposal

**Epic:** [Title from spec]
  Description: [Summary + link to Notion page]

  **Story 1:** [Feature/requirement name]
    Description: [Detailed from spec]
    Acceptance Criteria:
    - [criterion]
    - [criterion]

  **Story 2:** ...

[Dedup warnings if any]
```

Ask: **"Create these tickets? Any changes needed?"**

**WAIT for user response.** Do NOT proceed without approval.

### Step 6: Create Tickets

1. Create **Epic** via `createJiraIssue` (include Notion page link in description)
2. Create **Stories** linked to Epic via `createJiraIssue`
3. Index each in Kioku (if available):
   ```bash
   python3 $KIOKU --db $DB store --source jira --source-id [KEY] --type ticket \
     --title "[title]" --content "[description]" --status open \
     --metadata '{"issue_type":"[Epic|Story]","project":"[KEY]"}'
   ```
4. Link Notion page to Epic in Kioku:
   ```bash
   python3 $KIOKU --db $DB link --from-source notion --from-id [page-id] \
     --to-source jira --to-id [EPIC-KEY] --rel-type spec_to_ticket
   ```

### Step 7: Summary

Report created tickets:

```
## Created Tickets

| Key | Type | Title |
|-----|------|-------|
| PROJ-1 | Epic | [title] |
| PROJ-2 | Story | [title] |
| ...    | ...   | ...     |

Kioku: [indexed/skipped]

**Next steps:** Assign owners, set priorities, add to sprint
```

## Error Handling

| Error | Action |
|-------|--------|
| Notion page not found | Ask user to verify URL or search term |
| Multiple Notion matches | Present list, ask user to pick |
| Jira project not accessible | List available projects, ask user to choose |
| Kioku DB not initialized | Skip dedup, warn once, continue |
| Spec too large | Break into multiple epics, confirm with user |

## References

- `references/jira-field-mapping.md` — How spec sections map to Jira fields
- `references/example-output.md` — Example checkpoint outputs
