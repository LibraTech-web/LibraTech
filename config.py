"""
config.py
=========
Centralised application configuration.

All sensitive values are read from environment variables (via .env).
Never hard-code credentials directly in this file.

Usage inside create_app():
    from config import config_map
    app.config.from_object(config_map[config_name])

Available config names:
    "development"  â†’  DevelopmentConfig   (DEBUG on, SQL echo on)
    "production"   â†’  ProductionConfig    (DEBUG off, strict settings)
    "testing"      â†’  TestingConfig       (in-memory SQLite, fast tests)
    "default"      â†’  DevelopmentConfig
"""

import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load .env from the project root (where this file lives)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


def _build_db_uri() -> str:
    """
    Construct the MySQL connection URI from individual .env variables.

    Prefer explicit DB_* values for local XAMPP setups,
    then fall back to DATABASE_URL for cloud deployments.
    """
    user = os.environ.get("DB_USER")
    host = os.environ.get("DB_HOST")
    name = os.environ.get("DB_NAME")
    port = os.environ.get("DB_PORT", "3306")
    password = os.environ.get("DB_PASSWORD", "")

    if user and host and name:
        return (
            f"mysql+pymysql://{quote_plus(user)}:{quote_plus(password)}"
            f"@{quote_plus(host)}:{port}/{quote_plus(name)}"
        )

    if os.environ.get("DATABASE_URL"):
        return os.environ["DATABASE_URL"]

    user = "root"
    password = ""
    host = "localhost"
    name = "library_db"

    # mysql+pymysql is the pure-Python driver - no C extension needed
    return (
        f"mysql+pymysql://{quote_plus(user)}:{quote_plus(password)}"
        f"@{quote_plus(host)}:{port}/{quote_plus(name)}"
    )


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  Base configuration  (shared across all environments)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class Config:
    APP_NAME = os.environ.get("APP_NAME", "LibraTech")

    # â”€â”€ Security â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-dev-key-change-me")

    # â”€â”€ Database â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    SQLALCHEMY_DATABASE_URI = _build_db_uri()

    # Disable Flask-SQLAlchemy modification tracking (deprecated, wastes memory)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Connection pool tuning for MySQL
    # pool_recycle: recycle connections before MySQL's default wait_timeout (8h)
    # pool_pre_ping: test each connection before using it â€” prevents stale errors
    # pool_size / max_overflow: control concurrent DB connections
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle":  280,
        "pool_pre_ping": True,
        "pool_size":     10,
        "max_overflow":  20,
    }

    # â”€â”€ Email (Flask-Mail) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    MAIL_SERVER         = os.environ.get("MAIL_SERVER",   "smtp.gmail.com")
    MAIL_PORT           = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS        = os.environ.get("MAIL_USE_TLS",  "true").lower() == "true"
    MAIL_USERNAME       = os.environ.get("MAIL_USERNAME", "").strip()
    MAIL_PASSWORD       = os.environ.get("MAIL_PASSWORD", "").replace(" ", "").strip()
    MAIL_DEFAULT_SENDER = (
        os.environ.get("MAIL_DEFAULT_SENDER")
        or os.environ.get("MAIL_USERNAME")
        or "noreply@library.local"
    )
    # If SMTP is not configured in development, show reset link in UI.
    SHOW_RESET_LINK_ON_EMAIL_FAIL = False

    # Default admin bootstrap.
    # Change these values before first production use, or override via .env.
    DEFAULT_ADMIN_ENABLED = os.environ.get("DEFAULT_ADMIN_ENABLED", "true").lower() == "true"
    DEFAULT_ADMIN_USERNAME = os.environ.get("DEFAULT_ADMIN_USERNAME", "admin").strip()
    DEFAULT_ADMIN_EMAIL = os.environ.get("DEFAULT_ADMIN_EMAIL", "natividadkaeza05@gmail.com").strip().lower()
    DEFAULT_ADMIN_NAME = os.environ.get("DEFAULT_ADMIN_NAME", "System Administrator").strip()
    DEFAULT_ADMIN_PASSWORD = os.environ.get("DEFAULT_ADMIN_PASSWORD", "Admin12345").strip()

    # â”€â”€ Library business rules (overridable via settings table at runtime) â”€â”€â”€â”€
    DEFAULT_LOAN_DAYS          = 14
    DEFAULT_MAX_BOOKS           = 3
    DEFAULT_FINE_PER_DAY        = 0.50   # USD
    DEFAULT_RESERVATION_EXPIRY  = 3      # days


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  Environment-specific subclasses
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class DevelopmentConfig(Config):
    """
    Local development.
    - DEBUG mode gives a browser debugger on unhandled exceptions.
    - SQLALCHEMY_ECHO prints every SQL statement to the terminal â€”
      very useful while writing queries, but noisy in production.
    """
    DEBUG            = True
    SQLALCHEMY_ECHO  = False
    SHOW_RESET_LINK_ON_EMAIL_FAIL = False


class ProductionConfig(Config):
    """
    Live server.
    - DEBUG must be False â€” never expose the debugger in production.
    - SQL echo is off to avoid leaking query details in logs.
    """
    DEBUG            = False
    SQLALCHEMY_ECHO  = False

    # Enforce a real secret key in production
    @classmethod
    def validate(cls):
        if cls.SECRET_KEY == "fallback-dev-key-change-me":
            raise RuntimeError(
                "SECRET_KEY is not set. "
                "Set the SECRET_KEY environment variable before deploying."
            )


class TestingConfig(Config):
    """
    Automated tests.
    - SQLite in-memory database: fast, no MySQL required for CI/CD.
    - TESTING=True disables error catching so exceptions propagate to test runner.
    - WTF_CSRF_ENABLED=False lets tests submit forms without tokens.
    """
    TESTING          = True
    DEBUG            = True
    SQLALCHEMY_ECHO  = False
    WTF_CSRF_ENABLED = False

    # In-memory SQLite â€” wiped between test sessions
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    # SQLite doesn't support pool_size / max_overflow
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle":  280,
        "pool_pre_ping": True,
    }



config_map: dict = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "testing":     TestingConfig,
    "default":     DevelopmentConfig,
}
