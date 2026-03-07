# Jira Field Mapping

How Notion spec sections map to Jira issue fields.

## Epic Fields

| Jira Field | Source |
|------------|--------|
| Summary | Spec page title |
| Description | Spec overview/summary + Notion page link |
| Labels | Extracted from spec (e.g., "auth", "api", "frontend") |
| Components | Inferred from spec scope (if project has components) |
| Priority | User-specified or default to Medium |

## Story Fields

| Jira Field | Source |
|------------|--------|
| Summary | Feature/requirement name from spec |
| Description | Detailed requirement text from spec section |
| Acceptance Criteria | Extracted from spec or inferred from requirements |
| Labels | Inherited from Epic + specific to story |
| Story Points | Not set (leave for team estimation) |
| Epic Link | Parent Epic key |

## Description Template (Epic)

```
## Overview
[Spec summary paragraph]

## Source
[Notion page title](notion-url)

## Requirements
1. [req 1]
2. [req 2]
...

## Out of Scope
[excluded items from spec]
```

## Description Template (Story)

```
## Context
Part of Epic: [EPIC-KEY] — [epic title]

## Requirement
[detailed requirement from spec]

## Acceptance Criteria
- [ ] [criterion 1]
- [ ] [criterion 2]

## Technical Notes
[any implementation hints from spec]
```

## Notes

- Do NOT set assignee or sprint — leave for team to decide
- Set priority only if spec explicitly states it
- Include Notion page link in Epic description for traceability
- If spec has diagrams/images, reference them by URL in description
