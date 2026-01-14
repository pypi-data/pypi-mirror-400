# timber/common/services/security/oauth_service.py
"""
Core OAuth 2.0 Authorization Server and Resource Protector Service.

This service works with FastAPI by creating OAuth2Request objects directly.
"""
from authlib.oauth2.rfc6749 import AuthorizationServer 
from authlib.oauth2.rfc6749 import ResourceProtector
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc6749.resource_protector import TokenValidator
from authlib.oauth2.rfc7636 import CodeChallenge
from authlib.common.security import generate_token
from datetime import datetime, timedelta, timezone 
from typing import Optional, Dict, Any, List
import uuid
import logging

from common.models.registry import model_registry
from common.services.db_service import db_service

logger = logging.getLogger(__name__)

# --- Helper to get models from registry ---
def _get_model(name: str):
    """Retrieves a model class from the application's registry."""
    model = model_registry.get_model(name)
    if not model:
        logger.error(f"OAuth Model '{name}' not found in registry.")
    return model


# --- Patch OAuth2Client with missing Authlib methods ---
def _patch_oauth2_client_methods():
    """
    Add required Authlib methods to OAuth2Client at runtime.
    
    This patches the OAuth2Client model without modifying your model factory.
    These methods are required by Authlib's ClientMixin but may be missing
    from config-driven models.
    """
    OAuth2Client = _get_model('OAuth2Client')
    if not OAuth2Client:
        logger.warning("OAuth2Client model not found - cannot patch methods")
        return
    
    # Check if method already exists
    if hasattr(OAuth2Client, 'check_endpoint_auth_method'):
        logger.debug("OAuth2Client already has check_endpoint_auth_method")
        return
    
    import secrets
    
    def check_endpoint_auth_method(self, method, endpoint):
        """
        Check if client supports the given authentication method for the endpoint.
        
        Args:
            method: 'client_secret_post', 'client_secret_basic', or 'none'
            endpoint: 'token', 'introspection', or 'revocation'
        
        Returns:
            bool: True if method is supported for this endpoint
        """
        if endpoint == 'token':
            # If client has a configured method, use it strictly
            if hasattr(self, 'token_endpoint_auth_method') and self.token_endpoint_auth_method:
                result = method == self.token_endpoint_auth_method
                logger.debug(f"Client {self.client_id}: checking {method} against configured {self.token_endpoint_auth_method} = {result}")
                return result
            
            # Otherwise allow common methods
            result = method in ['client_secret_post', 'client_secret_basic', 'none']
            logger.debug(f"Client {self.client_id}: {method} allowed by default = {result}")
            return result
        
        return False
    
    def has_client_secret(self):
        """Check if the client has a secret configured"""
        return bool(getattr(self, 'client_secret', None))
    
    def check_client_secret(self, client_secret):
        """Validate client secret using constant-time comparison"""
        logger.debug(f"check_client_secret called for client {self.client_id}")
        logger.debug(f"Has client_secret attribute: {hasattr(self, 'client_secret')}")
        
        if not self.has_client_secret():
            logger.warning(f"Client {self.client_id} has no secret configured")
            return False
        
        stored_secret = self.client_secret
        provided_secret = client_secret
        
        logger.debug(f"Stored secret length: {len(stored_secret)}")
        logger.debug(f"Provided secret length: {len(provided_secret)}")
        logger.debug(f"Stored secret (first 10 chars): {stored_secret[:10]}...")
        logger.debug(f"Provided secret (first 10 chars): {provided_secret[:10]}...")
        
        result = secrets.compare_digest(stored_secret, provided_secret)
        logger.debug(f"Secret comparison result: {result}")
        
        return result
    
    def get_client_id(self):
        """Return the client_id"""
        return self.client_id
    
    def get_default_redirect_uri(self):
        """Return the first redirect URI from registered list"""
        if not hasattr(self, 'redirect_uris') or not self.redirect_uris:
            return ''
        uris = [uri.strip() for uri in self.redirect_uris.split(',')]
        return uris[0] if uris else ''
    
    def check_redirect_uri(self, uri):
        """Check if redirect URI is registered"""
        if not uri or not hasattr(self, 'redirect_uris') or not self.redirect_uris:
            return False
        
        # Handle both PostgreSQL array and comma-separated string
        if isinstance(self.redirect_uris, list):
            uris = self.redirect_uris
        elif isinstance(self.redirect_uris, str):
            # Strip PostgreSQL array braces if present
            uris_str = self.redirect_uris.strip('{}')
            uris = [u.strip() for u in uris_str.split(',')]
        else:
            return False
        
        return uri in uris
    
    def get_allowed_scope(self, scope):
        """Return allowed scopes for this client"""
        if not scope:
            return ''
        if not hasattr(self, 'scope') or not self.scope:
            return ''
        
        # Handle both formats
        if isinstance(self.scope, list):
            allowed = set(self.scope)
        else:
            allowed = set(self.scope.split())
        
        requested = set(scope.split())
        return ' '.join([s for s in requested if s in allowed])
    
    def check_response_type(self, response_type):
        """Check if response_type is allowed"""
        if not hasattr(self, 'response_types') or not self.response_types:
            return False
        
        # Handle both PostgreSQL array and comma-separated string
        if isinstance(self.response_types, list):
            allowed = self.response_types
        elif isinstance(self.response_types, str):
            # Strip PostgreSQL array braces if present
            resp_str = self.response_types.strip('{}')
            allowed = [rt.strip() for rt in resp_str.split(',')]
        else:
            return False
        
        return response_type in allowed
    
    def check_grant_type(self, grant_type):
        """Check if grant_type is allowed"""
        if not hasattr(self, 'grant_types') or not self.grant_types:
            return False
        
        # Handle both PostgreSQL array and comma-separated string
        if isinstance(self.grant_types, list):
            allowed = self.grant_types
        elif isinstance(self.grant_types, str):
            # Strip PostgreSQL array braces if present
            grants_str = self.grant_types.strip('{}')
            allowed = [gt.strip() for gt in grants_str.split(',')]
        else:
            return False
        
        return grant_type in allowed
    
    # Patch the methods onto the class
    OAuth2Client.check_endpoint_auth_method = check_endpoint_auth_method
    OAuth2Client.has_client_secret = has_client_secret
    OAuth2Client.check_client_secret = check_client_secret
    OAuth2Client.get_client_id = get_client_id
    OAuth2Client.get_default_redirect_uri = get_default_redirect_uri
    OAuth2Client.check_redirect_uri = check_redirect_uri
    OAuth2Client.get_allowed_scope = get_allowed_scope
    OAuth2Client.check_response_type = check_response_type
    OAuth2Client.check_grant_type = check_grant_type
    
    logger.info("Patched OAuth2Client with required Authlib methods")


