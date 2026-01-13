"""PostgreSQL connection and SQLAlchemy setup for the SDK."""

from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# Create the declarative base for all SQLAlchemy models
Base = declarative_base()


class PostgresManager:
    """Manages PostgreSQL connections and sessions.

    Usage:
        from sdk_248 import postgres, Organization

        # Initialize PostgreSQL
        postgres.initialize(
            connection_string="postgresql://user:pass@host:5432/db"
        )

        # Use sessions
        with postgres.session() as session:
            orgs = session.query(Organization).all()

        # Or create tables
        postgres.create_tables()
    """

    _engine: Optional[Engine] = None
    _session_factory: Optional[sessionmaker] = None
    _initialized: bool = False

    def initialize(
        self,
        connection_string: str,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> None:
        """Initialize PostgreSQL connection.

        Args:
            connection_string: PostgreSQL connection URI
            echo: If True, log all SQL statements
            pool_size: Connection pool size
            max_overflow: Max connections beyond pool_size
        """
        self._engine = create_engine(
            connection_string,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self._session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
        )
        self._initialized = True

    def initialize_with_engine(self, engine: Engine) -> None:
        """Initialize with an existing SQLAlchemy engine.

        Args:
            engine: Existing SQLAlchemy Engine instance
        """
        self._engine = engine
        self._session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
        )
        self._initialized = True

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Get a database session (context manager).

        Yields:
            SQLAlchemy Session instance

        Example:
            with postgres.session() as session:
                orgs = session.query(Organization).all()
        """
        if not self._initialized:
            raise RuntimeError("PostgreSQL not initialized. Call initialize() first.")

        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_session(self) -> Session:
        """Create a new session (caller responsible for closing).

        Returns:
            SQLAlchemy Session instance
        """
        if not self._initialized:
            raise RuntimeError("PostgreSQL not initialized. Call initialize() first.")
        return self._session_factory()

    @property
    def engine(self) -> Engine:
        """Get the SQLAlchemy engine."""
        if not self._initialized:
            raise RuntimeError("PostgreSQL not initialized. Call initialize() first.")
        return self._engine

    def create_tables(self) -> None:
        """Create all tables defined in models."""
        if not self._initialized:
            raise RuntimeError("PostgreSQL not initialized. Call initialize() first.")
        Base.metadata.create_all(bind=self._engine)

    def drop_tables(self) -> None:
        """Drop all tables defined in models. Use with caution!"""
        if not self._initialized:
            raise RuntimeError("PostgreSQL not initialized. Call initialize() first.")
        Base.metadata.drop_all(bind=self._engine)

    @property
    def is_initialized(self) -> bool:
        """Check if the database is initialized."""
        return self._initialized


# Global instance for convenience
postgres = PostgresManager()
