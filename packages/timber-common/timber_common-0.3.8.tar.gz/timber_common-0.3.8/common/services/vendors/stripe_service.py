# common/services/vendors/stripe_service.py
"""
Stripe Service - Shared Subscription Management

Reusable Stripe integration for subscription-based applications.
Used by Grove API but can be imported by any OakQuant application.

Usage:
    from timber.services.stripe_service import stripe_service
    
    # Create checkout session
    session = stripe_service.create_checkout_session(
        user_id="user_123",
        user_email="user@example.com"
    )
    
    # Handle webhook
    result = stripe_service.handle_webhook(payload, sig_header)
"""

import stripe
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SubscriptionTier(str, Enum):
    """Available subscription tiers"""
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class SubscriptionStatus:
    """Subscription status for a user"""
    user_id: str
    tier: SubscriptionTier
    status: str  # active, past_due, canceled, etc.
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False


class StripeService:
    """
    Stripe integration service for subscription management.
    
    This service handles:
    - Checkout session creation
    - Billing portal sessions
    - Webhook processing
    - Subscription status queries
    
    Designed to be reusable across multiple OakQuant applications.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        webhook_secret: Optional[str] = None,
        default_price_id: Optional[str] = None,
        default_success_url: str = "/subscription?status=success",
        default_cancel_url: str = "/subscription?status=cancel",
        default_portal_return_url: str = "/subscription"
    ):
        """
        Initialize the Stripe service.
        
        Args:
            api_key: Stripe secret key (or set STRIPE_SECRET_KEY env var)
            webhook_secret: Stripe webhook signing secret
            default_price_id: Default price ID for subscriptions
            default_success_url: Default redirect after successful payment
            default_cancel_url: Default redirect if payment cancelled
            default_portal_return_url: Default return URL from billing portal
        """
        self._api_key = api_key
        self._webhook_secret = webhook_secret
        self._default_price_id = default_price_id
        self._default_success_url = default_success_url
        self._default_cancel_url = default_cancel_url
        self._default_portal_return_url = default_portal_return_url
        
        # Callbacks for application-specific logic
        self._get_user_callback: Optional[Callable] = None
        self._update_user_callback: Optional[Callable] = None
        self._get_customer_id_callback: Optional[Callable] = None
        self._save_customer_id_callback: Optional[Callable] = None
        
        self._initialized = False
    
    def configure(
        self,
        api_key: Optional[str] = None,
        webhook_secret: Optional[str] = None,
        default_price_id: Optional[str] = None,
        get_user: Optional[Callable] = None,
        update_user: Optional[Callable] = None,
        get_customer_id: Optional[Callable] = None,
        save_customer_id: Optional[Callable] = None
    ):
        """
        Configure the service with application-specific settings.
        
        This allows different applications to provide their own:
        - User lookup/update functions
        - Customer ID storage
        - Configuration values
        
        Args:
            api_key: Stripe secret key
            webhook_secret: Stripe webhook signing secret
            default_price_id: Default subscription price ID
            get_user: Callback to get user by ID: (user_id) -> user_object
            update_user: Callback to update user: (user_id, updates_dict) -> None
            get_customer_id: Callback to get Stripe customer ID: (user_id) -> str
            save_customer_id: Callback to save Stripe customer ID: (user_id, customer_id) -> None
        """
        import os
        
        self._api_key = api_key or os.getenv('STRIPE_SECRET_KEY')
        self._webhook_secret = webhook_secret or os.getenv('STRIPE_WEBHOOK_SECRET')
        self._default_price_id = default_price_id or os.getenv('STRIPE_PREMIUM_PRICE_ID')
        
        if get_user:
            self._get_user_callback = get_user
        if update_user:
            self._update_user_callback = update_user
        if get_customer_id:
            self._get_customer_id_callback = get_customer_id
        if save_customer_id:
            self._save_customer_id_callback = save_customer_id
        
        if self._api_key:
            stripe.api_key = self._api_key
            self._initialized = True
            logger.info("Stripe service configured successfully")
        else:
            logger.warning("Stripe service not configured - missing API key")
    
    def _ensure_initialized(self):
        """Ensure service is configured before use."""
        if not self._initialized:
            self.configure()  # Try to configure from environment
        if not self._initialized:
            raise RuntimeError("Stripe service not configured. Call configure() first.")
    
    # ===== Checkout Session =====
    
    def create_checkout_session(
        self,
        user_id: str,
        user_email: Optional[str] = None,
        price_id: Optional[str] = None,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> stripe.checkout.Session:
        """
        Create a Stripe Checkout session for subscription.
        
        Args:
            user_id: Internal user ID (stored as client_reference_id)
            user_email: User's email for Stripe receipt
            price_id: Stripe Price ID (uses default if not provided)
            success_url: Redirect URL after successful payment
            cancel_url: Redirect URL if cancelled
            metadata: Additional metadata to store with session
            
        Returns:
            Stripe Checkout Session object
        """
        self._ensure_initialized()
        
        session_params = {
            'line_items': [{
                'price': price_id or self._default_price_id,
                'quantity': 1,
            }],
            'mode': 'subscription',
            'client_reference_id': str(user_id),
            'success_url': success_url or self._default_success_url,
            'cancel_url': cancel_url or self._default_cancel_url,
        }
        
        if user_email:
            session_params['customer_email'] = user_email
        
        if metadata:
            session_params['metadata'] = metadata
        
        # If we have an existing customer ID, use it
        if self._get_customer_id_callback:
            customer_id = self._get_customer_id_callback(user_id)
            if customer_id:
                session_params['customer'] = customer_id
                del session_params.get('customer_email', None)  # Can't use both
        
        logger.info(f"Creating checkout session for user {user_id}")
        session = stripe.checkout.Session.create(**session_params)
        
        return session
    
    # ===== Billing Portal =====
    
    def create_portal_session(
        self,
        user_id: str,
        return_url: Optional[str] = None
    ) -> stripe.billing_portal.Session:
        """
        Create a Stripe Billing Portal session.
        
        Allows users to manage subscriptions, payment methods, and invoices.
        
        Args:
            user_id: Internal user ID
            return_url: URL to redirect after portal session
            
        Returns:
            Stripe Billing Portal Session object
        """
        self._ensure_initialized()
        
        # Get the customer ID for this user
        customer_id = None
        if self._get_customer_id_callback:
            customer_id = self._get_customer_id_callback(user_id)
        
        if not customer_id:
            raise ValueError(f"No Stripe customer found for user {user_id}")
        
        logger.info(f"Creating portal session for user {user_id}")
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url or self._default_portal_return_url
        )
        
        return session
    
    # ===== Subscription Status =====
    
    def get_subscription_status(self, user_id: str) -> SubscriptionStatus:
        """
        Get current subscription status for a user.
        
        Args:
            user_id: Internal user ID
            
        Returns:
            SubscriptionStatus object
        """
        self._ensure_initialized()
        
        # Get customer ID
        customer_id = None
        if self._get_customer_id_callback:
            customer_id = self._get_customer_id_callback(user_id)
        
        if not customer_id:
            # User has no Stripe customer - free tier
            return SubscriptionStatus(
                user_id=user_id,
                tier=SubscriptionTier.FREE,
                status="none"
            )
        
        # Fetch subscriptions from Stripe
        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            status='all',
            limit=1
        )
        
        if not subscriptions.data:
            return SubscriptionStatus(
                user_id=user_id,
                tier=SubscriptionTier.FREE,
                status="none",
                stripe_customer_id=customer_id
            )
        
        sub = subscriptions.data[0]
        
        # Determine tier from price ID
        tier = self._determine_tier_from_subscription(sub)
        
        return SubscriptionStatus(
            user_id=user_id,
            tier=tier,
            status=sub.status,
            stripe_customer_id=customer_id,
            stripe_subscription_id=sub.id,
            current_period_end=datetime.fromtimestamp(sub.current_period_end),
            cancel_at_period_end=sub.cancel_at_period_end
        )
    
    def _determine_tier_from_subscription(
        self, 
        subscription: stripe.Subscription
    ) -> SubscriptionTier:
        """Determine subscription tier from Stripe subscription."""
        # This can be customized based on your price IDs
        if subscription.status in ['active', 'trialing']:
            return SubscriptionTier.PREMIUM
        return SubscriptionTier.FREE
    
    # ===== Webhook Handling =====
    
    def handle_webhook(
        self,
        payload: bytes,
        sig_header: str
    ) -> Dict[str, Any]:
        """
        Process a Stripe webhook event.
        
        Handles:
        - checkout.session.completed
        - customer.subscription.updated
        - customer.subscription.deleted
        - invoice.payment_failed
        
        Args:
            payload: Raw request body
            sig_header: Stripe-Signature header value
            
        Returns:
            Processing result
        """
        self._ensure_initialized()
        
        if not self._webhook_secret:
            raise ValueError("Webhook secret not configured")
        
        # Verify signature
        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=self._webhook_secret
            )
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {e}")
            raise ValueError("Invalid signature")
        
        event_type = event['type']
        event_data = event['data']['object']
        
        logger.info(f"Processing Stripe webhook: {event_type}")
        
        # Route to appropriate handler
        handlers = {
            'checkout.session.completed': self._handle_checkout_completed,
            'customer.subscription.updated': self._handle_subscription_updated,
            'customer.subscription.deleted': self._handle_subscription_deleted,
            'invoice.payment_failed': self._handle_payment_failed,
        }
        
        handler = handlers.get(event_type)
        if handler:
            return handler(event_data)
        else:
            logger.debug(f"Unhandled webhook event type: {event_type}")
            return {"status": "ignored", "event_type": event_type}
    
    def _handle_checkout_completed(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful checkout."""
        user_id = session.get('client_reference_id')
        customer_id = session.get('customer')
        subscription_id = session.get('subscription')
        
        if not user_id:
            logger.error("Checkout completed without client_reference_id")
            return {"status": "error", "reason": "missing user_id"}
        
        logger.info(f"Checkout completed for user {user_id}")
        
        # Save customer ID for future use
        if self._save_customer_id_callback and customer_id:
            self._save_customer_id_callback(user_id, customer_id)
        
        # Update user subscription tier
        if self._update_user_callback:
            self._update_user_callback(user_id, {
                'subscription_tier': SubscriptionTier.PREMIUM.value,
                'stripe_customer_id': customer_id,
                'stripe_subscription_id': subscription_id
            })
        
        return {"status": "success", "user_id": user_id, "tier": "premium"}
    
    def _handle_subscription_updated(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription updates."""
        customer_id = subscription.get('customer')
        status = subscription.get('status')
        
        logger.info(f"Subscription updated for customer {customer_id}: {status}")
        
        # Application should implement lookup by customer_id
        # and update the user's subscription status
        
        return {"status": "processed", "subscription_status": status}
    
    def _handle_subscription_deleted(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription cancellation."""
        customer_id = subscription.get('customer')
        
        logger.info(f"Subscription deleted for customer {customer_id}")
        
        # Application should implement lookup by customer_id
        # and downgrade the user to free tier
        
        return {"status": "processed", "action": "downgraded"}
    
    def _handle_payment_failed(self, invoice: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed payment."""
        customer_id = invoice.get('customer')
        
        logger.warning(f"Payment failed for customer {customer_id}")
        
        # Application might want to notify the user
        # or mark the subscription as past_due
        
        return {"status": "processed", "action": "payment_failed_notification"}


# Singleton instance for easy import
stripe_service = StripeService()


# Export
__all__ = ['StripeService', 'stripe_service', 'SubscriptionTier', 'SubscriptionStatus']