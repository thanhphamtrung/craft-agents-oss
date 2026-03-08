# Jira Status Mapping

Maps Jira statuses to Kioku status values. Jira statuses vary by project workflow.

## Default Mapping

| Kioku Status | Jira Statuses |
|-------------|---------------|
| `open` | Open, To Do, Backlog, New, Reopened, Selected for Development |
| `in_progress` | In Progress, In Review, In QA, Code Review, Testing, Blocked |
| `closed` | Done, Closed, Resolved, Released, Cancelled, Won't Do, Declined |

## Rules

1. Match is **case-insensitive** (e.g., "IN PROGRESS" -> `in_progress`)
2. If status not in table, default to `open` and log warning
3. User can override by providing custom mapping at sync time

## Custom Mapping (User Override)

If user says "In our project, 'Waiting' means in_progress", apply that override for the session.

## Common Workflow Variants

### Simplified (3-column board)
To Do -> In Progress -> Done

### Software Development
Backlog -> Selected for Dev -> In Progress -> In Review -> Done

### Kanban
New -> Analysis -> Dev -> QA -> Release -> Closed

### Support/Service Desk
Open -> Waiting for Support -> Waiting for Customer -> Resolved -> Closed