# --- Create OAuth2Request wrapper for FastAPI/Starlette ---

class PayloadObject:
    """
    Object wrapper for form data to provide attribute access.
    
    Authlib expects request.payload.grant_type (attribute access),
    not request.payload['grant_type'] (dict access).
    
    Authlib also expects request.payload.data.get("key") for optional params.
    """
    
    def __init__(self, form_data):
        self._data = dict(form_data) if form_data else {}
        # Store form data as object attributes for Authlib
        for key, value in self._data.items():
            setattr(self, key, value)
    
    @property
    def data(self):
        """Return the underlying dict - Authlib uses payload.data.get("key")"""
        return self._data
    
    def get(self, key, default=None):
        """Dict-like get method for compatibility."""
        return self._data.get(key, default)
    
    def __getitem__(self, key):
        """Dict-like item access for compatibility."""
        return self._data[key]
    
    def __contains__(self, key):
        """Dict-like 'in' operator for compatibility."""
        return key in self._data
    
    @property
    def datalist(self):
        """Return data as dict for validation."""
        # For validation that checks multiple values
        return {k: [v] for k, v in self._data.items()}


class StarletteOAuth2Request:
    """
    OAuth2Request wrapper for Starlette/FastAPI Request objects.
    
    This class wraps a Starlette Request and provides the interface
    that Authlib expects for OAuth2 request handling.
    
    CRITICAL: Authlib expects:
    - request.payload (form data as object with attribute access)
    - request.args (query params as dict)
    - request.form (form data as dict)
    - request.data (form data as dict)
    """
    
    def __init__(self, request):
        self._request = request
        self._form_data = None
        self._payload = None
        
    async def _load_form(self):
        """Load form data asynchronously if not already loaded."""
        if self._form_data is None:
            self._form_data = dict(await self._request.form())
            self._payload = PayloadObject(self._form_data)
        return self._form_data
    
    @property
    def payload(self):
        """
        Form data as object with attribute access.
        
        CRITICAL: Authlib's base.py expects request.payload.grant_type
        This MUST be an object with attributes, not a dict.
        """
        if self._payload is None:
            # If form hasn't been loaded yet, we need to do it synchronously
            # This happens when Authlib accesses payload before we've parsed the form
            import asyncio
            if self._form_data is None:
                # Try to get the event loop
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # We're in an async context but payload is accessed synchronously
                        # This shouldn't happen, but if it does, raise a clear error
                        raise RuntimeError(
                            "Form data not loaded. Call await request._load_form() before accessing payload."
                        )
                    else:
                        # Load it synchronously
                        self._form_data = dict(loop.run_until_complete(self._request.form()))
                        self._payload = PayloadObject(self._form_data)
                except RuntimeError:
                    # No event loop, create one
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    self._form_data = dict(loop.run_until_complete(self._request.form()))
                    self._payload = PayloadObject(self._form_data)
                    loop.close()
        return self._payload
    
    @property
    def args(self):
        """Query parameters as dict - Authlib expects this."""
        return dict(self._request.query_params)
    
    @property
    def form(self):
        """Form data as dict - needed for client authentication."""
        if self._form_data is None:
            return {}
        return self._form_data
    
    @property
    def data(self):
        """Form data as dict - alternative to form."""
        if self._form_data is None:
            return {}
        return self._form_data
    
    @property
    def method(self):
        """HTTP method."""
        return self._request.method
    
    @property
    def url(self):
        """Request URL as string."""
        return str(self._request.url)
    
    @property
    def headers(self):
        """Request headers."""
        return self._request.headers
    
    @property
    def client_id(self):
        """Get client_id from form data."""
        if self._form_data:
            return self._form_data.get('client_id')
        return None
    
    @property
    def grant_type(self):
        """Get grant_type from form data."""
        if self._form_data:
            return self._form_data.get('grant_type')
        return None
    
    def __getattr__(self, name):
        """Delegate other attribute access to the wrapped request."""
        return getattr(self._request, name)


