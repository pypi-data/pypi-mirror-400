"""
Database utilities for SQLAlchemy operations.
"""
from typing import Generator, Optional
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy.pool import StaticPool

from common.utils.config import config


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self, database_url: Optional[str] = None, echo: Optional[bool] = None):
        """
        Initialize database manager.
        
        Args:
            database_url: Database URL (defaults to config.DATABASE_URL)
            echo: Enable SQL logging (defaults to config.DATABASE_ECHO)
        """
        self.database_url = database_url or config.get_db_url()
        self.echo = echo if echo is not None else config.DATABASE_ECHO
        
        # Configure engine based on database type
        engine_kwargs = {
            "echo": self.echo,
        }
        
        # Special handling for SQLite
        if self.database_url.startswith("sqlite"):
            engine_kwargs["connect_args"] = {"check_same_thread": False}
            # Use StaticPool for in-memory databases
            if ":memory:" in self.database_url:
                engine_kwargs["poolclass"] = StaticPool
        
        self.engine = create_engine(self.database_url, **engine_kwargs)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Enable foreign key constraints for SQLite
        if self.database_url.startswith("sqlite"):
            @event.listens_for(self.engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
    
    def create_all_tables(self):
        """Create all tables defined in models."""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_all_tables(self):
        """Drop all tables (use with caution!)."""
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope around a series of operations.
        
        Usage:
            with db.session_scope() as session:
                session.add(obj)
                # Changes are automatically committed
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def health_check(self) -> bool:
        """Check if database connection is healthy."""
        try:
            with self.session_scope() as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            print(f"Database health check failed: {e}")
            return False


# Create a default database manager instance
db_manager = DatabaseManager()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for getting database sessions.
    
    Usage with FastAPI:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()