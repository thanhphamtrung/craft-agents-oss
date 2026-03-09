# Codebase Exploration Report: PM-Search Skill & Knowledge Base Architecture

**Date:** 2026-03-09  
**Scope:** Skills structure, kioku-lite implementation, pm-sync-jira integration, pm-search readiness

---

## Executive Summary

The Craft Agents codebase has a mature skill ecosystem. Two critical PM skills exist:
- **pm-sync-jira**: Syncs Jira tickets into local SQLite via kioku-lite
- **pm-spec-to-tickets**: Converts Notion specs → Jira tickets with human checkpoints

**`pm-search` does NOT exist yet** — opportunity to build a complementary skill for searching the kioku knowledge base by integrating with existing pm-sync-jira data.

---

## 1. Skill Directory Structure

### Pattern
```
.claude/skills/
└── {skill-name}/
    ├── SKILL.md              (required, <150 lines, YAML frontmatter + instructions)
    ├── scripts/              (optional, Python/Node.js, cross-platform, with tests)
    ├── references/           (optional, <150 lines each doc, loaded on-demand)
    └── assets/               (optional, templates/images, NOT in context)
```

### Existing PM Skills

| Skill | Files | Type | Purpose |
|-------|-------|------|---------|
| **kioku-lite** | SKILL.md + scripts/kioku.py + references/schema.md | Core | Local SQLite knowledge base with BM25 search |
| **pm-sync-jira** | SKILL.md + references/ | Integration | Fetches Jira via MCP, stores in kioku |
| **pm-spec-to-tickets** | SKILL.md + references/ | Integration | Converts Notion specs → Jira via human-in-loop |
| **pm-search** | — | — | **DOES NOT EXIST** |

---

## 2. Kioku-Lite Architecture

### Core Purpose
Local-first personal memory engine for agents. Zero Docker. Stores knowledge from Jira/Notion/Slack in SQLite with FTS5 BM25 ranking.

### Database Location
- Path: `.claude/kioku/pm.db` (local, gitignored, persistent)
- Initialization: `python3 .claude/skills/kioku-lite/scripts/kioku.py --db .claude/kioku/pm.db init`

### Data Schema

#### Table: `items`
Core knowledge storage. Upsertable by `(source, source_id)`.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | Auto-increment |
| source | TEXT NOT NULL | `jira`, `notion`, `slack` |
| source_id | TEXT NOT NULL | E.g., `PROJ-123`, `page-abc` |
| type | TEXT NOT NULL | `ticket`, `doc`, `spec`, `message` |
| title | TEXT NOT NULL | Item title |
| content | TEXT | Full description (can be 10K+ chars) |
| status | TEXT | `open`, `in_progress`, `closed` |
| metadata | TEXT | JSON blob (assignee, labels, priority, etc.) |
| created_at | TEXT | ISO datetime |
| updated_at | TEXT | ISO datetime |

Unique constraint: `(source, source_id)` → idempotent upserts.

#### Table: `relationships`
Links between items across sources.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | Auto-increment |
| from_source | TEXT | E.g., `jira` |
| from_source_id | TEXT | E.g., `PROJ-10` |
| to_source | TEXT | E.g., `jira` |
| to_source_id | TEXT | E.g., `PROJ-123` |
| rel_type | TEXT | Relationship type (see below) |

Relationship types: `spec_to_ticket`, `epic_to_story`, `thread_to_ticket`, `blocks`, `related_to`, `duplicates`, `clones`.

#### Table: `items_fts`
FTS5 virtual table. Auto-synced via triggers. Indexes: title, content, source, type, status.
Ranking: BM25 (default).

### Kioku API (Python CLI)

All commands return JSON: `{"ok": true|false, ...}`.

#### `init`
```bash
python3 kioku.py --db DB_PATH init
```
Creates schema once. Safe to call repeatedly.

#### `store`
```bash
python3 kioku.py --db DB --source jira --source-id PROJ-123 \
  --type ticket --title "..." --content "..." \
  --status open --metadata '{"assignee":"alice"}'
```
Upserts by (source, source_id). Returns: `{"ok": true, "action": "upserted", "id": X}`.

#### `search`
```bash
python3 kioku.py --db DB --query "login authentication" --limit 10
```
BM25 full-text search. Returns:
```json
{
  "ok": true,
  "count": 3,
  "results": [
    {
      "id": 1,
      "source": "jira",
      "source_id": "PROJ-123",
      "type": "ticket",
      "title": "Fix login bug",
      "content": "...",
      "status": "open",
      "metadata": "{...}",
      "created_at": "...",
      "updated_at": "...",
      "rank": -0.847  // BM25 score (lower = more relevant)
    }
  ]
}
```

