# timber/common/__init__.py
"""
Timber Common - Shared library for OakQuant workflow system

A comprehensive library providing:
- Config-driven model creation (NEW)
- Modular persistence services (NEW)
- Field-level encryption (NEW)
- GDPR compliance (NEW)
- Vector search integration (NEW)
- Data fetching from multiple financial APIs (yfinance, Alpha Vantage, Polygon.io)
- Database utilities and ORM support via SQLAlchemy
- Data validation and helpers
- Curated company data management

Quick Start (New Architecture):
    from timber.common import initialize_timber, get_model
    
    # Initialize Timber
    initialize_timber(
        model_config_dirs=['./config/models'],
        enable_encryption=True
    )
    
    # Use dynamic models
    User = get_model('User')
    StockResearchSession = get_model('StockResearchSession')

Quick Start (Legacy Services):
    from timber.common.services import stock_data_service
    
    # Fetch stock data
    df, error = stock_data_service.fetch_historical_data('AAPL', period='1y')
"""

__version__ = "0.2.0"

# =============================================================================
# NEW ARCHITECTURE - Core Timber Components
# =============================================================================

from .init import (
    initialize_timber,
    shutdown_timber,
    get_initialization_status,
    is_initialized,
    reset_initialization
)

# Import config instance and class
from .utils.config import config, Config
from .config.model_loader import model_loader, ModelConfigLoader

from .models.base import Base, db_manager
from .models.registry import (
    model_registry,
    register_model,
    get_model,
    get_session_model
)
from .models.factory import model_factory

from .models.mixins import (
    TimestampMixin,
    SoftDeleteMixin,
    EncryptedFieldMixin,
    GDPRComplianceMixin,
    SearchableMixin,
    CacheableMixin,
    AuditMixin
)

# =============================================================================
# CORE SERVICES 
# =============================================================================

# These are your existing services from the old architecture
# Import them conditionally to avoid breaking existing code

try:
    from common.services.data_fetcher import stock_data_service, StockDataService
    STOCK_DATA_AVAILABLE = True
except ImportError:
    STOCK_DATA_AVAILABLE = False
    stock_data_service = None
    StockDataService = None

try:
    from common.services.data_fetcher import curated_data_loader, CuratedDataLoader
    CURATED_DATA_AVAILABLE = True
except ImportError:
    CURATED_DATA_AVAILABLE = False
    curated_data_loader = None
    CuratedDataLoader = None

try:
    from .services.db_service import db_service, DBService, get_db
    DB_SERVICE_AVAILABLE = True
except ImportError:
    # Fall back to new db_manager
    DB_SERVICE_AVAILABLE = False
    db_service = None
    DBService = None
    # Use new architecture's get_db
    get_db = db_manager.get_db_session

# =============================================================================
# UTILITIES
# =============================================================================

try:
    from .utils.helpers import (
        parse_natural_period_to_dates,
        standardize_symbol,
        format_currency,
    )
    HELPERS_AVAILABLE = True
except ImportError:
    HELPERS_AVAILABLE = False
    parse_natural_period_to_dates = None
    standardize_symbol = None
    format_currency = None

try:
    from .utils.validators import (
        validate_stock_symbol,
        validate_date_string,
        validate_date_range,
        validate_dataframe,
        validate_price_data,
    )
    VALIDATORS_AVAILABLE = True
except ImportError:
    VALIDATORS_AVAILABLE = False
    validate_stock_symbol = None
    validate_date_string = None
    validate_date_range = None
    validate_dataframe = None
    validate_price_data = None

# =============================================================================
# SUBMODULES
# =============================================================================

from . import models

# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Version
    '__version__',
    
    # ===== NEW ARCHITECTURE =====
    
    # Initialization
    'initialize_timber',
    'shutdown_timber',
    'get_initialization_status',
    'is_initialized',
    'reset_initialization',
    
    # Configuration
    'config',
    'Config',
    'model_loader',
    'ModelConfigLoader',
    
    # Database
    'Base',
    'db_manager',
    'get_db',
    
    # Models
    'model_registry',
    'register_model',
    'get_model',
    'get_session_model',
    'model_factory',
    
    # Mixins
    'TimestampMixin',
    'SoftDeleteMixin',
    'EncryptedFieldMixin',
    'GDPRComplianceMixin',
    'SearchableMixin',
    'CacheableMixin',
    'AuditMixin',
    
    # ===== CORE SERVICES =====
    
    # Stock data service
    'stock_data_service',
    'StockDataService',
    
    # Curated data service
    'curated_data_loader',
    'CuratedDataLoader',
    
    # DB service (legacy)
    'db_service',
    'DBService',
    
    # ===== UTILITIES =====
    
    # Helpers
    'parse_natural_period_to_dates',
    'standardize_symbol',
    'format_currency',
    
    # Validators
    'validate_stock_symbol',
    'validate_date_string',
    'validate_date_range',
    'validate_dataframe',
    'validate_price_data',
    
    # ===== SUBMODULES =====
    
    'models',
]


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_version() -> str:
    """Return the current version of timber_common."""
    return __version__


def get_available_features() -> dict:
    """
    Get information about available features.
    
    Returns:
        Dictionary showing which features are available
    """
    return {
        'version': __version__,
        'new_architecture': {
            'models': True,
            'persistence': True,
            'encryption': True,
            'gdpr': True,
            'vector_search': True,
        },
        'legacy_services': {
            'stock_data_service': STOCK_DATA_AVAILABLE,
            'curated_data_loader': CURATED_DATA_AVAILABLE,
            'db_service': DB_SERVICE_AVAILABLE,
        },
        'utilities': {
            'helpers': HELPERS_AVAILABLE,
            'validators': VALIDATORS_AVAILABLE,
        }
    }


def validate_configuration() -> dict:
    """
    Validate the current configuration.
    
    Returns:
        Dictionary with validation results
    """
    results = {
        'new_architecture': True,
        'database_url': config.DATABASE_URL is not None,
        'encryption_key': config.ENCRYPTION_KEY is not None,
    }
    
    # Test database connection if initialized
    if db_manager._engine:
        results['database_connected'] = db_manager.check_connection()
    else:
        results['database_connected'] = None
        results['note'] = 'Database not initialized. Call initialize_timber() first.'
    
    # Check legacy services
    if DB_SERVICE_AVAILABLE and db_service:
        try:
            results['legacy_db_healthy'] = db_service.health_check()
        except Exception as e:
            results['legacy_db_healthy'] = False
            results['legacy_db_error'] = str(e)
    
    return results


def print_status():
    """Print current Timber status to console."""
    print("=" * 60)
    print("Timber Common Library Status")
    print("=" * 60)
    
    features = get_available_features()
    
    print(f"\nVersion: {features['version']}")
    
    print("\n🆕 New Architecture:")
    for feature, available in features['new_architecture'].items():
        status = "✓" if available else "✗"
        print(f"  {status} {feature}")
    
    print("\n📦 Legacy Services:")
    for service, available in features['legacy_services'].items():
        status = "✓" if available else "✗"
        print(f"  {status} {service}")
    
    print("\n🔧 Utilities:")
    for util, available in features['utilities'].items():
        status = "✓" if available else "✗"
        print(f"  {status} {util}")
    
    if db_manager._engine:
        status = get_initialization_status()
        print(f"\n📊 Database:")
        print(f"  Models registered: {status['models_registered']}")
        print(f"  Session types: {status['session_types']}")
        print(f"  Tables: {status['database_tables']}")
        print(f"  Connected: {status['database_connected']}")
    else:
        print(f"\n📊 Database: Not initialized")
        print(f"  Call initialize_timber() to set up")
    
    print("\n" + "=" * 60)