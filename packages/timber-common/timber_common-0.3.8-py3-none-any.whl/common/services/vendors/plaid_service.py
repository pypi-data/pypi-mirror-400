# common/services/vendors/plaid_service.py
"""
Plaid Service - Shared Financial Data Integration

Reusable Plaid integration for financial data access.
Used by Grove API but can be imported by any OakQuant application.

Usage:
    from timber.services.plaid_service import plaid_service
    
    # Configure with callbacks
    plaid_service.configure(
        client_id="your_client_id",
        secret="your_secret",
        save_access_token=my_save_function
    )
    
    # Create link token
    link_token = plaid_service.create_link_token(user_id="user_123")
"""

import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# Plaid SDK import (install with: pip install plaid-python)
try:
    import plaid
    from plaid.api import plaid_api
    from plaid.model.link_token_create_request import LinkTokenCreateRequest
    from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
    from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
    from plaid.model.products import Products
    from plaid.model.country_code import CountryCode
    PLAID_AVAILABLE = True
except ImportError:
    PLAID_AVAILABLE = False
    logger.warning("Plaid SDK not installed. Install with: pip install plaid-python")


class PlaidEnvironment(str, Enum):
    """Plaid API environments"""
    SANDBOX = "sandbox"
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class PlaidProduct(str, Enum):
    """Available Plaid products"""
    TRANSACTIONS = "transactions"
    AUTH = "auth"
    BALANCE = "balance"
    IDENTITY = "identity"
    INVESTMENTS = "investments"
    LIABILITIES = "liabilities"
    ASSETS = "assets"


@dataclass
class PlaidItem:
    """Represents a connected Plaid Item (bank connection)"""
    item_id: str
    user_id: str
    institution_id: Optional[str] = None
    institution_name: Optional[str] = None
    access_token_encrypted: Optional[str] = None  # Never store plain
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    status: str = "active"


@dataclass
class LinkTokenResponse:
    """Response from creating a link token"""
    link_token: str
    expiration: str
    request_id: str


