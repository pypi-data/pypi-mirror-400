# timber/common/services/inventory/loader.py
"""
Timber Inventory Loader

Flexible loader that initializes Timber with configurable directories
and generates a complete capabilities inventory with optional caching.

Supports loading models and configs from multiple directories (e.g., timber, grove, canopy).

Usage:
    from common.services.inventory.loader import load_timber_capabilities
    
    capabilities = load_timber_capabilities(
        model_dirs=['data/models', 'grove/data/models'],
        config_dirs=['modules/config', 'grove/modules/config'],
        enable_cache=True  # Enable caching for fast repeated queries
    )
    
    # Access inventory
    inventory = capabilities.generate_full_inventory()
"""

import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from ...init import initialize_timber
from .available_capabilities import AvailableCapabilitiesService

logger = logging.getLogger(__name__)


def load_timber_capabilities(
    model_dirs: Optional[List[str]] = None,
    config_dirs: Optional[List[str]] = None,
    services: Optional[Dict[str, Any]] = None,
    enable_encryption: bool = False,
    enable_gdpr: bool = True,
    enable_auto_vector_ingestion: bool = False,
    create_tables: bool = True,
    validate_config: bool = True,
    auto_discover_services: bool = True,
    enable_cache: bool = True,
    cache_ttl_hours: int = 24,
    cache_dir: Optional[Path] = None
) -> AvailableCapabilitiesService:
    """
    Load Timber with specified directories and create capabilities inventory.
    
    This function:
    1. Initializes Timber with models from multiple directories
    2. Optionally loads configurations from multiple directories
    3. Auto-discovers available services
    4. Creates a capabilities inventory service (with optional caching)
    
    Args:
        model_dirs: List of directories containing YAML model definitions
                   Example: ['data/models', 'grove/data/models', 'canopy/data/models']
        config_dirs: List of directories containing configuration files
                    Example: ['modules/config', 'grove/modules/config']
        services: Dictionary of service instances to include in inventory
                 Example: {'session_service': session_service, 'notification_service': notification_service}
        enable_encryption: Enable field-level encryption
        enable_gdpr: Enable GDPR compliance features
        enable_auto_vector_ingestion: Enable automatic vector ingestion
        create_tables: Automatically create all database tables
        validate_config: Validate configuration before proceeding
        auto_discover_services: Automatically discover and include Timber services
        enable_cache: Enable multi-level caching for inventory queries
        cache_ttl_hours: Cache time-to-live in hours (default: 24)
        cache_dir: Directory for file-based cache (default: .timber_cache)
    
    Returns:
        AvailableCapabilitiesService instance with full capabilities
        (CachedCapabilitiesService if caching is enabled)
    
    Example:
        # Load from multiple applications
        capabilities = load_timber_capabilities(
            model_dirs=[
                'timber/data/models',
                'grove/data/models',
                'canopy/data/models'
            ],
            config_dirs=[
                'timber/modules/config',
                'grove/modules/config'
            ]
        )
        
        # Generate inventory
        inventory = capabilities.generate_full_inventory()
        
        # Save to file
        capabilities.save_inventory_to_file('full_capabilities.json')
    """
    
    # Set default directories if not provided
    if model_dirs is None:
        model_dirs = ['data/models']
    
    # Validate and filter existing directories
    validated_model_dirs = _validate_directories(model_dirs, "model")
    validated_config_dirs = _validate_directories(config_dirs or [], "config")
    
    if not validated_model_dirs:
        logger.warning("No valid model directories found. Proceeding with empty model set.")
    
    # Initialize Timber with all model directories
    logger.info(f"Initializing Timber with {len(validated_model_dirs)} model directories...")
    try:
        initialize_timber(
            model_config_dirs=validated_model_dirs,
            enable_encryption=enable_encryption,
            enable_gdpr=enable_gdpr,
            enable_auto_vector_ingestion=enable_auto_vector_ingestion,
            create_tables=create_tables,
            validate_config=validate_config
        )
        logger.info("✓ Timber initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Timber: {e}")
        raise
    
    # Load configurations from config directories
    if validated_config_dirs:
        logger.info(f"Loading configurations from {len(validated_config_dirs)} directories...")
        for config_dir in validated_config_dirs:
            _load_config_directory(config_dir)
    
    # Auto-discover services if requested
    if auto_discover_services and services is None:
        services = _discover_timber_services()
    elif auto_discover_services and services:
        # Merge auto-discovered with provided services
        discovered = _discover_timber_services()
        services = {**discovered, **services}
    
    # Create capabilities service (with or without caching)
    if enable_cache:
        try:
            from .cached_capabilities import CachedCapabilitiesService
            capabilities = CachedCapabilitiesService(
                services=services,
                enable_cache=True,
                cache_ttl_hours=cache_ttl_hours,
                cache_dir=cache_dir
            )
            logger.info("✓ Capabilities inventory ready (with caching)")
        except ImportError:
            logger.warning("CachedCapabilitiesService not available, falling back to uncached")
            capabilities = AvailableCapabilitiesService(services=services)
            logger.info("✓ Capabilities inventory ready (without caching)")
    else:
        capabilities = AvailableCapabilitiesService(services=services)
        logger.info("✓ Capabilities inventory ready (caching disabled)")
    
    return capabilities


