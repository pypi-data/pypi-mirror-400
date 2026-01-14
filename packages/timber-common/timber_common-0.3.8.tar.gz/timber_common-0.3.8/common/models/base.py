# timber/common/models/base.py
"""
Base Model Infrastructure

Provides the SQLAlchemy declarative base and database management utilities.
All models should inherit from Base.

ENHANCED: Now includes connection retry logic to handle authentication and network issues.
"""

import time
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import OperationalError, DBAPIError
from contextlib import contextmanager
from typing import Optional, Generator
import logging

logger = logging.getLogger(__name__)

# Create the declarative base (SQLAlchemy 2.0 compatible)
Base = declarative_base()


class DatabaseManager:
    """
    Manages database connections, sessions, and operations.
    
    Singleton pattern ensures only one instance manages the database.
    Provides session management with context managers and pooling.
    
    ENHANCED: Includes automatic retry logic for connection failures.
    """
    
    _instance: Optional['DatabaseManager'] = None
    _engine = None
    _session_factory = None
    _scoped_session_factory = None
    
    # Retry configuration
    _max_retries = 5
    _retry_delay = 2  # seconds
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized_instance = False
        return cls._instance
    
    def __init__(self):
        if self._initialized_instance:
            return
        self._initialized_instance = True
        logger.info("DatabaseManager created")
    
    def initialize(
        self,
        database_url: str,
        echo: bool = False,
        pool_size: int = 20,
        max_overflow: int = 40,
        pool_pre_ping: bool = True,
        pool_recycle: int = 3600,
        max_retries: int = 5,
        retry_delay: int = 2
    ):
        """
        Initialize the database engine and session factories with retry logic.
        
        Args:
            database_url: SQLAlchemy database URL
            echo: If True, log all SQL statements
            pool_size: Number of connections to maintain in the pool
            max_overflow: Maximum overflow size of the pool
            pool_pre_ping: Test connections before using them
            pool_recycle: Recycle connections after this many seconds
            max_retries: Maximum number of connection attempts
            retry_delay: Base delay between retries (uses exponential backoff)
        """
        if self._engine is not None and self._initialized:
            logger.warning("Database already initialized. Skipping.")
            return
        
        logger.info(f"Initializing database engine (with retry logic)...")
        logger.info(f"Connection attempts: {max_retries}, Base delay: {retry_delay}s")
        
        # Store retry configuration
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        
        # Try to connect with retries
        for attempt in range(max_retries):
            try:
                logger.info(f"Connection attempt {attempt + 1}/{max_retries}...")
                
                # Create engine with connection pooling
                self._engine = create_engine(
                    database_url,
                    echo=echo,
                    poolclass=QueuePool,
                    pool_size=pool_size,
                    max_overflow=max_overflow,
                    pool_pre_ping=pool_pre_ping,
                    pool_recycle=pool_recycle
                )
                
                # Create session factories
                self._session_factory = sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=self._engine
                )
                self._scoped_session_factory = scoped_session(self._session_factory)
                
                # Set up event listeners
                self._setup_event_listeners()
                
                # Test the connection
                logger.info("Testing database connection...")
                with self._engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                    logger.info("✓ Connection test successful")
                
                # Mark as initialized
                self._initialized = True
                logger.info("✓ Database engine initialized successfully")
                return
                
            except (OperationalError, DBAPIError) as e:
                logger.error(f"✗ Connection attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # Final attempt failed
                    logger.error("=" * 70)
                    logger.error("FATAL: Failed to connect to database after all retries")
                    logger.error("=" * 70)
                    logger.error(f"Database URL: {self._mask_credentials(database_url)}")
                    logger.error(f"Error: {e}")
                    logger.error("")
                    logger.error("Possible causes:")
                    logger.error("  1. Wrong password in DATABASE_URL (.env file)")
                    logger.error("  2. Database user doesn't exist")
                    logger.error("  3. Database server not running")
                    logger.error("  4. Wrong host or port")
                    logger.error("")
                    logger.error("To fix:")
                    logger.error("  1. Check your .env file DATABASE_URL")
                    logger.error("  2. Verify PostgreSQL is running: pg_isready")
                    logger.error("  3. Test connection: psql <DATABASE_URL>")
                    logger.error("=" * 70)
                    raise ConnectionError(
                        f"Failed to connect to database after {max_retries} attempts"
                    ) from e
    
    def _mask_credentials(self, url: str) -> str:
        """Mask credentials in database URL for logging."""
        if '@' in url:
            protocol, rest = url.split('://', 1)
            if '@' in rest:
                _, host_and_db = rest.split('@', 1)
                return f"{protocol}://***:***@{host_and_db}"
        return url
    
    def _setup_event_listeners(self):
        """Set up SQLAlchemy event listeners for monitoring."""
        @event.listens_for(self._engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            logger.debug("New database connection established")
        
        @event.listens_for(self._engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            logger.debug("Connection checked out from pool")
        
        @event.listens_for(self._engine, "checkin")
        def receive_checkin(dbapi_conn, connection_record):
            logger.debug("Connection returned to pool")
    
    def get_engine(self):
        """Get the SQLAlchemy engine."""
        if self._engine is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._engine
    
    def get_session(self, retry: bool = True) -> Session:
        """
        Get a new database session with optional retry logic.
        
        Args:
            retry: Whether to retry on connection failure
        
        Returns:
            New SQLAlchemy session
        """
        if self._session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        attempts = self._max_retries if retry else 1
        
        for attempt in range(attempts):
            try:
                session = self._session_factory()
                
                # Validate session with a simple query
                try:
                    session.execute(text("SELECT 1"))
                except Exception as e:
                    logger.error(f"Session validation failed: {e}")
                    session.close()
                    raise
                
                return session
                
            except (OperationalError, DBAPIError) as e:
                logger.error(f"Session creation attempt {attempt + 1} failed: {e}")
                
                if attempt < attempts - 1:
                    wait_time = self._retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise ConnectionError(
                        f"Failed to create database session after {attempts} attempts"
                    ) from e
    
    def get_scoped_session(self) -> Session:
        """
        Get a thread-local scoped session.
        
        Returns:
            Thread-local SQLAlchemy session
        """
        if self._scoped_session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._scoped_session_factory()
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope around a series of operations.
        
        Usage:
            with db_manager.session_scope() as session:
                user = User(name='John')
                session.add(user)
                # Automatically commits on exit
        
        Yields:
            SQLAlchemy session that will automatically commit or rollback
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
            logger.debug("Session committed successfully")
        except Exception as e:
            session.rollback()
            logger.error(f"Session rollback due to error: {e}")
            raise
        finally:
            session.close()
            logger.debug("Session closed")
    
    def create_all_tables(self):
        """
        Create all tables defined in models.
        
        This should be called after all models have been imported/registered.
        """
        if self._engine is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        logger.info("Creating all database tables...")
        try:
            Base.metadata.create_all(self._engine)
            logger.info("All tables created successfully")
        except (OperationalError, DBAPIError) as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def drop_all_tables(self):
        """
        Drop all tables. USE WITH CAUTION!
        
        This will delete all data in the database.
        """
        if self._engine is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(self._engine)
        logger.warning("All tables dropped")
    
    def dispose(self):
        """
        Dispose of the connection pool.
        
        Call this when shutting down the application.
        """
        if self._engine is not None:
            logger.info("Disposing database engine...")
            self._engine.dispose()
            self._engine = None
            self._session_factory = None
            self._scoped_session_factory = None
            self._initialized = False
            logger.info("Database engine disposed")
    
    def get_db_session(self) -> Generator[Session, None, None]:
        """
        Dependency injection helper for FastAPI/Flask.
        
        Usage (FastAPI):
            @app.get("/users/")
            def get_users(db: Session = Depends(db_manager.get_db_session)):
                return db.query(User).all()
        
        Yields:
            Database session
        """
        session = self.get_session()
        try:
            yield session
        finally:
            session.close()
    
    def execute_sql(self, sql: str, params: dict = None):
        """
        Execute raw SQL statement.
        
        Args:
            sql: SQL statement to execute
            params: Parameters for the SQL statement
        
        Returns:
            Result of the SQL execution
        """
        with self.session_scope() as session:
            result = session.execute(text(sql), params or {})
            return result
    
    def check_connection(self) -> bool:
        """
        Check if database connection is working.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            with self.session_scope() as session:
                session.execute(text("SELECT 1"))
            logger.info("Database connection check: OK")
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False
    
    def get_table_names(self) -> list:
        """
        Get list of all table names in the database.
        
        Returns:
            List of table names
        """
        if self._engine is None:
            raise RuntimeError("Database not initialized")
        
        from sqlalchemy import inspect
        inspector = inspect(self._engine)
        return inspector.get_table_names()
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.
        
        Args:
            table_name: Name of the table
        
        Returns:
            True if table exists, False otherwise
        """
        return table_name in self.get_table_names()


# Singleton instance
db_manager = DatabaseManager()


# Convenience function for backward compatibility
def get_db():
    """Get a database session (generator for dependency injection)."""
    return db_manager.get_db_session()