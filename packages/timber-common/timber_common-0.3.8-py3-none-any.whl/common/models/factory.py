# timber/common/models/factory.py
"""
Model Factory for Configuration-Driven Model Generation

Dynamically creates SQLAlchemy models from YAML/JSON configuration files.
Supports encryption, caching, GDPR compliance, and relationships.

FIXED VERSION - Corrects primaryjoin/secondaryjoin evaluation issue
"""

from typing import Dict, Any, Type, List, Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, Date, JSON, Time, Interval, LargeBinary, Numeric
from sqlalchemy import ForeignKey, Index, UniqueConstraint, Table, MetaData 
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import DeclarativeMeta
import uuid
import logging
import sys 
import types

from .registry import model_registry
from .base import Base
from .mixins import get_mixin_class

logger = logging.getLogger(__name__)

# Make Base.metadata available in the module scope
metadata = Base.metadata

# ============================================================================
# CRITICAL FIX: Inject Base and metadata into dynamic module's scope
# ============================================================================
DYNAMIC_MODEL_MODULE = 'common.models.dynamic'

try:
    # Check if the module is already loaded
    dynamic_module = sys.modules.get(DYNAMIC_MODEL_MODULE)
    
    if not dynamic_module:
        # Create the module object in memory and add it to sys.modules
        dynamic_module = types.ModuleType(DYNAMIC_MODEL_MODULE)
        sys.modules[DYNAMIC_MODEL_MODULE] = dynamic_module
        logger.debug(f"Created dynamic module placeholder: {DYNAMIC_MODEL_MODULE}")
    
    # Force the required objects into the dynamic module's scope
    setattr(dynamic_module, 'Base', Base) 
    setattr(dynamic_module, 'metadata', metadata) 
    logger.debug(f"Injected 'Base' and 'metadata' into {DYNAMIC_MODEL_MODULE} scope.")
    
except Exception as e:
    logger.error(f"FATAL SCOPE INJECTION FAILURE: {e}") 


# Try to import pgvector if available
try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    class Vector:
        def __init__(self, dimension):
            pass
    logger.warning("pgvector is not installed. Vector model type will be a placeholder.")


# Type mapping from config strings to SQLAlchemy types
TYPE_MAPPING = {
    'String': String,
    'Integer': Integer,
    'Float': Float,
    'Boolean': Boolean,
    'Text': Text,
    'DateTime': DateTime,
    'Date': Date,
    'JSON': JSON,
    'Vector': Vector,
    'Time': Time,
    'Interval': Interval,
    'Numeric': Numeric,
    'Decimal': Numeric,
    'LargeBinary': LargeBinary,
    'Binary': LargeBinary,
    'Blob': LargeBinary,
}


def parse_column_type(type_str: str) -> Any:
    """
    Parse a column type string into SQLAlchemy type.
    
    Examples:
        'String(36)' -> String(36)
        'Integer' -> Integer
        'Text' -> Text
        'Vector(1536)' -> Vector(1536)
    
    Args:
        type_str: Type string from config
    
    Returns:
        SQLAlchemy type instance
    """
    # Handle parameterized types like String(36)
    if '(' in type_str:
        base_type, params = type_str.split('(', 1)
        params = params.rstrip(')')
        
        if base_type not in TYPE_MAPPING:
            raise ValueError(f"Unknown type: {base_type}")
        
        # Parse parameters (handle both single and multiple params)
        param_values = [p.strip() for p in params.split(',')]
        param_values = [int(p) if p.isdigit() else p for p in param_values]
        
        if len(param_values) == 1:
            return TYPE_MAPPING[base_type](param_values[0])
        else:
            return TYPE_MAPPING[base_type](*param_values)
    
    # Handle simple types
    if type_str not in TYPE_MAPPING:
        raise ValueError(f"Unknown type: {type_str}")
    
    return TYPE_MAPPING[type_str]


