---
phase: 3
title: Testing & Validation
status: partial
priority: P1
effort: 30m
---

# Phase 3: Testing & Validation

## Context

- Depends on: Phase 1 (kioku-lite) + Phase 2 (SKILL.md)
- Goal: Verify the skill works end-to-end with a real Notion spec

## Overview

Test the `pm-spec-to-tickets` skill by running it against a real Notion page. Validate both checkpoint flows, Jira ticket creation, and Kioku indexing.

## Test Plan

### Test 1: Kioku Lite Smoke Test
1. [x] Run `kioku.py init` -- verify DB created at `.claude/kioku/pm.db`
2. [x] Run `kioku.py store` with sample item -- verify insertion
3. [x] Run `kioku.py store` same item again -- verify upsert (no duplicate)
4. [x] Run `kioku.py search` -- verify FTS5 returns relevant results
5. [x] Run `kioku.py link` -- verify relationship created
6. [x] Run `kioku.py get` -- verify retrieval

### Test 2: MCP Tool Availability
1. [ ] Call `getVisibleJiraProjects` -- verify Jira MCP responds
2. [ ] Call `notion-search` with a known page -- verify Notion MCP responds
3. [ ] Document actual tool names if they differ from spec
**Status: Pending -- requires live Notion/Jira MCP connections**

### Test 3: Full Skill Flow (Manual)
1. [ ] Activate `@pm-spec-to-tickets` with a real Notion page URL
2. [ ] Verify Checkpoint 1: agent presents structured spec summary, waits for approval
3. [ ] Approve with minor adjustments, verify agent incorporates them
4. [ ] Verify Checkpoint 2: agent proposes epic + stories, waits for approval
5. [ ] Approve ticket creation
6. [ ] Verify tickets created in Jira with correct fields
7. [ ] Verify items indexed in Kioku
8. [ ] Verify relationships (spec -> epic, epic -> stories) in Kioku
**Status: Pending -- requires live end-to-end test with real Notion/Jira**

### Test 4: Edge Cases
1. [ ] Ambiguous Notion search (multiple results) -- agent should ask to disambiguate
2. [ ] Empty/minimal spec -- agent should flag insufficient content
3. [ ] Kioku DB not initialized -- skill should proceed without dedup, warn user
4. [ ] Very large spec -- agent should break into multiple epics or paginate
**Status: Pending -- requires live end-to-end test with edge case scenarios**

## Validation Checklist

- [ ] Skill activates correctly via `@pm-spec-to-tickets`
- [ ] Notion content read successfully
- [ ] Checkpoint 1 output is structured and actionable
- [ ] Checkpoint 2 output shows clear ticket breakdown
- [ ] Jira tickets created with correct hierarchy (Epic -> Stories)
- [ ] Kioku stores and links items correctly
- [ ] Error cases handled gracefully (no crashes, clear messages)

## Success Criteria

- Skill completes full flow: Notion -> Checkpoint 1 -> Checkpoint 2 -> Jira tickets
- Created tickets have meaningful descriptions, not just titles
- Dedup check works when Kioku has existing data
- Skill degrades gracefully when Kioku is unavailable

## Post-Validation

- [ ] Fix any issues discovered during testing
- [ ] Update SKILL.md if instructions were ambiguous
- [ ] Update MCP tool names if they differed from documentation
- [ ] Document any Notion page format quirks in references