# --- Custom Subclass for Core Authlib Integration ---
class ModularAuthorizationServer(AuthorizationServer):
    """
    Subclassing the generic Authlib AuthorizationServer to implement 
    the mandatory query_client and save_token methods.
    """
    
    def query_client(self, client_id: str):
        """Implements the mandatory client query for Authlib."""
        logger.debug(f"query_client called with client_id: {client_id}")
        
        OAuth2Client = _get_model('OAuth2Client')
        if not OAuth2Client:
            logger.error("OAuth2Client model not found in registry")
            return None
        
        with db_service.session_scope() as session:
            client = session.query(OAuth2Client).filter_by(client_id=client_id).first()
            if client:
                session.expunge(client)
                logger.info(f"Found client: {client_id}")
            else:
                logger.warning(f"Client not found: {client_id}")
            return client

    def save_token(self, token_data: Dict[str, Any], request: Any):
        """Implements the mandatory token saving for Authlib."""
        logger.info(f"Saving token for user: {getattr(request, 'user', 'N/A')}")
        
        OAuth2Token = _get_model('OAuth2Token')
        if not OAuth2Token:
            logger.error("OAuth2Token model not found in registry")
            return

        user_id = getattr(request, 'user', None) and request.user.id or "client_only"

        try:
            issued_at = datetime.now(timezone.utc)
            expires_in = token_data['expires_in']
            expires_at = issued_at + timedelta(seconds=expires_in)
            
            with db_service.session_scope() as session:
                token = OAuth2Token(
                    user_id=user_id,
                    client_id=request.client.client_id,
                    token_type=token_data['token_type'],
                    access_token=token_data['access_token'],
                    refresh_token=token_data.get('refresh_token'),
                    scope=token_data['scope'],
                    expires_in=expires_in,
                    issued_at=issued_at,
                    expires_at=expires_at 
                )
                session.add(token)
                logger.info(f"Token saved successfully for user_id: {user_id}")
        except Exception as e:
            logger.error(f"Failed to save OAuth token: {e}", exc_info=True)
    
    def generate_token(self, client, grant_type, user=None, scope=None, expires_in=None, include_refresh_token=True):
        """Generate access and refresh tokens"""
        from authlib.common.security import generate_token as generate_token_string
        
        logger.debug(f"Generating token for grant_type: {grant_type}")
        
        token = {
            'token_type': 'Bearer',
            'access_token': generate_token_string(42),
            'expires_in': expires_in or 3600,
            'scope': scope or '',
        }
        
        if include_refresh_token:
            token['refresh_token'] = generate_token_string(48)
        
        logger.debug(f"Token generated: {token['access_token'][:20]}...")
        return token
    
    def handle_response(self, status_code, payload, headers):
        """
        Handle OAuth2 response by returning a tuple that FastAPI can process.
        
        This is required by Authlib but was not implemented, causing NotImplementedError.
        """
        return status_code, payload, headers
    
    def send_signal(self, name, *args, **kwargs):
        """
        Send a signal/event notification.
        
        Authlib uses this for hooks like 'after_authenticate_client'.
        We don't need to do anything with signals for basic OAuth,
        but the method must exist to avoid NotImplementedError.
        
        Args:
            name: Signal name (e.g., 'after_authenticate_client')
            *args, **kwargs: Signal-specific arguments
        """
        logger.debug(f"Signal sent: {name}")
        # Signals are optional - we don't need to do anything
        pass

    def create_oauth2_request(self, request):
        """
        Convert FastAPI/Starlette Request to an object Authlib can use.
        
        This should only be called with an already-wrapped StarletteOAuth2Request
        that has form data pre-loaded. For initial wrapping, use create_oauth2_request_async.
        """
        # If it's already wrapped, just return it
        if isinstance(request, StarletteOAuth2Request):
            return request
        # Otherwise create a new wrapper (but form data won't be loaded yet)
        return StarletteOAuth2Request(request)
    
    async def create_oauth2_request_async(self, request):
        """
        Async method to create and pre-load the OAuth2 request wrapper.
        
        Call this from your FastAPI endpoints before passing to create_token_response.
        """
        wrapped = StarletteOAuth2Request(request)
        await wrapped._load_form()
        return wrapped


