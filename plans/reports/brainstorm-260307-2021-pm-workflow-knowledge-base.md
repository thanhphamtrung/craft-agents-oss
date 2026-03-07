# Brainstorm: PM Full Workflow with Knowledge Base

**Date:** 2026-03-07
**Status:** Agreed
**Scope:** Full PM workflow using Craft Agents + Jira + Notion + Slack + Kioku Lite

---

## Problem Statement

Solo PM managing project across 3 tools (Jira, Notion, Slack) with constant context switching, manual status syncing, duplicate ticket creation, and time-consuming report generation. All 3 tools already connected as MCP sources in Craft Agents.

## Requirements

1. **Smart Bug Triage** — Slack bugs → Jira with dedup (reopen if exists, create if not)
2. **Daily Standup & Reports** — Auto-generate from Jira + Slack activity
3. **Spec → Tickets** — Notion PRDs/notes → Jira epics + stories
4. **Cross-Tool Search** — Unified query across all 3 tools
5. **Status Sync** — Keep Jira, Notion, Slack in sync on project status
6. **Dedup Intelligence** — Fuzzy match existing tickets to prevent duplicates

## Agreed Architecture

### Kioku Lite as Unified Knowledge Base

All workflows query a **local Kioku Lite SQLite database** instead of hitting APIs directly. Tri-hybrid search (BM25 + vector + knowledge graph) enables:
- Semantic dedup ("login broken on iOS" matches "auth fails on mobile Safari")
- Cross-tool correlation (ticket ↔ spec ↔ Slack thread)
- Fast local queries without API latency
- Relationship tracking via knowledge graph

### Layered Build Approach

| Layer | Data Source | What's Indexed | Value Unlocked |
|-------|-----------|---------------|----------------|
| **1** | Jira | Tickets (id, title, description, status, assignee, labels, components) | Bug dedup, ticket search, status queries |
| **2** | Slack | Thread summaries from key channels (#bugs, #general, #dev) | Context enrichment, triage source, standup data |
| **3** | Notion | Specs, PRDs, meeting notes (page id, title, content, properties) | Spec→ticket flow, cross-tool search |

### Sync Strategy: On-Demand

- User triggers sync manually ("sync Jira tickets", "sync Slack #bugs")
- No scheduled crons — keeps system simple, avoids staleness complexity
- Each sync is idempotent (upsert by source ID)
- Sync skill reports: N new, N updated, N unchanged

### Data Schema (Kioku)

Each indexed item stored with:
- `source`: jira | slack | notion
- `source_id`: unique ID from source system (e.g., PROJ-123, slack thread ts, notion page id)
- `type`: ticket | message | doc | spec
- `title`: searchable title
- `content`: full text for vector + BM25 search
- `status`: open | closed | in_progress | etc.
- `metadata`: JSON blob (assignee, labels, channel, created_at, updated_at)
- `relationships`: links to related items (ticket→spec, thread→ticket)

---

## 5 Workflows (Build Order)

### Workflow 1: Knowledge Base Foundation + Jira Sync (Layer 1)
**Type:** Craft Skill
**Trigger:** On-demand ("sync Jira tickets")
**Flow:**
1. Skill calls Jira MCP → fetch all tickets (or by project/filter)
2. For each ticket: upsert into Kioku (source_id = ticket key)
3. Store relationships (epic→stories, linked issues)
4. Report summary: N synced, N new, N updated

### Workflow 2: Smart Bug Triage
**Type:** Craft Skill + Automation (Slack channel watch)
**Trigger:** On-demand prompt OR automation on #bugs channel
**Flow:**
1. Read bug report from Slack message
2. Search Kioku for similar tickets (vector + BM25)
3. If match found (above threshold):
   - If closed → suggest reopen, show original ticket
   - If open → suggest adding comment with new context
   - Present candidates for user confirmation
4. If no match → create new Jira ticket, index in Kioku
5. Post result back to Slack thread

### Workflow 3: Daily Standup & Reports
**Type:** Craft Skill + Automation (cron)
**Trigger:** Scheduled (daily 9am) or on-demand
**Flow:**
1. Query Kioku for tickets changed in last 24h
2. Query Slack MCP for key channel activity
3. Generate standup: done, in progress, blockers
4. Post to designated Slack channel

### Workflow 4: Spec → Tickets
**Type:** Craft Skill
**Trigger:** On-demand ("create tickets from this spec")
**Flow:**
1. Read Notion page via Notion MCP
2. Index in Kioku (Layer 3)
3. Extract requirements/features from spec
4. Search Kioku for existing related tickets
5. Propose epic + stories (show diff from existing)
6. On approval → create in Jira, index in Kioku, link to spec

### Workflow 5: Cross-Tool Search
**Type:** Craft Skill
**Trigger:** On-demand ("what's the status of payment refund?")
**Flow:**
1. Search Kioku across all indexed sources
2. Return unified results with source links
3. Synthesize summary answer

---

## Implementation Plan: Layer 1 (Jira → Kioku)

### What to Build

1. **`pm-sync-jira` skill** — Fetches Jira tickets, upserts into Kioku
2. **`pm-search` skill** — Searches Kioku knowledge base, returns results
3. **`pm-triage` skill** — Takes bug description, finds duplicates, creates/reopens ticket

### Kioku Setup
- Use existing `kioku-lite` skill (already available)
- SQLite database at workspace level
- Categories: `jira-ticket`, `slack-thread`, `notion-doc`

### Jira Fields to Index
- Key (PROJ-123)
- Summary (title)
- Description (full text)
- Status (To Do, In Progress, Done)
- Issue Type (Bug, Story, Epic, Task)
- Priority
- Labels
- Components
- Assignee
- Created/Updated dates
- Links (epic link, related issues)

### Success Criteria
- [ ] Jira tickets indexed in Kioku with full metadata
- [ ] Search finds semantically similar tickets (not just keyword match)
- [ ] Dedup correctly identifies "same bug, different words" cases
- [ ] Sync is idempotent (re-running doesn't create duplicates)
- [ ] Triage flow: Slack bug → search → create or reopen → Slack reply

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Kioku vector search quality for ticket dedup | May miss or false-match | Tune similarity threshold, require user confirmation |
| Stale data (on-demand sync) | Agent works with outdated info | Clear messaging: "last synced 2h ago", easy re-sync |
| Jira API rate limits | Sync may be slow for large projects | Paginate, sync incrementally (updated_after) |
| Mixed Notion formats | Spec extraction may be inconsistent | Handle in skill prompt, let agent adapt per doc |

## Unresolved Questions

1. What Jira project key to target? (or all projects?)
2. Which Slack channels should be indexed in Layer 2?
3. Kioku similarity threshold for dedup — needs tuning after initial data load
4. Should triage auto-create tickets or always confirm with you first?
