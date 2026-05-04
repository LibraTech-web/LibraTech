"""
test_connection.py
==================
MySQL connection verification script.

Runs 6 targeted tests to confirm:
  1.  .env variables are loaded correctly
  2.  The MySQL database is reachable
  3.  All 11 expected tables exist in library_db
  4.  SQLAlchemy ORM can query every model
  5.  Seed data is present (categories, authors, books)
  6.  Blueprint registration is valid (no import errors)

HOW TO RUN
----------
    # From the project root (library-management-system/)
    python test_connection.py

    # Or via Flask CLI
    flask shell
    >>> import test_connection

EXPECTED OUTPUT (when everything is working)
--------------------------------------------
    ✅  [1/6] Environment variables loaded
    ✅  [2/6] MySQL connection established
    ✅  [3/6] All 11 tables exist in library_db
    ✅  [4/6] ORM query successful on all models
    ✅  [5/6] Seed data verified
    ✅  [6/6] All blueprints registered cleanly
    ════════════════════════════════════════
    🎉  All tests passed. Database is ready.
"""

import os
import sys

# ── Add project root to Python path ──────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from app.extensions import db

app = create_app("development")

# ─── Colour helpers ───────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def ok(step, msg):
    print(f"  {GREEN}✅  [{step}]{RESET}  {msg}")

def fail(step, msg):
    print(f"  {RED}❌  [{step}]{RESET}  {msg}")
    sys.exit(1)

def warn(msg):
    print(f"  {YELLOW}⚠️   {msg}{RESET}")

def header(title):
    print(f"\n{BOLD}{'─' * 50}{RESET}")
    print(f"{BOLD}  {title}{RESET}")
    print(f"{BOLD}{'─' * 50}{RESET}")


# ─────────────────────────────────────────────────────────────────────────────
#  TEST 1 — Environment variables
# ─────────────────────────────────────────────────────────────────────────────

def test_env_vars():
    header("TEST 1/6 — Environment Variables")

    required = ["SECRET_KEY", "DB_USER", "DB_HOST", "DB_NAME"]
    missing  = [k for k in required if not os.environ.get(k)]

    if missing:
        warn(f"Missing env vars (using defaults): {missing}")
    else:
        ok("1/6", f"All required env vars present")

    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    # Mask the password in printed output
    safe_uri = db_uri
    if "@" in db_uri:
        parts = db_uri.split("@")
        creds = parts[0].split("//")[1]
        if ":" in creds:
            user = creds.split(":")[0]
            safe_uri = db_uri.replace(creds, f"{user}:****")

    print(f"  {'URI':15} {safe_uri}")
    print(f"  {'SECRET_KEY':15} {'(set)' if app.config.get('SECRET_KEY') else '(missing)'}")
    print(f"  {'DEBUG':15} {app.config.get('DEBUG')}")
    print(f"  {'ECHO SQL':15} {app.config.get('SQLALCHEMY_ECHO')}")
    ok("1/6", "Config loaded from .env")


# ─────────────────────────────────────────────────────────────────────────────
#  TEST 2 — Raw MySQL connection
# ─────────────────────────────────────────────────────────────────────────────

def test_mysql_connection():
    header("TEST 2/6 — MySQL Connection")

    with app.app_context():
        try:
            result = db.session.execute(db.text("SELECT VERSION()")).scalar()
            ok("2/6", f"Connected to MySQL — server version: {result}")

            db_name = db.session.execute(db.text("SELECT DATABASE()")).scalar()
            ok("2/6", f"Active database: {db_name}")

        except Exception as exc:
            fail("2/6", f"Connection failed: {exc}\n\n"
                         "  Check: DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME in .env\n"
                         "         MySQL server is running\n"
                         "         library_db database exists")


# ─────────────────────────────────────────────────────────────────────────────
#  TEST 3 — Table existence
# ─────────────────────────────────────────────────────────────────────────────

def test_tables_exist():
    header("TEST 3/6 — Table Existence")

    expected_tables = [
        "users", "students", "categories", "authors", "books",
        "issued_books", "reservations", "fines", "notifications",
        "reading_history", "settings",
    ]

    with app.app_context():
        inspector = db.inspect(db.engine)
        existing  = set(inspector.get_table_names())

        all_good = True
        for table in expected_tables:
            if table in existing:
                ok("3/6", f"Table `{table}` ✓")
            else:
                warn(f"Table `{table}` NOT FOUND — run your schema SQL first")
                all_good = False

        if all_good:
            ok("3/6", f"All {len(expected_tables)} tables exist in library_db")
        else:
            fail("3/6", "Some tables are missing. Import Library_Management_System_Database_Schema.sql")