# --- Token Validator for Resource Protection ---
class MyTokenValidator(TokenValidator):
    
    def _to_aware_utc(self, dt: datetime) -> datetime:
        """Helper to force offset-naive datetimes to be timezone-aware UTC."""
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def _is_token_expired(self, token: Any) -> bool:
        """Utility to check expiry based on DB columns, since method is missing."""
        if not hasattr(token, 'expires_at') or token.expires_at is None:
            return False 
            
        # FIX 2: Ensure comparison is between two timezone-aware datetimes
        token_expiry_aware = self._to_aware_utc(token.expires_at)
        return datetime.now(timezone.utc) > token_expiry_aware

    def authenticate_token(self, token_string: str):
        """Authenticates an access token from the database."""
        OAuth2Token = _get_model('OAuth2Token')
        if not OAuth2Token: return None
            
        with db_service.session_scope() as session:
            token = session.query(OAuth2Token).filter_by(access_token=token_string).first()
            
            if token and not self._is_token_expired(token):
                session.expunge(token) 
                return token
            return None

    def request_invalid(self, request: Any):
        return False 

    def token_expired(self, token: Any):
        """Checks if the token has expired. Relies on model's logic."""
        # FIX 2: Use internal method to check expiry
        return self._is_token_expired(token)

    def scope_insufficient(self, token: Any, scope: str):
        if not scope: return False
        token_scopes = set(token.scope.split())
        required_scopes = set(scope.split())
        return not token_scopes.issuperset(required_scopes)

# --- OAuth Grant Type Implementations ---

class MyAuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    
    def _to_aware_utc(self, dt: datetime) -> datetime:
        """Helper to force offset-naive datetimes to be timezone-aware UTC."""
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def _is_code_expired(self, auth_code: Any) -> bool:
        """Utility to check Auth Code expiry based on DB columns."""
        if not hasattr(auth_code, 'expires_at') or auth_code.expires_at is None:
            return True 
            
        # FIX 2: Ensure comparison is between two timezone-aware datetimes
        code_expiry_aware = self._to_aware_utc(auth_code.expires_at)
        return datetime.now(timezone.utc) > code_expiry_aware

    def save_authorization_code(self, code: str, request: Any):
        """Saves the authorization code and associated request data."""
        OAuth2AuthorizationCode = _get_model('OAuth2AuthorizationCode')
        if not OAuth2AuthorizationCode:
            raise Exception("Authorization Code Model not available.")
            
        issued_at = datetime.now(timezone.utc)
        expires_at = issued_at + timedelta(minutes=5) # Auth Code standard expiry
        
        with db_service.session_scope() as session:
            auth_code = OAuth2AuthorizationCode(
                user_id=request.user.id,
                client_id=request.client.client_id, 
                code=code,
                redirect_uri=request.redirect_uri,
                scope=request.scope,
                issued_at=issued_at,
                expires_at=expires_at 
            )
            session.add(auth_code)
            
            # FIX: Expunge object before returning it to the test/Authlib for later use
            session.flush()
            session.expunge(auth_code)
            
            return auth_code

    def query_authorization_code(self, code: str, client: Any):
        """Retrieves an authorization code from the database."""
        OAuth2AuthorizationCode = _get_model('OAuth2AuthorizationCode')
        if not OAuth2AuthorizationCode: return None
            
        with db_service.session_scope() as session:
            auth_code = session.query(OAuth2AuthorizationCode).filter_by(
                code=code, client_id=client.client_id).first() 
                
            if auth_code and not self._is_code_expired(auth_code):
                session.expunge(auth_code) 
                return auth_code
            return None

    def delete_authorization_code(self, authorization_code: Any):
        OAuth2AuthorizationCode = _get_model('OAuth2AuthorizationCode')
        if not OAuth2AuthorizationCode: return
        with db_service.session_scope() as session:
            session.delete(session.merge(authorization_code))

    def authenticate_user(self, authorization_code: Any):
        User = _get_model('User')
        if not User: return None
        with db_service.session_scope() as session:
            user = session.query(User).get(authorization_code.user_id)
            if user: session.expunge(user) 
            return user


class MyPasswordGrant(grants.ResourceOwnerPasswordCredentialsGrant):
    """
    Password Grant (Resource Owner Password Credentials Grant).
    
    This grant type allows the client to exchange a username and password
    directly for an access token. It should only be used by trusted clients.
    
    Supports multiple client authentication methods:
    - client_secret_basic: Client credentials in Authorization header
    - client_secret_post: Client credentials in request body
    - none: Public clients (no authentication)
    """
    
    # CRITICAL: Support multiple authentication methods for web and mobile clients
    # client_secret_basic: For server-to-server (credentials in Authorization header)
    # client_secret_post: For web apps (credentials in POST body with username/password)
    # none: For public clients like mobile apps or SPAs
    TOKEN_ENDPOINT_AUTH_METHODS = ['client_secret_basic', 'client_secret_post', 'none']
    
    def authenticate_user(self, username: str, password: str):
        """
        Authenticate a user by username (email) and password.
        
        Args:
            username: User's email address
            password: User's plain-text password
            
        Returns:
            User object if authentication succeeds, None otherwise
        """
        logger.info(f"authenticate_user called with username: {username}")
        
        User = _get_model('User')
        if not User:
            logger.error("User model not found in registry")
            return None
        
        try:
            with db_service.session_scope() as session:
                # Find user by email
                logger.debug(f"Querying for user with email: {username}")
                user = session.query(User).filter_by(email=username).first()
                
                if not user:
                    logger.warning(f"Password grant: User not found: {username}")
                    # List available users for debugging
                    all_users = session.query(User).all()
                    logger.debug(f"Available users in database: {[u.email for u in all_users[:5]]}")
                    return None
                
                logger.debug(f"User found: {user.email}, ID: {user.id}")
                
                # Check if user is active
                is_active = getattr(user, 'is_active', True)
                logger.debug(f"User is_active: {is_active}")
                
                if not is_active:
                    logger.warning(f"Password grant: User not active: {username}")
                    return None
                
                # Verify password
                logger.debug(f"Checking password for user: {username}")
                
                if not hasattr(user, 'check_password'):
                    logger.error(f"User model has no check_password method!")
                    return None
                
                password_valid = user.check_password(password)
                logger.debug(f"Password validation result: {password_valid}")
                
                if not password_valid:
                    logger.warning(f"Password grant: Invalid password for user: {username}")
                    return None
                
                # Update last login
                if hasattr(user, 'update_last_login'):
                    logger.debug(f"Updating last login for user: {username}")
                    user.update_last_login()
                    session.flush()
                
                # Expunge to avoid detached instance issues
                session.expunge(user)
                
                logger.info(f"Password grant: User authenticated successfully: {username}")
                return user
                
        except Exception as e:
            logger.error(f"Password grant authentication error: {e}", exc_info=True)
            return None
        
        
