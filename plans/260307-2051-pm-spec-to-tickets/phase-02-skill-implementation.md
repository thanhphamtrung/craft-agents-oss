---
phase: 2
title: pm-spec-to-tickets SKILL.md Implementation
status: done
priority: P1
effort: 1h
---

# Phase 2: pm-spec-to-tickets SKILL.md

## Context

- Brainstorm: `plans/reports/brainstorm-260307-2021-pm-workflow-knowledge-base.md`
- Depends on: Phase 1 (kioku-lite setup)
- Reference skills: `use-mcp`, `brainstorm`, `project-management` for format patterns
- Skill format: YAML frontmatter + markdown instructions (<150 lines)

## Overview

Write the `pm-spec-to-tickets` SKILL.md -- a markdown instruction file that guides agents through the two-checkpoint flow: read Notion spec, get user approval on interpretation, propose tickets, get approval, create in Jira + index in Kioku.

## Key Insights

- This is a PROMPT, not code. Quality depends on clear, unambiguous instructions.
- Two-checkpoint design prevents the agent from creating wrong tickets silently.
- MCP tools are already available -- skill just needs to reference correct tool names.
- Kioku dedup is a "nice-to-have" guard, not a blocker. Skill should work even if Kioku DB is empty.
- Must handle: user provides Notion URL, page name, or search query.

## File Structure

```
.claude/skills/pm-spec-to-tickets/
  SKILL.md              -- Core skill instructions
  references/
    jira-field-mapping.md   -- How spec sections map to Jira fields
    example-output.md       -- Example checkpoint outputs for consistency
```

## SKILL.md Outline

```yaml
---
name: ck:pm-spec-to-tickets
description: "Read Notion specs and create Jira epics + stories with two-checkpoint approval flow. Use for converting PRDs, feature specs, or requirements docs into actionable Jira tickets."
argument-hint: "[Notion URL, page name, or search query]"
---
```

### Sections to Include

1. **When to Use** -- Converting specs/PRDs/notes to Jira tickets
2. **Prerequisites** -- Notion MCP, Atlassian MCP connected; kioku-lite initialized (optional)
3. **Workflow** (the core instruction set):

#### Step 1: Resolve Notion Page
- If URL provided: use `notion-fetch` with URL
- If page name: use `notion-search` to find, confirm with user if ambiguous
- Extract full page content

#### Step 2: Checkpoint 1 -- Spec Review
Present structured summary to user:
- **Spec Title**: from page
- **Features/Requirements**: numbered list extracted from content
- **Scope**: what's included vs excluded
- **Ambiguities**: anything unclear, missing acceptance criteria, undefined terms
- **Dependencies**: external systems, APIs, other features mentioned
- Ask: "Is this interpretation correct? Anything to add, remove, or clarify?"
- WAIT for user response. Do not proceed without approval.
- If user adjusts: incorporate changes into working interpretation.

#### Step 3: Discover Jira Context
- Ask user for Jira project key (no hardcoded default)
- Use `getVisibleJiraProjects` to list available projects for reference
- Use `getJiraProjectIssueTypesMetadata` to get available issue types
- Use `getJiraIssueTypeMetaWithFields` to get fields for Epic and Story types

#### Step 4: Dedup Check (if Kioku available)
- Search kioku for each proposed feature/requirement title
- Flag any matches above threshold
- Present dedup warnings: "Similar ticket exists: PROJ-123 -- Fix login flow"

#### Step 5: Checkpoint 2 -- Ticket Proposal
Present proposed tickets:
```
Epic: [Title from spec]
  Description: [Summary + link to Notion page]

  Story 1: [Feature/requirement name]
    Description: [Detailed from spec]
    Acceptance Criteria: [Extracted or inferred]

  Story 2: ...

  [Dedup warnings if any]
```
- Ask: "Create these tickets? Any changes needed?"
- WAIT for user response.

#### Step 6: Create Tickets
- Create Epic via `createJiraIssue`
- Create Stories linked to Epic via `createJiraIssue`
- Index each in Kioku via `kioku.py store`
- Link Notion page to Epic in Kioku via `kioku.py link`
- Report created ticket keys with links

#### Step 7: Summary
- List all created tickets (key, title, type)
- Confirm Kioku indexing status
- Suggest next steps (assign, prioritize, add to sprint)

4. **Error Handling** -- What to do if Notion page not found, Jira project not accessible, etc.
5. **Security** -- Standard scope declaration + never expose credentials

## Implementation Steps

1. [x] Create directory: `.claude/skills/pm-spec-to-tickets/`
2. [x] Create `references/jira-field-mapping.md` -- Map spec sections to Jira fields (summary, description, acceptance criteria, labels, components, priority)
3. [x] Create `references/example-output.md` -- Example of Checkpoint 1 and Checkpoint 2 outputs for consistency
4. [x] Write `SKILL.md` -- Full skill instructions following outline above
5. [x] Review: ensure SKILL.md is under 150 lines (use references for overflow)
6. [x] Verify all MCP tool names are correct: `notion-fetch`, `notion-search`, `createJiraIssue`, `getVisibleJiraProjects`, `getJiraProjectIssueTypesMetadata`, `getJiraIssueTypeMetaWithFields`

## MCP Tool Reference

### Notion
| Tool | Usage |
|------|-------|
| `notion-fetch` | Read page content by URL |
| `notion-search` | Search pages by title/query |
| `notion-get-page` | Get page by ID |

### Jira (Atlassian)
| Tool | Usage |
|------|-------|
| `getVisibleJiraProjects` | List accessible projects |
| `getJiraProjectIssueTypesMetadata` | Get issue types for a project |
| `getJiraIssueTypeMetaWithFields` | Get fields for a specific issue type |
| `createJiraIssue` | Create ticket (Epic, Story, etc.) |
| `searchJiraIssuesUsingJql` | Search existing tickets (backup dedup) |

### Kioku
| Command | Usage |
|---------|-------|
| `kioku.py search` | Dedup check against existing indexed items |
| `kioku.py store` | Index newly created tickets |
| `kioku.py link` | Create spec-to-ticket relationships |

## Success Criteria

- [x] SKILL.md follows Craft Agents format (frontmatter, <150 lines)
- [x] Two-checkpoint flow is clearly described with explicit WAIT instructions
- [x] All MCP tool names are correct and usage is specified
- [x] Kioku integration is optional/graceful (works without kioku DB)
- [x] References provide enough detail without bloating SKILL.md
- [x] Another agent can execute the skill without additional guidance

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| MCP tool names may differ from docs | Verify by calling `getVisibleJiraProjects` and `notion-search` during testing |
| Notion page structure varies wildly | Skill instructions should be flexible: "extract requirements however structured" |
| User may not know Jira project key | Step 3 discovers available projects dynamically |
| Spec too large for single ticket breakdown | Instruct agent to break into multiple epics if scope warrants |
