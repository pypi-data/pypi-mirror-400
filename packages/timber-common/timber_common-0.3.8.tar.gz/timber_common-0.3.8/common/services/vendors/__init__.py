
# timber/services/__init__.py
"""
Timber Shared Services

Reusable business logic services for OakQuant applications.
These services encapsulate third-party integrations and can be
used by any application (Grove, Canopy, etc.)

Usage:
    from timber.services import stripe_service, plaid_service
    
    # Configure services at application startup
    stripe_service.configure(
        api_key=os.getenv('STRIPE_SECRET_KEY'),
        get_user=my_get_user_function,
        update_user=my_update_user_function
    )
    
    # Use services
    checkout = stripe_service.create_checkout_session(user_id="123")
"""

from .stripe_service import (
    StripeService,
    stripe_service,
    SubscriptionTier,
    SubscriptionStatus
)

from .plaid_service import (
    PlaidService,
    plaid_service,
    PlaidEnvironment,
    PlaidProduct,
    PlaidItem,
    LinkTokenResponse
)


__all__ = [
    # Stripe
    'StripeService',
    'stripe_service',
    'SubscriptionTier',
    'SubscriptionStatus',
    
    # Plaid
    'PlaidService',
    'plaid_service',
    'PlaidEnvironment',
    'PlaidProduct',
    'PlaidItem',
    'LinkTokenResponse',
]