class MyRefreshTokenGrant(grants.RefreshTokenGrant):
    
    def _is_refresh_token_active(self, token: Any) -> bool:
        """Utility to check refresh token validity (simple, based on access token expiry)."""
        # FIX: Access the token validator via the server object
        validator = self.server.resource_protector.get_token_validator(token.token_type)
        return not validator._is_token_expired(token)

    def authenticate_refresh_token(self, refresh_token: str):
        """Authenticates the refresh token from the database."""
        OAuth2Token = _get_model('OAuth2Token')
        if not OAuth2Token: return None
            
        with db_service.session_scope() as session:
            token = session.query(OAuth2Token).filter_by(refresh_token=refresh_token).first()
            
            # FIX: Use internal method
            if token and self._is_refresh_token_active(token): 
                session.expunge(token) 
                return token
            return None

    def create_access_token(self, token: Any, client: Any, request: Any):
        OAuth2Token = _get_model('OAuth2Token')
        if not OAuth2Token: return None
            
        with db_service.session_scope() as session:
            old_token = session.merge(token)
            session.delete(old_token)
            
            issued_at = datetime.now(timezone.utc)
            expires_at = issued_at + timedelta(seconds=3600)
            
            new_token = OAuth2Token(
                user_id=token.user_id,
                client_id=client.client_id,
                token_type=token.token_type,
                scope=request.scope,
                access_token=str(uuid.uuid4()), 
                refresh_token=str(uuid.uuid4()), 
                expires_in=3600,
                issued_at=issued_at,
                expires_at=expires_at
            )
            session.add(new_token)
            session.expunge(new_token) 
            return new_token


class MyClientCredentialsGrant(grants.ClientCredentialsGrant):
    def authenticate_client(self, client: Any):
        return client 

    def create_access_token(self, client: Any, request: Any):
        OAuth2Token = _get_model('OAuth2Token')
        if not OAuth2Token: return None
            
        with db_service.session_scope() as session:
            issued_at = datetime.now(timezone.utc)
            expires_at = issued_at + timedelta(seconds=3600)
            
            new_token = OAuth2Token(
                user_id="client_only", 
                client_id=client.client_id,
                token_type='bearer',
                scope=request.scope,
                access_token=str(uuid.uuid4()),
                expires_in=3600,
                issued_at=issued_at,
                expires_at=expires_at
            )
            session.add(new_token)
            session.expunge(new_token) 
            return new_token

# --- Core Service Objects ---

authorization = ModularAuthorizationServer()
resource_protector = ResourceProtector() 

# --- Initialization Function (Simplified for library use) ---

def init_oauth_service():
    """
    Initializes the core OAuth server logic.
    """
    logger.info("Initializing core OAuth service objects (Framework-Agnostic).")
    
    # CRITICAL: Patch OAuth2Client with required Authlib methods
    # This must be done before registering grants
    _patch_oauth2_client_methods()
    
    # Register Grant Types
    authorization.register_grant(MyAuthorizationCodeGrant, [CodeChallenge(required=False)]) 
    authorization.register_grant(MyPasswordGrant)
    authorization.register_grant(MyRefreshTokenGrant)
    authorization.register_grant(MyClientCredentialsGrant)
    
    # Register the validator explicitly
    resource_protector.register_token_validator(MyTokenValidator())
    
    # Attach resource protector instance to the authorization server instance
    authorization.resource_protector = resource_protector 
    
    logger.info("OAuth service initialized with Authorization Code, Password, Refresh, and Client Credentials grants.")

# Call the initialization function immediately to set up the grants
init_oauth_service()


__all__ = [
    'authorization',
    'resource_protector',
    'init_oauth_service',
    'MyAuthorizationCodeGrant',
    'MyPasswordGrant',
    'MyRefreshTokenGrant',
    '_get_model', 
]