"""
db.py — shared PostgreSQL connection helper for the structured project store.

The M2 hybrid search needs a structured SQL database (projects, pylons,
calculation notes…) alongside the ChromaDB vector store. This module centralises
the Postgres connection so every caller (hybrid_search, ingest scripts, and
later M4) uses the same config, read from environment variables.

Environment variables (with docker-compose defaults):
    POSTGRES_HOST      (default: localhost)
    POSTGRES_PORT      (default: 5432)
    POSTGRES_DB        (default: bimlo)
    POSTGRES_USER      (default: bimlo)
    POSTGRES_PASSWORD  (default: bimlo)
"""

import os
from typing import Optional

try:
    import psycopg2
    _PSYCOPG_AVAILABLE = True
except ImportError:  # pragma: no cover - import guard
    psycopg2 = None
    _PSYCOPG_AVAILABLE = False


def pg_config() -> dict:
    """Return connection kwargs pulled from the environment."""
    return {
        "host":     os.getenv("POSTGRES_HOST", "localhost"),
        "port":     int(os.getenv("POSTGRES_PORT", "5432")),
        "dbname":   os.getenv("POSTGRES_DB", "bimlo"),
        "user":     os.getenv("POSTGRES_USER", "bimlo"),
        "password": os.getenv("POSTGRES_PASSWORD", "bimlo"),
    }


def get_pg_conn(timeout: int = 5):
    """
    Open a new PostgreSQL connection.

    Raises RuntimeError if psycopg2 isn't installed so callers can fall back
    gracefully instead of crashing the request.
    """
    if not _PSYCOPG_AVAILABLE:
        raise RuntimeError("psycopg2 not installed — cannot reach Postgres")
    cfg = pg_config()
    return psycopg2.connect(connect_timeout=timeout, **cfg)


def pg_available() -> bool:
    """Cheap health check: True if we can connect and run SELECT 1."""
    if not _PSYCOPG_AVAILABLE:
        return False
    try:
        conn = get_pg_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        conn.close()
        return True
    except Exception:
        return False
