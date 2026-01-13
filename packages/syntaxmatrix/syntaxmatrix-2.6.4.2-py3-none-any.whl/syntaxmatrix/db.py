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



# ─────────────────────────────────────────────────────────
# Page 
# ─────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            name TEXT PRIMARY KEY,
            content TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS askai_cells (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            question TEXT,
            output TEXT,
            code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS secretes (
            name TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

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
            mime       TEXT,
            source     TEXT,
            source_url TEXT,
            author     TEXT,
            licence    TEXT,
            tags       TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Default settings (if they don't exist yet)
    default_settings = [
        ("branding.site_title", "SyntaxMatrix"),
        ("branding.project_name", "smxAI"),
        ("branding.bot_icon", "default_bot_icon.png"),
    ]

    for key, value in default_settings:
        existing_value = conn.execute(
            "SELECT value FROM app_settings WHERE key = ?", (key,)
        ).fetchone()
        if not existing_value:
            conn.execute(
                "INSERT INTO app_settings (key, value) VALUES (?, ?)", (key, value)
            )

    conn.commit()
    conn.close()


# ***************************************
# Pages Helpers
# ***************************************
def get_pages():
    """Return {page_name: html} resolving relative paths under syntaxmatrixdir/templates."""
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT name, content FROM pages").fetchall()
    conn.close()

    pages = {}
    for name, file_path in rows:
        # If the DB holds a relative path (e.g. 'templates/about.html'), make it absolute.
        if file_path and not os.path.isabs(file_path):
            file_path = os.path.join(_CLIENT_DIR, file_path)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                pages[name] = f.read()
        except Exception:
            pages[name] = f"<p>Missing file for page '{name}'.</p>"
    return pages


def get_page_html(name: str):
    """
    Return the latest HTML for a single page by reading the file path stored in DB.
    This avoids stale in-memory cache (smx.pages) across Gunicorn workers.
    """
    if not name:
        return None

    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            "SELECT content FROM pages WHERE lower(name) = lower(?)",
            (name.strip(),)
        ).fetchone()
    finally:
        conn.close()

    if not row:
        return None

    stored = (row[0] or "").strip()
    if not stored:
        return None

    # Backwards compatible: if DB ever stored raw HTML instead of a file path
    if stored.lstrip().startswith("<"):
        return stored

    # Resolve path (relative under syntaxmatrixdir)
    abs_path = stored if os.path.isabs(stored) else os.path.join(_CLIENT_DIR, stored)

    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def add_page(name, html):
    """Create templates/<slug>.html and store a relative path in the DB."""
    filename = secure_filename(name.lower()) + ".html"
    abs_path = os.path.join(TEMPLATES_DIR, filename)

    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(html)

    rel_path = f"templates/{filename}"
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO pages (name, content) VALUES (?, ?)", (name, rel_path))

    conn.commit()
    conn.close()


def update_page(old_name, new_name, html):
    """
    Overwrite the page file; if the title changes, rename the file.
    Always store a relative path 'templates/<slug>.html' in the DB.
    """
    import sqlite3, os
    from werkzeug.utils import secure_filename

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    row = cur.execute("SELECT content FROM pages WHERE name = ?", (old_name,)).fetchone()
    if not row:
        conn.close()
        return

    # Resolve current path (absolute if DB stored absolute; otherwise under syntaxmatrixdir)
    current = row[0] or ""
    if current and not os.path.isabs(current):
        current_abs = os.path.join(_CLIENT_DIR, current)
    else:
        current_abs = current

    # Target filename/path for the new name
    new_filename = secure_filename(new_name.lower()) + ".html"
    target_abs   = os.path.join(_CLIENT_DIR, "templates", new_filename)
    os.makedirs(os.path.dirname(target_abs), exist_ok=True)

    # If name changed and the old file exists, rename; otherwise we’ll just write fresh
    if old_name != new_name and current_abs and os.path.exists(current_abs) and current_abs != target_abs:
        try:
            os.replace(current_abs, target_abs)
        except Exception:
            # If rename fails (e.g. old file missing), we’ll write the new file below
            pass

    # Write the HTML (create if missing, overwrite if present)
    with open(target_abs, "w", encoding="utf-8") as f:
        f.write(html)

    # Store a relative, OS-agnostic path in the DB
    rel_path = f"templates/{new_filename}"
    cur.execute(
        "UPDATE pages SET name = ?, content = ? WHERE name = ?",
        (new_name, rel_path, old_name)
    )
    conn.commit()
    conn.close()

def delete_page(name):
    """
    Delete the page file (if present) and remove the row from the DB.
    Works whether 'content' is absolute or relative.
    """
    import sqlite3, os

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    row = cur.execute("SELECT content FROM pages WHERE name = ?", (name,)).fetchone()
    if row:
        path = row[0] or ""
        abs_path = path if os.path.isabs(path) else os.path.join(_CLIENT_DIR, path)
        if os.path.exists(abs_path):
            try:
                os.remove(abs_path)
            except Exception:
                # Don’t block deletion if the file cannot be removed
                pass

    cur.execute("DELETE FROM pages WHERE name = ?", (name,))
    conn.commit()
    conn.close()


# ***************************************
# Secrete Helpers
# ***************************************
def set_secret(name: str, value: str) -> None:
    """Create/update a secret in the local SyntaxMatrix DB."""
    if not name:
        return
    name = name.strip().upper()
    conn = sqlite3.connect(DB_PATH)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO secretes (name, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(name) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (name, value),
            )
    finally:
        conn.close()


def get_secret(name: str) -> str | None:
    """Get a secret value, or None if missing."""
    if not name:
        return None
    name = name.strip().upper()
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute("SELECT value FROM secretes WHERE name = ?", (name,)).fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def delete_secret(name: str) -> None:
    if not name:
        return
    name = name.strip().upper()
    conn = sqlite3.connect(DB_PATH)
    try:
        with conn:
            conn.execute("DELETE FROM secretes WHERE name = ?", (name,))
    finally:
        conn.close()


def list_secret_names() -> list[str]:
    """Return secret names only (never values)."""
    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute("SELECT name FROM secretes ORDER BY name").fetchall()
        return [r[0] for r in rows]
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────
# Page navigation metadata (show_in_nav / nav_label)
# ─────────────────────────────────────────────────────────
def _init_page_nav_table():
    """Ensure the page_nav table exists and has all expected columns."""
    import sqlite3  # safe if already imported at top
    conn = sqlite3.connect(DB_PATH)
    try:
        with conn:
            # Create table if missing (with nav_order already defined)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS page_nav (
                    page_name   TEXT PRIMARY KEY,
                    show_in_nav INTEGER NOT NULL DEFAULT 1,
                    nav_label   TEXT,
                    nav_order   INTEGER
                )
            """)

            # If table existed before, make sure nav_order column is present
            cur = conn.execute("PRAGMA table_info(page_nav)")
            cols = [row[1] for row in cur.fetchall()]
            if "nav_order" not in cols:
                conn.execute("ALTER TABLE page_nav ADD COLUMN nav_order INTEGER")
    finally:
        conn.close()


def set_page_nav(
    page_name: str,
    show_in_nav: bool = True,
    nav_label: str | None = None,
    nav_order: int | None = None,
) -> None:
    """
    Upsert navigation preferences for a page.
    """
    if not page_name:
        return
    _init_page_nav_table()
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    try:
        with conn:
            conn.execute("""
                INSERT INTO page_nav (page_name, show_in_nav, nav_label, nav_order)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(page_name) DO UPDATE SET
                    show_in_nav = excluded.show_in_nav,
                    nav_label   = excluded.nav_label,
                    nav_order   = excluded.nav_order
                """, (page_name.lower(), 1 if show_in_nav else 0, nav_label, nav_order),
            )
    finally:
        conn.close()


def get_page_nav_map() -> dict:
    """
    Return a dict mapping page_name -> {"show_in_nav": bool, "nav_label": str|None, "nav_order": int|None}.
    """
    _init_page_nav_table()
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("SELECT page_name, show_in_nav, nav_label, nav_order FROM page_nav")
        rows = cur.fetchall()
    finally:
        conn.close()

    result = {}
    for name, show, label, order_val in rows:
        if not name:
            continue
        result[name.lower()] = {
            "show_in_nav": bool(show),
            "nav_label": label,
            "nav_order": order_val,
        }
    return result


# ─────────────────────────────────────────────────────────
# Page layouts (builder JSON) kept separate from final HTML
# ─────────────────────────────────────────────────────────
def _init_page_layouts_table():
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS page_layouts (
                    page_name   TEXT PRIMARY KEY,
                    layout_json TEXT NOT NULL,
                    is_detached INTEGER NOT NULL DEFAULT 0,
                    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    finally:
        conn.close()


def upsert_page_layout(page_name: str, layout_json: str, is_detached: bool | None = None) -> None:
    if not page_name:
        return
    _init_page_layouts_table()
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    try:
        with conn:
            if is_detached is None:
                conn.execute(
                    """
                    INSERT INTO page_layouts (page_name, layout_json)
                    VALUES (?, ?)
                    ON CONFLICT(page_name) DO UPDATE SET
                        layout_json = excluded.layout_json,
                        updated_at  = CURRENT_TIMESTAMP
                    """,
                    (page_name.lower(), layout_json),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO page_layouts (page_name, layout_json, is_detached)
                    VALUES (?, ?, ?)
                    ON CONFLICT(page_name) DO UPDATE SET
                        layout_json = excluded.layout_json,
                        is_detached = excluded.is_detached,
                        updated_at  = CURRENT_TIMESTAMP
                    """,
                    (page_name.lower(), layout_json, 1 if is_detached else 0),
                )
    finally:
        conn.close()


