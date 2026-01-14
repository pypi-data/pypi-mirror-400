# common/services/integrations/__init__.py
"""
Integration Factory

A configuration-driven integration system that:
- Loads integration definitions from YAML files
- Manages credentials separately for reuse
- Handles multiple authentication types (Basic, API Key, OAuth2, etc.)
- Maps request/response data using field mappings
- Provides caching, retry, and circuit breaker patterns

Quick Start:
    
    from common.services.integrations import (
        integration_service,
        initialize_integrations,
        call_integration,
    )
    
    # Initialize at startup
    await initialize_integrations(
        config_path='config/integrations/integration_config.yaml',
        base_dir='/app',
    )
    
    # Execute an integration
    response = await call_integration(
        'alpha_vantage_quote',
        params={'symbol': 'AAPL'},
    )
    
    if response.success:
        print(f"Price: {response.data['price']}")
    else:
        print(f"Error: {response.error_message}")

Module Exports:
    - IntegrationService: Main service class
    - integration_service: Singleton service instance
    - IntegrationRegistry: Registry for integrations
    - integration_registry: Singleton registry instance
    - AuthService: Authentication handling
    - auth_service: Singleton auth instance
    - MappingService: Field mapping
    - mapping_service: Singleton mapping instance
    
Data Models:
    - IntegrationRequest: Request to execute
    - IntegrationResponse: Execution response
    - Credential: Authentication credential
    - IntegrationDefinition: Integration configuration
    
Utility Functions:
    - initialize_integrations(): Initialize the system
    - call_integration(): Execute an integration
    - get_integration(): Get integration by ID
    - list_integrations(): List available integrations
"""

from .models import (
    # Enums
    AuthType,
    HttpMethod,
    ParamLocation,
    FieldType,
    CircuitState,
    
    # Credential models
    Credential,
    BasicAuthConfig,
    ApiKeyConfig,
    OAuth2ClientCredentialsConfig,
    OAuth2AuthCodeConfig,
    BearerTokenConfig,
    CustomHeadersConfig,
    AwsSignatureConfig,
    CertificateConfig,
    
    # Integration models
    IntegrationDefinition,
    ConnectionConfig,
    RetryConfig,
    EndpointConfig,
    RequestConfig,
    ResponseConfig,
    BodyConfig,
    FieldMapping,
    CacheConfig,
    RateLimitConfig,
    
    # Execution models
    IntegrationRequest,
    IntegrationResponse,
    CachedToken,
    CircuitBreakerState,
)

from .registry import (
    IntegrationRegistry,
    integration_registry,
    get_integration,
    get_credential,
    list_integrations as registry_list_integrations,
)

from .auth_service import (
    AuthService,
    auth_service,
)

from .mapping_service import (
    MappingService,
    mapping_service,
    register_transformer,
    TRANSFORMERS,
)

from .integration_service import (
    IntegrationService,
    integration_service,
    call_integration,
    initialize_from_config,
)

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

async def initialize_integrations(
    config_path: Optional[str] = None,
    credential_paths: Optional[List[str]] = None,
    integration_paths: Optional[List[str]] = None,
    base_dir: Optional[str] = None,
    use_config: bool = True,
) -> Dict[str, Any]:
    """
    Initialize the integration factory.
    
    Should be called once at application startup.
    
    Args:
        config_path: Path to integration_config.yaml
        credential_paths: Paths to credential YAML files
        integration_paths: Paths to integration definition YAML files
        base_dir: Base directory for relative paths
        use_config: If True and no paths provided, use Config singleton
        
    Returns:
        Initialization summary with counts of loaded items
        
    Example:
        # Option 1: Use unified Config (recommended)
        summary = await initialize_integrations()
        
        # Option 2: Explicit paths
        summary = await initialize_integrations(
            credential_paths=['config/integrations/credentials/'],
            integration_paths=['config/integrations/definitions/'],
            base_dir='/app',
            use_config=False,
        )
    """
    # If no explicit paths and use_config enabled, try to use Config
    if use_config and not any([config_path, credential_paths, integration_paths]):
        return await initialize_from_config()
    
    # Otherwise use explicit paths
    return await integration_service.initialize(
        config_path=config_path,
        credential_paths=credential_paths,
        integration_paths=integration_paths,
        base_dir=base_dir,
    )


async def shutdown_integrations():
    """
    Shutdown the integration factory.
    
    Should be called at application shutdown to release resources.
    """
    await integration_service.close()
    logger.info("Integration factory shutdown complete")


def list_integrations(enabled_only: bool = True) -> List[Dict[str, Any]]:
    """
    List available integrations.
    
    Args:
        enabled_only: Only list enabled integrations
        
    Returns:
        List of integration summaries
    """
    return integration_service.list_integrations(enabled_only=enabled_only)


def get_integration_stats() -> Dict[str, Any]:
    """
    Get integration service statistics.
    
    Returns:
        Stats including call counts, cache hits, errors
    """
    return integration_service.get_stats()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    'AuthType',
    'HttpMethod',
    'ParamLocation',
    'FieldType',
    'CircuitState',
    
    # Credential models
    'Credential',
    'BasicAuthConfig',
    'ApiKeyConfig',
    'OAuth2ClientCredentialsConfig',
    'OAuth2AuthCodeConfig',
    'BearerTokenConfig',
    'CustomHeadersConfig',
    'AwsSignatureConfig',
    'CertificateConfig',
    
    # Integration models
    'IntegrationDefinition',
    'ConnectionConfig',
    'RetryConfig',
    'EndpointConfig',
    'RequestConfig',
    'ResponseConfig',
    'BodyConfig',
    'FieldMapping',
    'CacheConfig',
    'RateLimitConfig',
    
    # Execution models
    'IntegrationRequest',
    'IntegrationResponse',
    'CachedToken',
    'CircuitBreakerState',
    
    # Services
    'IntegrationService',
    'integration_service',
    'IntegrationRegistry',
    'integration_registry',
    'AuthService',
    'auth_service',
    'MappingService',
    'mapping_service',
    
    # Transformers
    'register_transformer',
    'TRANSFORMERS',
    
    # Convenience functions
    'initialize_integrations',
    'initialize_from_config',
    'shutdown_integrations',
    'call_integration',
    'get_integration',
    'get_credential',
    'list_integrations',
    'get_integration_stats',
]
