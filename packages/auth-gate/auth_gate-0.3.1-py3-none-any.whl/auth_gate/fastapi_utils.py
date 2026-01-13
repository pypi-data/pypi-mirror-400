"""
FastAPI dependency injection utilities for authentication with subscription support.
"""

import logging
from typing import Awaitable, Callable, Optional

from fastapi import Depends, Header, HTTPException, Request, status

from .config import get_settings
from .exceptions import SubscriptionInactiveError, TierInsufficientError
from .schemas import AuthContext, ServiceContext, UserContext
from .subscription import (
    SubscriptionStatus,
    SubscriptionTier,
    meets_minimum_tier,
    parse_subscription_tier,
)
from .user_auth import HMACVerifier, get_user_validator

logger = logging.getLogger(__name__)


# Core authentication dependencies
async def get_current_auth(
    request: Request,
    authorization: Optional[str] = Header(None),
    x_token_verified: Optional[str] = Header(None, alias="X-Token-Verified"),
    x_auth_source: Optional[str] = Header(None, alias="X-Auth-Source"),
    # User headers
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    x_username: Optional[str] = Header(None, alias="X-Username"),
    x_user_email: Optional[str] = Header(None, alias="X-User-Email"),
    x_user_roles: Optional[str] = Header(None, alias="X-User-Roles"),
    x_user_scopes: Optional[str] = Header(None, alias="X-User-Scopes"),
    # Service headers
    x_service_name: Optional[str] = Header(None, alias="X-Service-Name"),
    x_service_authenticated: Optional[str] = Header(None, alias="X-Service-Authenticated"),
    x_service_roles: Optional[str] = Header(None, alias="X-Service-Roles"),
    # Common headers
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    x_client_id: Optional[str] = Header(None, alias="X-Client-ID"),
    # Organization header
    x_organization_id: Optional[str] = Header(None, alias="X-Organization-ID"),
    # Subscription headers
    x_subscription_tier: Optional[str] = Header(None, alias="X-Subscription-Tier"),
    x_subscription_status: Optional[str] = Header(None, alias="X-Subscription-Status"),
) -> AuthContext:
    """
    Main dependency for getting authenticated user or service.

    Returns either UserContext or ServiceContext based on the authentication type.

    Example:
        @app.get("/api/resource")
        async def get_resource(auth: AuthContext = Depends(get_current_auth)):
            if isinstance(auth, UserContext):
                return {"user_id": auth.user_id}
            elif isinstance(auth, ServiceContext):
                return {"service": auth.service_name}

    Args:
        Various authentication headers for both users and services

    Returns:
        AuthContext (UserContext or ServiceContext) with authenticated information

    Raises:
        HTTPException: If authentication fails
    """
    validator = get_user_validator()
    return await validator.get_current_user(
        request,
        authorization,
        x_token_verified,
        x_auth_source,
        x_user_id,
        x_username,
        x_user_email,
        x_user_roles,
        x_user_scopes,
        x_service_name,
        x_service_authenticated,
        x_service_roles,
        x_session_id,
        x_client_id,
        x_organization_id,
        x_subscription_tier,
        x_subscription_status,
    )


