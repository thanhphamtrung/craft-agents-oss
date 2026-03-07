# Jira Field Mapping

How Notion spec sections map to Jira issue fields.

## Epic Fields

| Jira Field | Source |
|------------|--------|
| Summary | Spec page title (concise, actionable) |
| Description | Structured from spec sections (see template below) |
| Labels | Extracted from spec (e.g., "auth", "api", "frontend") |
| Components | Inferred from spec scope (if project has components) |
| Priority | User-specified or default to Medium |
| Fix Version | From spec timeline/phase if specified |

## Story Fields

| Jira Field | Source |
|------------|--------|
| Summary | Feature/requirement name from spec (concise, actionable) |
| Description | Structured from spec sections (see template below) |
| Acceptance Criteria | Extracted from spec or inferred — must be specific and testable |
| Labels | Inherited from Epic + specific to story |
| Story Points | Not set (leave for team estimation) |
| Epic Link | Parent Epic key |

## Description Template (Epic)

```
## Objective
[Clear, concise statement of what this epic aims to achieve]

## Context
[Background information — why this work matters, what problem it solves,
any relevant history or motivation]

## Scope

**Included:**
- [item 1]
- [item 2]
- ...

**Not Included:**
- [excluded item 1]
- [excluded item 2]
- ...

## Success Criteria
- [measurable criterion 1]
- [measurable criterion 2]
- ...

## Risks & Dependencies
- [risk or dependency 1]
- [risk or dependency 2]
- ...

## Other Information
[Architecture notes, technical constraints, integration details,
diagrams, or any additional context from the spec]

## Source
[Notion page title](notion-url)
```

## Description Template (Story)

```
## User Story
As a [role], when [situation/trigger], I want to [action]
so that [outcome/value].

## Context
Part of Epic: [EPIC-KEY] — [epic title]
[Background — why this story exists, what problem it addresses]

## Acceptance Criteria
- [ ] [criterion 1 — specific, testable]
- [ ] [criterion 2 — specific, testable]
- ...

## Other Information
- Inputs: [what this story consumes — data, APIs, user actions]
- Outputs: [what this story produces — UI changes, API responses, side effects]
- Dependencies: [blockers, related stories, external services]
- Spec: [link to relevant section in Notion if applicable]
```

## Task Fields

| Jira Field | Source |
|------------|--------|
| Summary | Task name — action-oriented, describes the work (concise) |
| Description | Structured from spec sections (see template below) |
| Labels | Inherited from Epic + specific to task |
| Epic Link | Parent Epic key (if part of an epic) |
| Priority | User-specified or default to Medium |

## Description Template (Task)

```
## Summary
[Clear, concise description of the work to be done]

## Context
Part of Epic: [EPIC-KEY] — [epic title]
[Background — why this task is needed, what it enables]

## Acceptance Criteria
- [ ] [criterion 1 — specific, verifiable]
- [ ] [criterion 2 — specific, verifiable]
- ...

## Other Information
- Inputs: [what this task consumes — data, configs, specs]
- Outputs: [what this task produces — artifacts, changes, deliverables]
- Dependencies: [blockers, related tasks, external services]
- Spec: [link to relevant section in Notion if applicable]
```

## Bug Fields

| Jira Field | Source |
|------------|--------|
| Summary | Bug title — concise description of the defect |
| Description | Structured from report sections (see template below) |
| Labels | Component area + "bug" |
| Priority | Based on impact severity (Critical/High/Medium/Low) |
| Epic Link | Parent Epic key (if related to an epic) |
| Affects Version | Version where bug was observed |

## Description Template (Bug)

```
## Impact
[Who is affected and how — business impact, user experience degradation,
data accuracy issues]

## Expected Behaviour
[What should happen under normal conditions]

## Actual Behaviour
[What actually happens — be specific about symptoms and frequency]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]
4. [Observe the issue]

## Environment
[App version, platform, OS, browser, user account, relevant config]

## Workarounds
[Any known workarounds, or "N/A" if none]

## Other Information
[Screenshots, logs, patterns observed, frequency notes,
related tickets, or any additional context]
```

## Notes

- Do NOT set assignee or sprint — leave for team to decide
- Set priority only if spec explicitly states it
- Include Notion page link in Epic description for traceability
- If spec has diagrams/images, reference them by URL in description
- Use **Story** for user-facing features (has user story format)
- Use **Task** for technical/internal work (no user story — uses summary format)
