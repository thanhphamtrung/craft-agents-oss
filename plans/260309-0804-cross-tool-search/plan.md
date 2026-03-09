---
title: "Cross-Tool Search Skill (pm-search)"
description: "SKILL.md-only skill for unified search across Jira/Slack/Notion via kioku-lite CLI"
status: complete
priority: P2
effort: 1.5h
branch: main
tags: [pm, skill, search, kioku]
created: 2026-03-09
---

# Cross-Tool Search Skill (pm-search)

## Overview

Pure SKILL.md skill that teaches the agent how to search across all PM sources (Jira, Slack, Notion) using existing kioku-lite CLI. No new scripts needed — just workflow instructions.

## Phases

| Phase | Description | Status | Effort |
|-------|-------------|--------|--------|
| 1 | Add search filters to kioku.py | Complete | 45min |
| 2 | Create pm-search SKILL.md | Complete | 45min |

## Key Decision

**kioku.py search currently lacks `--source`, `--type`, `--status` filters.** The brainstorm spec assumes these exist. Phase 1 adds them to kioku.py before building the skill.

## Dependencies

- kioku-lite skill (exists)
- `.claude/kioku/pm.db` (created by pm-sync-jira)

## Files

- **Modify:** `.claude/skills/kioku-lite/scripts/kioku.py` (add search filters)
- **Create:** `.claude/skills/pm-search/SKILL.md`
