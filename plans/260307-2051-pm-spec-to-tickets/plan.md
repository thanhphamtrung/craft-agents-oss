---
title: "pm-spec-to-tickets Craft Agents Skill"
description: "Skill that reads Notion specs and creates Jira epics + stories with two-checkpoint approval flow"
status: in-progress
priority: P1
effort: 2h
branch: main
tags: [pm-workflow, skill, jira, notion, kioku]
created: 2026-03-07
---

# pm-spec-to-tickets Skill

Build a Craft Agents skill at `.claude/skills/pm-spec-to-tickets/SKILL.md` that reads Notion specs, extracts requirements, and creates Jira epics + stories via a two-checkpoint human-in-the-loop flow.

## Phases

| # | Phase | Status | Effort | File |
|---|-------|--------|--------|------|
| 1 | Kioku Lite Setup | done | 30m | [phase-01](./phase-01-kioku-lite-setup.md) |
| 2 | SKILL.md Implementation | done | 1h | [phase-02](./phase-02-skill-implementation.md) |
| 3 | Testing & Validation | partial | 30m | [phase-03](./phase-03-testing-validation.md) |

## Resolved Questions

1. **Jira project key** -- Skill asks user at runtime. No hardcoded default.
2. **Kioku DB location** -- Default `.claude/kioku/pm.db`. Skill asks user yes/no to confirm or override.
3. **Notion page format variance** -- Agent handles it. Skill instructions say "extract requirements however structured."

## Key Dependencies

- Atlassian MCP (Jira) -- already connected
- Notion MCP -- already connected
- Kioku Lite -- does NOT exist yet, must be set up in Phase 1
- No Jira board data yet -- this skill bootstraps ticket creation

## Architecture

```
User: @pm-spec-to-tickets [Notion URL]
  |
  v
[Checkpoint 1: Spec Review]
  Agent reads Notion page -> structured summary
  User confirms/adjusts interpretation
  |
  v
[Checkpoint 2: Ticket Proposal]
  Agent proposes epic + stories
  Dedup check via Kioku (if data exists)
  User approves ticket creation
  |
  v
[Create in Jira + Index in Kioku]
```
