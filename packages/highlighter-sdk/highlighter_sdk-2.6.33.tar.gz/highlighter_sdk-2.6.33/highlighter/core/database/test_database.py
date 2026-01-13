import shutil
from pathlib import Path

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

__all__ = [
    "TestDatabase",
    "RuntimeDatabaseTemplate",
]


class TestDatabase:
    """The Highlighter agent database

    Each instance creates its own in-memory SQLite database to ensure test isolation.
    """

    def __init__(self):
        # Create a fresh in-memory database for each instance
        # This ensures tests don't interfere with each other
        self.engine: Engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        SQLModel.metadata.create_all(self.engine)

    def get_session(self):
        return Session(self.engine)


class RuntimeDatabaseTemplate:
    """Create a single migrated SQLite DB that tests can restore quickly.

    Pytest spins up many ``Runtime`` instances and each one initialises
    ``highlighter.core.database.Database`` which, in turn, runs Alembic
    migrations. Applying all migrations for every test case is slow and noisy.

    ``RuntimeDatabaseTemplate`` initialises the on-disk database once per test
    session, captures the fully migrated file as ``database.template.sqlite``
    and provides a cheap ``reset()`` helper that clones the template back into
    ``database.sqlite`` before each test. That keeps the schema current while
    avoiding repeated calls to Alembic.
    """

    def __init__(self, cache_dir: Path):
        self._cache_dir = Path(cache_dir)
        self._db_dir = self._cache_dir / "agents" / "db"
        self._db_path = self._db_dir / "database.sqlite"
        self._template_path = self._db_dir / "database.template.sqlite"

    def prepare(self) -> None:
        """Ensure the template file exists and mirrors the latest migrations."""

        from highlighter.core.database.database import (
            Database,  # Local import to avoid cycles
        )

        self._db_dir.mkdir(parents=True, exist_ok=True)

        db = None
        try:
            db = Database()
            # ``Database`` runs Alembic migrations + metadata.create_all(...) on init
        finally:
            if db is not None:
                db.close()

        if not self._db_path.exists():
            raise RuntimeError(f"Expected database at {self._db_path} after migrations ran")

        shutil.copy2(self._db_path, self._template_path)

    def reset(self) -> None:
        """Restore the working DB from the pre-migrated template."""

        if not self._template_path.exists():
            raise RuntimeError("Runtime DB template missing – call prepare() first")

        self._db_dir.mkdir(parents=True, exist_ok=True)

        # Replace the working database with a pristine copy for the next test
        if self._db_path.exists():
            self._db_path.unlink()
        shutil.copy2(self._template_path, self._db_path)