#### `get`
```bash
python3 kioku.py --db DB --source jira --source-id PROJ-123
```
Returns single item + all relationships (both inbound & outbound).

#### `link`
```bash
python3 kioku.py --db DB --from-source jira --from-id PROJ-10 \
  --to-source jira --to-id PROJ-123 --rel-type epic_to_story
```
Creates relationship. Safe to call repeatedly (unique constraint).

#### `delete`
```bash
python3 kioku.py --db DB --source jira --source-id PROJ-123
```
Removes item and all relationships.

### Key Implementation Details (kioku.py)

- **Language:** Python 3 stdlib only (sqlite3, argparse, json, datetime)
- **Database connection:** WAL mode for concurrency
- **FTS triggers:** Auto-sync FTS index on INSERT/UPDATE/DELETE
- **Error handling:** JSON responses with error messages
- **Idempotency:** store = INSERT ON CONFLICT DO UPDATE; link = INSERT OR IGNORE

---

## 3. PM-Sync-Jira Skill

### Purpose
Fetches Jira tickets (by project/JQL), enriches with full details, stores in kioku with relationships.

### Prerequisites
- Atlassian MCP connected (`searchJiraIssuesUsingJql`, `getJiraIssue`, `getVisibleJiraProjects`)
- Kioku initialized

### Workflow (6 Steps)

**Step 0:** Verify kioku DB exists. If not, auto-init.

**Step 1:** Parse user input into JQL:
- Project key: `project = ACME ORDER BY updated DESC`
- Custom JQL: use as-is
- Incremental: `project = ACME AND updated >= "2026-03-07"`

**Step 2:** Paginated fetch via searchJiraIssuesUsingJql:
- startAt=0, maxResults=50
- Loop until startAt + 50 >= total

**Step 3:** Enrich each ticket via getJiraIssue:
- Full description
- Issue links (blocks, relates, duplicates)
- Epic/parent field

**Step 4:** Store in kioku for each ticket:
```bash
python3 kioku.py --db .claude/kioku/pm.db store \
  --source jira --source-id PROJ-123 --type ticket \
  --title "Fix login bug" \
  --content "Description + acceptance criteria..." \
  --status open \
  --metadata '{
    "issue_type": "Story",
    "priority": "High",
    "labels": ["auth"],
    "components": ["Backend"],
    "assignee": "alice",
    "reporter": "bob",
    "project": "PROJ",
    "sprint": "Sprint 5",
    "created": "2026-01-15",
    "updated": "2026-03-07",
    "resolution": null
  }'
```

Status mapping (Jira → Kioku):
- `open`: Open, To Do, Backlog, New, Reopened, Selected for Development
- `in_progress`: In Progress, In Review, In QA, Code Review, Testing, Blocked
- `closed`: Done, Closed, Resolved, Released, Cancelled, Won't Do, Declined

**Step 5:** Create relationships for epic links & issue links:
```bash
python3 kioku.py --db .claude/kioku/pm.db link \
  --from-source jira --from-id PROJ-10 \
  --to-source jira --to-id PROJ-123 \
  --rel-type epic_to_story
```

Issue link type mapping:
- "blocks" / "is blocked by" → `blocks`
- "relates to" → `related_to`
- "duplicates" / "is duplicated by" → `duplicates`
- "clones" / "is cloned by" → `clones`

**Step 6:** Summary report with counts by type, warnings, next steps.

### Key Pattern: Two-Phase Sync
1. **Fetch & Store:** All tickets stored independently (safe to retry)
2. **Relationships:** Created after all items exist (ensures both sides present)

---

## 4. PM-Spec-to-Tickets Skill

### Purpose
Converts Notion specs → Jira epics + stories/tasks/bugs, with two human approval checkpoints.

### Workflow (7 Steps)

**Step 0:** Verify kioku DB. Ask user if not initialized.

**Step 1:** Resolve Notion page (URL or search).

**Step 2:** **Checkpoint 1** — Present spec summary, ask for approval.

**Step 3:** Get Jira context:
- Ask project key
- Fetch available projects
- Fetch field schemas for Epic/Story/Task/Bug

**Step 4:** Dedup check (if kioku available):
```bash
python3 kioku.py --db .claude/kioku/pm.db search --query "[feature title]" --limit 5
```
Flag similar existing tickets.