def create_column_from_config(col_config: Dict[str, Any], is_association_table: bool = False) -> Column:
    """
    Create a SQLAlchemy Column from configuration dict.
    
    Args:
        col_config: Column configuration dict
        is_association_table: If True, adjust foreign key handling for Table() constructor
    
    Returns:
        SQLAlchemy Column instance
    """
    name = col_config['name']
    col_type = parse_column_type(col_config['type'])
    
    # Build column arguments
    args = [col_type]
    kwargs = {}
    
    # Handle foreign keys (ForeignKey object is a positional argument after type)
    if 'foreign_key' in col_config:
        args.append(ForeignKey(col_config['foreign_key']))
    
    # Handle column properties
    if col_config.get('primary_key'):
        kwargs['primary_key'] = True
    
    if 'nullable' in col_config:
        kwargs['nullable'] = col_config['nullable']
    elif is_association_table:
        # Association table columns are typically NOT nullable
        kwargs['nullable'] = False

    if col_config.get('indexed') or col_config.get('index'):
        kwargs['index'] = True
    
    if col_config.get('unique'):
        kwargs['unique'] = True
    
    # Handle default values
    if 'default' in col_config:
        default_value = col_config['default']
        
        # Special handling for uuid4
        if default_value == 'uuid4':
            kwargs['default'] = lambda: str(uuid.uuid4())
        elif callable(default_value):
            kwargs['default'] = default_value
        else:
            kwargs['default'] = default_value
    
    return Column(name, *args, **kwargs)


def create_association_table_from_config(table_config: Dict[str, Any], metadata: MetaData) -> Table:
    """
    Creates a SQLAlchemy Table object from config and registers it globally
    in the Base's metadata and the correct module's scope for lookup by name.
    
    Args:
        table_config: Association table configuration dict
        metadata: SQLAlchemy MetaData object
    
    Returns:
        SQLAlchemy Table object
    """
    table_name = table_config['name']
    columns_list = []
    
    for col_config in table_config['columns']:
        # Create column using existing logic but hint it's for an association table
        columns_list.append(create_column_from_config(col_config, is_association_table=True))
    
    # Create the Table object and bind it to Base.metadata
    table_obj = Table(table_name, metadata, *columns_list)

    # CRITICAL FIX: Register the Table object as a global variable
    dynamic_module_name = 'common.models.dynamic' 
    if dynamic_module_name in sys.modules:
        setattr(sys.modules[dynamic_module_name], table_name, table_obj)
        logger.debug(f"Registered Association Table '{table_name}' in module scope: {dynamic_module_name}")
    else:
        logger.warning(f"Could not register association table '{table_name}' in module scope '{dynamic_module_name}' (module not imported)")
    
    return table_obj


