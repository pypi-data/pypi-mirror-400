import logging
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import NullPool
from sqlmodel import Session, SQLModel, create_engine

from highlighter.core.config import HighlighterRuntimeConfig

__all__ = [
    "Database",
]


def _set_sqlite_pragma(dbapi_conn, connection_record):
    """Configure SQLite connection for better concurrent access.

    This function is called automatically on each new database connection.
    """
    cursor = dbapi_conn.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for concurrency
        cursor.execute("PRAGMA synchronous=NORMAL")  # Faster with WAL mode
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        cursor.execute("PRAGMA temp_store=MEMORY")  # Use memory for temp tables
    finally:
        cursor.close()


class Database:
    """SQLite-backed metadata store used by the Runtime and Recorder.

    ``Database`` always ensures the schema is on the latest Alembic revision
    before exposing an engine. The pytest suite relies on
    ``RuntimeDatabaseTemplate`` (see ``highlighter.core.database.test_database``)
    to run ``Database`` once at session start, capture the migrated file, and
    cheaply reset the on-disk database before each test. Production code keeps
    calling ``Database`` directly.
    """

    def __init__(self):
        hl_cfg = HighlighterRuntimeConfig.load()
        self.highlighter_path_to_database_file = str(hl_cfg.agent.db_file())
        self._engine = create_engine(
            f"sqlite:///{self.highlighter_path_to_database_file}",
            connect_args={
                "check_same_thread": False,
                "timeout": 30,  # 30-second busy timeout
            },
            poolclass=NullPool,  # Disable pooling for SQLite - connections created/closed per use
        )

        # Configure SQLite for better concurrent access
        event.listens_for(self._engine, "connect")(_set_sqlite_pragma)

        # Run Alembic migrations to ensure schema is up to date
        self._run_migrations()

        # Create any tables that don't exist (for new databases)
        SQLModel.metadata.create_all(self._engine)

    def _run_migrations(self):
        """Run Alembic migrations to upgrade database schema."""
        from alembic.migration import MigrationContext
        from sqlalchemy import inspect

        # Get the directory containing alembic.ini
        alembic_dir = Path(__file__).parent
        alembic_ini_path = alembic_dir / "alembic.ini"

        if not alembic_ini_path.exists():
            # No migrations configured, skip
            return

        # Configure Alembic with absolute paths
        alembic_cfg = Config(str(alembic_ini_path))
        alembic_cfg.set_main_option("script_location", str(alembic_dir / "alembic"))
        alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{self.highlighter_path_to_database_file}")
        alembic_cfg.config_file_name = None  # Prevent alembic/env.py from reconfiguring logging
        self._configure_alembic_logging(alembic_cfg)

        # Check if database has migration history
        with self._engine.begin() as connection:
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()

            # Check if datafile table exists
            inspector = inspect(self._engine)
            tables = inspector.get_table_names()

            if current_rev is None and "datafile" in tables:
                # Database exists but no migration history - stamp it with initial migration
                command.stamp(alembic_cfg, "839d46550586")  # Initial migration revision

        # Run migrations to latest version
        command.upgrade(alembic_cfg, "head")

    def _configure_alembic_logging(self, alembic_cfg: Config) -> None:
        """Route Alembic logs through the Highlighter runtime handlers.

        Alembic's default behaviour is to read logging settings from
        ``alembic.ini`` and emit directly to stderr. That results in noisy test
        output and – more importantly – skips the application's RotatingFile
        handler. By disabling Alembic's logging configuration step and
        synchronising the ``alembic`` logger's level with the Highlighter logger
        we ensure migration messages respect ``HighlighterRuntimeConfig``
        settings and end up in the standard runtime log file.
        """

        # Skip Alembic's logging.config.fileConfig to avoid duplicate handlers
        alembic_cfg.attributes["configure_logger"] = False

        highlighter_logger = logging.getLogger("highlighter")
        # Inherit from root if the highlighter logger hasn't been configured yet
        effective_level = highlighter_logger.getEffectiveLevel()

        alembic_logger = logging.getLogger("alembic")
        alembic_logger.handlers.clear()
        alembic_logger.setLevel(effective_level)
        alembic_logger.propagate = True

    @property
    def engine(self) -> Engine:
        return self._engine

    def get_session(self):
        return Session(self.engine)

    def close(self):
        self._engine.dispose()  # Call this when shutting down your app