**Step 5:** **Checkpoint 2** — Present proposed tickets, ask for creation approval.

**Step 6:** Create tickets:
- Epic via createJiraIssue (includes Notion link in description)
- Stories/Tasks/Bugs linked to Epic
- Index each in kioku
- Create `spec_to_ticket` relationship in kioku

**Step 7:** Summary report.

### Key Pattern: Human-in-Loop
Two explicit approval checkpoints prevent automation mistakes. Dedup via kioku prevents duplicate ticket creation.

---

## 5. PM-Search Skill — Architecture & Patterns

### Status
**DOES NOT EXIST YET** — Ready for implementation.

### Proposed Function
Search across synced Jira/Notion/Slack data stored in kioku. Complement to pm-sync-jira (read vs. write).

### Design Opportunities

#### Option A: Simple CLI Wrapper
```bash
python3 kioku.py --db .claude/kioku/pm.db search --query "authentication" --limit 20
```
Skill would:
1. Check kioku DB initialized
2. Accept user query
3. Call kioku search command
4. Format & display results with rich details (relationships, metadata)
5. Offer follow-up actions (dedup, filter by status/type, etc.)

#### Option B: Advanced Search with Filters
Extend kioku.py search command with:
- `--source` filter: `jira`, `notion`, `slack`
- `--type` filter: `ticket`, `doc`, `spec`, `message`
- `--status` filter: `open`, `in_progress`, `closed`
- `--sort`: `relevance` (default) or `updated`

#### Option C: Relationship Explorer
Starting from a ticket, traverse relationships:
```bash
python3 kioku.py --db DB get-related --source jira --source-id PROJ-123
```
Returns: item + all inbound/outbound relationships with full item details.

### Recommended Implementation Pattern
1. SKILL.md: <150 lines, focus on use cases & examples
2. references/: query-syntax.md, filter-guide.md, relationship-types.md
3. No scripts needed (use kioku.py directly via CLI)
4. Return formatted markdown with tables, grouping by relationship type

### Integration with Existing Skills
- **Requires:** kioku initialized (checked automatically)
- **Input:** Queries synced by pm-sync-jira
- **Output:** Results feed into pm-spec-to-tickets dedup checks

---

## 6. Skills Convention & Best Practices

### SKILL.md Structure
```yaml
---
name: ck:skill-name          # kebab-case
description: <200 chars      # Specific triggers, not generic
argument-hint: "[optional]"  # E.g., "[query]"
license: MIT                 # Optional
---

# Skill Title

## Prerequisites
- List MCP/tools/config needed

## Workflow
- Step-by-step numbered guide
- Code blocks for commands
- Clear checkpoint/approval flow

## Error Handling
- Table of errors & actions

## References
- Links to bundled docs
```

### Key Patterns in Existing Skills

| Pattern | Example | Purpose |
|---------|---------|---------|
| **Initialization check** | pm-sync-jira Step 0 | Verify prerequisites (kioku, MCP) before work |
| **Paginated API loops** | pm-sync-jira Step 2 | Handle large datasets (startAt, maxResults, break condition) |
| **Two-phase operations** | pm-sync-jira fetch→store→link | Ensures data consistency (all items exist before linking) |
| **Human checkpoints** | pm-spec-to-tickets Steps 2, 5 | Critical approval gates for automation |
| **Dedup via search** | pm-spec-to-tickets Step 4 | Prevent duplicate creation using kioku search |
| **Metadata JSON** | pm-sync-jira metadata | Rich structured data alongside text (assignee, labels, priority) |
| **Status mapping** | pm-sync-jira jira-status-mapping.md | Domain-specific enum translation |

### References Convention
- One doc per concept (<150 lines each)
- Practical guides, not educational
- Linked in SKILL.md via grep patterns if large

### Skill Activation
- Named: `ck:{name}` (e.g., `ck:pm-sync-jira`)
- Auto-loads SKILL.md when mentioned with `@`
- No restart needed
- Craft Desktop: installed to `{workspace}/skills/{name}/SKILL.md`

---

