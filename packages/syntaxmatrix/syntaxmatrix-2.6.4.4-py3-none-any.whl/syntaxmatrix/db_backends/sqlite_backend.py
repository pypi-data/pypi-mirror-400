from __future__ import annotations
import sqlite3
import os
import json
from werkzeug.utils import secure_filename
from syntaxmatrix.project_root import detect_project_root


_CLIENT_DIR = detect_project_root()
DB_PATH = os.path.join(_CLIENT_DIR, "data", "syntaxmatrix.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

TEMPLATES_DIR = os.path.join(_CLIENT_DIR, "templates")
os.makedirs(TEMPLATES_DIR, exist_ok=True)


# ------------ Utils ------------
def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _col_exists(conn, table: str, col: str) -> bool:
    cur = conn.execute(f"PRAGMA table_info({table})")
    cols = [r["name"] for r in cur.fetchall()]
    return col in cols

def _ensure_column(conn, table: str, col: str, col_sql: str):
    if not _col_exists(conn, table, col):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_sql}")

def _ensure_index(conn, idx_sql: str):
    try:
        conn.execute(idx_sql)
    except Exception:
        pass


# ------------ Schema init ------------
def init_db():
    conn = connect_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            name TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS page_layouts (
            name TEXT PRIMARY KEY,
            layout_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            subject TEXT,
            meta TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    _init_media_assets_table(conn)

    conn.commit()
    conn.close()


# ------------ Pages ------------
def get_pages():
    conn = connect_db()
    cur = conn.execute("SELECT name FROM pages ORDER BY name")
    rows = [r["name"] for r in cur.fetchall()]
    conn.close()
    return rows

def get_page(name: str):
    conn = connect_db()
    cur = conn.execute("SELECT name, content FROM pages WHERE name = ?", (name,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def add_page(name: str, content: str):
    conn = connect_db()
    conn.execute("INSERT OR REPLACE INTO pages (name, content) VALUES (?, ?)", (name, content))
    conn.commit()
    conn.close()

def update_page(name: str, content: str):
    conn = connect_db()
    conn.execute("UPDATE pages SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?", (content, name))
    conn.commit()
    conn.close()

def delete_page(name: str):
    conn = connect_db()
    conn.execute("DELETE FROM pages WHERE name = ?", (name,))
    conn.execute("DELETE FROM page_layouts WHERE name = ?", (name,))
    conn.commit()
    conn.close()

def rename_page(old_name: str, new_name: str):
    conn = connect_db()
    conn.execute("UPDATE pages SET name = ? WHERE name = ?", (new_name, old_name))
    conn.execute("UPDATE page_layouts SET name = ? WHERE name = ?", (new_name, old_name))
    conn.commit()
    conn.close()


# ------------ Layouts ------------
def upsert_page_layout(name: str, layout_json: str):
    conn = connect_db()
    conn.execute(
        "INSERT OR REPLACE INTO page_layouts (name, layout_json) VALUES (?, ?)",
        (name, layout_json)
    )
    conn.commit()
    conn.close()

def get_page_layout(name: str):
    conn = connect_db()
    cur = conn.execute("SELECT name, layout_json FROM page_layouts WHERE name = ?", (name,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_page_layouts():
    conn = connect_db()
    cur = conn.execute("SELECT name, layout_json FROM page_layouts ORDER BY name")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


# ------------ Settings ------------
def get_setting(key: str, default=None):
    conn = connect_db()
    cur = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return default
    try:
        return json.loads(row["value"])
    except Exception:
        return row["value"]

def set_setting(key: str, value):
    conn = connect_db()
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
        (key, json.dumps(value))
    )
    conn.commit()
    conn.close()

def delete_setting(key: str):
    conn = connect_db()
    conn.execute("DELETE FROM settings WHERE key = ?", (key,))
    conn.commit()
    conn.close()


# ------------ Audit log ------------
def audit(action: str, subject: str = "", meta: dict | None = None):
    conn = connect_db()
    conn.execute(
        "INSERT INTO audit_log (action, subject, meta) VALUES (?, ?, ?)",
        (action, subject, json.dumps(meta or {}))
    )
    conn.commit()
    conn.close()


# ------------ Media assets (dedupe + metadata) ------------
MEDIA_DIR = os.path.join(_CLIENT_DIR, "uploads", "media")
os.makedirs(MEDIA_DIR, exist_ok=True)

MEDIA_IMAGES_DIR = os.path.join(MEDIA_DIR, "images")
os.makedirs(MEDIA_IMAGES_DIR, exist_ok=True)

MEDIA_THUMBS_DIR = os.path.join(MEDIA_DIR, "thumbs")
os.makedirs(MEDIA_THUMBS_DIR, exist_ok=True)

def _init_media_assets_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS media_assets (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            kind       TEXT NOT NULL DEFAULT 'image',
            rel_path   TEXT NOT NULL UNIQUE,
            thumb_path TEXT,
            sha256     TEXT,
            dhash      TEXT,
            width      INTEGER,
            height     INTEGER,
            bytes      INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    _ensure_index(conn, "CREATE INDEX IF NOT EXISTS idx_media_assets_kind ON media_assets(kind)")
    _ensure_index(conn, "CREATE INDEX IF NOT EXISTS idx_media_assets_sha256 ON media_assets(sha256)")
    _ensure_index(conn, "CREATE INDEX IF NOT EXISTS idx_media_assets_dhash ON media_assets(dhash)")

def upsert_media_asset(kind: str, rel_path: str, thumb_path: str | None = None,
                       sha256: str | None = None, dhash: str | None = None,
                       width: int | None = None, height: int | None = None, bytes_: int | None = None):
    conn = connect_db()
    _init_media_assets_table(conn)
    conn.execute(
        """
        INSERT INTO media_assets (kind, rel_path, thumb_path, sha256, dhash, width, height, bytes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(rel_path) DO UPDATE SET
            kind=excluded.kind,
            thumb_path=excluded.thumb_path,
            sha256=excluded.sha256,
            dhash=excluded.dhash,
            width=excluded.width,
            height=excluded.height,
            bytes=excluded.bytes
        """,
        (kind, rel_path, thumb_path, sha256, dhash, width, height, bytes_)
    )
    conn.commit()
    conn.close()

def get_media_asset_by_rel_path(rel_path: str):
    conn = connect_db()
    cur = conn.execute("SELECT * FROM media_assets WHERE rel_path = ?", (rel_path,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def list_media_assets(kind: str = "image"):
    conn = connect_db()
    cur = conn.execute("SELECT * FROM media_assets WHERE kind = ? ORDER BY id DESC", (kind,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def normalise_media_filename(filename: str) -> str:
    filename = secure_filename(filename or "file")
    if not filename:
        filename = "file"
    return filename