async def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(None),
    x_token_verified: Optional[str] = Header(None, alias="X-Token-Verified"),
    x_auth_source: Optional[str] = Header(None, alias="X-Auth-Source"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    x_username: Optional[str] = Header(None, alias="X-Username"),
    x_user_email: Optional[str] = Header(None, alias="X-User-Email"),
    x_user_roles: Optional[str] = Header(None, alias="X-User-Roles"),
    x_user_scopes: Optional[str] = Header(None, alias="X-User-Scopes"),
    x_service_name: Optional[str] = Header(None, alias="X-Service-Name"),
    x_service_authenticated: Optional[str] = Header(None, alias="X-Service-Authenticated"),
    x_service_roles: Optional[str] = Header(None, alias="X-Service-Roles"),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    x_client_id: Optional[str] = Header(None, alias="X-Client-ID"),
    x_organization_id: Optional[str] = Header(None, alias="X-Organization-ID"),
    x_subscription_tier: Optional[str] = Header(None, alias="X-Subscription-Tier"),
    x_subscription_status: Optional[str] = Header(None, alias="X-Subscription-Status"),
) -> UserContext:
    """
    Dependency for getting authenticated user (user-only, rejects services).

    This enforces that the request must be from a user, not a service.

    Example:
        @app.get("/api/profile")
        async def get_profile(user: UserContext = Depends(get_current_user)):
            return {"user_id": user.user_id}

    Args:
        Various authentication headers

    Returns:
        UserContext with authenticated user information

    Raises:
        HTTPException: If authentication fails or if authenticated as service
    """
    auth = await get_current_auth(
        request,
        authorization,
        x_token_verified,
        x_auth_source,
        x_user_id,
        x_username,
        x_user_email,
        x_user_roles,
        x_user_scopes,
        x_service_name,
        x_service_authenticated,
        x_service_roles,
        x_session_id,
        x_client_id,
        x_organization_id,
        x_subscription_tier,
        x_subscription_status,
    )

    if isinstance(auth, ServiceContext):
        logger.warning(f"Service {auth.service_name} attempted to access user-only endpoint")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires user authentication",
        )

    return auth


async def get_current_service(
    request: Request,
    authorization: Optional[str] = Header(None),
    x_token_verified: Optional[str] = Header(None, alias="X-Token-Verified"),
    x_auth_source: Optional[str] = Header(None, alias="X-Auth-Source"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    x_username: Optional[str] = Header(None, alias="X-Username"),
    x_user_email: Optional[str] = Header(None, alias="X-User-Email"),
    x_user_roles: Optional[str] = Header(None, alias="X-User-Roles"),
    x_user_scopes: Optional[str] = Header(None, alias="X-User-Scopes"),
    x_service_name: Optional[str] = Header(None, alias="X-Service-Name"),
    x_service_authenticated: Optional[str] = Header(None, alias="X-Service-Authenticated"),
    x_service_roles: Optional[str] = Header(None, alias="X-Service-Roles"),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    x_client_id: Optional[str] = Header(None, alias="X-Client-ID"),
    x_organization_id: Optional[str] = Header(None, alias="X-Organization-ID"),
    x_subscription_tier: Optional[str] = Header(None, alias="X-Subscription-Tier"),
    x_subscription_status: Optional[str] = Header(None, alias="X-Subscription-Status"),
) -> ServiceContext:
    """
    Dependency for getting authenticated service (service-only, rejects users).

    This enforces that the request must be from a service, not a user.

    Example:
        @app.post("/api/internal/sync")
        async def sync_data(service: ServiceContext = Depends(get_current_service)):
            return {"service": service.service_name}

    Args:
        Various authentication headers

    Returns:
        ServiceContext with authenticated service information

    Raises:
        HTTPException: If authentication fails or if authenticated as user
    """
    auth = await get_current_auth(
        request,
        authorization,
        x_token_verified,
        x_auth_source,
        x_user_id,
        x_username,
        x_user_email,
        x_user_roles,
        x_user_scopes,
        x_service_name,
        x_service_authenticated,
        x_service_roles,
        x_session_id,
        x_client_id,
        x_organization_id,
        x_subscription_tier,
        x_subscription_status,
    )

    if isinstance(auth, UserContext):
        logger.warning(f"User {auth.user_id} attempted to access service-only endpoint")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires service authentication",
        )

    return auth


