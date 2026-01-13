"""
Custom exceptions for auth-gate.
"""

from typing import Optional

from fastapi import HTTPException, status

from .subscription import SubscriptionStatus, SubscriptionTier


class TierInsufficientError(HTTPException):
    """Raised when user's subscription tier is insufficient."""

    def __init__(
        self,
        required_tier: SubscriptionTier,
        current_tier: SubscriptionTier,
        detail: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail or f"Subscription tier '{required_tier.value}' or higher required",
            headers={
                "X-Required-Tier": required_tier.value,
                "X-Current-Tier": current_tier.value,
                "X-Upgrade-URL": "/subscription/upgrade",
            },
        )
        self.required_tier = required_tier
        self.current_tier = current_tier


class SubscriptionInactiveError(HTTPException):
    """Raised when subscription is not active."""

    def __init__(
        self,
        current_status: SubscriptionStatus,
        detail: Optional[str] = None,
    ):
        action_messages = {
            SubscriptionStatus.SUSPENDED: "Please contact support to reactivate your subscription",
            SubscriptionStatus.CANCELLED: "Please resubscribe to access this feature",
            SubscriptionStatus.PAST_DUE: "Please update your payment method",
        }

        message = detail or action_messages.get(current_status, "Your subscription is not active")

        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message,
            headers={
                "X-Subscription-Status": current_status.value,
                "X-Required-Action": action_messages.get(current_status, "Check subscription"),
            },
        )
        self.current_status = current_status
