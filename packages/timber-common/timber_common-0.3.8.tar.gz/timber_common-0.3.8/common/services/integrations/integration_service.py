# common/services/integrations/integration_service.py
"""
Integration Service

Main service for executing integrations. Orchestrates:
- Registry lookup
- Authentication
- Request building
- HTTP execution
- Response mapping
- Caching
- Circuit breaker
- Retry logic
- Logging/metrics
"""

from __future__ import annotations
import asyncio
import hashlib
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin

import httpx

from .models import (
    IntegrationDefinition,
    IntegrationRequest,
    IntegrationResponse,
    HttpMethod,
    Credential,
)
from .registry import integration_registry
from .auth_service import auth_service
from .mapping_service import mapping_service

logger = logging.getLogger(__name__)


class ResponseCache:
    """Simple in-memory response cache with TTL."""
    
    def __init__(self):
        self._cache: Dict[str, tuple] = {}  # key -> (response, expires_at)
    
    def get(self, key: str) -> Optional[IntegrationResponse]:
        """Get cached response if not expired."""
        if key in self._cache:
            response, expires_at = self._cache[key]
            if datetime.now(timezone.utc) < expires_at:
                return response
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, response: IntegrationResponse, ttl_seconds: int):
        """Cache a response."""
        from datetime import timedelta
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        self._cache[key] = (response, expires_at)
    
    def delete(self, key: str):
        """Remove cached response."""
        self._cache.pop(key, None)
    
    def clear(self):
        """Clear all cached responses."""
        self._cache.clear()


