# timber/common/services/inventory/__init__.py
"""
Timber Inventory Module

Self-documenting capability manager for Timber and applications built on it.

This module provides:
- Automatic discovery of models, services, and configuration
- JSON export of all capabilities
- Flexible loading from multiple directories
- Multi-level caching for fast repeated queries
- CLI and programmatic interfaces

Usage:
    from common.services.inventory import load_timber_capabilities
    
    # Load capabilities with caching
    capabilities = load_timber_capabilities(
        model_dirs=['data/models', 'grove/data/models'],
        enable_cache=True,
        cache_ttl_hours=24
    )
    
    # Generate inventory (fast with caching)
    inventory = capabilities.generate_full_inventory()
    
    # Save to file
    capabilities.save_inventory_to_file('capabilities.json')
"""

from .available_capabilities import (
    AvailableCapabilitiesService,
    print_capabilities_summary
)

from .loader import (
    load_timber_capabilities,
    generate_capabilities_json,
    load_timber_only,
    load_timber_with_grove,
    load_full_oakquant
)

# Optional cached service (requires redis package)
try:
    from .cached_capabilities import CachedCapabilitiesService
    __all_exports = [
        # Main services
        'AvailableCapabilitiesService',
        'CachedCapabilitiesService',
        'print_capabilities_summary',
        
        # Loaders
        'load_timber_capabilities',
        'generate_capabilities_json',
        'load_timber_only',
        'load_timber_with_grove',
        'load_full_oakquant',
    ]
except ImportError:
    __all_exports = [
        # Main service
        'AvailableCapabilitiesService',
        'print_capabilities_summary',
        
        # Loaders
        'load_timber_capabilities',
        'generate_capabilities_json',
        'load_timber_only',
        'load_timber_with_grove',
        'load_full_oakquant',
    ]

__all__ = __all_exports