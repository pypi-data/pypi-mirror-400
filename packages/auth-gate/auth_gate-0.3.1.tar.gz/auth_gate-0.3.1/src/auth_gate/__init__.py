"""
Tradelink Authentication Client

Enterprise authentication client for microservices with Kong/Keycloak integration
and subscription tier support.
"""

from .config import AuthMode, AuthSettings, get_settings, reset_settings
from .exceptions import SubscriptionInactiveError, TierInsufficientError
from .fastapi_utils import (
    PlatformRole,
    get_current_auth,
    get_current_service,
    get_current_user,
    get_optional_auth,
    get_optional_user,
    get_organization_id,
    get_subscription_tier,
    is_bypass_mode,
    is_using_keycloak,
    is_using_kong,
    require_active_subscription,
    require_admin,
    require_basic,
    require_buyer,
    require_buyer_or_admin,
    require_customer,
    require_enterprise,
    require_moderator,
    require_paid_subscription,
    require_platform_admin,
    require_professional,
    require_roles,
    require_scopes,
    require_service_roles,
    require_supplier,
    require_supplier_capable,
    require_supplier_capable_or_admin,
    require_supplier_or_admin,
    require_tier,
    require_tier_and_active,
    require_user_admin,
    require_user_customer,
    require_user_moderator,
    require_user_role,
    require_user_roles,
    require_user_supplier,
    require_verified_supplier,
    verify_hmac_signature,
)
from .middleware import AuthMiddleware
from .s2s_auth import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
    ServiceAuthClient,
    ServiceToken,
    get_service_auth_client,
)
from .schemas import AuthContext, BaseAuthContext, ServiceContext, UserContext
from .subscription import (
    TIER_HIERARCHY,
    SubscriptionStatus,
    SubscriptionTier,
    compare_tiers,
    get_tier_level,
    get_tiers_at_or_above,
    get_tiers_below,
    is_paid_tier,
    meets_minimum_tier,
    parse_subscription_status,
    parse_subscription_tier,
)
from .user_auth import HMACVerifier, UserValidator, get_user_validator

__version__ = "0.3.1"

__all__ = [
    # Version
    "__version__",
    # Configuration
    "AuthSettings",
    "AuthMode",
    "get_settings",
    "reset_settings",
    # Schemas & Type Aliases
    "UserContext",
    "ServiceContext",
    "AuthContext",
    "BaseAuthContext",
    # Platform Role Constants
    "PlatformRole",
    # Subscription Types
    "SubscriptionTier",
    "SubscriptionStatus",
    "TIER_HIERARCHY",
    # Subscription Utilities
    "meets_minimum_tier",
    "compare_tiers",
    "get_tier_level",
    "get_tiers_at_or_above",
    "get_tiers_below",
    "is_paid_tier",
    "parse_subscription_tier",
    "parse_subscription_status",
    # Exceptions
    "TierInsufficientError",
    "SubscriptionInactiveError",
    # User Authentication
    "UserValidator",
    "HMACVerifier",
    "get_user_validator",
    # Service-to-Service
    "ServiceAuthClient",
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    "CircuitState",
    "ServiceToken",
    "get_service_auth_client",
    # Middleware
    "AuthMiddleware",
    # FastAPI Dependencies - Core
    "get_current_auth",
    "get_current_user",
    "get_current_service",
    "get_optional_auth",
    "get_optional_user",
    "get_organization_id",
    "get_subscription_tier",
    # FastAPI Dependencies - Roles
    "require_roles",
    "require_user_roles",
    "require_service_roles",
    "require_scopes",
    "require_admin",
    "require_supplier",
    "require_customer",
    "require_moderator",
    "require_supplier_or_admin",
    "require_user_admin",
    "require_user_customer",
    "require_user_supplier",
    "require_user_moderator",
    # FastAPI Dependencies - Platform Roles
    "require_user_role",
    "require_buyer",
    "require_buyer_or_admin",
    "require_supplier_capable",
    "require_supplier_capable_or_admin",
    "require_verified_supplier",
    "require_platform_admin",
    # FastAPI Dependencies - Subscription
    "require_tier",
    "require_active_subscription",
    "require_tier_and_active",
    "require_basic",
    "require_professional",
    "require_enterprise",
    "require_paid_subscription",
    # Utilities
    "verify_hmac_signature",
    # Mode Utilities
    "is_using_kong",
    "is_using_keycloak",
    "is_bypass_mode",
]
