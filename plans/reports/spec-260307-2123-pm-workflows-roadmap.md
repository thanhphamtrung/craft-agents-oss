# PM Workflows — Product Spec

**Project:** Craft Agents — PM Automation
**Date:** 2026-03-07
**Status:** Draft
**Owner:** Thanh Pham

---

## Problem

Solo PM managing across Jira, Notion, and Slack. Constant context switching, manual status syncing, duplicate tickets, and time-consuming reports. All 3 tools already connected as MCP sources in Craft Agents.

## Goal

Build 5 Claude Code skills that automate PM workflows using Jira, Notion, and Slack MCPs — backed by a local Kioku Lite knowledge base for dedup, search, and cross-tool correlation.

## Architecture

**Core layer:** Kioku Lite (SQLite) as unified index. Tri-hybrid search (BM25 + vector + knowledge graph). All workflows query Kioku instead of hitting APIs directly.

**Sync strategy:** On-demand, idempotent (upsert by source ID). No crons for sync — user triggers manually.

**Data schema per item:**
- `source` — jira | slack | notion
- `source_id` — unique ID from source (e.g. PROJ-123, thread ts, page id)
- `type` — ticket | message | doc | spec
- `title` — searchable title
- `content` — full text for search
- `status` — open | closed | in_progress | etc.
- `metadata` — JSON (assignee, labels, channel, dates)
- `relationships` — links between items (ticket→spec, thread→ticket)

---

## Workflows (in build order)

### Phase 1: Spec → Tickets

**Skill name:** `pm-spec-to-tickets`
**Trigger:** On-demand — "create tickets from this spec"

**What it does:**
1. Read a Notion page via Notion MCP (user provides URL or page ID)
2. Extract requirements, features, and acceptance criteria from the spec
3. Search Kioku for existing related tickets (avoid duplicates)
4. Propose an epic + stories structure (show what already exists vs. new)
5. User reviews and approves the proposed tickets
6. On approval → create epic + stories in Jira via Jira MCP
7. Index new tickets in Kioku, link back to the Notion spec

**Inputs:** Notion page URL or ID, target Jira project key
**Outputs:** Created Jira epic + stories, confirmation summary

**Acceptance criteria:**
- Correctly parses spec into logical stories with clear titles and descriptions
- Detects and flags overlap with existing Jira tickets
- Two-checkpoint approval: (1) proposed structure, (2) before Jira creation
- Created tickets have proper epic links and labels
- All created tickets indexed in Kioku with spec relationship

---

### Phase 2: Knowledge Base Foundation + Jira Sync

**Skill name:** `pm-sync-jira`
**Trigger:** On-demand — "sync Jira tickets"

**What it does:**
1. Call Jira MCP → fetch tickets (by project, filter, or all)
2. For each ticket: upsert into Kioku (keyed by ticket key)
3. Store relationships (epic→stories, linked issues)
4. Report summary: N synced, N new, N updated

**Jira fields to index:** Key, Summary, Description, Status, Issue Type, Priority, Labels, Components, Assignee, Created/Updated dates, Epic link, Related issues

**Acceptance criteria:**
- All target Jira tickets indexed with full metadata
- Sync is idempotent — re-running doesn't create duplicates
- Incremental sync support (filter by `updated_after`)
- Summary report after each sync

---

### Phase 3: Cross-Tool Search

**Skill name:** `pm-search`
**Trigger:** On-demand — "what's the status of payment refund?"

**What it does:**
1. Take a natural language query from user
2. Search Kioku across all indexed sources (Jira, Slack, Notion)
3. Return unified results with source, type, status, and direct links
4. Synthesize a summary answer from the results

**Acceptance criteria:**
- Returns results from all indexed sources in a single query
- Results ranked by relevance (semantic, not just keyword)
- Each result includes source link for quick navigation
- Handles queries about status, ownership, history, and relationships

---

### Phase 4: Smart Bug Triage

**Skill name:** `pm-triage`
**Trigger:** On-demand — user pastes a bug report or points to a Slack message

**What it does:**
1. Read bug report (from Slack message or direct input)
2. Search Kioku for similar existing tickets (vector + BM25)
3. If match found:
   - Closed ticket → suggest reopen, show original
   - Open ticket → suggest adding comment with new context
   - Present candidates for user confirmation
4. If no match → create new Jira ticket, index in Kioku
5. Post result back to Slack thread (if source was Slack)

**Acceptance criteria:**
- Finds semantically similar tickets ("login broken on iOS" matches "auth fails on mobile Safari")
- Similarity threshold tunable, always requires user confirmation
- Created tickets include Slack thread link as context
- Slack reply posted with ticket link

---

### Phase 5: Daily Standup & Reports

**Skill name:** `pm-standup`
**Trigger:** On-demand or scheduled (daily cron)

**What it does:**
1. Query Kioku for tickets changed in last 24h
2. Query Slack MCP for key channel activity (configurable channels)
3. Generate standup report: Done, In Progress, Blockers
4. Post to designated Slack channel

**Acceptance criteria:**
- Report covers ticket movements + Slack highlights
- Grouped by: completed, in progress, blocked
- Mentions relevant people and ticket links
- Clean, scannable format suitable for Slack

---

## Dependencies Between Phases

```
Phase 1 (Spec→Tickets) — standalone, uses Notion + Jira MCPs directly
    ↓
Phase 2 (Jira Sync) — indexes tickets created by Phase 1 + existing tickets
    ↓
Phase 3 (Search) — requires Kioku populated by Phase 2
    ↓
Phase 4 (Triage) — requires search from Phase 3 for dedup
    ↓
Phase 5 (Standup) — requires Kioku data from Phase 2 + Slack MCP
```

Phase 1 can start immediately (no Kioku dependency for v1). Phases 2-5 build on each other.

---

## Risks

| Risk | Mitigation |
|------|------------|
| Kioku vector search quality for dedup | Tune similarity threshold, require user confirmation |
| Stale data from on-demand sync | Show "last synced X ago", easy re-sync command |
| Jira API rate limits on large projects | Paginate, sync incrementally |
| Mixed Notion doc formats | Handle in skill prompt, let agent adapt per doc |

## Open Questions

1. Which Jira project key(s) to target?
2. Which Slack channels to index for Layer 2?
3. Kioku similarity threshold — needs tuning after initial data load
4. Should triage auto-create tickets or always confirm first?
