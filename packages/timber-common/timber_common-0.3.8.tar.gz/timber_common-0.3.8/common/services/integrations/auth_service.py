# common/services/integrations/auth_service.py
"""
Authentication Service

Handles authentication for integrations including:
- Basic Auth
- API Key (header, query param, body)
- OAuth2 Client Credentials (with token caching)
- OAuth2 Authorization Code (with refresh)
- Bearer Token
- Custom Headers
- AWS Signature V4
- Certificate-based (mTLS)
"""

from __future__ import annotations
import base64
import hashlib
import hmac
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlencode
import httpx

from .models import (
    Credential,
    AuthType,
    CachedToken,
    BasicAuthConfig,
    ApiKeyConfig,
    OAuth2ClientCredentialsConfig,
    BearerTokenConfig,
    CustomHeadersConfig,
    ParamLocation,
)
from .registry import integration_registry

logger = logging.getLogger(__name__)


class TokenCache:
    """In-memory token cache with TTL."""
    
    def __init__(self):
        self._cache: Dict[str, CachedToken] = {}
    
    def get(self, key: str) -> Optional[CachedToken]:
        """Get a cached token if not expired."""
        token = self._cache.get(key)
        if token and not token.is_expired():
            return token
        return None
    
    def set(self, key: str, token: CachedToken):
        """Cache a token."""
        self._cache[key] = token
    
    def delete(self, key: str):
        """Remove a cached token."""
        self._cache.pop(key, None)
    
    def clear(self):
        """Clear all cached tokens."""
        self._cache.clear()


