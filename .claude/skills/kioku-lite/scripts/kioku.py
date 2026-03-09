#!/usr/bin/env python3
"""Kioku Lite — Local SQLite knowledge base with BM25 full-text search.

CLI tool for agents to store, search, link, and retrieve knowledge items
across sources (Jira, Notion, Slack, etc.).
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone


# ── Schema ────────────────────────────────────────────────────────────────────

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    source_id TEXT NOT NULL,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    status TEXT DEFAULT 'open',
    metadata TEXT DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE(source, source_id)
);

CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_source TEXT NOT NULL,
    from_source_id TEXT NOT NULL,
    to_source TEXT NOT NULL,
    to_source_id TEXT NOT NULL,
    rel_type TEXT NOT NULL,
    UNIQUE(from_source, from_source_id, to_source, to_source_id, rel_type)
);

CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
    title, content, source, type, status,
    content='items',
    content_rowid='id'
);

-- Triggers to keep FTS index in sync with items table
CREATE TRIGGER IF NOT EXISTS items_ai AFTER INSERT ON items BEGIN
    INSERT INTO items_fts(rowid, title, content, source, type, status)
    VALUES (new.id, new.title, new.content, new.source, new.type, new.status);
END;

CREATE TRIGGER IF NOT EXISTS items_ad AFTER DELETE ON items BEGIN
    INSERT INTO items_fts(items_fts, rowid, title, content, source, type, status)
    VALUES ('delete', old.id, old.title, old.content, old.source, old.type, old.status);
END;

CREATE TRIGGER IF NOT EXISTS items_au AFTER UPDATE ON items BEGIN
    INSERT INTO items_fts(items_fts, rowid, title, content, source, type, status)
    VALUES ('delete', old.id, old.title, old.content, old.source, old.type, old.status);
    INSERT INTO items_fts(rowid, title, content, source, type, status)
    VALUES (new.id, new.title, new.content, new.source, new.type, new.status);
END;
"""


