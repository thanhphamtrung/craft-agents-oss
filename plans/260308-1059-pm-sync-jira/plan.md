---
title: "pm-sync-jira: Jira-to-Kioku Sync Skill"
description: "Craft skill that fetches Jira tickets via MCP and upserts them into Kioku knowledge base with relationships"
status: pending
priority: P1
effort: 2h
branch: main
tags: [skill, jira, kioku, sync, pm]
created: 2026-03-08
---

# pm-sync-jira Implementation Plan

## Overview

Pure prompt-orchestration skill (no Python scripts). Calls Jira MCP to fetch tickets, pipes each through `kioku.py` CLI to store/link. Follows `pm-spec-to-tickets` conventions.

## Deliverables

| File | Purpose |
|------|---------|
| `.claude/skills/pm-sync-jira/SKILL.md` | Main skill prompt |
| `.claude/skills/pm-sync-jira/references/jira-status-mapping.md` | Status mapping guide |
| `.claude/skills/pm-sync-jira/references/example-output.md` | Example sync output |

## Phases

| # | Phase | Status | Effort |
|---|-------|--------|--------|
| 1 | Write SKILL.md | pending | 1h |
| 2 | Write reference docs | pending | 30m |
| 3 | Manual testing & iteration | pending | 30m |

## Key Decisions

- No Python — pure SKILL.md prompt orchestration
- User provides project key or JQL; no hardcoded defaults
- Jira MCP `searchJiraIssuesUsingJql` returns ~50/page; skill loops with `startAt`
- Status mapping flexible: reference doc provides defaults, user can override
- Incremental sync via `updated >= "YYYY-MM-DD"` JQL clause
- Relationships: `epic_to_story` for epic links, `related_to` for issue links

## Dependencies

- Kioku Lite (exists at `.claude/skills/kioku-lite/`)
- Jira MCP (Atlassian tools available)

## Details

See [Phase 1](./phase-01-write-skill-md.md) and [Phase 2](./phase-02-write-references.md).
