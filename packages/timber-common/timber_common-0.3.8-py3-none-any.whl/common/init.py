# timber/common/init.py
"""
Timber Initialization

Main entry point for initializing the Timber library with all models and services.
This should be called once at application startup.
"""

from typing import List, Optional
import logging

from .utils.config import config  # Use singleton instance, not class
from .config.model_loader import model_loader
from .models.base import db_manager, Base
from .models.registry import model_registry

logger = logging.getLogger(__name__)

# ============================================================================
# SINGLETON PROTECTION - Prevent double initialization
# ============================================================================
_timber_initialized = False
_initialization_lock = False


def initialize_timber(
    database_url: Optional[str] = None,
    model_config_dirs: Optional[List[str]] = None,
    enable_encryption: bool = config.ENABLE_ENCRYPTION,
    enable_auto_vector_ingestion: bool = config.ENABLE_AUTO_VECTOR_INGESTION,
    enable_gdpr: bool = config.ENABLE_GDPR,
    create_tables: bool = True,
    validate_config: bool = True,
    force_reinit: bool = False  # NEW: Allow forced re-initialization if needed
) -> None:
    """
    Initialize the Timber library with all models and services.
    
    This is the main entry point for using Timber. Call this once at
    application startup before using any models or services.
    
    **IMPORTANT**: This function is idempotent. Calling it multiple times
    will NOT re-initialize unless force_reinit=True is passed.
    
    Args:
        database_url: Database connection string (uses config.DATABASE_URL if not provided)
        model_config_dirs: List of directories containing model YAML configs
        enable_encryption: Enable field-level encryption
        enable_auto_vector_ingestion: Enable automatic vector DB ingestion
        enable_gdpr: Enable GDPR compliance features
        create_tables: Automatically create all database tables
        validate_config: Validate configuration before proceeding
        force_reinit: Force re-initialization even if already initialized
    
    Example:
        >>> from timber.common import initialize_timber
        >>> initialize_timber(
        ...     model_config_dirs=['./config/models'],
        ...     enable_encryption=True
        ... )
    """
    global _timber_initialized, _initialization_lock
    
    # ===== SINGLETON CHECK - Prevent double initialization =====
    if _timber_initialized and not force_reinit:
        logger.debug("Timber already initialized, skipping re-initialization")
        logger.debug(f"  Models registered: {len(model_registry.list_models())}")
        logger.debug(f"  Session types: {len(model_registry.list_session_types())}")
        logger.debug("  Call with force_reinit=True to force re-initialization")
        return
    
    # Prevent concurrent initialization
    if _initialization_lock:
        logger.warning("Timber initialization already in progress, waiting...")
        # In a production system, you might want to use a proper lock here
        return
    
    _initialization_lock = True
    
    try:
        logger.info("=" * 60)
        logger.info("Initializing Timber Library")
        logger.info("=" * 60)
        
        # ===== Step 1: Validate Configuration =====
        if validate_config:
            logger.info("Step 1: Validating configuration...")
            try:
                config.validate()
                logger.info("✓ Configuration validated")
            except ValueError as e:
                logger.error(f"✗ Configuration validation failed: {e}")
                raise
        
        # ===== Step 2: Initialize Database =====
        logger.info("Step 2: Initializing database...")
        db_url = database_url or config.DATABASE_URL
        
        try:
            db_manager.initialize(
                database_url=db_url,
                echo=config.DATABASE_ECHO,
                pool_size=config.DB_POOL_SIZE,
                max_overflow=config.DB_MAX_OVERFLOW,
                pool_recycle=config.DB_POOL_RECYCLE
            )
            
            # Test connection
            if db_manager.check_connection():
                logger.info("✓ Database initialized and connected")
            else:
                logger.warning("⚠ Database initialized but connection check failed")
                
        except Exception as e:
            logger.error(f"✗ Database initialization failed: {e}")
            raise
        
        # ===== Step 3: Load Core Models =====
        logger.info("Step 3: Loading core models...")
        try:
            # Import core models to register them
            from .models.core.user import User
            from .models.core.tag import Tag
            
            # Register core models
            model_registry.register_model(User)
            model_registry.register_model(Tag)
            
            logger.info(f"✓ Loaded {len(model_registry.list_models())} core models")
            
        except Exception as e:
            logger.error(f"✗ Core model loading failed: {e}")
            raise
        
        # ===== Step 4: Load Dynamic Models from Configs =====
        logger.info("Step 4: Loading dynamic models from configs...")
        
        if model_config_dirs is None:
            model_config_dirs = [str(config.MODEL_CONFIG_DIR)]
        
        try:
            for config_dir in model_config_dirs:
                logger.info(f"  Loading models from: {config_dir}")
                model_loader.load_from_directory(config_dir)
            
            total_models = len(model_registry.list_models())
            logger.info(f"✓ Total models loaded: {total_models}")
            
        except Exception as e:
            logger.error(f"✗ Dynamic model loading failed: {e}")
            raise
        
        # ===== Step 5: Set Up Encryption =====
        if enable_encryption:
            logger.info("Step 5: Setting up encryption...")
            
            if not config.ENCRYPTION_KEY:
                logger.warning("⚠ Encryption enabled but no ENCRYPTION_KEY set")
            else:
                try:
                    from .services.encryption.field_encryption import encryption_service
                    logger.info("✓ Encryption service initialized")
                except Exception as e:
                    logger.error(f"✗ Encryption setup failed: {e}")
                    raise
        else:
            logger.info("Step 5: Encryption disabled")
        
        # ===== Step 6: Set Up GDPR =====
        if enable_gdpr:
            logger.info("Step 6: Setting up GDPR compliance...")
            try:
                from .services.gdpr.deletion import gdpr_service
                logger.info("✓ GDPR service initialized")
            except Exception as e:
                logger.warning(f"⚠ GDPR setup failed: {e}")
                # Don't fail initialization for this
        else:
            logger.info("Step 6: GDPR compliance disabled")
        
        # ===== Step 7: Set Up Vector Ingestion =====
        if enable_auto_vector_ingestion:
            logger.info("Step 7: Setting up auto vector ingestion...")
            try:
                from .services.vector.auto_ingestion import setup_auto_ingestion
                
                setup_auto_ingestion()
                logger.info("✓ Auto vector ingestion enabled")
                
            except Exception as e:
                logger.warning(f"⚠ Auto vector ingestion setup failed: {e}")
                # Don't fail initialization for this
        else:
            logger.info("Step 7: Auto vector ingestion disabled")
        
        # ===== Step 8: Initialize Services =====
        logger.info("Step 8: Initializing services...")
        try:
            from .services.persistence import persistence_manager
            
            logger.info("✓ Services initialized")
            
        except Exception as e:
            logger.error(f"✗ Service initialization failed: {e}")
            raise
        
        # ===== Step 9: Create Database Tables =====
        if create_tables:
            logger.info("Step 9: Creating database tables...")
            try:
                db_manager.create_all_tables()
                
                # Log created tables
                tables = db_manager.get_table_names()
                logger.info(f"✓ Created {len(tables)} tables")
                logger.debug(f"  Tables: {', '.join(tables)}")
                
            except Exception as e:
                logger.error(f"✗ Table creation failed: {e}")
                raise
        else:
            logger.info("Step 9: Skipping table creation")
        
        # ===== Mark as initialized =====
        _timber_initialized = True
        
        # ===== Initialization Complete =====
        logger.info("=" * 60)
        logger.info("✓ Timber initialization complete!")
        logger.info("=" * 60)
        
        # Log summary
        logger.info("\nSummary:")
        logger.info(f"  Environment: {config.OAK_ENV}")
        logger.info(f"  Models registered: {len(model_registry.list_models())}")
        logger.info(f"  Session types: {len(model_registry.list_session_types())}")
        logger.info(f"  Database tables: {len(db_manager.get_table_names())}")
        logger.info(f"  Encryption: {'Enabled' if enable_encryption else 'Disabled'}")
        logger.info(f"  Auto vector ingestion: {'Enabled' if enable_auto_vector_ingestion else 'Disabled'}")
        logger.info(f"  GDPR: {'Enabled' if enable_gdpr else 'Disabled'}")
        logger.info("")
        
    finally:
        _initialization_lock = False


