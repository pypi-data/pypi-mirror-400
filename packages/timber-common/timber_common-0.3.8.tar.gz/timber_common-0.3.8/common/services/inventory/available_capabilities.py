# timber/common/services/inventory/available_capabilities.py
"""
Timber Available Capabilities Service

Self-documenting service that discovers and catalogs all Timber capabilities.
Provides JSON output detailing:
- Loaded models and their schemas
- Available services and their methods
- configuration settings
- Database capabilities
- How to use each feature

This serves as both documentation and a capability manager for applications
built on Timber.
"""

import json
import inspect
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import RelationshipProperty

from common.utils import config

from ...models.base import Base, db_manager
from ...models.registry import model_registry
from ...config import Config

logger = logging.getLogger(__name__)


class AvailableCapabilitiesService:
    """
    Discovers and catalogs all Timber capabilities.
    
    Provides a complete inventory of:
    - Models (tables, columns, relationships)
    - Services (methods, parameters, usage)
    - Configuration (settings, paths)
    - Database (connection info, statistics)
    
    Usage:
        capabilities = AvailableCapabilitiesService()
        report = capabilities.generate_full_inventory()
        print(json.dumps(report, indent=2))
    """
    
    def __init__(self, services: Optional[Dict[str, Any]] = None):
        """
        Initialize capabilities service.
        
        Args:
            services: Optional dictionary of services to inventory
                     Format: {'service_name': service_instance}
        """
        self.logger = logger
        self.services = services or {}
    
    # ========================================================================
    # Main Inventory Generation
    # ========================================================================
    
    def generate_full_inventory(self) -> Dict[str, Any]:
        """
        Generate complete inventory of all Timber capabilities.
        
        Returns:
            Dictionary containing full inventory with metadata
        """
        self.logger.info("Generating Timber capabilities inventory...")
        
        inventory = {
            "metadata": self._get_metadata(),
            "configuration": self._get_configuration_inventory(),
            "database": self._get_database_inventory(),
            "models": self._get_models_inventory(),
            "services": self._get_services_inventory(),
            "usage_examples": self._get_usage_examples(),
            "summary": {}  # Filled at end
        }
        
        # Generate summary statistics
        inventory["summary"] = self._generate_summary(inventory)
        
        self.logger.info("Timber capabilities inventory generated successfully")
        return inventory
    
    def save_inventory_to_file(self, filepath: str = "timber_capabilities.json") -> str:
        """
        Generate inventory and save to JSON file.
        
        Args:
            filepath: Path to save inventory JSON
        
        Returns:
            Path to saved file
        """
        inventory = self.generate_full_inventory()
        
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(inventory, f, indent=2, default=str)
        
        self.logger.info(f"Capabilities inventory saved to: {output_path.absolute()}")
        return str(output_path.absolute())
    
    # ========================================================================
    # Metadata
    # ========================================================================
    
    def _get_metadata(self) -> Dict[str, Any]:
        """Get inventory metadata."""
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "timber_version": "1.0.0",
            "inventory_version": "1.0.0",
            "description": "Complete inventory of Timber capabilities"
        }
    
    # ========================================================================
    # Configuration Inventory
    # ========================================================================
    
    def _get_configuration_inventory(self) -> Dict[str, Any]:
        """Get configuration settings inventory."""
        return {
            "description": "Timber configuration settings and paths",
            "settings": {
                "environment": {
                    "value": config.OAK_ENV,
                    "description": "Current environment (development/production)"
                },
                "database": {
                    "url": self._safe_database_url(config.DATABASE_URL),
                    "echo": config.DATABASE_ECHO,
                    "description": "Database connection settings"
                },
                "embedding": {
                    "model": config.EMBEDDING_MODEL,
                    "dimension": config.EMBEDDING_DIMENSION,
                    "description": "Vector embedding configuration"
                },
                "cache": {
                    "enabled": config.CACHE_ENABLED,
                    "ttl_hours": config.CACHE_TTL_HOURS,
                    "redis_enabled": config.REDIS_ENABLED,
                    "description": "Caching configuration"
                },
                "security": {
                    "encryption_enabled": config.ENABLE_ENCRYPTION,
                    "gdpr_enabled": config.ENABLE_GDPR,
                    "description": "Security and compliance settings"
                },
                "features": {
                    "auto_vector_ingestion": config.ENABLE_AUTO_VECTOR_INGESTION,
                    "description": "Feature flags"
                }
            },
            "paths": {
                "model_config_dir": str(config.MODEL_CONFIG_DIR),
                "description": "Directory containing YAML model configurations"
            },
            "logging": {
                "level": config.LOG_LEVEL,
                "description": "Logging verbosity level"
            },
            "usage": {
                "description": "How to access configuration",
                "example": "from common.config import config; db_url = config.DATABASE_URL"
            }
        }
    
    def _safe_database_url(self, url: str) -> str:
        """Sanitize database URL to hide credentials."""
        if '@' in url:
            protocol, rest = url.split('://', 1)
            if '@' in rest:
                _, host_and_db = rest.split('@', 1)
                return f"{protocol}://***:***@{host_and_db}"
        return url
    
    # ========================================================================
    # Database Inventory
    # ========================================================================
    
    def _get_database_inventory(self) -> Dict[str, Any]:
        """Get database connection and statistics inventory."""
        inventory = {
            "description": "Database connection and statistics",
            "connection": {
                "status": "connected" if db_manager._engine else "not initialized",
                "database_url": self._safe_database_url(config.DATABASE_URL),
            },
            "statistics": {},
            "capabilities": {
                "session_management": "Context managers and scoped sessions",
                "connection_pooling": "QueuePool with configurable size",
                "transaction_support": "Automatic rollback on error"
            },
            "usage": {
                "description": "How to use database sessions",
                "examples": [
                    {
                        "pattern": "Context Manager (Recommended)",
                        "code": "with db_manager.session_scope() as session:\n    session.add(obj)\n    session.commit()"
                    },
                    {
                        "pattern": "Manual Session",
                        "code": "session = db_manager.get_session()\ntry:\n    session.add(obj)\n    session.commit()\nfinally:\n    session.close()"
                    },
                    {
                        "pattern": "Dependency Injection (FastAPI)",
                        "code": "def endpoint(db: Session = Depends(db_manager.get_db_session)):\n    return db.query(User).all()"
                    }
                ]
            }
        }
        
        # Get statistics if database is connected
        if db_manager._engine:
            try:
                table_names = db_manager.get_table_names()
                inventory["statistics"] = {
                    "total_tables": len(table_names),
                    "table_names": sorted(table_names)
                }
            except Exception as e:
                inventory["statistics"] = {"error": str(e)}
        
        return inventory
    
    # ========================================================================
    # Models Inventory
    # ========================================================================
    
    def _get_models_inventory(self) -> Dict[str, Any]:
        """Get complete models inventory with schemas and relationships."""
        inventory = {
            "description": "All loaded SQLAlchemy models with full schemas",
            "total_models": len(model_registry._models),
            "models": {}
        }
        
        # Get all registered models
        for model_name, model_class in model_registry._models.items():
            inventory["models"][model_name] = self._get_model_details(model_class)
        
        # Add session type registry
        if model_registry._session_types:
            inventory["session_types"] = {
                session_type: model_name
                for session_type, model_name in model_registry._session_types.items()
            }
        
        return inventory
    
    def _get_model_details(self, model_class: type) -> Dict[str, Any]:
        """Get detailed information about a model."""
        mapper = sa_inspect(model_class)
        
        details = {
            "table_name": model_class.__tablename__,
            "description": model_class.__doc__ or "No description available",
            "module": model_class.__module__,
            "columns": self._get_columns_info(mapper),
            "relationships": self._get_relationships_info(mapper),
            "primary_keys": [col.name for col in mapper.primary_key],
            "usage": {
                "description": f"How to use {model_class.__name__}",
                "import": f"from common.models.registry import model_registry; {model_class.__name__} = model_registry.get_model('{model_class.__name__}')",
                "create": f"obj = {model_class.__name__}(column1=value1, column2=value2)",
                "query": f"session.query({model_class.__name__}).filter_by(id=1).first()"
            }
        }
        
        # Add session type if applicable
        if hasattr(model_class, '__session_type__'):
            details["session_type"] = model_class.__session_type__
        
        # Add mixins if available
        if hasattr(model_class, '_config') and 'mixins' in model_class._config:
            details["mixins"] = model_class._config['mixins']
        
        return details
    
    def _get_columns_info(self, mapper) -> Dict[str, Dict[str, Any]]:
        """Get detailed column information."""
        columns = {}
        
        for col in mapper.columns:
            col_info = {
                "type": str(col.type),
                "nullable": col.nullable,
                "primary_key": col.primary_key,
                "unique": col.unique,
                "index": col.index if hasattr(col, 'index') else False,
                "description": col.doc or "No description"
            }
            
            # Add foreign key info
            if col.foreign_keys:
                fk = list(col.foreign_keys)[0]
                col_info["foreign_key"] = {
                    "references": str(fk.column),
                    "target_table": fk.column.table.name
                }
            
            # Add default value
            if col.default:
                col_info["default"] = str(col.default.arg) if hasattr(col.default, 'arg') else str(col.default)
            
            columns[col.name] = col_info
        
        return columns
    
    def _get_relationships_info(self, mapper) -> Dict[str, Dict[str, Any]]:
        """Get detailed relationship information."""
        relationships = {}
        
        for rel_name, rel_prop in mapper.relationships.items():
            rel_info = {
                "type": self._determine_relationship_type(rel_prop),
                "target_model": rel_prop.mapper.class_.__name__,
                "lazy": rel_prop.lazy,
                "uselist": rel_prop.uselist,
                "description": f"Relationship to {rel_prop.mapper.class_.__name__}"
            }
            
            # Add cascade info
            if rel_prop.cascade:
                rel_info["cascade"] = str(rel_prop.cascade)
            
            # Add secondary table for many-to-many
            if rel_prop.secondary is not None:
                rel_info["secondary_table"] = rel_prop.secondary.name
                rel_info["relationship_type"] = "many-to-many"
            
            relationships[rel_name] = rel_info
        
        return relationships
    
    def _determine_relationship_type(self, rel_prop: RelationshipProperty) -> str:
        """Determine the type of relationship."""
        if rel_prop.secondary is not None:
            return "many-to-many"
        elif rel_prop.uselist:
            return "one-to-many"
        else:
            return "many-to-one"
    
    # ========================================================================
    # Services Inventory
    # ========================================================================
    
    def _get_services_inventory(self) -> Dict[str, Any]:
        """Get inventory of all available services."""
        inventory = {
            "description": "Available Timber services and their methods",
            "services": {}
        }
        
        # Add provided services
        for service_name, service_instance in self.services.items():
            inventory["services"][service_name] = self._get_service_details(
                service_instance, 
                f"{service_name} service"
            )
        
        # Add db_manager
        inventory["services"]["db_manager"] = self._get_db_manager_details()
        
        inventory["usage"] = {
            "description": "How to use services",
            "import": "Services are typically imported from their modules",
            "singleton": "Most services are singletons - always use the imported instance"
        }
        
        return inventory
    
    def _get_service_details(self, service: Any, description: str) -> Dict[str, Any]:
        """Get detailed information about a service."""
        service_class = service.__class__
        
        details = {
            "description": description,
            "class": service_class.__name__,
            "module": service_class.__module__,
            "singleton": True,
            "methods": {}
        }
        
        # Get all public methods
        for name, method in inspect.getmembers(service_class, predicate=inspect.isfunction):
            if not name.startswith('_'):  # Public methods only
                details["methods"][name] = self._get_method_details(method)
        
        return details
    
    def _get_method_details(self, method) -> Dict[str, Any]:
        """Get detailed information about a method."""
        sig = inspect.signature(method)
        
        details = {
            "description": method.__doc__.strip().split('\n')[0] if method.__doc__ else "No description",
            "parameters": {},
            "returns": "See docstring for return type"
        }
        
        # Get parameter details
        for param_name, param in sig.parameters.items():
            if param_name != 'self':
                param_info = {
                    "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                    "required": param.default == inspect.Parameter.empty
                }
                if param.default != inspect.Parameter.empty:
                    param_info["default"] = str(param.default)
                
                details["parameters"][param_name] = param_info
        
        return details
    
    def _get_db_manager_details(self) -> Dict[str, Any]:
        """Get database manager details."""
        return {
            "description": "Database connection and session management",
            "class": "DatabaseManager",
            "module": "common.models.base",
            "singleton": True,
            "methods": {
                "get_session": {
                    "description": "Get a new database session",
                    "parameters": {},
                    "returns": "Session"
                },
                "session_scope": {
                    "description": "Context manager for transactional scope",
                    "parameters": {},
                    "returns": "Generator[Session]",
                    "usage": "with db_manager.session_scope() as session: ..."
                },
                "create_all_tables": {
                    "description": "Create all tables in database",
                    "parameters": {},
                    "returns": "None"
                },
                "check_connection": {
                    "description": "Check if database connection is working",
                    "parameters": {},
                    "returns": "bool"
                }
            }
        }
    
    # ========================================================================
    # Usage Examples
    # ========================================================================
    
    def _get_usage_examples(self) -> Dict[str, Any]:
        """Get comprehensive usage examples."""
        return {
            "description": "Common usage patterns and examples",
            "initialization": {
                "description": "How to initialize Timber in your application",
                "code": """
from common import initialize_timber

# Initialize with model configs
initialize_timber(
    model_config_dirs=['data/models'],
    enable_encryption=False,
    enable_auto_vector_ingestion=False
)
"""
            },
            "working_with_models": {
                "description": "Query and manipulate models",
                "code": """
from common.models.base import db_manager
from common.models.registry import model_registry

# Get a model class
User = model_registry.get_model('User')

# Create a record
with db_manager.session_scope() as session:
    user = User(id="123", username="john")
    session.add(user)
    session.commit()

# Query records
with db_manager.session_scope() as session:
    users = session.query(User).filter_by(username="john").all()
"""
            },
            "using_services": {
                "description": "How to use Timber services",
                "code": """
# Services are pre-loaded by the loader
# Access them from the capabilities object or import directly

# Example: Using session service (if loaded)
# from common.services.persistence.session import session_service
# session = session_service.create_session(...)
"""
            }
        }
    
    # ========================================================================
    # Summary
    # ========================================================================
    
    def _generate_summary(self, inventory: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from inventory."""
        return {
            "total_models": len(inventory["models"]["models"]),
            "total_tables": inventory["database"]["statistics"].get("total_tables", 0),
            "total_services": len(inventory["services"]["services"]),
            "environment": inventory["configuration"]["settings"]["environment"]["value"],
            "database_status": inventory["database"]["connection"]["status"],
            "features_enabled": {
                "encryption": inventory["configuration"]["settings"]["security"]["encryption_enabled"],
                "gdpr": inventory["configuration"]["settings"]["security"]["gdpr_enabled"],
                "auto_vector_ingestion": inventory["configuration"]["settings"]["features"]["auto_vector_ingestion"],
                "caching": inventory["configuration"]["settings"]["cache"]["enabled"]
            }
        }
    
    # ========================================================================
    # Query Methods
    # ========================================================================
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific model.
        
        Args:
            model_name: Name of the model
        
        Returns:
            Model information dictionary or None if not found
        """
        model_class = model_registry.get_model(model_name)
        if model_class:
            return self._get_model_details(model_class)
        return None
    
    def list_all_models(self) -> List[str]:
        """
        Get list of all registered model names.
        
        Returns:
            List of model names
        """
        return sorted(model_registry._models.keys())
    
    def list_all_services(self) -> List[str]:
        """
        Get list of all available service names.
        
        Returns:
            List of service names
        """
        return list(self.services.keys()) + ['db_manager']
    
    def get_capabilities_summary(self) -> Dict[str, Any]:
        """
        Get a quick summary of Timber capabilities.
        
        Returns:
            Summary dictionary
        """
        inventory = self.generate_full_inventory()
        return inventory["summary"]


def print_capabilities_summary(capabilities: AvailableCapabilitiesService):
    """Print a summary of Timber capabilities to console."""
    summary = capabilities.get_capabilities_summary()
    
    print("\n" + "="*70)
    print("TIMBER CAPABILITIES SUMMARY")
    print("="*70)
    print(f"Environment: {summary['environment']}")
    print(f"Database Status: {summary['database_status']}")
    print(f"\nModels Loaded: {summary['total_models']}")
    print(f"Database Tables: {summary['total_tables']}")
    print(f"Services Available: {summary['total_services']}")
    print(f"\nFeatures Enabled:")
    for feature, enabled in summary['features_enabled'].items():
        status = "✓" if enabled else "✗"
        print(f"  {status} {feature}")
    print("="*70)
    print("\nFor full inventory: capabilities.generate_full_inventory()")
    print("Save to file: capabilities.save_inventory_to_file('inventory.json')")
    print("="*70 + "\n")