class AuthService:
    """
    Service for handling authentication across different providers.
    
    Supports multiple auth types and manages token lifecycle.
    """
    
    def __init__(self):
        self._token_cache = TokenCache()
        self._http_client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client for token requests."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client
    
    async def close(self):
        """Close the HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
    
    # =========================================================================
    # MAIN AUTHENTICATION METHOD
    # =========================================================================
    
    async def apply_authentication(
        self,
        credential: Credential,
        headers: Dict[str, str],
        params: Dict[str, Any],
        body: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> Tuple[Dict[str, str], Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        Apply authentication to a request.
        
        Args:
            credential: The credential to use
            headers: Request headers (modified in place)
            params: Query parameters (modified in place)
            body: Request body (modified in place if needed)
            user_id: User ID for user-context OAuth
            
        Returns:
            Tuple of (headers, params, body) with auth applied
        """
        auth_type = credential.type
        
        if auth_type == AuthType.NONE:
            pass
        
        elif auth_type == AuthType.BASIC:
            headers = self._apply_basic_auth(credential, headers)
        
        elif auth_type == AuthType.API_KEY:
            headers, params, body = self._apply_api_key(
                credential, headers, params, body
            )
        
        elif auth_type == AuthType.BEARER_TOKEN:
            headers = self._apply_bearer_token(credential, headers)
        
        elif auth_type == AuthType.OAUTH2_CLIENT_CREDENTIALS:
            headers = await self._apply_oauth2_client_credentials(
                credential, headers
            )
        
        elif auth_type == AuthType.OAUTH2_AUTHORIZATION_CODE:
            headers = await self._apply_oauth2_authorization_code(
                credential, headers, user_id
            )
        
        elif auth_type == AuthType.CUSTOM_HEADERS:
            headers = self._apply_custom_headers(credential, headers)
        
        elif auth_type == AuthType.AWS_SIGNATURE_V4:
            # AWS Signature requires request details, handled separately
            logger.warning("AWS Signature V4 requires special handling")
        
        elif auth_type == AuthType.CERTIFICATE:
            # Certificate auth is handled at HTTP client level
            logger.debug("Certificate auth handled by HTTP client")
        
        else:
            logger.warning(f"Unknown auth type: {auth_type}")
        
        return headers, params, body
    
    # =========================================================================
    # BASIC AUTH
    # =========================================================================
    
    def _apply_basic_auth(
        self,
        credential: Credential,
        headers: Dict[str, str],
    ) -> Dict[str, str]:
        """Apply Basic authentication."""
        config = credential.get_typed_config()
        
        if isinstance(config, BasicAuthConfig):
            credentials = f"{config.username}:{config.password}"
            encoded = base64.b64encode(credentials.encode()).decode()
            headers['Authorization'] = f"Basic {encoded}"
        else:
            # Fallback for dict config
            username = credential.config.get('username', '')
            password = credential.config.get('password', '')
            credentials = f"{username}:{password}"
            encoded = base64.b64encode(credentials.encode()).decode()
            headers['Authorization'] = f"Basic {encoded}"
        
        logger.debug("Applied Basic authentication")
        return headers
    
    # =========================================================================
    # API KEY
    # =========================================================================
    
    def _apply_api_key(
        self,
        credential: Credential,
        headers: Dict[str, str],
        params: Dict[str, Any],
        body: Optional[Dict[str, Any]],
    ) -> Tuple[Dict[str, str], Dict[str, Any], Optional[Dict[str, Any]]]:
        """Apply API key authentication."""
        config = credential.config
        key = config.get('key', '')
        location = config.get('location', 'header')
        prefix = config.get('prefix', '')
        
        if location == 'header':
            header_name = config.get('header_name', 'X-API-Key')
            headers[header_name] = f"{prefix}{key}"
            
        elif location == 'query_param':
            param_name = config.get('param_name', 'api_key')
            params[param_name] = key
            
        elif location == 'body':
            if body is not None:
                param_name = config.get('param_name', 'api_key')
                body[param_name] = key
        
        logger.debug(f"Applied API key authentication (location: {location})")
        return headers, params, body
    
    # =========================================================================
    # BEARER TOKEN
    # =========================================================================
    
    def _apply_bearer_token(
        self,
        credential: Credential,
        headers: Dict[str, str],
    ) -> Dict[str, str]:
        """Apply Bearer token authentication."""
        config = credential.config
        token = config.get('token', '')
        header_name = config.get('header_name', 'Authorization')
        prefix = config.get('prefix', 'Bearer ')
        
        headers[header_name] = f"{prefix}{token}"
        
        logger.debug("Applied Bearer token authentication")
        return headers
    
    # =========================================================================
    # CUSTOM HEADERS
    # =========================================================================
    
    def _apply_custom_headers(
        self,
        credential: Credential,
        headers: Dict[str, str],
    ) -> Dict[str, str]:
        """Apply custom headers."""
        config = credential.config
        custom_headers = config.get('headers', {})
        
        headers.update(custom_headers)
        
        logger.debug(f"Applied {len(custom_headers)} custom headers")
        return headers
    
    # =========================================================================
    # OAUTH2 CLIENT CREDENTIALS
    # =========================================================================
    
    async def _apply_oauth2_client_credentials(
        self,
        credential: Credential,
        headers: Dict[str, str],
    ) -> Dict[str, str]:
        """Apply OAuth2 client credentials authentication."""
        config = credential.config
        
        # Check cache first
        cache_key = f"oauth2_cc:{credential.id}"
        buffer_seconds = config.get('token_expiry_buffer_seconds', 300)
        
        cached_token = self._token_cache.get(cache_key)
        if cached_token and not cached_token.is_expired(buffer_seconds):
            headers['Authorization'] = f"{cached_token.token_type} {cached_token.access_token}"
            logger.debug(f"Using cached OAuth2 token for {credential.id}")
            return headers
        
        # Fetch new token
        token = await self._fetch_oauth2_token(config)
        
        if token:
            # Cache the token
            if config.get('cache_token', True):
                self._token_cache.set(cache_key, token)
            
            headers['Authorization'] = f"{token.token_type} {token.access_token}"
            logger.debug(f"Fetched new OAuth2 token for {credential.id}")
        else:
            logger.error(f"Failed to get OAuth2 token for {credential.id}")
        
        return headers
    
    async def _fetch_oauth2_token(
        self,
        config: Dict[str, Any],
    ) -> Optional[CachedToken]:
        """Fetch OAuth2 token from token endpoint."""
        token_url = config.get('token_url')
        client_id = config.get('client_id')
        client_secret = config.get('client_secret')
        scopes = config.get('scopes', [])
        extra_params = config.get('extra_params', {})
        
        if not all([token_url, client_id, client_secret]):
            logger.error("Missing OAuth2 configuration")
            return None
        
        # Build token request
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            **extra_params,
        }
        
        if scopes:
            data['scope'] = ' '.join(scopes)
        
        try:
            client = await self._get_client()
            response = await client.post(
                token_url,
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
            )
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Calculate expiry time
                expires_in = token_data.get('expires_in')
                expires_at = None
                if expires_in:
                    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
                
                return CachedToken(
                    access_token=token_data.get('access_token'),
                    token_type=token_data.get('token_type', 'Bearer'),
                    expires_at=expires_at,
                    refresh_token=token_data.get('refresh_token'),
                    scope=token_data.get('scope'),
                    extra={
                        'instance_url': token_data.get('instance_url'),  # Salesforce
                    }
                )
            else:
                logger.error(
                    f"OAuth2 token request failed: {response.status_code} - {response.text}"
                )
                return None
                
        except Exception as e:
            logger.error(f"OAuth2 token request error: {e}")
            return None
    
    # =========================================================================
    # OAUTH2 AUTHORIZATION CODE
    # =========================================================================
    
    async def _apply_oauth2_authorization_code(
        self,
        credential: Credential,
        headers: Dict[str, str],
        user_id: Optional[str] = None,
    ) -> Dict[str, str]:
        """Apply OAuth2 authorization code authentication (user context)."""
        if not user_id:
            logger.error("OAuth2 Authorization Code requires user_id")
            return headers
        
        config = credential.config
        
        # Look up user's token from storage
        token = await self._get_user_token(credential.id, user_id)
        
        if not token:
            logger.error(f"No token found for user {user_id}, credential {credential.id}")
            return headers
        
        # Check if refresh is needed
        buffer_seconds = config.get('token_expiry_buffer_seconds', 300)
        if token.is_expired(buffer_seconds):
            if token.refresh_token and config.get('refresh_enabled', True):
                token = await self._refresh_oauth2_token(config, token)
                if token:
                    await self._store_user_token(credential.id, user_id, token)
            else:
                logger.error(f"Token expired and no refresh available for user {user_id}")
                return headers
        
        if token:
            headers['Authorization'] = f"{token.token_type} {token.access_token}"
        
        return headers
    
    async def _get_user_token(
        self,
        credential_id: str,
        user_id: str,
    ) -> Optional[CachedToken]:
        """Get user's OAuth token from storage."""
        # TODO: Implement database storage lookup
        # For now, use in-memory cache
        cache_key = f"oauth2_user:{credential_id}:{user_id}"
        return self._token_cache.get(cache_key)
    
    async def _store_user_token(
        self,
        credential_id: str,
        user_id: str,
        token: CachedToken,
    ):
        """Store user's OAuth token."""
        # TODO: Implement database storage
        cache_key = f"oauth2_user:{credential_id}:{user_id}"
        self._token_cache.set(cache_key, token)
    
    async def _refresh_oauth2_token(
        self,
        config: Dict[str, Any],
        token: CachedToken,
    ) -> Optional[CachedToken]:
        """Refresh an OAuth2 token."""
        if not token.refresh_token:
            return None
        
        token_url = config.get('token_url')
        client_id = config.get('client_id')
        client_secret = config.get('client_secret')
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': token.refresh_token,
            'client_id': client_id,
            'client_secret': client_secret,
        }
        
        try:
            client = await self._get_client()
            response = await client.post(
                token_url,
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
            )
            
            if response.status_code == 200:
                token_data = response.json()
                
                expires_in = token_data.get('expires_in')
                expires_at = None
                if expires_in:
                    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
                
                return CachedToken(
                    access_token=token_data.get('access_token'),
                    token_type=token_data.get('token_type', 'Bearer'),
                    expires_at=expires_at,
                    refresh_token=token_data.get('refresh_token', token.refresh_token),
                    scope=token_data.get('scope'),
                )
            else:
                logger.error(f"Token refresh failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return None
    
    # =========================================================================
    # OAUTH2 AUTHORIZATION URL (for initial auth flow)
    # =========================================================================
    
    def get_authorization_url(
        self,
        credential_id: str,
        state: str,
        additional_params: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        """
        Generate OAuth2 authorization URL for user consent.
        
        Args:
            credential_id: The credential to use
            state: CSRF protection state parameter
            additional_params: Additional URL parameters
            
        Returns:
            Authorization URL or None if not applicable
        """
        credential = integration_registry.get_credential(credential_id)
        if not credential or credential.type != AuthType.OAUTH2_AUTHORIZATION_CODE:
            return None
        
        config = credential.config
        
        params = {
            'client_id': config.get('client_id'),
            'redirect_uri': config.get('redirect_uri'),
            'response_type': 'code',
            'state': state,
        }
        
        scopes = config.get('scopes', [])
        if scopes:
            params['scope'] = ' '.join(scopes)
        
        if additional_params:
            params.update(additional_params)
        
        auth_url = config.get('auth_url')
        return f"{auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(
        self,
        credential_id: str,
        code: str,
        user_id: str,
    ) -> Optional[CachedToken]:
        """
        Exchange authorization code for tokens.
        
        Args:
            credential_id: The credential to use
            code: Authorization code from callback
            user_id: User to store token for
            
        Returns:
            Token if successful
        """
        credential = integration_registry.get_credential(credential_id)
        if not credential:
            return None
        
        config = credential.config
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': config.get('client_id'),
            'client_secret': config.get('client_secret'),
            'redirect_uri': config.get('redirect_uri'),
        }
        
        try:
            client = await self._get_client()
            response = await client.post(
                config.get('token_url'),
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
            )
            
            if response.status_code == 200:
                token_data = response.json()
                
                expires_in = token_data.get('expires_in')
                expires_at = None
                if expires_in:
                    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
                
                token = CachedToken(
                    access_token=token_data.get('access_token'),
                    token_type=token_data.get('token_type', 'Bearer'),
                    expires_at=expires_at,
                    refresh_token=token_data.get('refresh_token'),
                    scope=token_data.get('scope'),
                )
                
                # Store the token
                await self._store_user_token(credential_id, user_id, token)
                
                return token
            else:
                logger.error(f"Code exchange failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Code exchange error: {e}")
            return None
    
    # =========================================================================
    # TOKEN MANAGEMENT
    # =========================================================================
    
    def clear_cached_token(self, credential_id: str):
        """Clear cached token for a credential."""
        cache_key = f"oauth2_cc:{credential_id}"
        self._token_cache.delete(cache_key)
        logger.debug(f"Cleared cached token for {credential_id}")
    
    def clear_user_token(self, credential_id: str, user_id: str):
        """Clear user's cached token."""
        cache_key = f"oauth2_user:{credential_id}:{user_id}"
        self._token_cache.delete(cache_key)
        logger.debug(f"Cleared user token for {credential_id}:{user_id}")
    
    def clear_all_tokens(self):
        """Clear all cached tokens."""
        self._token_cache.clear()
        logger.info("Cleared all cached tokens")


# Singleton instance
auth_service = AuthService()