def shutdown_timber() -> None:
    """
    Shutdown Timber and clean up resources.
    
    Call this when shutting down the application to properly
    dispose of database connections and other resources.
    """
    global _timber_initialized
    
    logger.info("Shutting down Timber...")
    
    try:
        # Dispose of database engine
        db_manager.dispose()
        logger.info("✓ Database connections disposed")
        
        # Reset initialization flag
        _timber_initialized = False
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    
    logger.info("✓ Timber shutdown complete")


def get_initialization_status() -> dict:
    """
    Get current initialization status.
    
    Returns:
        Dictionary with initialization status including whether Timber is initialized
    """
    return {
        'initialized': _timber_initialized,
        'models_registered': len(model_registry.list_models()),
        'session_types': len(model_registry.list_session_types()),
        'database_tables': len(db_manager.get_table_names()) if db_manager._engine else 0,
        'database_connected': db_manager.check_connection() if db_manager._engine else False,
        'configuration': config.to_dict()
    }


def is_initialized() -> bool:
    """
    Check if Timber has been initialized.
    
    Returns:
        True if Timber is initialized, False otherwise
    """
    return _timber_initialized


def reset_initialization(confirm: bool = False) -> None:
    """
    Reset initialization state (FOR TESTING ONLY).
    
    This should only be used in test environments to reset state
    between tests. Never use in production code.
    
    Args:
        confirm: Must be True to actually reset (safety check)
    """
    global _timber_initialized
    
    if not confirm:
        raise ValueError(
            "reset_initialization() requires confirm=True. "
            "This function should only be used in tests!"
        )
    
    logger.warning("⚠ Resetting Timber initialization state (test mode)")
    _timber_initialized = False