## 7. Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SOURCES                             │
├──────────────────────┬──────────────────────┬──────────────────┤
│      JIRA            │     NOTION           │    SLACK         │
│  (MCPs+API)          │   (MCPs+API)         │  (MCPs+API)      │
└──────────────────────┴──────────────────────┴──────────────────┘
           ↓                    ↓                       ↓
    ┌──────────────────────────────────────────────────────┐
    │          PM-SYNC-JIRA (Fetch & Store)               │
    │          PM-SPEC-TO-TICKETS (Create)                │
    └──────────────────────────────────────────────────────┘
           ↓
    ┌──────────────────────────────────────────────────────┐
    │              KIOKU-LITE (SQLite)                     │
    │  .claude/kioku/pm.db                                 │
    │                                                       │
    │  Tables:                                             │
    │  • items (source, source_id, type, title, ...)      │
    │  • relationships (from→to, rel_type)                │
    │  • items_fts (FTS5 BM25 index)                       │
    └──────────────────────────────────────────────────────┘
           ↓
    ┌──────────────────────────────────────────────────────┐
    │          PM-SEARCH (Query & Explore)  [NEW]          │
    │          (Does not exist yet)                         │
    └──────────────────────────────────────────────────────┘
           ↓
    ┌──────────────────────────────────────────────────────┐
    │              USER INTERFACE                          │
    │  Rich markdown tables, relationships, metadata       │
    └──────────────────────────────────────────────────────┘
```

---

## 8. Key Files Reference

| Path | Type | Purpose |
|------|------|---------|
| `.claude/skills/kioku-lite/SKILL.md` | Skill | User guide to kioku commands |
| `.claude/skills/kioku-lite/scripts/kioku.py` | Python CLI | Core knowledge base engine |
| `.claude/skills/kioku-lite/references/schema.md` | Reference | Database schema documentation |
| `.claude/skills/pm-sync-jira/SKILL.md` | Skill | Workflow for syncing Jira |
| `.claude/skills/pm-sync-jira/references/jira-status-mapping.md` | Reference | Status enum translation |
| `.claude/skills/pm-sync-jira/references/example-output.md` | Reference | Example sync session |
| `.claude/skills/pm-spec-to-tickets/SKILL.md` | Skill | Workflow for Notion→Jira |
| `.claude/skills/pm-spec-to-tickets/references/jira-field-mapping.md` | Reference | Spec→Jira field mapping |
| `.claude/skills/skill-creator/references/skill-anatomy-and-requirements.md` | Reference | Skill structure standards |

---

## 9. PM-Search Skill Readiness Assessment

### Prerequisites to Build PM-Search

✓ **Kioku-lite fully functional**
- Schema stable, CLI complete
- BM25 search ranking works
- Relationship tracking implemented

✓ **pm-sync-jira populates kioku**
- Jira tickets stored with metadata
- Relationships created (epic→story, blocks, etc.)
- Proven two-phase pattern

✓ **pm-spec-to-tickets creates data**
- Notion specs converted to Jira
- spec_to_ticket relationships tracked
- Dedup searches already use kioku

✓ **Skill conventions established**
- Template patterns clear
- SKILL.md + references structure proven
- Error handling patterns documented

### What PM-Search Should Do

1. **Basic search:** Query kioku BM25 across all sources
2. **Filtered search:** By source (jira/notion/slack), type, status
3. **Relationship exploration:** Show related tickets
4. **Dedup detection:** Flag similar items
5. **Rich output:** Format as markdown tables with metadata

### No Scripts Needed
- Reuse kioku.py CLI directly
- Skill focuses on workflow/formatting
- References provide query syntax guide

---

## 10. Token Efficiency Patterns

### Progressive Disclosure
1. **Metadata** (~200 chars) — always in context
2. **SKILL.md** (<150 lines) — loaded when skill activated
3. **References** — loaded as-needed
4. **Scripts** — executed without loading to context (except error output)

### Kioku-Lite Pattern
- No embedding vectors (uses BM25, not AI search)
- Local SQLite (no API calls for search)
- Deterministic results (debugging & reproducibility)

### Data Deduplication
- Kioku upsert by (source, source_id) prevents duplicates
- Relationship unique constraints prevent duplicate links
- Search dedup check before ticket creation

---

## Unresolved Questions

None. Codebase structure is clear and well-documented.

---

## Recommendations

1. **Implement pm-search skill** using Option B (advanced filters) or hybrid approach
2. **Keep it CLI-focused** — reuse kioku.py, don't rewrite search logic
3. **Add relationship explorer** — traversing epic→stories is high-value for project mgmt
4. **Create references/** with:
   - `query-syntax.md` — Examples of BM25 queries
   - `filter-guide.md` — Source/type/status filter combinations
   - `relationship-types.md` — All supported rel_types and use cases
5. **Integration test** — pm-sync-jira (populate) → pm-search (query) → pm-spec-to-tickets (dedup)

