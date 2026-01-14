"""
Database Service with Connection Retry Logic for Timber Common

Features:
- Automatic retry on connection failures with exponential backoff
- SQLAlchemy session management with context managers
- Connection validation and health checks
- Connection pooling with configurable parameters
- Thread-safe singleton pattern
- Complete CRUD operations (query, count, create, update, delete, get_by_id)
- Advanced operations (get_or_create, upsert, bulk operations)
- Relationship management (add/set many-to-many)
"""

import time
import logging
from typing import Optional, Generator, Any, Dict, List, Type, Tuple
from contextlib import contextmanager
from sqlalchemy import create_engine, event, text, desc, asc
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase, joinedload
from sqlalchemy.exc import OperationalError, DBAPIError, IntegrityError
from sqlalchemy.pool import QueuePool

from common.utils.config import config

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class DBService:
    """
    Singleton service for managing SQLAlchemy engine and sessions with retry logic.
    
    Provides both low-level session management and high-level CRUD operations.
    """
    _instance: Optional['DBService'] = None
    _engine = None
    _SessionLocal = None
    _max_retries = 5
    _retry_delay = 2  # seconds

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBService, cls).__new__(cls)
            cls._instance._initialize_engine()
        return cls._instance

    def _initialize_engine(self, max_retries: int = 5, delay: int = 5):
        """
        Initializes the SQLAlchemy engine with connection pooling and retries.
        
        Args:
            max_retries: Maximum number of connection attempts
            delay: Delay between retries in seconds
        """
        db_url = config.get_db_url()
        pool_config = config.get_pool_config()
        
        logger.info(f"Attempting to initialize DB engine to {config.DB_HOST}:{config.DB_PORT}...")

        for attempt in range(max_retries):
            try:
                # Create engine with connection pooling
                self._engine = create_engine(
                    db_url,
                    echo=config.DATABASE_ECHO,
                    poolclass=QueuePool,
                    pool_size=pool_config['pool_size'],
                    max_overflow=pool_config['max_overflow'],
                    pool_timeout=pool_config['pool_timeout'],
                    pool_recycle=pool_config['pool_recycle'],
                    pool_pre_ping=True,  # Verify connections before using
                )
                
                # Set up event listeners for connection management
                @event.listens_for(self._engine, "connect")
                def receive_connect(dbapi_conn, connection_record):
                    """Log new connections."""
                    logger.debug("New database connection established")
                
                @event.listens_for(self._engine, "checkout")
                def receive_checkout(dbapi_conn, connection_record, connection_proxy):
                    """Validate connection on checkout from pool."""
                    logger.debug("Connection checked out from pool")
                
                # Create session factory
                self._SessionLocal = sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=self._engine
                )
                
                # Test the connection
                with self._engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                
                logger.info("DB engine successfully initialized.")
                return
                
            except (OperationalError, DBAPIError) as e:
                logger.error(f"DB connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise ConnectionError(
                        "Failed to connect to PostgreSQL after multiple retries."
                    ) from e

    def get_session(self, retry: bool = True) -> Session:
        """
        Creates a new database session with retry logic.
        
        Args:
            retry: Whether to retry on connection failure (default: True)
            
        Returns:
            SQLAlchemy Session object
            
        Raises:
            ConnectionError: If unable to create session after retries
        """
        if not self._SessionLocal:
            raise ConnectionError("Database engine is not initialized.")
        
        attempts = self._max_retries if retry else 1
        
        for attempt in range(attempts):
            try:
                session = self._SessionLocal()
                
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
                    wait_time = self._retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise ConnectionError(
                        f"Failed to create database session after {attempts} attempts"
                    ) from e

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.
        Automatically handles commits, rollbacks, and session cleanup.
        
        Usage:
            with db_service.session_scope() as session:
                user = User(name="John")
                session.add(user)
                # Auto-commits on exit if no exception
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session rolled back due to error: {e}")
            raise
        finally:
            session.close()

    def execute_query(
        self,
        query: str,
        params: Optional[dict] = None,
        fetch_one: bool = False,
        fetch_all: bool = False
    ) -> Any:
        """
        Execute a raw SQL query with automatic session management.
        
        Args:
            query: SQL query string
            params: Query parameters as dictionary
            fetch_one: Return single row
            fetch_all: Return all rows
            
        Returns:
            Query results or None
        """
        with self.session_scope() as session:
            result = session.execute(text(query), params or {})
            
            if fetch_one:
                return result.fetchone()
            elif fetch_all:
                return result.fetchall()
            else:
                return None

    def create_all_tables(self):
        """Create all tables defined in models that inherit from Base."""
        if not self._engine:
            raise ConnectionError("Database engine is not initialized.")
        
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=self._engine)
        logger.info("Database tables created successfully.")

    def drop_all_tables(self):
        """Drop all tables (use with caution!)."""
        if not self._engine:
            raise ConnectionError("Database engine is not initialized.")
        
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(bind=self._engine)
        logger.info("All database tables dropped.")

    def health_check(self) -> bool:
        """
        Check if database connection is healthy.
        
        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            with self.session_scope() as session:
                session.execute(text("SELECT 1"))
            logger.info("Database health check: OK")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    def get_engine(self):
        """Returns the SQLAlchemy engine (for advanced use cases)."""
        return self._engine

    def close(self):
        """Dispose of the engine and close all connections."""
        if self._engine:
            self._engine.dispose()
            logger.info("Database engine disposed and all connections closed.")

    # ========================================================================
    # Helper Methods for CRUD Operations
    # ========================================================================
    
    def _get_model_class(self, model_name: str) -> Type:
        """
        Get SQLAlchemy model class by name.
        
        Args:
            model_name: Name of the model (e.g., 'UserGoal', 'Notification')
            
        Returns:
            Model class
            
        Raises:
            ValueError: If model not found
        """
        # Lazy import to avoid circular dependency
        try:
            # Try the model registry first
            from common.models.registry import model_registry
            model_class = model_registry.get_model(model_name)
            if model_class:
                return model_class
        except (ImportError, AttributeError):
            pass
        
        try:
            # Try get_model function
            from common.models.registry import get_model
            model_class = get_model(model_name)
            if model_class:
                return model_class
        except (ImportError, AttributeError):
            pass
        
        try:
            # Try direct import from common.models
            from common import models
            model_class = getattr(models, model_name, None)
            if model_class:
                return model_class
        except (ImportError, AttributeError):
            pass
        
        raise ValueError(f"Unknown model: {model_name}. Model not found in registry.")
    
    def _apply_filters(self, query, model_class: Type, filters: Dict[str, Any]):
        """Apply filters to query."""
        # Handle None or empty filters
        if not filters:
            return query
        
        # Handle string filters (invalid input - return unfiltered)
        if isinstance(filters, str):
            logger.warning(f"Received string filters instead of dict: {filters}")
            return query
        
        # Handle non-dict filters
        if not isinstance(filters, dict):
            logger.warning(f"Received non-dict filters: {type(filters)}")
            return query
        
        # Apply filters
        for field, value in filters.items():
            if value is not None:  # Skip None values
                if hasattr(model_class, field):
                    query = query.filter(getattr(model_class, field) == value)
                else:
                    logger.warning(f"Model {model_class.__name__} has no field '{field}'")
        return query
    
    def _apply_ordering(self, query, model_class: Type, order_by: List[Dict[str, str]]):
        """Apply ordering to query."""
        for order_spec in order_by:
            if isinstance(order_spec, dict):
                for direction, field in order_spec.items():
                    if hasattr(model_class, field):
                        col = getattr(model_class, field)
                        if direction == 'desc':
                            query = query.order_by(desc(col))
                        else:
                            query = query.order_by(asc(col))
                    else:
                        logger.warning(f"Model {model_class.__name__} has no field '{field}'")
        return query
    
    def _load_relationships(self, query, model_class: Type, relationships: List[str]):
        """Eagerly load relationships."""
        for rel_name in relationships:
            if hasattr(model_class, rel_name):
                query = query.options(joinedload(getattr(model_class, rel_name)))
            else:
                logger.warning(f"Model {model_class.__name__} has no relationship '{rel_name}'")
        return query
    
    def _serialize_record(self, record, include_relationships: List[str] = None) -> Dict[str, Any]:
        """Convert SQLAlchemy model instance to dict."""
        if include_relationships is None:
            include_relationships = []
        
        # Serialize base columns
        result = {
            col.name: getattr(record, col.name)
            for col in record.__table__.columns
        }
        
        # Serialize relationships if loaded
        for rel_name in include_relationships:
            if hasattr(record, rel_name):
                rel_value = getattr(record, rel_name)
                if rel_value is not None:
                    if isinstance(rel_value, list):
                        # One-to-many or many-to-many
                        result[rel_name] = [
                            {col.name: getattr(item, col.name) for col in item.__table__.columns}
                            for item in rel_value
                        ]
                    else:
                        # Many-to-one or one-to-one
                        result[rel_name] = {
                            col.name: getattr(rel_value, col.name)
                            for col in rel_value.__table__.columns
                        }
        
        return result
    
    # ========================================================================
    # Basic CRUD Operations
    # ========================================================================
    
    def query(
        self,
        model: str,
        filters: Optional[Dict[str, Any]] = None,
        include_relationships: Optional[List[str]] = None,
        order_by: Optional[List[Dict[str, str]]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query database records.
        
        Args:
            model: Model name (e.g., 'UserGoal', 'Notification')
            filters: Dict of field: value pairs to filter by
            include_relationships: List of relationship names to eagerly load
            order_by: List of ordering specs [{'desc': 'created_at'}]
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of record dicts
            
        Example:
            results = db_service.query(
                model='UserGoal',
                filters={'user_id': 'abc123', 'status': 'active'},
                include_relationships=['tags'],
                order_by=[{'desc': 'created_at'}],
                limit=50
            )
        """
        # Normalize filters to dict
        if filters is None:
            filters = {}
        elif isinstance(filters, str):
            logger.warning(f"Filters passed as string, using empty filters. Got: {filters}")
            filters = {}
        elif not isinstance(filters, dict):
            logger.warning(f"Filters not a dict (type: {type(filters)}), using empty filters")
            filters = {}
        
        if include_relationships is None:
            include_relationships = []
        if order_by is None:
            order_by = []
        
        model_class = self._get_model_class(model)
        
        with self.session_scope() as session:
            # Build base query
            query = session.query(model_class)
            
            # Apply filters
            query = self._apply_filters(query, model_class, filters)
            
            # Load relationships
            query = self._load_relationships(query, model_class, include_relationships)
            
            # Apply ordering
            query = self._apply_ordering(query, model_class, order_by)
            
            # Apply pagination
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            
            # Execute query
            results = query.all()
            
            # Serialize results
            return [
                self._serialize_record(record, include_relationships)
                for record in results
            ]
    
    def count(
        self,
        model: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count database records matching filters.
        
        Args:
            model: Model name
            filters: Dict of field: value pairs to filter by
            
        Returns:
            Count of matching records
            
        Example:
            count = db_service.count(
                model='UserGoal',
                filters={'user_id': 'abc123', 'status': 'active'}
            )
        """
        if filters is None:
            filters = {}
        
        model_class = self._get_model_class(model)
        
        with self.session_scope() as session:
            query = session.query(model_class)
            query = self._apply_filters(query, model_class, filters)
            return query.count()
    
    def create(
        self,
        model: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new database record.
        
        Args:
            model: Model name
            data: Dict of field: value pairs for the new record
            
        Returns:
            Created record as dict
            
        Example:
            new_goal = db_service.create(
                model='UserGoal',
                data={
                    'user_id': 'abc123',
                    'title': 'Learn Python',
                    'status': 'active'
                }
            )
        """
        model_class = self._get_model_class(model)
        
        with self.session_scope() as session:
            # Create instance
            record = model_class(**data)
            
            # Save to database
            session.add(record)
            session.commit()
            session.refresh(record)
            
            # Serialize and return
            return self._serialize_record(record)
    
    def update(
        self,
        model: str,
        filters: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Dict[str, int]:
        """
        Update database records matching filters.
        
        Args:
            model: Model name
            filters: Dict of field: value pairs to identify records
            data: Dict of field: value pairs to update
            
        Returns:
            Dict with 'updated_count' key
            
        Example:
            result = db_service.update(
                model='UserGoal',
                filters={'id': 'goal-123'},
                data={'status': 'completed'}
            )
        """
        model_class = self._get_model_class(model)
        
        with self.session_scope() as session:
            query = session.query(model_class)
            query = self._apply_filters(query, model_class, filters)
            
            # Perform update
            count = query.update(data)
            session.commit()
            
            return {'updated_count': count}
    
    def delete(
        self,
        model: str,
        filters: Dict[str, Any]
    ) -> Dict[str, int]:
        """
        Delete database records matching filters.
        
        Args:
            model: Model name
            filters: Dict of field: value pairs to identify records
            
        Returns:
            Dict with 'deleted_count' key
            
        Example:
            result = db_service.delete(
                model='UserGoal',
                filters={'id': 'goal-123'}
            )
        """
        model_class = self._get_model_class(model)
        
        with self.session_scope() as session:
            query = session.query(model_class)
            query = self._apply_filters(query, model_class, filters)
            
            # Perform delete
            count = query.delete()
            session.commit()
            
            return {'deleted_count': count}
    
    def get_by_id(
        self,
        model: str,
        record_id: str,
        include_relationships: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a single record by ID.
        
        Args:
            model: Model name
            record_id: Primary key value
            include_relationships: List of relationships to load
            
        Returns:
            Record dict or None if not found
            
        Example:
            goal = db_service.get_by_id(
                model='UserGoal',
                record_id='goal-123',
                include_relationships=['tags']
            )
        """
        results = self.query(
            model=model,
            filters={'id': record_id},
            include_relationships=include_relationships,
            limit=1
        )
        return results[0] if results else None
    
    # ========================================================================
    # Advanced CRUD Operations
    # ========================================================================
    
    def get_or_create(
        self,
        model: str,
        filters: Dict[str, Any],
        defaults: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], bool]:
        """
        Get existing record or create if it doesn't exist.
        
        Args:
            model: Model name
            filters: Dict of field: value pairs to search for
            defaults: Dict of additional fields to set if creating (optional)
            
        Returns:
            Tuple of (record_dict, created_boolean)
            - record_dict: The found or created record
            - created_boolean: True if created, False if found existing
            
        Example:
            goal, created = db_service.get_or_create(
                model='UserGoal',
                filters={'user_id': 'abc123', 'title': 'Learn Python'},
                defaults={'status': 'active', 'progress': 0}
            )
            if created:
                print("Created new goal")
            else:
                print("Found existing goal")
        """
        if defaults is None:
            defaults = {}
        
        # Try to find existing record
        existing = self.query(model=model, filters=filters, limit=1)
        
        if existing:
            return existing[0], False
        
        # Create new record with filters + defaults
        create_data = {**filters, **defaults}
        new_record = self.create(model=model, data=create_data)
        
        return new_record, True
    
    def upsert(
        self,
        model: str,
        filters: Dict[str, Any],
        data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], bool]:
        """
        Update existing record or create if it doesn't exist.
        
        Args:
            model: Model name
            filters: Dict of field: value pairs to identify record
            data: Dict of field: value pairs to set
            
        Returns:
            Tuple of (record_dict, created_boolean)
            - record_dict: The updated or created record
            - created_boolean: True if created, False if updated
            
        Example:
            record, created = db_service.upsert(
                model='VectorEmbedding',
                filters={'content_id': 'doc-123'},
                data={'embedding': [0.1, 0.2, ...], 'updated_at': datetime.now()}
            )
        """
        # Try to find and update existing record
        existing = self.query(model=model, filters=filters, limit=1)
        
        if existing:
            # Update existing
            self.update(model=model, filters=filters, data=data)
            # Fetch updated record
            updated = self.query(model=model, filters=filters, limit=1)
            return updated[0], False
        
        # Create new record with filters + data
        create_data = {**filters, **data}
        new_record = self.create(model=model, data=create_data)
        
        return new_record, True
    
    def bulk_insert(
        self,
        model: str,
        records: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Insert multiple records at once (bulk operation).
        
        Args:
            model: Model name
            records: List of dicts, each containing field: value pairs
            
        Returns:
            Dict with 'inserted_count' key
            
        Example:
            result = db_service.bulk_insert(
                model='VectorEmbedding',
                records=[
                    {'content_id': 'doc-1', 'embedding': [...]},
                    {'content_id': 'doc-2', 'embedding': [...]},
                    {'content_id': 'doc-3', 'embedding': [...]}
                ]
            )
            # Returns: {'inserted_count': 3}
        """
        if not records:
            return {'inserted_count': 0}
        
        model_class = self._get_model_class(model)
        
        with self.session_scope() as session:
            # Create model instances
            instances = [model_class(**record_data) for record_data in records]
            
            # Bulk insert
            session.bulk_save_objects(instances)
            session.commit()
            
            return {'inserted_count': len(instances)}
    
    def bulk_update(
        self,
        model: str,
        updates: List[Dict[str, Any]],
        id_field: str = 'id'
    ) -> Dict[str, int]:
        """
        Update multiple records at once (bulk operation).
        
        Args:
            model: Model name
            updates: List of dicts, each containing fields to update including ID
            id_field: Name of the ID field (default: 'id')
            
        Returns:
            Dict with 'updated_count' key
            
        Example:
            result = db_service.bulk_update(
                model='Notification',
                updates=[
                    {'id': 'notif-1', 'read': True},
                    {'id': 'notif-2', 'read': True},
                    {'id': 'notif-3', 'read': True}
                ]
            )
            # Returns: {'updated_count': 3}
        """
        if not updates:
            return {'updated_count': 0}
        
        model_class = self._get_model_class(model)
        
        with self.session_scope() as session:
            # Use SQLAlchemy bulk_update_mappings
            session.bulk_update_mappings(model_class, updates)
            session.commit()
            
            return {'updated_count': len(updates)}
    
    def bulk_delete(
        self,
        model: str,
        filters: Dict[str, Any]
    ) -> Dict[str, int]:
        """
        Delete multiple records matching filters (bulk operation).
        
        This is essentially the same as regular delete() but explicitly named
        for bulk operations to make intent clear.
        
        Args:
            model: Model name
            filters: Dict of field: value pairs to identify records
            
        Returns:
            Dict with 'deleted_count' key
            
        Example:
            result = db_service.bulk_delete(
                model='VectorEmbedding',
                filters={'content_type': 'temp', 'created_before': date}
            )
        """
        return self.delete(model=model, filters=filters)
    
    # ========================================================================
    # Relationship Management Operations
    # ========================================================================
    
    def add_many_to_many(
        self,
        model: str,
        record_id: str,
        relationship: str,
        related_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Add items to a many-to-many relationship.
        
        Args:
            model: Model name (e.g., 'UserGoal')
            record_id: ID of the main record
            relationship: Name of the relationship (e.g., 'tags')
            related_ids: List of IDs to add to the relationship
            
        Returns:
            Dict with 'added_count' and 'record' keys
            
        Example:
            result = db_service.add_many_to_many(
                model='UserGoal',
                record_id='goal-123',
                relationship='tags',
                related_ids=['tag-1', 'tag-2', 'tag-3']
            )
        """
        model_class = self._get_model_class(model)
        
        with self.session_scope() as session:
            # Get the main record
            record = session.query(model_class).filter(
                getattr(model_class, 'id') == record_id
            ).first()
            
            if not record:
                raise ValueError(f"Record not found: {model} with id {record_id}")
            
            # Get the relationship attribute
            if not hasattr(record, relationship):
                raise ValueError(f"Model {model} has no relationship '{relationship}'")
            
            rel_attr = getattr(record, relationship)
            
            # Get related model class
            rel_property = getattr(model_class, relationship).property
            related_model_class = rel_property.mapper.class_
            
            # Query for related records
            related_records = session.query(related_model_class).filter(
                getattr(related_model_class, 'id').in_(related_ids)
            ).all()
            
            # Add to relationship (only adds if not already present)
            added_count = 0
            for related_record in related_records:
                if related_record not in rel_attr:
                    rel_attr.append(related_record)
                    added_count += 1
            
            session.commit()
            session.refresh(record)
            
            return {
                'added_count': added_count,
                'record': self._serialize_record(record, include_relationships=[relationship])
            }
    
    def set_many_to_many(
        self,
        model: str,
        record_id: str,
        relationship: str,
        related_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Set (replace) items in a many-to-many relationship.
        
        Clears existing relationships and sets to the provided list.
        
        Args:
            model: Model name (e.g., 'UserGoal')
            record_id: ID of the main record
            relationship: Name of the relationship (e.g., 'tags')
            related_ids: List of IDs to set as the relationship
            
        Returns:
            Dict with 'set_count' and 'record' keys
            
        Example:
            result = db_service.set_many_to_many(
                model='UserGoal',
                record_id='goal-123',
                relationship='tags',
                related_ids=['tag-1', 'tag-2']  # Replaces all existing tags
            )
        """
        model_class = self._get_model_class(model)
        
        with self.session_scope() as session:
            # Get the main record
            record = session.query(model_class).filter(
                getattr(model_class, 'id') == record_id
            ).first()
            
            if not record:
                raise ValueError(f"Record not found: {model} with id {record_id}")
            
            # Get the relationship attribute
            if not hasattr(record, relationship):
                raise ValueError(f"Model {model} has no relationship '{relationship}'")
            
            # Get related model class
            rel_property = getattr(model_class, relationship).property
            related_model_class = rel_property.mapper.class_
            
            # Query for related records
            related_records = session.query(related_model_class).filter(
                getattr(related_model_class, 'id').in_(related_ids)
            ).all()
            
            # Replace relationship
            setattr(record, relationship, related_records)
            
            session.commit()
            session.refresh(record)
            
            return {
                'set_count': len(related_records),
                'record': self._serialize_record(record, include_relationships=[relationship])
            }
    
    def remove_many_to_many(
        self,
        model: str,
        record_id: str,
        relationship: str,
        related_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Remove items from a many-to-many relationship.
        
        Args:
            model: Model name (e.g., 'UserGoal')
            record_id: ID of the main record
            relationship: Name of the relationship (e.g., 'tags')
            related_ids: List of IDs to remove from the relationship
            
        Returns:
            Dict with 'removed_count' and 'record' keys
            
        Example:
            result = db_service.remove_many_to_many(
                model='UserGoal',
                record_id='goal-123',
                relationship='tags',
                related_ids=['tag-2']  # Removes tag-2, keeps others
            )
        """
        model_class = self._get_model_class(model)
        
        with self.session_scope() as session:
            # Get the main record
            record = session.query(model_class).filter(
                getattr(model_class, 'id') == record_id
            ).first()
            
            if not record:
                raise ValueError(f"Record not found: {model} with id {record_id}")
            
            # Get the relationship attribute
            if not hasattr(record, relationship):
                raise ValueError(f"Model {model} has no relationship '{relationship}'")
            
            rel_attr = getattr(record, relationship)
            
            # Remove related records
            removed_count = 0
            for related_item in list(rel_attr):
                if getattr(related_item, 'id') in related_ids:
                    rel_attr.remove(related_item)
                    removed_count += 1
            
            session.commit()
            session.refresh(record)
            
            return {
                'removed_count': removed_count,
                'record': self._serialize_record(record, include_relationships=[relationship])
            }


# Create singleton instance
db_service = DBService()


# Helper function for dependency injection (e.g., with FastAPI)
def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for getting database sessions.
    
    Usage with FastAPI:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    session = db_service.get_session()
    try:
        yield session
    finally:
        session.close()