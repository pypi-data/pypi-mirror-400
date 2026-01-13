# syntaxmatrix/db_contract.py
from __future__ import annotations

from typing import Dict, Iterable, Optional


# Keep this list tight: only functions that the framework truly depends on.
# If we add more later, we do it deliberately.
CORE_REQUIRED_FUNCTIONS = (
    # Pages
    "get_pages",
    "get_page_html",
    "add_page",
    "update_page",
    "delete_page",

    # Secrets
    "get_secrets",
    "set_secret",
    "delete_secret",

    # Nav
    "get_nav_links",
    "set_nav_links",

    # Page layouts (builder)
    "get_page_layout",
    "upsert_page_layout",
    "delete_page_layout",

    # Media library
    "add_media_file",
    "list_media_files",
    "delete_media_file",

    # Generic settings (used by branding + profiles + other admin toggles)
    "get_setting",
    "set_setting",

    # Optional: some backends may want init, but we do not force it here.
)


def assert_backend_implements_core_api(ns: Dict[str, object], *, provider: str = "") -> None:
    """
    Validate that the loaded backend provides the minimum required surface.

    `ns` is usually `globals()` from syntaxmatrix.db (the facade module).

    We keep this strict for non-SQLite providers, because:
    - SQLite is the built-in reference backend.
    - Premium/Cloud backends must be complete, or we fail fast with a clear error.
    """
    missing = []
    for fn in CORE_REQUIRED_FUNCTIONS:
        obj = ns.get(fn)
        if not callable(obj):
            missing.append(fn)

    if missing:
        prov = provider or "unknown"
        raise RuntimeError(
            "SyntaxMatrix DB backend validation failed.\n"
            f"Provider: {prov}\n"
            "Missing required functions:\n"
            f"  - " + "\n  - ".join(missing) + "\n\n"
            "Fix:\n"
            "- If you are using the premium Postgres backend, ensure the premium package is installed\n"
            "  and that your backend module's install(ns) correctly injects these functions.\n"
            "- If you are writing your own backend, implement the missing functions.\n"
        )