async def get_optional_auth(
    request: Request,
    authorization: Optional[str] = Header(None),
    x_token_verified: Optional[str] = Header(None, alias="X-Token-Verified"),
    x_auth_source: Optional[str] = Header(None, alias="X-Auth-Source"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    x_username: Optional[str] = Header(None, alias="X-Username"),
    x_user_email: Optional[str] = Header(None, alias="X-User-Email"),
    x_user_roles: Optional[str] = Header(None, alias="X-User-Roles"),
    x_user_scopes: Optional[str] = Header(None, alias="X-User-Scopes"),
    x_service_name: Optional[str] = Header(None, alias="X-Service-Name"),
    x_service_authenticated: Optional[str] = Header(None, alias="X-Service-Authenticated"),
    x_service_roles: Optional[str] = Header(None, alias="X-Service-Roles"),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    x_client_id: Optional[str] = Header(None, alias="X-Client-ID"),
    x_organization_id: Optional[str] = Header(None, alias="X-Organization-ID"),
    x_subscription_tier: Optional[str] = Header(None, alias="X-Subscription-Tier"),
    x_subscription_status: Optional[str] = Header(None, alias="X-Subscription-Status"),
) -> Optional[AuthContext]:
    """
    Optional authentication - returns None if not authenticated.

    Use this for endpoints where authentication is optional for both users and services.

    Example:
        @app.get("/api/products")
        async def list_products(auth: Optional[AuthContext] = Depends(get_optional_auth)):
            if auth:
                # Show personalized products
                pass
            else:
                # Show public products
                pass

    Args:
        Various authentication headers

    Returns:
        AuthContext (UserContext or ServiceContext) if authenticated, None otherwise
    """
    try:
        return await get_current_auth(
            request,
            authorization,
            x_token_verified,
            x_auth_source,
            x_user_id,
            x_username,
            x_user_email,
            x_user_roles,
            x_user_scopes,
            x_service_name,
            x_service_authenticated,
            x_service_roles,
            x_session_id,
            x_client_id,
            x_organization_id,
            x_subscription_tier,
            x_subscription_status,
        )
    except HTTPException:
        return None


async def get_optional_user(
    request: Request,
    authorization: Optional[str] = Header(None),
    x_token_verified: Optional[str] = Header(None, alias="X-Token-Verified"),
    x_auth_source: Optional[str] = Header(None, alias="X-Auth-Source"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    x_username: Optional[str] = Header(None, alias="X-Username"),
    x_user_email: Optional[str] = Header(None, alias="X-User-Email"),
    x_user_roles: Optional[str] = Header(None, alias="X-User-Roles"),
    x_user_scopes: Optional[str] = Header(None, alias="X-User-Scopes"),
    x_service_name: Optional[str] = Header(None, alias="X-Service-Name"),
    x_service_authenticated: Optional[str] = Header(None, alias="X-Service-Authenticated"),
    x_service_roles: Optional[str] = Header(None, alias="X-Service-Roles"),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    x_client_id: Optional[str] = Header(None, alias="X-Client-ID"),
    x_organization_id: Optional[str] = Header(None, alias="X-Organization-ID"),
    x_subscription_tier: Optional[str] = Header(None, alias="X-Subscription-Tier"),
    x_subscription_status: Optional[str] = Header(None, alias="X-Subscription-Status"),
) -> Optional[UserContext]:
    """
    Optional user authentication - returns None if not authenticated or if service.

    Use this for endpoints where user authentication is optional but services are ignored.

    Example:
        @app.get("/api/user/recommendations")
        async def get_recommendations(user: Optional[UserContext] = Depends(get_optional_user)):
            if user:
                # Show personalized recommendations
                pass
            else:
                # Show general recommendations
                pass

    Args:
        Various authentication headers

    Returns:
        UserContext if authenticated as user, None otherwise (including if service)
    """
    try:
        auth = await get_current_auth(
            request,
            authorization,
            x_token_verified,
            x_auth_source,
            x_user_id,
            x_username,
            x_user_email,
            x_user_roles,
            x_user_scopes,
            x_service_name,
            x_service_authenticated,
            x_service_roles,
            x_session_id,
            x_client_id,
            x_organization_id,
            x_subscription_tier,
            x_subscription_status,
        )
        if isinstance(auth, UserContext):
            return auth
        return None
    except HTTPException:
        return None


# Role-based access control factories
def require_roles(*required_roles: str):
    """
    Factory for role-checking dependencies.

    Creates a dependency that ensures the user/service has at least one of the specified roles.
    Works with both UserContext and ServiceContext.

    Example:
        require_editor = require_roles("editor", "admin")

        @app.post("/api/articles")
        async def create_article(auth: AuthContext = Depends(require_editor)):
            if isinstance(auth, UserContext):
                return {"created_by": auth.user_id}
            else:
                return {"created_by_service": auth.service_name}

    Args:
        *required_roles: Variable number of role names

    Returns:
        Dependency function that validates roles
    """

    async def role_checker(auth: AuthContext = Depends(get_current_auth)) -> AuthContext:
        if not auth.has_any_role(list(required_roles)):
            identifier = auth.user_id if isinstance(auth, UserContext) else auth.service_name
            logger.warning(f"Auth {identifier} lacks required roles: {required_roles}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(required_roles)}",
            )
        return auth

    return role_checker


def require_user_roles(*required_roles: str):
    """
    Factory for user-only role-checking dependencies.

    Creates a dependency that ensures the USER has at least one of the specified roles.
    Services are rejected even if they have the role.

    Example:
        require_user_editor = require_user_roles("editor", "admin")

        @app.post("/api/user/articles")
        async def create_article(user: UserContext = Depends(require_user_editor)):
            return {"created_by": user.user_id}

    Args:
        *required_roles: Variable number of role names

    Returns:
        Dependency function that validates user roles
    """

    async def role_checker(user: UserContext = Depends(get_current_user)) -> UserContext:
        if not user.has_any_role(list(required_roles)):
            logger.warning(f"User {user.user_id} lacks required roles: {required_roles}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(required_roles)}",
            )
        return user

    return role_checker


def require_service_roles(*required_roles: str):
    """
    Factory for service-only role-checking dependencies.

    Creates a dependency that ensures the SERVICE has at least one of the specified roles.
    Users are rejected even if they have the role.

    Example:
        require_data_processor = require_service_roles("data-processor", "admin")

        @app.post("/api/internal/process")
        async def process_data(service: ServiceContext = Depends(require_data_processor)):
            return {"processed_by": service.service_name}

    Args:
        *required_roles: Variable number of role names

    Returns:
        Dependency function that validates service roles
    """

    async def role_checker(
        service: ServiceContext = Depends(get_current_service),
    ) -> ServiceContext:
        if not service.has_any_role(list(required_roles)):
            logger.warning(f"Service {service.service_name} lacks required roles: {required_roles}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(required_roles)}",
            )
        return service

    return role_checker


def require_scopes(*required_scopes: str):
    """
    Factory for scope-checking dependencies (user-only).

    Creates a dependency that ensures the USER has all specified scopes.
    Services don't have scopes, so they are automatically rejected.

    Example:
        require_write = require_scopes("write", "publish")

        @app.post("/api/publish")
        async def publish(user: UserContext = Depends(require_write)):
            return {"published_by": user.user_id}

    Args:
        *required_scopes: Variable number of scope names

    Returns:
        Dependency function that validates scopes
    """

    async def scope_checker(user: UserContext = Depends(get_current_user)) -> UserContext:
        missing_scopes = [s for s in required_scopes if not user.has_scope(s)]
        if missing_scopes:
            logger.warning(f"User {user.user_id} lacks required scopes: {missing_scopes}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires scopes: {', '.join(missing_scopes)}",
            )
        return user

    return scope_checker


# ============================================================================
# Platform Role Constants
# ============================================================================


class PlatformRole:
    """
    Platform-wide role constants.

    These roles are assigned via Keycloak realm roles and injected by Kong
    into the X-User-Roles header. Use these constants for role-based access control.

    Role Hierarchy:
    - USER: Base role for all authenticated users
    - BUYER_CAPABLE: Can create purchase orders (assigned via org membership)
    - SUPPLIER_CAPABLE: Can list products (assigned via org membership)
    - VERIFIED_SUPPLIER: Completed supplier verification process
    - PLATFORM_ADMIN: Full platform access (composite role)

    Usage:
        from auth_gate import PlatformRole, require_roles

        # Check for specific platform role
        require_buyer = require_roles(PlatformRole.BUYER_CAPABLE)

        # Check for verified supplier
        require_verified = require_roles(PlatformRole.VERIFIED_SUPPLIER)
    """

    USER = "user"
    """Base authenticated user role - assigned at registration"""

    BUYER_CAPABLE = "buyer_capable"
    """Can create purchase orders - assigned when joining BUYER/BOTH org"""

    SUPPLIER_CAPABLE = "supplier_capable"
    """Can list products and fulfill orders - assigned when joining SUPPLIER/BOTH org"""

    VERIFIED_SUPPLIER = "verified_supplier"
    """Completed supplier verification - assigned by verification service"""

    PLATFORM_ADMIN = "platform_admin"
    """Full platform access - composite role including all others"""


# Pre-configured role dependencies for common use cases (work with both users and services)
require_admin = require_roles("admin")
"""Dependency that requires admin role (user or service)"""

require_supplier = require_roles("supplier")
"""Dependency that requires supplier role (user or service)"""

require_customer = require_roles("customer")
"""Dependency that requires customer role (user or service)"""

require_moderator = require_roles("moderator")
"""Dependency that requires moderator role (user or service)"""

require_supplier_or_admin = require_roles("supplier", "admin")
"""Dependency that requires either supplier or admin role (user or service)"""

# Pre-configured user-only role dependencies
require_user_admin = require_user_roles("admin")
"""Dependency that requires admin role (user only)"""

require_user_supplier = require_user_roles("supplier")
"""Dependency that requires supplier role (user only)"""

require_user_customer = require_user_roles("customer")
"""Dependency that requires customer role (user only)"""

require_user_moderator = require_user_roles("moderator")
"""Dependency that requires moderator role (user only)"""

# ============================================================================
# Platform Role Dependencies (based on Keycloak realm roles)
# ============================================================================

# Base user role - all authenticated users should have this
require_user_role = require_user_roles(PlatformRole.USER)
"""Dependency that requires base 'user' role (user only)"""

# Buyer capability - users who can create purchase orders
require_buyer = require_user_roles(PlatformRole.BUYER_CAPABLE)
"""Dependency that requires buyer_capable role (user only)"""

require_buyer_or_admin = require_user_roles(PlatformRole.BUYER_CAPABLE, PlatformRole.PLATFORM_ADMIN)
"""Dependency that requires buyer_capable or platform_admin role (user only)"""

# Supplier capability - users who can list products
require_supplier_capable = require_user_roles(PlatformRole.SUPPLIER_CAPABLE)
"""Dependency that requires supplier_capable role (user only)"""

require_supplier_capable_or_admin = require_user_roles(
    PlatformRole.SUPPLIER_CAPABLE, PlatformRole.PLATFORM_ADMIN
)
"""Dependency that requires supplier_capable or platform_admin role (user only)"""

# Verified supplier - suppliers who passed verification
require_verified_supplier = require_user_roles(PlatformRole.VERIFIED_SUPPLIER)
"""Dependency that requires verified_supplier role (user only)"""

# Platform admin - full access
require_platform_admin = require_user_roles(PlatformRole.PLATFORM_ADMIN)
"""Dependency that requires platform_admin role (user only)"""


# HMAC verification for service-to-service communication
async def verify_hmac_signature(
    request: Request,
    x_authz_signature: Optional[str] = Header(None, alias="X-Authz-Signature"),
    x_authz_ts: Optional[str] = Header(None, alias="X-Authz-Ts"),
    auth: AuthContext = Depends(get_current_auth),
) -> AuthContext:
    """
    Dependency to verify HMAC signatures from Kong.

    Use this when Kong is configured with HMAC plugin for additional security.
    Works with both user and service authentication.

    Example:
        @app.post("/api/sensitive")
        async def sensitive_operation(auth: AuthContext = Depends(verify_hmac_signature)):
            if isinstance(auth, UserContext):
                return {"verified_user": auth.user_id}
            else:
                return {"verified_service": auth.service_name}

    Args:
        request: FastAPI request
        x_authz_signature: HMAC signature header
        x_authz_ts: Timestamp header
        auth: Authenticated user or service context

    Returns:
        AuthContext if HMAC is valid

    Raises:
        HTTPException: If HMAC verification fails
    """
    settings = get_settings()

    if not settings.VERIFY_HMAC:
        return auth

    if not x_authz_signature or not x_authz_ts:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing HMAC headers",
        )

    verifier = HMACVerifier(settings.INTERNAL_HMAC_KEY)

    # Get the identifier for HMAC verification
    if isinstance(auth, UserContext):
        identifier = auth.user_id
    else:
        identifier = auth.service_name

    if not verifier.verify_signature(
        x_authz_signature,
        x_authz_ts,
        identifier,
        auth.session_id or "",
        request.method,
        request.url.path,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid HMAC signature",
        )

    return auth


# Utility functions for checking authentication mode
def is_using_kong() -> bool:
    """Check if using Kong authentication"""
    settings = get_settings()
    return settings.is_production


def is_using_keycloak() -> bool:
    """Check if using direct Keycloak authentication"""
    settings = get_settings()
    return settings.is_development


def is_bypass_mode() -> bool:
    """Check if in bypass/testing mode"""
    settings = get_settings()
    return settings.is_testing


# ============================================================================
# Subscription-related Dependencies
# ============================================================================


async def get_subscription_tier(
    x_subscription_tier: Optional[str] = Header(None, alias="X-Subscription-Tier"),
) -> SubscriptionTier:
    """
    Dependency for extracting subscription tier directly from header.

    Example:
        @app.get("/api/feature")
        async def get_feature(tier: SubscriptionTier = Depends(get_subscription_tier)):
            if tier == SubscriptionTier.ENTERPRISE:
                return {"feature": "enterprise-data"}
    """
    return parse_subscription_tier(x_subscription_tier)


async def get_organization_id(
    x_organization_id: Optional[str] = Header(None, alias="X-Organization-ID"),
) -> Optional[str]:
    """
    Dependency for extracting organization ID directly from header.

    Example:
        @app.get("/api/org-data")
        async def get_org_data(org_id: str = Depends(get_organization_id)):
            return {"organization": org_id}
    """
    return x_organization_id


def require_tier(
    minimum_tier: SubscriptionTier,
    allow_services: bool = True,
) -> Callable[..., Awaitable[AuthContext]]:
    """
    Factory function that creates a dependency requiring a minimum subscription tier.

    Args:
        minimum_tier: The minimum tier required to access the endpoint
        allow_services: Whether to allow service-to-service calls (default: True)

    Returns:
        A FastAPI dependency function

    Example:
        @app.get("/api/analytics/advanced")
        async def get_advanced_analytics(
            auth: AuthContext = Depends(require_tier(SubscriptionTier.PROFESSIONAL))
        ):
            return {"data": "advanced analytics"}
    """

    async def _require_tier(
        auth: AuthContext = Depends(get_current_auth),
    ) -> AuthContext:
        # Service-to-service calls bypass tier check if allowed
        if auth.is_service:
            if allow_services:
                return auth
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This endpoint requires user authentication",
            )

        # Check tier requirement
        if not meets_minimum_tier(auth.subscription_tier, minimum_tier):
            raise TierInsufficientError(
                required_tier=minimum_tier,
                current_tier=auth.subscription_tier,
            )

        return auth

    return _require_tier


