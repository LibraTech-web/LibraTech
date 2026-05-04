"""
Database Migration Script
=========================
Safely adds missing columns to the reading_history table
without affecting existing data.

Usage:
    cd lib_management_system
    python run_db_migration.py
"""

import os
import sys

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(__file__))

from config import _build_db_uri
import pymysql


def parse_db_uri(uri: str) -> dict:
    """Parse mysql+pymysql:// URI into connection kwargs."""
    # strip protocol
    uri = uri.replace("mysql+pymysql://", "")
    # split auth and host
    auth, rest = uri.split("@", 1)
    user, password = auth.split(":", 1)
    # password may contain URL-encoded characters
    from urllib.parse import unquote_plus
    user = unquote_plus(user)
    password = unquote_plus(password)
    # rest: host:port/db
    if "/" in rest:
        host_port, db = rest.split("/", 1)
    else:
        host_port, db = rest, None

    if ":" in host_port:
        host, port = host_port.rsplit(":", 1)
        port = int(port)
    else:
        host, port = host_port, 3306

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": db,
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
    }


def column_exists(conn, table: str, column: str) -> bool:
    """Check if a column exists in a table."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 1 FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME   = %s
              AND COLUMN_NAME  = %s
            """,
            (table, column),
        )
        return cur.fetchone() is not None


def add_column(conn, table: str, column: str, definition: str):
    """Add a column to a table."""
    with conn.cursor() as cur:
        sql = f"ALTER TABLE `{table}` ADD COLUMN `{column}` {definition}"
        print(f"  Executing: {sql}")
        cur.execute(sql)
        conn.commit()
        print(f"  ✓ Added '{column}' to '{table}'")


def main():
    uri = _build_db_uri()
    print(f"Connecting to: {uri.replace(uri.split('://')[1].split('@')[0], '****:****')}")

    kwargs = parse_db_uri(uri)
    try:
        conn = pymysql.connect(**kwargs)
    except Exception as e:
        print(f"\n✗ Could not connect to MySQL: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure MySQL is running (XAMPP Control Panel → Start MySQL)")
        print("  2. Check .env DB_HOST, DB_USER, DB_PASSWORD, DB_NAME values")
        sys.exit(1)

    print("Connected successfully.\n")

    # ── Apply migrations ────────────────────────────────────────────────
    migrations = [
        ("reading_history", "borrowed_at", "DATETIME DEFAULT NULL"),
        ("reading_history", "returned_at", "DATETIME DEFAULT NULL"),
    ]

    applied = 0
    skipped = 0

    for table, column, definition in migrations:
        if column_exists(conn, table, column):
            print(f"Column '{column}' already exists in '{table}' — skipping.")
            skipped += 1
        else:
            add_column(conn, table, column, definition)
            applied += 1

    print(f"\n{'─'*50}")
    print(f"Migration complete: {applied} applied, {skipped} skipped.")

    # ── Verify ──────────────────────────────────────────────────────────
    print("\nVerifying reading_history columns:")
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME   = 'reading_history'
            ORDER BY ORDINAL_POSITION
            """
        )
        for row in cur.fetchall():
            nullable = "NULL" if row["IS_NULLABLE"] == "YES" else "NOT NULL"
            print(f"  • {row['COLUMN_NAME']:20s} {row['DATA_TYPE']:15s} {nullable}")

    conn.close()
    print("\nDone. You can now restart the Flask application.")


if __name__ == "__main__":
    main()

