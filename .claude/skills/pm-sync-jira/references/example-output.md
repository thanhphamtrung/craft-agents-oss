# Example Sync Output

## User Request
"Sync all tickets from project ACME"

## Agent Execution Flow

### Step 1: Scope
```
Syncing project ACME — all tickets, no date filter.
JQL: project = ACME ORDER BY updated DESC
```

### Step 2: Fetch
```
Fetching tickets from Jira...
  Page 1: tickets 1-50 of 127
  Page 2: tickets 51-100 of 127
  Page 3: tickets 101-127 of 127
Fetched 127 tickets.
```

### Step 3: Enrich
```
Enriching tickets with full details and links...
  Processing 1/127: ACME-1 (Epic)
  Processing 2/127: ACME-2 (Story)
  ...
  Processing 127/127: ACME-127 (Task)
```

### Step 4: Store
```
Storing tickets in Kioku...
  ACME-1: stored (Epic)
  ACME-2: stored (Story)
  ...
127 tickets synced.
```

### Step 5: Relationships
```
Creating relationships...
  ACME-1 -> ACME-2: epic_to_story
  ACME-1 -> ACME-3: epic_to_story
  ACME-5 -> ACME-12: blocks
  ACME-8 -> ACME-9: related_to
Created 43 relationships.
```

### Step 6: Summary
```
## Sync Complete

**Scope:** project = ACME
**Total:** 127 tickets synced
**Relationships:** 43

| Type | Count |
|------|-------|
| Epic | 3 |
| Story | 48 |
| Task | 52 |
| Bug | 19 |
| Sub-task | 5 |

### Warnings
- ACME-44: empty description
- ACME-99 -> EXT-5: link skipped (target not in scope)

### Next Steps
- Search: `kioku search --query "authentication"`
- Incremental: re-run with "ACME since 2026-03-08"
```