class PlaidService:
    """
    Plaid integration service for financial data access.
    
    This service handles:
    - Link token creation
    - Public token exchange
    - Transaction fetching
    - Account balance queries
    
    Designed to be reusable across multiple OakQuant applications.
    """
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        secret: Optional[str] = None,
        environment: PlaidEnvironment = PlaidEnvironment.SANDBOX,
        default_products: Optional[List[PlaidProduct]] = None,
        default_country_codes: Optional[List[str]] = None
    ):
        """
        Initialize the Plaid service.
        
        Args:
            client_id: Plaid client ID
            secret: Plaid secret
            environment: Plaid environment (sandbox, development, production)
            default_products: Default products to request
            default_country_codes: Default country codes
        """
        self._client_id = client_id
        self._secret = secret
        self._environment = environment
        self._default_products = default_products or [
            PlaidProduct.TRANSACTIONS,
            PlaidProduct.AUTH
        ]
        self._default_country_codes = default_country_codes or ["US"]
        
        # Callbacks for application-specific logic
        self._save_access_token_callback: Optional[Callable] = None
        self._get_access_token_callback: Optional[Callable] = None
        self._save_item_callback: Optional[Callable] = None
        self._get_items_callback: Optional[Callable] = None
        
        self._client: Optional[Any] = None
        self._initialized = False
    
    def configure(
        self,
        client_id: Optional[str] = None,
        secret: Optional[str] = None,
        environment: Optional[PlaidEnvironment] = None,
        save_access_token: Optional[Callable] = None,
        get_access_token: Optional[Callable] = None,
        save_item: Optional[Callable] = None,
        get_items: Optional[Callable] = None
    ):
        """
        Configure the service with application-specific settings.
        
        Args:
            client_id: Plaid client ID
            secret: Plaid secret
            environment: Plaid environment
            save_access_token: Callback to save encrypted access token
            get_access_token: Callback to get access token for item
            save_item: Callback to save Plaid item info
            get_items: Callback to get user's Plaid items
        """
        import os
        
        self._client_id = client_id or os.getenv('PLAID_CLIENT_ID')
        self._secret = secret or os.getenv('PLAID_SECRET')
        
        if environment:
            self._environment = environment
        else:
            env_str = os.getenv('PLAID_ENVIRONMENT', 'sandbox').lower()
            self._environment = PlaidEnvironment(env_str)
        
        if save_access_token:
            self._save_access_token_callback = save_access_token
        if get_access_token:
            self._get_access_token_callback = get_access_token
        if save_item:
            self._save_item_callback = save_item
        if get_items:
            self._get_items_callback = get_items
        
        if self._client_id and self._secret and PLAID_AVAILABLE:
            self._init_client()
            self._initialized = True
            logger.info(f"Plaid service configured ({self._environment.value})")
        elif not PLAID_AVAILABLE:
            logger.warning("Plaid SDK not available")
        else:
            logger.warning("Plaid service not configured - missing credentials")
    
    def _init_client(self):
        """Initialize the Plaid API client."""
        if not PLAID_AVAILABLE:
            raise RuntimeError("Plaid SDK not installed")
        
        # Map environment to Plaid host
        host_map = {
            PlaidEnvironment.SANDBOX: plaid.Environment.Sandbox,
            PlaidEnvironment.DEVELOPMENT: plaid.Environment.Development,
            PlaidEnvironment.PRODUCTION: plaid.Environment.Production,
        }
        
        configuration = plaid.Configuration(
            host=host_map[self._environment],
            api_key={
                'clientId': self._client_id,
                'secret': self._secret,
            }
        )
        
        api_client = plaid.ApiClient(configuration)
        self._client = plaid_api.PlaidApi(api_client)
    
    def _ensure_initialized(self):
        """Ensure service is configured before use."""
        if not self._initialized:
            self.configure()
        if not self._initialized:
            raise RuntimeError("Plaid service not configured. Call configure() first.")
    
    # ===== Link Token =====
    
    def create_link_token(
        self,
        user_id: str,
        products: Optional[List[PlaidProduct]] = None,
        redirect_uri: Optional[str] = None,
        webhook_url: Optional[str] = None,
        access_token: Optional[str] = None  # For update mode
    ) -> LinkTokenResponse:
        """
        Create a Plaid Link token for initializing Plaid Link.
        
        Args:
            user_id: Internal user ID
            products: Products to enable (uses default if not provided)
            redirect_uri: OAuth redirect URI (for OAuth institutions)
            webhook_url: URL for Plaid webhooks
            access_token: Existing access token for update mode
            
        Returns:
            LinkTokenResponse with link_token
        """
        self._ensure_initialized()
        
        products_to_use = products or self._default_products
        
        # Build request
        request_params = {
            'user': LinkTokenCreateRequestUser(client_user_id=str(user_id)),
            'client_name': 'OakQuant',
            'products': [Products(p.value) for p in products_to_use],
            'country_codes': [CountryCode(c) for c in self._default_country_codes],
            'language': 'en',
        }
        
        if redirect_uri:
            request_params['redirect_uri'] = redirect_uri
        
        if webhook_url:
            request_params['webhook'] = webhook_url
        
        if access_token:
            # Update mode - re-authenticate existing connection
            request_params['access_token'] = access_token
            del request_params['products']  # Not allowed in update mode
        
        request = LinkTokenCreateRequest(**request_params)
        
        logger.info(f"Creating Plaid link token for user {user_id}")
        response = self._client.link_token_create(request)
        
        return LinkTokenResponse(
            link_token=response['link_token'],
            expiration=response['expiration'],
            request_id=response['request_id']
        )
    
    # ===== Public Token Exchange =====
    
    def exchange_public_token(
        self,
        public_token: str,
        user_id: str,
        institution_id: Optional[str] = None,
        institution_name: Optional[str] = None
    ) -> PlaidItem:
        """
        Exchange a public token for an access token.
        
        The access token is encrypted and stored via the callback.
        
        Args:
            public_token: Public token from Plaid Link
            user_id: Internal user ID
            institution_id: Institution identifier
            institution_name: Institution display name
            
        Returns:
            PlaidItem representing the connection
        """
        self._ensure_initialized()
        
        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        
        logger.info(f"Exchanging public token for user {user_id}")
        response = self._client.item_public_token_exchange(request)
        
        access_token = response['access_token']
        item_id = response['item_id']
        
        # Create item record
        item = PlaidItem(
            item_id=item_id,
            user_id=user_id,
            institution_id=institution_id,
            institution_name=institution_name,
            created_at=datetime.utcnow(),
            status="active"
        )
        
        # Save via callbacks
        if self._save_access_token_callback:
            self._save_access_token_callback(
                user_id=user_id,
                item_id=item_id,
                access_token=access_token  # Callback should encrypt!
            )
        
        if self._save_item_callback:
            self._save_item_callback(item)
        
        logger.info(f"Successfully linked item {item_id} for user {user_id}")
        return item
    
    # ===== Account Data =====
    
    def get_accounts(self, user_id: str, item_id: str) -> List[Dict[str, Any]]:
        """
        Get accounts for a linked item.
        
        Args:
            user_id: Internal user ID
            item_id: Plaid item ID
            
        Returns:
            List of account dictionaries
        """
        self._ensure_initialized()
        
        if not self._get_access_token_callback:
            raise RuntimeError("get_access_token callback not configured")
        
        access_token = self._get_access_token_callback(user_id, item_id)
        if not access_token:
            raise ValueError(f"No access token found for item {item_id}")
        
        from plaid.model.accounts_get_request import AccountsGetRequest
        request = AccountsGetRequest(access_token=access_token)
        response = self._client.accounts_get(request)
        
        return [account.to_dict() for account in response['accounts']]
    
    def get_balances(self, user_id: str, item_id: str) -> List[Dict[str, Any]]:
        """
        Get real-time balances for accounts.
        
        Args:
            user_id: Internal user ID
            item_id: Plaid item ID
            
        Returns:
            List of accounts with balance information
        """
        self._ensure_initialized()
        
        if not self._get_access_token_callback:
            raise RuntimeError("get_access_token callback not configured")
        
        access_token = self._get_access_token_callback(user_id, item_id)
        if not access_token:
            raise ValueError(f"No access token found for item {item_id}")
        
        from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
        request = AccountsBalanceGetRequest(access_token=access_token)
        response = self._client.accounts_balance_get(request)
        
        return [account.to_dict() for account in response['accounts']]
    
    def get_transactions(
        self,
        user_id: str,
        item_id: str,
        start_date: date,
        end_date: date,
        account_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get transactions for a date range.
        
        Args:
            user_id: Internal user ID
            item_id: Plaid item ID
            start_date: Start of date range
            end_date: End of date range
            account_ids: Optional filter by account IDs
            
        Returns:
            List of transaction dictionaries
        """
        self._ensure_initialized()
        
        if not self._get_access_token_callback:
            raise RuntimeError("get_access_token callback not configured")
        
        access_token = self._get_access_token_callback(user_id, item_id)
        if not access_token:
            raise ValueError(f"No access token found for item {item_id}")
        
        from plaid.model.transactions_get_request import TransactionsGetRequest
        from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
        
        options = None
        if account_ids:
            options = TransactionsGetRequestOptions(account_ids=account_ids)
        
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options=options
        )
        
        response = self._client.transactions_get(request)
        
        transactions = response['transactions']
        
        # Handle pagination
        while len(transactions) < response['total_transactions']:
            options = TransactionsGetRequestOptions(
                account_ids=account_ids,
                offset=len(transactions)
            )
            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date,
                end_date=end_date,
                options=options
            )
            response = self._client.transactions_get(request)
            transactions.extend(response['transactions'])
        
        return [t.to_dict() for t in transactions]
    
    # ===== Webhook Handling =====
    
    def handle_webhook(
        self,
        webhook_type: str,
        webhook_code: str,
        item_id: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a Plaid webhook event.
        
        Args:
            webhook_type: Type of webhook (TRANSACTIONS, ITEM, etc.)
            webhook_code: Specific event code
            item_id: Plaid item ID
            payload: Full webhook payload
            
        Returns:
            Processing result
        """
        logger.info(f"Processing Plaid webhook: {webhook_type}/{webhook_code} for {item_id}")
        
        if webhook_type == "TRANSACTIONS":
            return self._handle_transactions_webhook(webhook_code, item_id, payload)
        elif webhook_type == "ITEM":
            return self._handle_item_webhook(webhook_code, item_id, payload)
        else:
            logger.debug(f"Unhandled webhook type: {webhook_type}")
            return {"status": "ignored", "webhook_type": webhook_type}
    
    def _handle_transactions_webhook(
        self,
        code: str,
        item_id: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle transaction-related webhooks."""
        if code == "INITIAL_UPDATE":
            logger.info(f"Initial transactions available for {item_id}")
            return {"status": "processed", "action": "initial_sync_available"}
        elif code == "HISTORICAL_UPDATE":
            logger.info(f"Historical transactions available for {item_id}")
            return {"status": "processed", "action": "historical_sync_available"}
        elif code == "DEFAULT_UPDATE":
            new_transactions = payload.get('new_transactions', 0)
            logger.info(f"{new_transactions} new transactions for {item_id}")
            return {"status": "processed", "new_transactions": new_transactions}
        elif code == "TRANSACTIONS_REMOVED":
            removed = payload.get('removed_transactions', [])
            logger.info(f"{len(removed)} transactions removed for {item_id}")
            return {"status": "processed", "removed_count": len(removed)}
        
        return {"status": "ignored", "code": code}
    
    def _handle_item_webhook(
        self,
        code: str,
        item_id: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle item-related webhooks."""
        if code == "ERROR":
            error = payload.get('error', {})
            logger.error(f"Plaid item error for {item_id}: {error}")
            return {"status": "error", "error": error}
        elif code == "PENDING_EXPIRATION":
            logger.warning(f"Plaid item {item_id} expiring soon")
            return {"status": "warning", "action": "reauth_needed"}
        
        return {"status": "ignored", "code": code}


# Singleton instance for easy import
plaid_service = PlaidService()


# Export
__all__ = [
    'PlaidService',
    'plaid_service',
    'PlaidEnvironment',
    'PlaidProduct',
    'PlaidItem',
    'LinkTokenResponse'
]