def require_active_subscription(
    allow_services: bool = True,
) -> Callable[..., Awaitable[AuthContext]]:
    """
    Factory function that creates a dependency requiring an active subscription.

    Args:
        allow_services: Whether to allow service-to-service calls (default: True)

    Returns:
        A FastAPI dependency function

    Example:
        @app.get("/api/premium-feature")
        async def get_premium_feature(
            auth: AuthContext = Depends(require_active_subscription())
        ):
            return {"feature": "premium data"}
    """

    async def _require_active_subscription(
        auth: AuthContext = Depends(get_current_auth),
    ) -> AuthContext:
        # Service-to-service calls bypass subscription check if allowed
        if auth.is_service:
            if allow_services:
                return auth
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This endpoint requires user authentication",
            )

        # Check subscription status
        if auth.subscription_status != SubscriptionStatus.ACTIVE:
            raise SubscriptionInactiveError(
                current_status=auth.subscription_status,
            )

        return auth

    return _require_active_subscription


def require_tier_and_active(
    minimum_tier: SubscriptionTier,
    allow_services: bool = True,
) -> Callable[..., Awaitable[AuthContext]]:
    """
    Factory function requiring both minimum tier AND active subscription.

    This is the most common pattern for protected premium features.

    Args:
        minimum_tier: The minimum tier required
        allow_services: Whether to allow service-to-service calls

    Returns:
        A FastAPI dependency function

    Example:
        @app.get("/api/enterprise/reports")
        async def get_enterprise_reports(
            auth: AuthContext = Depends(
                require_tier_and_active(SubscriptionTier.ENTERPRISE)
            )
        ):
            return {"reports": [...]}
    """

    async def _require_tier_and_active(
        auth: AuthContext = Depends(get_current_auth),
    ) -> AuthContext:
        # Service-to-service calls bypass checks if allowed
        if auth.is_service:
            if allow_services:
                return auth
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This endpoint requires user authentication",
            )

        # Check subscription status first
        if auth.subscription_status != SubscriptionStatus.ACTIVE:
            raise SubscriptionInactiveError(
                current_status=auth.subscription_status,
            )

        # Then check tier requirement
        if not meets_minimum_tier(auth.subscription_tier, minimum_tier):
            raise TierInsufficientError(
                required_tier=minimum_tier,
                current_tier=auth.subscription_tier,
            )

        return auth

    return _require_tier_and_active


# ============================================================================
# Convenience Dependencies for Common Tiers
# ============================================================================

# Require basic tier or higher
require_basic = require_tier(SubscriptionTier.BASIC)
"""Dependency that requires basic tier or higher"""

# Require professional tier or higher
require_professional = require_tier(SubscriptionTier.PROFESSIONAL)
"""Dependency that requires professional tier or higher"""

# Require enterprise tier
require_enterprise = require_tier(SubscriptionTier.ENTERPRISE)
"""Dependency that requires enterprise tier"""


# Require paid subscription (any non-free tier)
async def require_paid_subscription(
    auth: AuthContext = Depends(get_current_auth),
) -> AuthContext:
    """
    Dependency that requires any paid subscription tier.

    Example:
        @app.get("/api/paid-feature")
        async def get_paid_feature(
            auth: AuthContext = Depends(require_paid_subscription)
        ):
            return {"feature": "paid-only data"}
    """
    if auth.is_service:
        return auth

    if not auth.is_paid_subscriber:
        raise TierInsufficientError(
            required_tier=SubscriptionTier.BASIC,
            current_tier=auth.subscription_tier,
            detail="A paid subscription is required to access this feature",
        )

    return auth