def create_relationship_from_config(rel_config: Dict[str, Any]) -> Any:
    """
    Create a SQLAlchemy relationship from configuration dict.
    
    FIXED VERSION: Properly handles primaryjoin/secondaryjoin string expressions
    by evaluating them with Base in scope.
    
    Args:
        rel_config: Relationship configuration dict
    
    Returns:
        SQLAlchemy relationship
    """
    name = rel_config['name']
    
    # Handle both 'model' and 'target_model' keys
    if 'model' in rel_config:
        model_name = rel_config['model']
    elif 'target_model' in rel_config:
        model_name = rel_config['target_model']
    else:
        raise ValueError(f"Relationship '{name}' must specify a target model using 'model' or 'target_model'.")
    
    kwargs = {}
    
    # Relationship type
    rel_type = rel_config.get('type', 'one_to_many')
    
    # Lazy loading strategy
    if rel_type == 'one_to_many':
        kwargs['lazy'] = rel_config.get('lazy', 'dynamic')
    elif rel_type == 'many_to_one':
        kwargs['lazy'] = rel_config.get('lazy', 'select')
    elif 'lazy' in rel_config:
        kwargs['lazy'] = rel_config['lazy']
    
    # Cascade options
    if 'cascade' in rel_config:
        kwargs['cascade'] = rel_config['cascade']
    
    # ========================================================================
    # Back reference handling
    # ========================================================================
    if 'backref' in rel_config:
        backref_config = rel_config['backref']
        if isinstance(backref_config, dict):
            # Complex backref with options
            backref_name = backref_config.get('name')
            if not backref_name:
                raise ValueError(f"backref dict must have 'name' key: {backref_config}")
            
            # Extract backref options
            backref_kwargs = {}
            if 'lazy' in backref_config:
                backref_kwargs['lazy'] = backref_config['lazy']
            if 'cascade' in backref_config:
                backref_kwargs['cascade'] = backref_config['cascade']
            if 'uselist' in backref_config:
                backref_kwargs['uselist'] = backref_config['uselist']
            if 'order_by' in backref_config:
                order_by_val = backref_config['order_by']
                if isinstance(order_by_val, list) and len(order_by_val) == 1:
                    backref_kwargs['order_by'] = order_by_val[0]
                else:
                    backref_kwargs['order_by'] = order_by_val
            
            # Create SQLAlchemy backref object
            kwargs['backref'] = backref(backref_name, **backref_kwargs)
        else:
            # Simple backref name - pass as string
            kwargs['backref'] = backref_config
    
    # Back populates
    if 'back_populates' in rel_config:
        kwargs['back_populates'] = rel_config['back_populates']
    
    # ========================================================================
    # CRITICAL FIX: Primary join condition
    # ========================================================================
    # The issue: Strings like "Base.metadata.tables['goal_tags'].c.tag_id" 
    # need Base in scope when evaluated
    if 'primaryjoin' in rel_config:
        join_string = rel_config['primaryjoin']
        if isinstance(join_string, str):
            # Create a lambda that evaluates the string with proper globals
            from .base import Base
            
            # Create evaluation namespace with Base and metadata
            eval_namespace = {
                'Base': Base,
                'metadata': Base.metadata,
            }
            
            # The lambda will evaluate the string when SQLAlchemy calls it
            # This happens during mapper configuration when all models exist
            kwargs['primaryjoin'] = lambda: eval(join_string, eval_namespace)
        else:
            kwargs['primaryjoin'] = join_string
    elif 'foreign_key_condition' in rel_config:
        # Support alternate key name
        join_string = rel_config['foreign_key_condition']
        if isinstance(join_string, str):
            from .base import Base
            eval_namespace = {
                'Base': Base,
                'metadata': Base.metadata,
            }
            kwargs['primaryjoin'] = lambda: eval(join_string, eval_namespace)
        else:
            kwargs['primaryjoin'] = join_string

    # ========================================================================
    # CRITICAL FIX: Secondary join condition
    # ========================================================================
    if 'secondaryjoin' in rel_config:
        join_string = rel_config['secondaryjoin']
        if isinstance(join_string, str):
            from .base import Base
            eval_namespace = {
                'Base': Base,
                'metadata': Base.metadata,
            }
            kwargs['secondaryjoin'] = lambda: eval(join_string, eval_namespace)
        else:
            kwargs['secondaryjoin'] = join_string
    
    # Foreign keys (informational only - SQLAlchemy will infer from primaryjoin)
    if 'foreign_keys' in rel_config:
        logger.debug(f"Relationship '{name}' specifies foreign_keys: {rel_config['foreign_keys']}")
    
    # ========================================================================
    # Overlaps parameter
    # ========================================================================
    if 'overlaps' in rel_config:
        overlaps_value = rel_config['overlaps']
        
        if isinstance(overlaps_value, str):
            # Clean multiline strings from YAML
            cleaned = overlaps_value.replace('\n', ' ').replace('\r', ' ')
            items = [item.strip() for item in cleaned.split(',') if item.strip()]
            kwargs['overlaps'] = ','.join(items)
        elif isinstance(overlaps_value, list):
            # Convert list to comma-separated string
            items = [str(item).strip() for item in overlaps_value if str(item).strip()]
            kwargs['overlaps'] = ','.join(items)
        else:
            kwargs['overlaps'] = str(overlaps_value)
    
    # ========================================================================
    # Order by
    # ========================================================================
    if 'order_by' in rel_config:
        order_by_value = rel_config['order_by']
        if isinstance(order_by_value, list):
            # If single item list, unwrap to string
            if len(order_by_value) == 1:
                kwargs['order_by'] = order_by_value[0]
            else:
                # Multiple items - pass as list
                kwargs['order_by'] = order_by_value
        else:
            # Already a string
            kwargs['order_by'] = order_by_value
    
    # Use list (for one-to-one relationships)
    if 'uselist' in rel_config:
        kwargs['uselist'] = rel_config['uselist']
    
    # Additional relationship parameters
    if 'remote_side' in rel_config:
        kwargs['remote_side'] = rel_config['remote_side']
    
    # Secondary table (for many-to-many)
    if 'secondary' in rel_config:
        secondary_value = rel_config['secondary']
        if isinstance(secondary_value, str):
            # CRITICAL FIX: Get the Table object directly from metadata
            # NO lambda, NO string evaluation - just the Table object
            from .base import Base
            
            if secondary_value in Base.metadata.tables:
                # Pass the actual Table object
                kwargs['secondary'] = Base.metadata.tables[secondary_value]
                logger.info(f"Using association table '{secondary_value}' from metadata")
            else:
                # Table not found - provide helpful error
                available = list(Base.metadata.tables.keys())
                raise ValueError(
                    f"Association table '{secondary_value}' not found in Base.metadata.tables. "
                    f"Available tables: {available}. "
                    f"Ensure association_tables are defined in YAML and created in Phase 0."
                )
        else:
            kwargs['secondary'] = secondary_value
    
    if 'post_update' in rel_config:
        kwargs['post_update'] = rel_config['post_update']
    
    if 'passive_deletes' in rel_config:
        kwargs['passive_deletes'] = rel_config['passive_deletes']
    
    if 'passive_updates' in rel_config:
        kwargs['passive_updates'] = rel_config['passive_updates']
    
    logger.debug(f"Creating relationship '{name}' -> {model_name} with kwargs: {list(kwargs.keys())}")
    
    return relationship(model_name, **kwargs)


