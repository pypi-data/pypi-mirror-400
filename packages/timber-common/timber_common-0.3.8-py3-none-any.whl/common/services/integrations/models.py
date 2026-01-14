# common/services/integrations/models.py
"""
Integration Factory Data Models

Pydantic models for type-safe integration configuration and execution.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, Union, Literal
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from pydantic import BaseModel, Field, validator
import re


# =============================================================================
# ENUMS
# =============================================================================

class AuthType(str, Enum):
    """Supported authentication types."""
    NONE = "none"
    BASIC = "basic"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    OAUTH2_CLIENT_CREDENTIALS = "oauth2_client_credentials"
    OAUTH2_AUTHORIZATION_CODE = "oauth2_authorization_code"
    CUSTOM_HEADERS = "custom_headers"
    AWS_SIGNATURE_V4 = "aws_signature_v4"
    CERTIFICATE = "certificate"


class HttpMethod(str, Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class ParamLocation(str, Enum):
    """Where to place authentication parameters."""
    QUERY_PARAM = "query_param"
    HEADER = "header"
    BODY = "body"


class FieldType(str, Enum):
    """Supported field types for mapping."""
    STRING = "string"
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ARRAY = "array"
    OBJECT = "object"


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


# =============================================================================
# CREDENTIAL MODELS
# =============================================================================

class BasicAuthConfig(BaseModel):
    """Basic authentication configuration."""
    username: str
    password: str
    encoding: str = "base64"


class ApiKeyConfig(BaseModel):
    """API key authentication configuration."""
    key: str
    location: ParamLocation = ParamLocation.HEADER
    param_name: Optional[str] = None
    header_name: Optional[str] = None
    prefix: str = ""


class OAuth2ClientCredentialsConfig(BaseModel):
    """OAuth2 client credentials configuration."""
    client_id: str
    client_secret: str
    token_url: str
    scopes: List[str] = Field(default_factory=list)
    cache_token: bool = True
    token_expiry_buffer_seconds: int = 300
    extra_params: Dict[str, str] = Field(default_factory=dict)


class OAuth2AuthCodeConfig(BaseModel):
    """OAuth2 authorization code configuration."""
    client_id: str
    client_secret: str
    auth_url: str
    token_url: str
    redirect_uri: str
    scopes: List[str] = Field(default_factory=list)
    token_storage: str = "database"
    refresh_enabled: bool = True


class BearerTokenConfig(BaseModel):
    """Bearer token configuration."""
    token: str
    header_name: str = "Authorization"
    prefix: str = "Bearer "


class CustomHeadersConfig(BaseModel):
    """Custom headers configuration."""
    headers: Dict[str, str]


class AwsSignatureConfig(BaseModel):
    """AWS Signature V4 configuration."""
    access_key_id: str
    secret_access_key: str
    region: str
    service: str


class CertificateConfig(BaseModel):
    """Certificate-based authentication configuration."""
    cert_path: str
    key_path: str
    ca_bundle_path: Optional[str] = None
    key_password: Optional[str] = None


class Credential(BaseModel):
    """Credential definition."""
    id: str
    name: str
    type: AuthType
    description: Optional[str] = None
    config: Dict[str, Any]
    
    def get_typed_config(self) -> Any:
        """Get configuration as typed model."""
        type_map = {
            AuthType.BASIC: BasicAuthConfig,
            AuthType.API_KEY: ApiKeyConfig,
            AuthType.OAUTH2_CLIENT_CREDENTIALS: OAuth2ClientCredentialsConfig,
            AuthType.OAUTH2_AUTHORIZATION_CODE: OAuth2AuthCodeConfig,
            AuthType.BEARER_TOKEN: BearerTokenConfig,
            AuthType.CUSTOM_HEADERS: CustomHeadersConfig,
            AuthType.AWS_SIGNATURE_V4: AwsSignatureConfig,
            AuthType.CERTIFICATE: CertificateConfig,
        }
        
        config_class = type_map.get(self.type)
        if config_class:
            return config_class(**self.config)
        return self.config


# =============================================================================
# INTEGRATION CONFIGURATION MODELS
# =============================================================================

class RetryConfig(BaseModel):
    """Retry configuration."""
    enabled: bool = True
    max_attempts: int = 3
    initial_delay_ms: int = 1000
    backoff_multiplier: float = 2.0
    max_delay_ms: int = 30000
    retry_on_status: List[int] = Field(default_factory=lambda: [408, 429, 500, 502, 503, 504])


class ConnectionConfig(BaseModel):
    """Connection configuration."""
    base_url: str
    timeout_seconds: int = 30
    retry: RetryConfig = Field(default_factory=RetryConfig)


class ParamDefinition(BaseModel):
    """Parameter definition for query params or path params."""
    name: str
    required: bool = False
    type: str = "string"
    description: Optional[str] = None
    default: Optional[Any] = None
    delimiter: Optional[str] = None  # For array types
    format: Optional[str] = None     # For date types
    template: Optional[str] = None   # For templated values
    validation: Optional[Dict[str, Any]] = None


class QueryParamsConfig(BaseModel):
    """Query parameters configuration."""
    static: Dict[str, Any] = Field(default_factory=dict)
    dynamic: List[ParamDefinition] = Field(default_factory=list)


class EndpointConfig(BaseModel):
    """Endpoint configuration."""
    path: str
    method: HttpMethod = HttpMethod.GET
    query_params: QueryParamsConfig = Field(default_factory=QueryParamsConfig)
    path_params: List[ParamDefinition] = Field(default_factory=list)


class FieldMapping(BaseModel):
    """Field mapping configuration."""
    source: str
    target: str
    type: FieldType = FieldType.STRING
    required: bool = False
    default: Optional[Any] = None
    format: Optional[str] = None
    transform: Optional[str] = None
    validation: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class BodyConfig(BaseModel):
    """Request body configuration."""
    type: str = "json"  # json, form, xml, raw
    template: Dict[str, Any] = Field(default_factory=dict)
    wrapper: Optional[Dict[str, str]] = None
    mapping: List[FieldMapping] = Field(default_factory=list)
    signing: Optional[Dict[str, Any]] = None


class RequestConfig(BaseModel):
    """Request configuration."""
    headers: Dict[str, str] = Field(default_factory=dict)
    body: Optional[BodyConfig] = None


class ResponseMappingConfig(BaseModel):
    """Response mapping configuration."""
    root_path: Optional[str] = None
    type: str = "object"  # object, array, time_series
    fields: List[FieldMapping] = Field(default_factory=list)


class ErrorHandlingConfig(BaseModel):
    """Error handling configuration."""
    error_path: Optional[str] = None
    error_code_path: Optional[str] = None
    rate_limit_path: Optional[str] = None
    error_mappings: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class ResponseConfig(BaseModel):
    """Response configuration."""
    expected_status: List[int] = Field(default_factory=lambda: [200])
    content_type: str = "application/json"
    mapping: Optional[ResponseMappingConfig] = None
    error_handling: Optional[ErrorHandlingConfig] = None
    success_condition: Optional[str] = None


class CacheConfig(BaseModel):
    """Cache configuration."""
    enabled: bool = False
    ttl_seconds: int = 300
    key_template: Optional[str] = None


class RateLimitConfig(BaseModel):
    """Rate limit configuration."""
    requests_per_minute: Optional[int] = None
    requests_per_day: Optional[int] = None


class AuthenticationRef(BaseModel):
    """Authentication reference configuration."""
    credential_ref: str


class IntegrationDefinition(BaseModel):
    """Complete integration definition."""
    id: str
    name: str
    description: Optional[str] = None
    version: str = "1.0"
    enabled: bool = True
    
    connection: ConnectionConfig
    authentication: Optional[AuthenticationRef] = None
    endpoint: EndpointConfig
    request: RequestConfig = Field(default_factory=RequestConfig)
    response: ResponseConfig = Field(default_factory=ResponseConfig)
    
    cache: CacheConfig = Field(default_factory=CacheConfig)
    rate_limit: Optional[RateLimitConfig] = None
    
    # Additional metadata
    tags: List[str] = Field(default_factory=list)
    owner: Optional[str] = None


# =============================================================================
# EXECUTION MODELS
# =============================================================================

@dataclass
class IntegrationRequest:
    """Request to execute an integration."""
    integration_id: str
    params: Dict[str, Any] = field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    path_params: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Execution options
    skip_cache: bool = False
    timeout_override: Optional[int] = None
    trace_id: Optional[str] = None
    
    # For OAuth user-context
    user_id: Optional[str] = None


@dataclass
class IntegrationResponse:
    """Response from integration execution."""
    success: bool
    status_code: int
    data: Optional[Any] = None
    raw_response: Optional[Dict[str, Any]] = None
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Metadata
    integration_id: str = ""
    duration_ms: float = 0.0
    from_cache: bool = False
    retry_count: int = 0
    trace_id: Optional[str] = None
    
    # Error information
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    # Timestamps
    requested_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None


@dataclass 
class CachedToken:
    """Cached OAuth token."""
    access_token: str
    token_type: str = "Bearer"
    expires_at: Optional[datetime] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self, buffer_seconds: int = 0) -> bool:
        """Check if token is expired or about to expire."""
        if self.expires_at is None:
            return False
        from datetime import timezone
        now = datetime.now(timezone.utc)
        if self.expires_at.tzinfo is None:
            # Assume UTC if no timezone
            from datetime import timezone
            expires_at = self.expires_at.replace(tzinfo=timezone.utc)
        else:
            expires_at = self.expires_at
        return now >= (expires_at - timedelta(seconds=buffer_seconds))


@dataclass
class CircuitBreakerState:
    """Circuit breaker state for an integration."""
    integration_id: str
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    
    # Configuration
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: int = 60


# =============================================================================
# HELPER IMPORTS
# =============================================================================

from datetime import timedelta  # Needed for CachedToken.is_expired
