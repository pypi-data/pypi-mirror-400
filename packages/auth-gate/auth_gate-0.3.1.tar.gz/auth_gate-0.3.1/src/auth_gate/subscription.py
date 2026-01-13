"""
Subscription tier types and utilities for auth-gate.
"""

from enum import Enum
from typing import List


class SubscriptionTier(str, Enum):
    """Subscription tier levels."""

    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Subscription status values."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"


# Tier hierarchy for comparison (index = priority level)
TIER_HIERARCHY: List[SubscriptionTier] = [
    SubscriptionTier.FREE,
    SubscriptionTier.BASIC,
    SubscriptionTier.PROFESSIONAL,
    SubscriptionTier.ENTERPRISE,
]


def get_tier_level(tier: SubscriptionTier) -> int:
    """Get the numeric level of a tier (for comparisons)."""
    try:
        return TIER_HIERARCHY.index(tier)
    except ValueError:
        return 0  # Default to FREE level


def meets_minimum_tier(user_tier: SubscriptionTier, required_tier: SubscriptionTier) -> bool:
    """
    Check if user_tier meets or exceeds required_tier.

    Args:
        user_tier: The user's current subscription tier
        required_tier: The minimum required tier

    Returns:
        True if user_tier >= required_tier in hierarchy
    """
    return get_tier_level(user_tier) >= get_tier_level(required_tier)


def compare_tiers(tier_a: SubscriptionTier, tier_b: SubscriptionTier) -> int:
    """
    Compare two tiers.

    Returns:
        negative if a < b, 0 if equal, positive if a > b
    """
    return get_tier_level(tier_a) - get_tier_level(tier_b)


def get_tiers_at_or_above(tier: SubscriptionTier) -> List[SubscriptionTier]:
    """Get all tiers at or above the given tier."""
    level = get_tier_level(tier)
    return TIER_HIERARCHY[level:]


def get_tiers_below(tier: SubscriptionTier) -> List[SubscriptionTier]:
    """Get all tiers below the given tier."""
    level = get_tier_level(tier)
    return TIER_HIERARCHY[:level]


def is_paid_tier(tier: SubscriptionTier) -> bool:
    """Check if a tier is a paid tier (non-free)."""
    return tier != SubscriptionTier.FREE


def parse_subscription_tier(
    value: str | None, default: SubscriptionTier = SubscriptionTier.FREE
) -> SubscriptionTier:
    """
    Safely parse a subscription tier string.

    Args:
        value: The tier string to parse
        default: Default tier if parsing fails

    Returns:
        Parsed SubscriptionTier or default
    """
    if not value:
        return default

    try:
        return SubscriptionTier(value.lower())
    except ValueError:
        return default


def parse_subscription_status(
    value: str | None, default: SubscriptionStatus = SubscriptionStatus.ACTIVE
) -> SubscriptionStatus:
    """
    Safely parse a subscription status string.

    Args:
        value: The status string to parse
        default: Default status if parsing fails

    Returns:
        Parsed SubscriptionStatus or default
    """
    if not value:
        return default

    try:
        return SubscriptionStatus(value.lower())
    except ValueError:
        return default