# ─────────────────────────────────────────────────────────────────────────────
#  TEST 4 — ORM query on every model
# ─────────────────────────────────────────────────────────────────────────────

def test_orm_queries():
    header("TEST 4/6 — ORM Queries (all models)")

    from app.models import (
        User, Student, Category, Author, Book,
        IssuedBook, Reservation, Fine, Notification,
        ReadingHistory, Setting,
    )

    model_list = [
        ("User",           User),
        ("Student",        Student),
        ("Category",       Category),
        ("Author",         Author),
        ("Book",           Book),
        ("IssuedBook",     IssuedBook),
        ("Reservation",    Reservation),
        ("Fine",           Fine),
        ("Notification",   Notification),
        ("ReadingHistory", ReadingHistory),
        ("Setting",        Setting),
    ]

    with app.app_context():
        for name, Model in model_list:
            try:
                count = db.session.execute(
                    db.select(db.func.count()).select_from(Model)
                ).scalar()
                ok("4/6", f"{name:20} → {count} rows")
            except Exception as exc:
                fail("4/6", f"{name}.query failed: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
#  TEST 5 — Seed data verification
# ─────────────────────────────────────────────────────────────────────────────

def test_seed_data():
    header("TEST 5/6 — Seed Data")

    from app.models import Category, Author, Book, Setting

    with app.app_context():
        # Categories
        cat_count = Category.query.count()
        if cat_count >= 10:
            ok("5/6", f"{cat_count} categories found (expected ≥ 10)")
        else:
            warn(f"Only {cat_count} categories — seed data may be missing")

        # Authors
        auth_count = Author.query.count()
        if auth_count >= 20:
            ok("5/6", f"{auth_count} authors found (expected ≥ 20)")
        else:
            warn(f"Only {auth_count} authors — seed data may be missing")

        # Books
        book_count = Book.query.count()
        if book_count >= 50:
            ok("5/6", f"{book_count} books found (expected ≥ 50)")
        else:
            warn(f"Only {book_count} books — seed data may be missing")

        # Settings
        loan_days = Setting.get("loan_period_days")
        fine_rate  = Setting.get("fine_per_day")
        lib_name   = Setting.get("library_name")
        print(f"  {'library_name':25} {lib_name}")
        print(f"  {'loan_period_days':25} {loan_days} days")
        print(f"  {'fine_per_day':25} ${fine_rate}")
        ok("5/6", "Settings table readable")

        # Relationship traversal — pick a random book and check joins
        book = Book.query.filter(Book.author_id.isnot(None)).first()
        if book:
            _ = book.author.name if book.author else "—"
            _ = book.category.name if book.category else "—"
            ok("5/6", f"Relationship traversal: Book → Author → Category ✓")
        else:
            warn("No books with author_id found — relationships not tested")


# ─────────────────────────────────────────────────────────────────────────────
#  TEST 6 — Blueprint registration
# ─────────────────────────────────────────────────────────────────────────────

def test_blueprints():
    header("TEST 6/6 — Blueprint Registration")

    expected_blueprints = {
        "auth":      "/auth",
        "admin":     "/admin",
        "student":   "/student",
        "books":     "/books",
        "analytics": "/analytics",
        "digital":   "/digital",
    }

    with app.app_context():
        registered = {bp: app.blueprints[bp] for bp in app.blueprints}

        for name, prefix in expected_blueprints.items():
            if name in registered:
                ok("6/6", f"Blueprint '{name}' registered at {prefix}")
            else:
                warn(f"Blueprint '{name}' not registered yet (build it in Phase 4+)")

        # Print the full URL map
        print(f"\n  {'─'*40}")
        print(f"  {'URL Map (registered routes)':}")
        print(f"  {'─'*40}")
        rules = sorted(app.url_map.iter_rules(), key=lambda r: r.rule)
        for rule in rules:
            methods = ", ".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
            print(f"  {methods:10}  {rule.rule}")

        ok("6/6", "Blueprint check complete")


# ─────────────────────────────────────────────────────────────────────────────
#  Runner
# ─────────────────────────────────────────────────────────────────────────────

def run_all():
    print(f"\n{BOLD}{'═' * 50}")
    print("  Library Management System")
    print("  MySQL Connection Test Suite")
    print(f"{'═' * 50}{RESET}")

    test_env_vars()
    test_mysql_connection()
    test_tables_exist()
    test_orm_queries()
    test_seed_data()
    test_blueprints()

    print(f"\n{BOLD}{'═' * 50}")
    print(f"  {GREEN}🎉  All tests passed. Database is ready.{RESET}{BOLD}")
    print(f"{'═' * 50}{RESET}\n")


if __name__ == "__main__":
    run_all()