def get_page_layout(page_name: str) -> dict | None:
    if not page_name:
        return None
    _init_page_layouts_table()
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            "SELECT page_name, layout_json, is_detached, updated_at FROM page_layouts WHERE page_name = ?",
            (page_name.lower(),),
        ).fetchone()
        if not row:
            return None
        return {
            "page_name": row[0],
            "layout_json": row[1],
            "is_detached": bool(row[2]),
            "updated_at": row[3],
        }
    finally:
        conn.close()


def _init_media_assets_table() -> None:

    conn = sqlite3.connect(DB_PATH)
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS media_assets (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind       TEXT NOT NULL DEFAULT 'image',
                    rel_path   TEXT NOT NULL UNIQUE,
                    thumb_path TEXT,
                    sha256     TEXT,
                    dhash      TEXT,
                    width      INTEGER,
                    height     INTEGER,
                    mime       TEXT,
                    source     TEXT,
                    source_url TEXT,
                    author     TEXT,
                    licence    TEXT,
                    tags       TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
    finally:
        conn.close()


def upsert_media_asset(
    *,
    rel_path: str,
    kind: str = "image",
    thumb_path: str | None = None,
    sha256: str | None = None,
    dhash: str | None = None,
    width: int | None = None,
    height: int | None = None,
    mime: str | None = None,
    source: str | None = None,
    source_url: str | None = None,
    author: str | None = None,
    licence: str | None = None,
    tags: str | None = None,
) -> None:
    if not rel_path:
        return
    _init_media_assets_table()

    conn = sqlite3.connect(DB_PATH)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO media_assets (
                    kind, rel_path, thumb_path, sha256, dhash, width, height, mime,
                    source, source_url, author, licence, tags
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(rel_path) DO UPDATE SET
                    kind       = excluded.kind,
                    thumb_path = excluded.thumb_path,
                    sha256     = excluded.sha256,
                    dhash      = excluded.dhash,
                    width      = excluded.width,
                    height     = excluded.height,
                    mime       = excluded.mime,
                    source     = excluded.source,
                    source_url = excluded.source_url,
                    author     = excluded.author,
                    licence    = excluded.licence,
                    tags       = excluded.tags
                """,
                (
                    kind, rel_path, thumb_path, sha256, dhash, width, height, mime,
                    source, source_url, author, licence, tags,
                ),
            )
    finally:
        conn.close()


def get_media_asset_by_rel_path(rel_path: str) -> dict | None:
    if not rel_path:
        return None
    _init_media_assets_table()
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            """
            SELECT kind, rel_path, thumb_path, sha256, dhash, width, height, mime,
                   source, source_url, author, licence, tags, created_at
            FROM media_assets WHERE rel_path = ?
            """,
            (rel_path,),
        ).fetchone()
        if not row:
            return None
        return {
            "kind": row[0],
            "rel_path": row[1],
            "thumb_path": row[2],
            "sha256": row[3],
            "dhash": row[4],
            "width": row[5],
            "height": row[6],
            "mime": row[7],
            "source": row[8],
            "source_url": row[9],
            "author": row[10],
            "licence": row[11],
            "tags": row[12],
            "created_at": row[13],
        }
    finally:
        conn.close()

# ***************************************
# App Settings Helpers (feature toggles)
# ***************************************
def set_setting(key: str, value: str) -> None:
    if not key:
        return
    key = key.strip()
    value = "" if value is None else str(value)
    conn = sqlite3.connect(DB_PATH)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO app_settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (key, value),
            )
    finally:
        conn.close()


def get_setting(key: str, default: str | None = None) -> str | None:
    if not key:
        return default
    key = key.strip()
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute("SELECT value FROM app_settings WHERE key = ?", (key,)).fetchone()
        return row[0] if row else default
    finally:
        conn.close()