def create_model_from_config(config: Dict[str, Any], base_class: Type[DeclarativeMeta] = Base) -> Type[DeclarativeMeta]:
    """
    Dynamically create a SQLAlchemy model from configuration.
    
    Args:
        config: Model configuration dict
        base_class: Base class to inherit from (default: Base)
    
    Returns:
        Dynamically created SQLAlchemy model class
    """
    model_name = config['name']
    table_name = config['table_name']
    
    logger.info(f"Creating model: {model_name} (table: {table_name})")
    
    # Build class attributes dict
    attrs = {
        '__tablename__': table_name,
        '__module__': config.get('module', 'common.models.dynamic'),
    }
    
    # Add session type if specified
    if 'session_type' in config:
        attrs['__session_type__'] = config['session_type']
    
    # Add table args if specified
    if 'table_args' in config:
        attrs['__table_args__'] = config['table_args']
    
    # Create columns
    for col_config in config.get('columns', []):
        col_name = col_config['name']
        attrs[col_name] = create_column_from_config(col_config, is_association_table=False)
    
    # Store relationship configs for later (after all models are created)
    relationship_configs = config.get('relationships', [])
    
    # Build mixin classes
    mixin_classes = []
    for mixin_name in config.get('mixins', []):
        mixin_class = get_mixin_class(mixin_name)
        if mixin_class:
            mixin_classes.append(mixin_class)
    
    # Create the model class
    # Inheritance order: (Base, *Mixins)
    bases = tuple([base_class] + mixin_classes)
    model_class = type(model_name, bases, attrs)
    
    # Add the dynamically created class to its designated module's scope
    # This prevents garbage collection before full registration
    try:
        module_name = attrs['__module__']
        if module_name in sys.modules:
            setattr(sys.modules[module_name], model_name, model_class)
        else:
            # Fallback if module is not yet imported
            globals()[model_name] = model_class
    except Exception as e:
        logger.warning(f"Could not add model {model_name} to module scope: {e}")
    
    # Store relationship configs for Phase 2
    if relationship_configs:
        model_class._relationship_configs = relationship_configs
    
    # Store additional metadata
    model_class._config = config
    
    logger.info(f"Model created: {model_name}")
    
    return model_class


def finalize_relationships(model_class: Type[DeclarativeMeta]) -> None:
    """
    Add relationships to a model after all models have been created.
    
    This is a two-phase process because relationships may reference
    models that haven't been created yet.
    
    Args:
        model_class: The model class to finalize
    """
    if not hasattr(model_class, '_relationship_configs'):
        return
    
    model_name = model_class.__name__
    
    for rel_config in model_class._relationship_configs:
        rel_name = rel_config['name']
        try:
            rel = create_relationship_from_config(rel_config)
            setattr(model_class, rel_name, rel)
            logger.debug(f"Added relationship '{rel_name}' to {model_name}")
        except Exception as e:
            logger.error(f"Failed to add relationship '{rel_name}' to {model_name}: {e}")
            raise  # Re-raise to stop initialization on relationship failure
    
    # Clean up
    delattr(model_class, '_relationship_configs')