def get_db(db_path: str) -> sqlite3.Connection:
    """Open a connection to the SQLite database."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def ensure_initialized(conn: sqlite3.Connection) -> bool:
    """Check if DB has been initialized with schema. Returns False if not."""
    try:
        conn.execute("SELECT 1 FROM items LIMIT 1")
        return True
    except sqlite3.OperationalError:
        return False


def fail_if_not_initialized(conn: sqlite3.Connection):
    """Exit with JSON error if DB is not initialized."""
    if not ensure_initialized(conn):
        conn.close()
        print(json.dumps({"ok": False, "error": "Database not initialized. Run 'init' first."}))
        sys.exit(1)


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_init(args):
    """Initialize the database with schema."""
    conn = get_db(args.db)
    conn.executescript(SCHEMA_SQL)
    conn.close()
    print(json.dumps({"ok": True, "db": args.db}))


def cmd_store(args):
    """Store or upsert an item using atomic INSERT ON CONFLICT."""
    conn = get_db(args.db)
    fail_if_not_initialized(conn)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    metadata = args.metadata or "{}"

    # Validate metadata is valid JSON
    try:
        json.loads(metadata)
    except json.JSONDecodeError:
        conn.close()
        print(json.dumps({"ok": False, "error": "Invalid JSON in --metadata"}))
        sys.exit(1)

    try:
        cursor = conn.execute(
            """INSERT INTO items (source, source_id, type, title, content, status, metadata, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(source, source_id) DO UPDATE SET
                   type=excluded.type, title=excluded.title, content=excluded.content,
                   status=excluded.status, metadata=excluded.metadata, updated_at=excluded.updated_at""",
            (args.source, args.source_id, args.type, args.title, args.content,
             args.status, metadata, now, now),
        )
        conn.commit()
        # Determine if it was insert or update by checking lastrowid behavior
        item_id = cursor.lastrowid
        action = "upserted"
        print(json.dumps({"ok": True, "action": action, "id": item_id,
                           "source": args.source, "source_id": args.source_id}))
    finally:
        conn.close()


def cmd_search(args):
    """Search items using FTS5 BM25 ranking with optional filters."""
    query = args.query.strip()
    if not query:
        print(json.dumps({"ok": True, "count": 0, "results": []}))
        return

    conn = get_db(args.db)
    fail_if_not_initialized(conn)
    limit = args.limit or 10

    # Build optional filter clauses on the real items table
    filters = []
    params = [query]
    if args.source:
        filters.append("i.source = ?")
        params.append(args.source)
    if args.type:
        filters.append("i.type = ?")
        params.append(args.type)
    if args.status:
        filters.append("i.status = ?")
        params.append(args.status)

    where_extra = (" AND " + " AND ".join(filters)) if filters else ""
    params.append(limit)

    try:
        cursor = conn.execute(
            f"""SELECT i.*, bm25(items_fts) AS rank
               FROM items_fts fts
               JOIN items i ON i.id = fts.rowid
               WHERE items_fts MATCH ?{where_extra}
               ORDER BY rank
               LIMIT ?""",
            params,
        )
        results = [dict(row) for row in cursor.fetchall()]
        print(json.dumps({"ok": True, "count": len(results), "results": results}))
    except sqlite3.OperationalError as e:
        print(json.dumps({"ok": False, "error": f"Search failed: {e}"}))
    finally:
        conn.close()


def cmd_get(args):
    """Get a single item by source and source_id."""
    conn = get_db(args.db)
    fail_if_not_initialized(conn)
    try:
        cursor = conn.execute(
            "SELECT * FROM items WHERE source = ? AND source_id = ?",
            (args.source, args.source_id),
        )
        row = cursor.fetchone()

        if row:
            item = dict(row)
            rels = conn.execute(
                """SELECT * FROM relationships
                   WHERE (from_source=? AND from_source_id=?) OR (to_source=? AND to_source_id=?)""",
                (args.source, args.source_id, args.source, args.source_id),
            ).fetchall()
            item["relationships"] = [dict(r) for r in rels]
            print(json.dumps({"ok": True, "item": item}))
        else:
            print(json.dumps({"ok": False, "error": "Not found"}))
    finally:
        conn.close()


def cmd_link(args):
    """Create a relationship between two items."""
    conn = get_db(args.db)
    fail_if_not_initialized(conn)
    try:
        conn.execute(
            """INSERT OR IGNORE INTO relationships
               (from_source, from_source_id, to_source, to_source_id, rel_type)
               VALUES (?, ?, ?, ?, ?)""",
            (args.from_source, args.from_id, args.to_source, args.to_id, args.rel_type),
        )
        conn.commit()
        print(json.dumps({"ok": True, "rel_type": args.rel_type,
                           "from": f"{args.from_source}:{args.from_id}",
                           "to": f"{args.to_source}:{args.to_id}"}))
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}))
    finally:
        conn.close()


def cmd_delete(args):
    """Delete an item and its relationships."""
    conn = get_db(args.db)
    fail_if_not_initialized(conn)
    try:
        cursor = conn.execute(
            "DELETE FROM items WHERE source = ? AND source_id = ?",
            (args.source, args.source_id),
        )
        conn.execute(
            """DELETE FROM relationships
               WHERE (from_source=? AND from_source_id=?) OR (to_source=? AND to_source_id=?)""",
            (args.source, args.source_id, args.source, args.source_id),
        )
        conn.commit()
        deleted = cursor.rowcount > 0
        print(json.dumps({"ok": True, "deleted": deleted,
                           "source": args.source, "source_id": args.source_id}))
    finally:
        conn.close()


# ── CLI Parser ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Kioku Lite — Local knowledge base")
    parser.add_argument("--db", required=True, help="Path to SQLite database file")
    sub = parser.add_subparsers(dest="command", required=True)

    # init
    sub.add_parser("init", help="Initialize database schema")

    # store
    p_store = sub.add_parser("store", help="Store/upsert an item")
    p_store.add_argument("--source", required=True, help="Source system (jira|notion|slack)")
    p_store.add_argument("--source-id", required=True, help="Unique ID from source")
    p_store.add_argument("--type", required=True, help="Item type (ticket|doc|spec|message)")
    p_store.add_argument("--title", required=True, help="Item title")
    p_store.add_argument("--content", default="", help="Item content/description")
    p_store.add_argument("--status", default="open", help="Status (open|closed|in_progress)")
    p_store.add_argument("--metadata", default="{}", help="JSON metadata blob")

    # search
    p_search = sub.add_parser("search", help="Search items via BM25 full-text search")
    p_search.add_argument("--query", required=True, help="Search query")
    p_search.add_argument("--limit", type=int, default=10, help="Max results")
    p_search.add_argument("--source", help="Filter by source (jira|slack|notion)")
    p_search.add_argument("--type", help="Filter by type (ticket|message|doc|spec)")
    p_search.add_argument("--status", help="Filter by status (open|closed|in_progress)")

    # get
    p_get = sub.add_parser("get", help="Get item by source + source_id")
    p_get.add_argument("--source", required=True)
    p_get.add_argument("--source-id", required=True)

    # link
    p_link = sub.add_parser("link", help="Create relationship between items")
    p_link.add_argument("--from-source", required=True)
    p_link.add_argument("--from-id", required=True)
    p_link.add_argument("--to-source", required=True)
    p_link.add_argument("--to-id", required=True)
    p_link.add_argument("--rel-type", required=True, help="Relationship type")

    # delete
    p_del = sub.add_parser("delete", help="Delete item and its relationships")
    p_del.add_argument("--source", required=True)
    p_del.add_argument("--source-id", required=True)

    args = parser.parse_args()
    commands = {
        "init": cmd_init, "store": cmd_store, "search": cmd_search,
        "get": cmd_get, "link": cmd_link, "delete": cmd_delete,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