class IntegrationService:
    """
    Main service for executing integrations.
    
    Usage:
        # Initialize (usually at app startup)
        await integration_service.initialize()
        
        # Execute an integration
        response = await integration_service.execute(
            IntegrationRequest(
                integration_id='alpha_vantage_quote',
                params={'symbol': 'AAPL'},
            )
        )
        
        # Or use the shorthand
        response = await integration_service.call(
            'alpha_vantage_quote',
            params={'symbol': 'AAPL'},
        )
    """
    
    def __init__(self):
        self._http_client: Optional[httpx.AsyncClient] = None
        self._response_cache = ResponseCache()
        self._initialized = False
        
        # Metrics
        self._call_count = 0
        self._error_count = 0
        self._cache_hits = 0
    
    # =========================================================================
    # INITIALIZATION
    # =========================================================================
    
    async def initialize(
        self,
        config_path: Optional[str] = None,
        credential_paths: Optional[List[str]] = None,
        integration_paths: Optional[List[str]] = None,
        base_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Initialize the integration service.
        
        Loads integrations and credentials from YAML files.
        
        Args:
            config_path: Path to integration_config.yaml
            credential_paths: Paths to credential files
            integration_paths: Paths to integration definition files
            base_dir: Base directory for relative paths
            
        Returns:
            Initialization summary
        """
        # Initialize registry
        summary = integration_registry.initialize(
            config_path=config_path,
            credential_paths=credential_paths,
            integration_paths=integration_paths,
            base_dir=base_dir,
        )
        
        # Create HTTP client
        self._http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            follow_redirects=True,
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        )
        
        self._initialized = True
        logger.info("IntegrationService initialized")
        
        return summary
    
    async def close(self):
        """Close the service and release resources."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
        
        await auth_service.close()
        self._initialized = False
        logger.info("IntegrationService closed")
    
    async def reload(self) -> Dict[str, Any]:
        """Reload all configurations."""
        return integration_registry.reload()
    
    # =========================================================================
    # MAIN EXECUTION
    # =========================================================================
    
    async def execute(
        self,
        request: IntegrationRequest,
    ) -> IntegrationResponse:
        """
        Execute an integration request.
        
        Args:
            request: The integration request
            
        Returns:
            Integration response
        """
        start_time = time.time()
        trace_id = request.trace_id or str(uuid.uuid4())[:8]
        
        self._call_count += 1
        
        # Get integration definition
        integration = integration_registry.get_integration(request.integration_id)
        if not integration:
            return self._error_response(
                request.integration_id,
                f"Integration not found: {request.integration_id}",
                trace_id=trace_id,
            )
        
        if not integration.enabled:
            return self._error_response(
                request.integration_id,
                f"Integration is disabled: {request.integration_id}",
                trace_id=trace_id,
            )
        
        # Check circuit breaker
        if integration_registry.is_circuit_open(request.integration_id):
            return self._error_response(
                request.integration_id,
                "Circuit breaker is open",
                error_code="CIRCUIT_OPEN",
                trace_id=trace_id,
            )
        
        # Check cache
        if not request.skip_cache and integration.cache.enabled:
            cache_key = self._build_cache_key(integration, request)
            cached = self._response_cache.get(cache_key)
            if cached:
                self._cache_hits += 1
                cached.from_cache = True
                logger.debug(f"[{trace_id}] Cache hit for {request.integration_id}")
                return cached
        
        # Execute with retry
        try:
            response = await self._execute_with_retry(
                integration,
                request,
                trace_id,
            )
            
            # Cache successful responses
            if response.success and integration.cache.enabled:
                cache_key = self._build_cache_key(integration, request)
                self._response_cache.set(
                    cache_key,
                    response,
                    integration.cache.ttl_seconds,
                )
            
            # Update circuit breaker
            if response.success:
                integration_registry.record_success(request.integration_id)
            else:
                integration_registry.record_failure(request.integration_id)
            
            # Calculate duration
            response.duration_ms = (time.time() - start_time) * 1000
            response.trace_id = trace_id
            
            return response
            
        except Exception as e:
            self._error_count += 1
            integration_registry.record_failure(request.integration_id)
            
            logger.error(f"[{trace_id}] Integration execution failed: {e}")
            
            return self._error_response(
                request.integration_id,
                str(e),
                trace_id=trace_id,
                duration_ms=(time.time() - start_time) * 1000,
            )
    
    async def _execute_with_retry(
        self,
        integration: IntegrationDefinition,
        request: IntegrationRequest,
        trace_id: str,
    ) -> IntegrationResponse:
        """Execute integration with retry logic."""
        retry_config = integration.connection.retry
        max_attempts = retry_config.max_attempts if retry_config.enabled else 1
        
        last_error = None
        retry_count = 0
        
        for attempt in range(max_attempts):
            try:
                response = await self._execute_single(
                    integration,
                    request,
                    trace_id,
                )
                
                # Check if we should retry based on status code
                if (
                    not response.success 
                    and retry_config.enabled
                    and response.status_code in retry_config.retry_on_status
                    and attempt < max_attempts - 1
                ):
                    retry_count += 1
                    delay = self._calculate_backoff(
                        attempt,
                        retry_config.initial_delay_ms,
                        retry_config.backoff_multiplier,
                        retry_config.max_delay_ms,
                    )
                    logger.debug(
                        f"[{trace_id}] Retry {attempt + 1}/{max_attempts} "
                        f"after {delay}ms (status: {response.status_code})"
                    )
                    await asyncio.sleep(delay / 1000)
                    continue
                
                response.retry_count = retry_count
                return response
                
            except httpx.TimeoutException as e:
                last_error = e
                retry_count += 1
                if attempt < max_attempts - 1:
                    delay = self._calculate_backoff(
                        attempt,
                        retry_config.initial_delay_ms,
                        retry_config.backoff_multiplier,
                        retry_config.max_delay_ms,
                    )
                    logger.debug(f"[{trace_id}] Timeout, retry {attempt + 1} after {delay}ms")
                    await asyncio.sleep(delay / 1000)
                    continue
                    
            except httpx.HTTPError as e:
                last_error = e
                retry_count += 1
                if attempt < max_attempts - 1:
                    delay = self._calculate_backoff(
                        attempt,
                        retry_config.initial_delay_ms,
                        retry_config.backoff_multiplier,
                        retry_config.max_delay_ms,
                    )
                    logger.debug(f"[{trace_id}] HTTP error, retry {attempt + 1} after {delay}ms")
                    await asyncio.sleep(delay / 1000)
                    continue
        
        # All retries exhausted
        raise last_error or Exception("Max retries exceeded")
    
    def _calculate_backoff(
        self,
        attempt: int,
        initial_delay_ms: int,
        multiplier: float,
        max_delay_ms: int,
    ) -> int:
        """Calculate exponential backoff delay."""
        delay = initial_delay_ms * (multiplier ** attempt)
        return min(int(delay), max_delay_ms)
    
    async def _execute_single(
        self,
        integration: IntegrationDefinition,
        request: IntegrationRequest,
        trace_id: str,
    ) -> IntegrationResponse:
        """Execute a single HTTP request."""
        # Build URL
        base_url = integration.connection.base_url
        path = mapping_service.build_path(
            integration.endpoint.path,
            integration.endpoint.path_params,
            request.path_params,
        )
        url = urljoin(base_url, path)
        
        # Build query parameters
        query_params = mapping_service.build_query_params(
            integration.endpoint.query_params.static,
            integration.endpoint.query_params.dynamic,
            request.params,
        )
        
        # Build headers
        headers = {**integration.request.headers, **request.headers}
        
        # Build body
        body = None
        if integration.request.body and request.body:
            body = mapping_service.build_request_body(
                integration.request.body,
                request.body,
            )
        elif request.body:
            body = request.body
        
        # Apply authentication
        credential = integration_registry.get_integration_credential(integration.id)
        if credential:
            headers, query_params, body = await auth_service.apply_authentication(
                credential,
                headers,
                query_params,
                body,
                request.user_id,
            )
        
        # Log request
        logger.debug(
            f"[{trace_id}] {integration.endpoint.method.value} {url} "
            f"params={list(query_params.keys())}"
        )
        
        # Execute request
        timeout = request.timeout_override or integration.connection.timeout_seconds
        
        http_response = await self._http_client.request(
            method=integration.endpoint.method.value,
            url=url,
            params=query_params,
            headers=headers,
            json=body if body else None,
            timeout=timeout,
        )
        
        # Process response
        return self._process_response(
            integration,
            http_response,
            trace_id,
        )
    
    def _process_response(
        self,
        integration: IntegrationDefinition,
        http_response: httpx.Response,
        trace_id: str,
    ) -> IntegrationResponse:
        """Process HTTP response and map data."""
        status_code = http_response.status_code
        success = status_code in integration.response.expected_status
        
        # Parse response body
        raw_response = None
        try:
            if http_response.content:
                content_type = http_response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    raw_response = http_response.json()
                else:
                    raw_response = {'_raw': http_response.text}
        except Exception as e:
            logger.warning(f"[{trace_id}] Failed to parse response: {e}")
            raw_response = {'_raw': http_response.text}
        
        # Check for error in response body
        error_message = None
        error_code = None
        
        if not success and integration.response.error_handling:
            error_handling = integration.response.error_handling
            
            if error_handling.error_path and raw_response:
                error_message = self._extract_path(
                    raw_response,
                    error_handling.error_path,
                )
            
            if error_handling.error_code_path and raw_response:
                error_code = self._extract_path(
                    raw_response,
                    error_handling.error_code_path,
                )
            
            # Check for rate limiting
            if error_handling.rate_limit_path and raw_response:
                rate_limit_msg = self._extract_path(
                    raw_response,
                    error_handling.rate_limit_path,
                )
                if rate_limit_msg:
                    error_code = 'RATE_LIMITED'
                    error_message = str(rate_limit_msg)
        
        # Map response data
        mapped_data = None
        if success and raw_response and integration.response.mapping:
            try:
                mapped_data = mapping_service.map_response(
                    raw_response,
                    integration.response.mapping,
                )
            except Exception as e:
                logger.warning(f"[{trace_id}] Response mapping failed: {e}")
                mapped_data = raw_response
        
        # Log response
        logger.debug(
            f"[{trace_id}] Response: {status_code} "
            f"success={success}"
        )
        
        return IntegrationResponse(
            success=success,
            status_code=status_code,
            data=mapped_data or raw_response,
            raw_response=raw_response,
            headers=dict(http_response.headers),
            integration_id=integration.id,
            error_message=error_message,
            error_code=error_code,
            requested_at=datetime.now(timezone.utc),
        )
    
    def _extract_path(self, data: Any, path: str) -> Any:
        """Extract value from nested data."""
        if not data or not path:
            return None
        
        parts = path.split('.')
        current = data
        
        for part in parts:
            if current is None:
                return None
            
            # Handle array notation
            if part.startswith('[') and part.endswith(']'):
                try:
                    idx = int(part[1:-1])
                    if isinstance(current, list) and idx < len(current):
                        current = current[idx]
                    else:
                        return None
                except ValueError:
                    return None
            elif isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list) and current:
                current = current[0].get(part) if isinstance(current[0], dict) else None
            else:
                return None
        
        return current
    
    def _build_cache_key(
        self,
        integration: IntegrationDefinition,
        request: IntegrationRequest,
    ) -> str:
        """Build cache key for a request."""
        template = integration.cache.key_template
        
        if template:
            # Substitute parameters in template
            key = template
            for param, value in request.params.items():
                key = key.replace(f"{{{param}}}", str(value))
            return key
        else:
            # Generate key from integration ID and parameters
            key_data = {
                'integration': integration.id,
                'params': request.params,
                'body': request.body,
            }
            key_str = json.dumps(key_data, sort_keys=True)
            return hashlib.md5(key_str.encode()).hexdigest()
    
    def _error_response(
        self,
        integration_id: str,
        message: str,
        error_code: Optional[str] = None,
        trace_id: Optional[str] = None,
        duration_ms: float = 0,
    ) -> IntegrationResponse:
        """Create an error response."""
        self._error_count += 1
        
        return IntegrationResponse(
            success=False,
            status_code=0,
            integration_id=integration_id,
            error_message=message,
            error_code=error_code or "ERROR",
            trace_id=trace_id,
            duration_ms=duration_ms,
            requested_at=datetime.now(timezone.utc),
        )
    
    # =========================================================================
    # CONVENIENCE METHODS
    # =========================================================================
    
    async def call(
        self,
        integration_id: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        path_params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        skip_cache: bool = False,
        user_id: Optional[str] = None,
    ) -> IntegrationResponse:
        """
        Shorthand for executing an integration.
        
        Args:
            integration_id: ID of the integration to execute
            params: Query parameters
            body: Request body data
            path_params: Path parameters
            headers: Additional headers
            skip_cache: Skip cache lookup
            user_id: User ID for OAuth user context
            
        Returns:
            Integration response
        """
        request = IntegrationRequest(
            integration_id=integration_id,
            params=params or {},
            body=body,
            path_params=path_params or {},
            headers=headers or {},
            skip_cache=skip_cache,
            user_id=user_id,
        )
        return await self.execute(request)
    
    async def get(
        self,
        integration_id: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> IntegrationResponse:
        """Execute a GET integration."""
        return await self.call(integration_id, params=params, **kwargs)
    
    async def post(
        self,
        integration_id: str,
        body: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> IntegrationResponse:
        """Execute a POST integration."""
        return await self.call(integration_id, params=params, body=body, **kwargs)
    
    # =========================================================================
    # MANAGEMENT
    # =========================================================================
    
    def clear_cache(self, integration_id: Optional[str] = None):
        """Clear response cache."""
        if integration_id:
            # Clear cache entries for specific integration
            # This is a simplified implementation
            self._response_cache.clear()
        else:
            self._response_cache.clear()
        logger.debug(f"Cleared cache for {integration_id or 'all'}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            'initialized': self._initialized,
            'total_calls': self._call_count,
            'total_errors': self._error_count,
            'cache_hits': self._cache_hits,
            'cache_hit_rate': (
                self._cache_hits / self._call_count 
                if self._call_count > 0 else 0
            ),
            'registry_status': integration_registry.get_status(),
        }
    
    def list_integrations(
        self,
        enabled_only: bool = True,
    ) -> List[Dict[str, Any]]:
        """List available integrations."""
        integrations = integration_registry.list_integrations(enabled_only=enabled_only)
        return [
            {
                'id': i.id,
                'name': i.name,
                'description': i.description,
                'enabled': i.enabled,
                'method': i.endpoint.method.value,
                'has_auth': i.authentication is not None,
            }
            for i in integrations
        ]


# Singleton instance
integration_service = IntegrationService()


# Convenience functions for direct usage
async def call_integration(
    integration_id: str,
    params: Optional[Dict[str, Any]] = None,
    body: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> IntegrationResponse:
    """Execute an integration (convenience function)."""
    return await integration_service.call(
        integration_id,
        params=params,
        body=body,
        **kwargs,
    )


async def initialize_from_config() -> Dict[str, Any]:
    """
    Initialize the integration service from the unified config.
    
    Uses the Config singleton to get paths and settings.
    
    Returns:
        Initialization summary
        
    Usage:
        from common.services.integrations import initialize_from_config
        
        # At application startup
        summary = await initialize_from_config()
    """
    try:
        from common.utils.config import config
        
        # Get configuration from unified config
        int_config = config.get_integration_config()
        
        # Initialize with config values
        return await integration_service.initialize(
            credential_paths=int_config['credentials_dirs'],
            integration_paths=int_config['definitions_dirs'],
            config_path=int_config.get('config_file'),
            base_dir=int_config.get('base_dir'),
        )
        
    except ImportError:
        logger.warning(
            "Config module not available, using default initialization. "
            "Install common.utils.config or pass paths directly."
        )
        return await integration_service.initialize()