def _validate_directories(directories: List[str], dir_type: str) -> List[str]:
    """
    Validate that directories exist and return list of valid paths.
    
    Args:
        directories: List of directory paths
        dir_type: Type of directory (for logging)
    
    Returns:
        List of valid directory paths
    """
    valid_dirs = []
    
    for dir_path in directories:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            valid_dirs.append(str(path))
            logger.debug(f"✓ Valid {dir_type} directory: {path}")
        else:
            logger.warning(f"✗ {dir_type.capitalize()} directory not found: {path}")
    
    return valid_dirs


def _load_config_directory(config_dir: str):
    """
    Load configuration files from a directory.
    
    Args:
        config_dir: Path to configuration directory
    """
    config_path = Path(config_dir)
    
    # Look for common config file patterns
    config_patterns = ['*.yaml', '*.yml', '*.json', '*.py']
    
    for pattern in config_patterns:
        config_files = list(config_path.glob(pattern))
        if config_files:
            logger.info(f"Found {len(config_files)} {pattern} files in {config_dir}")
            # TODO: Add actual config loading logic here if needed
            # For now, just log that configs were found


def _discover_timber_services() -> Dict[str, Any]:
    """
    Auto-discover available Timber services.
    
    Returns:
        Dictionary of discovered services
    """
    services = {}
    
    # Try to import common Timber services
    try:
        from ...services.persistence.session import session_service
        services['session_service'] = session_service
        logger.debug("✓ Discovered session_service")
    except ImportError:
        logger.debug("✗ session_service not available")
    
    try:
        from ...services.persistence.notification import notification_service
        services['notification_service'] = notification_service
        logger.debug("✓ Discovered notification_service")
    except ImportError:
        logger.debug("✗ notification_service not available")
    
    try:
        from ...services.persistence.tracker import tracker_service
        services['tracker_service'] = tracker_service
        logger.debug("✓ Discovered tracker_service")
    except ImportError:
        logger.debug("✗ tracker_service not available")
    
    if services:
        logger.info(f"✓ Auto-discovered {len(services)} services")
    else:
        logger.info("No services auto-discovered")
    
    return services


def generate_capabilities_json(
    output_file: str,
    model_dirs: Optional[List[str]] = None,
    config_dirs: Optional[List[str]] = None,
    services: Optional[Dict[str, Any]] = None,
    **kwargs
) -> str:
    """
    Convenience function to load Timber and generate capabilities JSON in one call.
    
    Args:
        output_file: Path to save capabilities JSON
        model_dirs: List of model directories
        config_dirs: List of config directories
        services: Dictionary of services
        **kwargs: Additional arguments passed to load_timber_capabilities
    
    Returns:
        Path to saved file
    
    Example:
        generate_capabilities_json(
            output_file='docs/api/capabilities.json',
            model_dirs=['data/models', 'grove/data/models']
        )
    """
    capabilities = load_timber_capabilities(
        model_dirs=model_dirs,
        config_dirs=config_dirs,
        services=services,
        **kwargs
    )
    
    return capabilities.save_inventory_to_file(output_file)


# Convenience functions for common use cases
def load_timber_only(model_dirs: Optional[List[str]] = None) -> AvailableCapabilitiesService:
    """
    Load only Timber (single application).
    
    Args:
        model_dirs: Model directories (default: ['data/models'])
    
    Returns:
        AvailableCapabilitiesService instance
    """
    return load_timber_capabilities(model_dirs=model_dirs or ['data/models'])


def load_timber_with_grove(
    timber_models: str = 'timber/data/models',
    grove_models: str = 'grove/data/models'
) -> AvailableCapabilitiesService:
    """
    Load Timber + Grove capabilities.
    
    Args:
        timber_models: Path to Timber models
        grove_models: Path to Grove models
    
    Returns:
        AvailableCapabilitiesService instance
    """
    return load_timber_capabilities(
        model_dirs=[timber_models, grove_models]
    )


def load_full_oakquant(
    timber_models: str = 'timber/data/models',
    grove_models: str = 'grove/data/models',
    canopy_models: str = 'canopy/data/models'
) -> AvailableCapabilitiesService:
    """
    Load full OakQuant stack (Timber + Grove + Canopy).
    
    Args:
        timber_models: Path to Timber models
        grove_models: Path to Grove models
        canopy_models: Path to Canopy models
    
    Returns:
        AvailableCapabilitiesService instance
    """
    return load_timber_capabilities(
        model_dirs=[timber_models, grove_models, canopy_models]
    )