"""
init_db.py — create the M2 structured schema in PostgreSQL.

In Docker the postgres container auto-runs db/init/*.sql on first boot, so you
normally don't need this. Use it to (re)apply the schema manually against an
already-running Postgres (all statements are IF NOT EXISTS, so it's idempotent):

    docker compose exec api python scripts/init_db.py

Env: POSTGRES_* connection (see services/db.py).
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.db import get_pg_conn

INIT_DIR = os.path.join(os.path.dirname(__file__), '..', 'db', 'init')
SQL_FILES = ["01_init.sql", "02_index.sql"]


def init_db():
    conn = get_pg_conn()
    conn.autocommit = True
    cursor = conn.cursor()

    for name in SQL_FILES:
        path = os.path.join(INIT_DIR, name)
        if not os.path.exists(path):
            print(f"⚠️  {path} not found — skipping")
            continue
        print(f"Applying {name}...")
        with open(path, "r", encoding="utf-8") as f:
            cursor.execute(f.read())

    conn.close()
    print("✅ Database schema initialised successfully.")


if __name__ == "__main__":
    init_db()