def create_indexes_from_config(model_class: Type[DeclarativeMeta], indexes_config: List[Dict[str, Any]]) -> None:
    """
    Create indexes for a model from configuration.
    
    Args:
        model_class: The model class
        indexes_config: List of index configuration dicts
    """
    for idx_config in indexes_config:
        columns = idx_config['columns']
        name = idx_config['name']
        
        # Get column objects
        col_objs = [getattr(model_class, col) for col in columns]
        
        # Create index
        kwargs = {}
        if idx_config.get('unique'):
            kwargs['unique'] = True
        
        Index(name, *col_objs, **kwargs)
        logger.debug(f"Created index '{name}' on {model_class.__name__}")


class ModelFactory:
    """
    Factory for creating models from configuration.
    
    Handles the three-phase process:
    0. Create association tables
    1. Create all model classes (without relationships)
    2. Finalize relationships (after all models exist)
    3. Create indexes
    """
    
    def __init__(self):
        self.created_models: List[Type[DeclarativeMeta]] = []
        self.all_configs: List[Dict[str, Any]] = []
    
    def create_models_from_config(self, configs: List[Dict[str, Any]]) -> List[Type[DeclarativeMeta]]:
        """
        Create multiple models from a list of configurations.
        
        Args:
            configs: List of configuration dicts (can contain 'models' and 'association_tables')
        
        Returns:
            List of created model classes
        """
        self.all_configs = configs
        models = []
        
        # ====================================================================
        # Phase 0: Create Association Tables
        # ====================================================================
        for config_block in configs:
            if 'association_tables' in config_block:
                for table_config in config_block['association_tables']:
                    try:
                        create_association_table_from_config(table_config, Base.metadata)
                        logger.info(f"Association table '{table_config['name']}' created successfully.")
                    except Exception as e:
                        logger.error(f"Failed to create association table '{table_config['name']}': {e}")
                        raise
        
        # Extract only the actual model definitions
        model_configs = [c for c in configs if 'name' in c and 'table_name' in c]
        
        # ====================================================================
        # Phase 1: Create all model classes (without relationships)
        # ====================================================================
        for config in model_configs:
            try:
                model_class = create_model_from_config(config)
                models.append(model_class)
                
                # Register the model
                model_registry.register_model(model_class, config)
                
            except Exception as e:
                logger.error(f"Failed to create model '{config.get('name', 'unknown')}': {e}")
                raise
        
        # ====================================================================
        # Phase 2: Finalize relationships
        # ====================================================================
        for model_class in models:
            try:
                finalize_relationships(model_class)
            except Exception as e:
                logger.error(f"Failed to finalize relationships for {model_class.__name__}: {e}")
                raise
        
        # ====================================================================
        # Phase 3: Create indexes
        # ====================================================================
        for model_class in models:
            if hasattr(model_class, '_config'):
                config = model_class._config
                if 'indexes' in config:
                    try:
                        create_indexes_from_config(model_class, config['indexes'])
                    except Exception as e:
                        logger.error(f"Failed to create indexes for {model_class.__name__}: {e}")
                        raise
        
        self.created_models.extend(models)
        return models
    
    def create_model_from_config_file(self, config_path: str) -> List[Type[DeclarativeMeta]]:
        """
        Create models from a YAML configuration file.
        
        Args:
            config_path: Path to YAML config file
        
        Returns:
            List of created model classes
        """
        import yaml
        
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Extract all configuration items
        configs = []
        
        # Add individual model definitions
        configs.extend(config_data.get('models', []))
        
        # Add the association_tables block as a separate dictionary
        if 'association_tables' in config_data:
            configs.append({'association_tables': config_data['association_tables']})
        
        return self.create_models_from_config(configs)


# Singleton instance
model_factory = ModelFactory()