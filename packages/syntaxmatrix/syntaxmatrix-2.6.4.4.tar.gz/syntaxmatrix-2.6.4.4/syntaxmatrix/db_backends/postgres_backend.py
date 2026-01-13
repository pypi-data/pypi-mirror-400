# syntaxmatrix/db_backends/postgres_backend.py
"""
PostgreSQL backend 
"""

def install(ns: dict) -> None:
    raise RuntimeError(
        "Postgres backend is not available in the free tier.\n\n"
        "You set SMX_DB_PROVIDER=postgres, but the premium Postgres backend package "
        "is not installed.\n\n"
        "Fix:\n"
        "- Install the SyntaxMatrix premium Postgres backend package, then restart.\n"
        "- Or set SMX_DB_PROVIDER=sqlite to use the built-in SQLite backend.\n"
    )
