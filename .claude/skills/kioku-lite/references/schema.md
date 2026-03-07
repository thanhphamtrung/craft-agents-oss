# Kioku Lite Database Schema

## Tables

### items
Primary storage for knowledge items from any source.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment ID |
| source | TEXT NOT NULL | Source system: `jira`, `notion`, `slack` |
| source_id | TEXT NOT NULL | Unique ID from source (e.g., `PROJ-123`, `page-abc`) |
| type | TEXT NOT NULL | Item type: `ticket`, `doc`, `spec`, `message` |
| title | TEXT NOT NULL | Item title |
| content | TEXT | Full content/description |
| status | TEXT | Status: `open`, `closed`, `in_progress` |
| metadata | TEXT | JSON blob for extra fields (assignee, labels, etc.) |
| created_at | TEXT | ISO datetime |
| updated_at | TEXT | ISO datetime |

**Unique constraint:** `(source, source_id)` — enables idempotent upserts.

### relationships
Links between items across sources.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment ID |
| from_source | TEXT NOT NULL | Source of origin item |
| from_source_id | TEXT NOT NULL | ID of origin item |
| to_source | TEXT NOT NULL | Source of target item |
| to_source_id | TEXT NOT NULL | ID of target item |
| rel_type | TEXT NOT NULL | Relationship type |

**Relationship types:** `spec_to_ticket`, `epic_to_story`, `thread_to_ticket`

### items_fts (FTS5 Virtual Table)
Full-text search index over items. Automatically synced via triggers.

**Indexed columns:** title, content, source, type, status
**Ranking:** BM25 (default FTS5 ranking function)
