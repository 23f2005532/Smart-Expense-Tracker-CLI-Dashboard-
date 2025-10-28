"""
Database configuration and initialization for Smart Expense Tracker.

Handles:
- SQLAlchemy initialization and engine creation
- Flask app integration via init_app(app)
- Alembic migrations setup (auto-detects migration folder)
- Session utilities for scripts (seed, CLI, etc.)
"""

import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_migrate import Migrate

# global db object used throughout the app
db = SQLAlchemy()
engine = None
SessionLocal = None
migrate = None


def init_app(app):
    """
    Initialize SQLAlchemy and Alembic (Flask-Migrate) with the Flask app.
    This should be called once inside `app.py` after app creation.
    """
    global engine, SessionLocal, migrate

    # Bind SQLAlchemy
    db.init_app(app)

    # Create engine manually for scripts and external sessions
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI")
    engine = create_engine(db_uri, future=True)

    # Create a scoped session factory for use outside Flask contexts (CLI, seed, etc.)
    SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

    # Setup Alembic migrations
    migrate = Migrate(app, db, directory=os.path.join(os.path.dirname(__file__), "../migrations"))

    # Ensure database and tables exist for dev (skip in prod)
    with app.app_context():
        db.create_all()

    print(f"✅ Database initialized and Alembic migration environment ready at {migrate.directory}")


def get_db_session():
    """
    Return a SQLAlchemy session (useful for CLI commands or scripts).
    Remember to close it after use.
    """
    global SessionLocal
    if not SessionLocal:
        raise RuntimeError("Database not initialized. Call init_app(app) first.")
    return SessionLocal()


def close_db_session(session):
    """Gracefully close a session created via get_db_session()."""
    try:
        session.close()
    except Exception:
        pass
