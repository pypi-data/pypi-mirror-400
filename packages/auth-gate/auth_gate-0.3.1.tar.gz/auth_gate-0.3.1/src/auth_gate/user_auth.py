"""
User and service authentication and validation logic
"""

import base64
import hashlib
import hmac
import logging
import time
from typing import Dict, List, Optional

import httpx
from fastapi import HTTPException, Request, status

from .config import AuthMode, get_settings
from .schemas import AuthContext, ServiceContext, UserContext
from .subscription import (
    parse_subscription_status,
    parse_subscription_tier,
)

logger = logging.getLogger(__name__)


class UserValidator:
    """
    Validates user and service authentication tokens and headers.
    Supports multiple authentication modes for different environments.
    """

    def __init__(self, mode: Optional[AuthMode] = None):
        """
        Initialize user validator.

        Args:
            mode: Authentication mode to use. If None, uses config default.
        """
        settings = get_settings()
        self.mode = mode or settings.auth_mode_enum
        self.keycloak_url = settings.KEYCLOAK_REALM_URL
        self.client_id = settings.KEYCLOAK_CLIENT_ID
        self.client_secret = settings.KEYCLOAK_CLIENT_SECRET
        self._http_client: Optional[httpx.AsyncClient] = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        """Lazy-loaded HTTP client with connection pooling"""
        if self._http_client is None:
            settings = get_settings()
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(settings.HTTP_TIMEOUT),
                limits=httpx.Limits(
                    max_keepalive_connections=settings.HTTP_MAX_KEEPALIVE_CONNECTIONS
                ),
            )
        return self._http_client

    async def validate_kong_headers(
        self,
        x_token_verified: Optional[str] = None,
        x_user_id: Optional[str] = None,
        x_username: Optional[str] = None,
        x_user_email: Optional[str] = None,
        x_user_roles: Optional[str] = None,
        x_user_scopes: Optional[str] = None,
        x_session_id: Optional[str] = None,
        x_client_id: Optional[str] = None,
        x_auth_source: Optional[str] = None,
        x_organization_id: Optional[str] = None,
        x_subscription_tier: Optional[str] = None,
        x_subscription_status: Optional[str] = None,
    ) -> UserContext:
        """
        Validate user headers from Kong token introspector.

        Args:
            Various Kong headers containing user claims

        Returns:
            UserContext with validated user information

        Raises:
            HTTPException: If validation fails
        """
        # Verify Kong has validated the token
        if x_token_verified != "true":
            logger.warning(f"Token not verified by Kong: {x_token_verified}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token not verified by API Gateway",
            )

        # User ID is required
        if not x_user_id:
            logger.error("Missing X-User-ID header from Kong")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication headers",
            )

        # Parse roles and scopes
        roles = []
        if x_user_roles:
            roles = [r.strip() for r in x_user_roles.split(",") if r.strip()]

        scopes = []
        if x_user_scopes:
            scopes = [s.strip() for s in x_user_scopes.split(" ") if s.strip()]

        # Parse subscription context
        subscription_tier = parse_subscription_tier(x_subscription_tier)
        subscription_status = parse_subscription_status(x_subscription_status)

        return UserContext(
            user_id=x_user_id,
            username=x_username,
            email=x_user_email,
            roles=roles,
            scopes=scopes,
            session_id=x_session_id,
            client_id=x_client_id,
            auth_source=x_auth_source or "kong",
            organization_id=x_organization_id,
            subscription_tier=subscription_tier,
            subscription_status=subscription_status,
        )

    async def validate_kong_service_headers(
        self,
        x_token_verified: Optional[str] = None,
        x_service_name: Optional[str] = None,
        x_service_authenticated: Optional[str] = None,
        x_service_roles: Optional[str] = None,
        x_session_id: Optional[str] = None,
        x_client_id: Optional[str] = None,
        x_auth_source: Optional[str] = None,
        x_organization_id: Optional[str] = None,
        x_subscription_tier: Optional[str] = None,
        x_subscription_status: Optional[str] = None,
    ) -> ServiceContext:
        """
        Validate service headers from Kong token introspector.

        Args:
            Various Kong headers containing service claims

        Returns:
            ServiceContext with validated service information

        Raises:
            HTTPException: If validation fails
        """
        # Verify Kong has validated the token
        if x_token_verified != "true":
            logger.warning(f"Token not verified by Kong: {x_token_verified}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token not verified by API Gateway",
            )

        # Service name is required
        if not x_service_name:
            logger.error("Missing X-Service-Name header from Kong")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid service authentication headers",
            )

        # Verify service is authenticated
        if x_service_authenticated != "true":
            logger.error(f"Service not authenticated: {x_service_authenticated}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Service not authenticated",
            )

        # Parse roles
        roles = []
        if x_service_roles:
            roles = [r.strip() for r in x_service_roles.split(",") if r.strip()]

        # Parse subscription context (services inherit defaults)
        subscription_tier = parse_subscription_tier(x_subscription_tier)
        subscription_status = parse_subscription_status(x_subscription_status)

        return ServiceContext(
            service_name=x_service_name,
            roles=roles,
            session_id=x_session_id,
            client_id=x_client_id or x_service_name,
            auth_source=x_auth_source or "kong",
            organization_id=x_organization_id,
            subscription_tier=subscription_tier,
            subscription_status=subscription_status,
        )

    async def validate_keycloak_token(self, token: str) -> AuthContext:
        """
        Direct token validation with Keycloak.
        Automatically detects if it's a user or service token.

        Args:
            token: Bearer token to validate

        Returns:
            UserContext or ServiceContext with validated information

        Raises:
            HTTPException: If validation fails
        """
        introspection_url = f"{self.keycloak_url}/protocol/openid-connect/token/introspect"

        try:
            response = await self.http_client.post(
                introspection_url,
                data={
                    "token": token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if response.status_code != 200:
                logger.error(f"Keycloak introspection failed: {response.status_code}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token validation failed",
                )

            data = response.json()

            if not data.get("active"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token is not active",
                )

            # Extract roles from various claim locations
            roles = self._extract_roles_from_claims(data)

            # Determine if this is a service token
            is_service = self._is_service_token(data, roles)

            # Parse subscription context from claims (if present)
            subscription_tier = parse_subscription_tier(data.get("subscription_tier"))
            subscription_status = parse_subscription_status(data.get("subscription_status"))
            organization_id = data.get("organization_id")

            if is_service:
                # Return service context
                return ServiceContext(
                    service_name=data.get("client_id"),
                    service_id=data.get("sub"),
                    roles=roles,
                    session_id=data.get("sid"),
                    client_id=data.get("client_id"),
                    auth_source="keycloak",
                    organization_id=organization_id,
                    subscription_tier=subscription_tier,
                    subscription_status=subscription_status,
                )
            else:
                # Return user context
                return UserContext(
                    user_id=data.get("sub"),
                    username=data.get("username") or data.get("preferred_username"),
                    email=data.get("email"),
                    roles=roles,
                    scopes=data.get("scope", "").split(" "),
                    session_id=data.get("sid"),
                    client_id=data.get("client_id"),
                    auth_source="keycloak",
                    organization_id=organization_id,
                    subscription_tier=subscription_tier,
                    subscription_status=subscription_status,
                )

        except httpx.RequestError as e:
            logger.error(f"Failed to connect to Keycloak: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable",
            )

    def _is_service_token(self, claims: Dict, roles: List[str]) -> bool:
        """
        Determine if token is a service token based on claims and roles.

        Detection logic (in priority order):
        1. Contains 'service' role (or 'service-account' role)
        2. Has typ or token_type claim set to 'service'
        3. Has client_id but no username/email/preferred_username

        Args:
            claims: Token claims
            roles: Extracted roles

        Returns:
            True if this is a service token
        """
        # Check for service role
        service_role_indicators = ["service"]
        if any(role in roles for role in service_role_indicators):
            return True

        # Check explicit token type
        token_type = claims.get("typ") or claims.get("token_type")
        if token_type and token_type.lower() == "service":
            return True

        # Check if has client_id but no user-specific claims
        has_client = bool(claims.get("client_id"))
        has_user_claims = any(
            [
                claims.get("username"),
                claims.get("preferred_username"),
                claims.get("email"),
                claims.get("name"),
                claims.get("given_name"),
                claims.get("family_name"),
            ]
        )

        if has_client and not has_user_claims:
            return True

        return False

    def _extract_roles_from_claims(self, claims: Dict) -> List[str]:
        """Extract roles from various claim locations"""
        roles = []

        # Realm roles
        if "realm_access" in claims and "roles" in claims["realm_access"]:
            roles.extend(claims["realm_access"]["roles"])

        # Resource/client roles
        if "resource_access" in claims:
            for client, access in claims["resource_access"].items():
                if "roles" in access:
                    # Prefix client roles to distinguish them
                    roles.extend([f"{client}:{role}" for role in access["roles"]])

        return roles

    async def get_current_user(
        self,
        request: Request,
        authorization: Optional[str] = None,
        x_token_verified: Optional[str] = None,
        x_auth_source: Optional[str] = None,
        # User headers
        x_user_id: Optional[str] = None,
        x_username: Optional[str] = None,
        x_user_email: Optional[str] = None,
        x_user_roles: Optional[str] = None,
        x_user_scopes: Optional[str] = None,
        # Service headers
        x_service_name: Optional[str] = None,
        x_service_authenticated: Optional[str] = None,
        x_service_roles: Optional[str] = None,
        # Common headers
        x_session_id: Optional[str] = None,
        x_client_id: Optional[str] = None,
        # Organization header
        x_organization_id: Optional[str] = None,
        # Subscription headers
        x_subscription_tier: Optional[str] = None,
        x_subscription_status: Optional[str] = None,
    ) -> AuthContext:
        """
        Main authentication method supporting multiple modes and both user/service auth.

        Args:
            request: FastAPI request object
            authorization: Authorization header
            Various Kong headers for user and service authentication

        Returns:
            UserContext or ServiceContext with authenticated information

        Raises:
            HTTPException: If authentication fails
        """
        if self.mode == AuthMode.BYPASS:
            # Testing mode - return mock user
            logger.warning("SECURITY BYPASS MODE - FOR TESTING ONLY")
            return UserContext(
                user_id="00000000-0000-0000-0000-000000000000",
                username="testuser",
                roles=["admin"],
                auth_source="bypass",
                email="test@example.com",
                session_id="test_session",
                client_id="test_client",
                organization_id=None,
            )

        elif self.mode == AuthMode.KONG_HEADERS:
            # Production mode - validate Kong headers
            # Determine if this is user or service authentication based on auth_source or available headers
            auth_source_value = x_auth_source or ""

            if auth_source_value == "service" or (x_service_name and x_service_authenticated):
                # Service authentication
                return await self.validate_kong_service_headers(
                    x_token_verified,
                    x_service_name,
                    x_service_authenticated,
                    x_service_roles,
                    x_session_id,
                    x_client_id,
                    x_auth_source,
                    x_organization_id,
                    x_subscription_tier,
                    x_subscription_status,
                )
            else:
                # User authentication (default)
                return await self.validate_kong_headers(
                    x_token_verified,
                    x_user_id,
                    x_username,
                    x_user_email,
                    x_user_roles,
                    x_user_scopes,
                    x_session_id,
                    x_client_id,
                    x_auth_source,
                    x_organization_id,
                    x_subscription_tier,
                    x_subscription_status,
                )

        elif self.mode == AuthMode.DIRECT_KEYCLOAK:
            # Development mode - validate directly with Keycloak
            if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing or invalid authorization header",
                )

            token = authorization.replace("Bearer ", "")
            return await self.validate_keycloak_token(token)

        else:
            raise ValueError(f"Invalid auth mode: {self.mode}")

    async def close(self):
        """Clean up resources"""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None


class HMACVerifier:
    """
    Verifies HMAC signatures for service-to-service communication.
    Used when Kong is configured with HMAC plugin.
    """

    def __init__(self, secret_key: str, max_skew_seconds: int = 60):
        """
        Initialize HMAC verifier.

        Args:
            secret_key: HMAC secret key
            max_skew_seconds: Maximum allowed timestamp skew
        """
        self.secret_key = secret_key.encode("utf-8")
        self.max_skew_seconds = max_skew_seconds

    def verify_signature(
        self,
        signature: str,
        timestamp: str,
        user_id: str,
        session_id: str,
        method: str,
        path: str,
    ) -> bool:
        """
        Verify HMAC signature matches expected value.

        Args:
            signature: HMAC signature from header
            timestamp: Request timestamp
            user_id: User ID from context
            session_id: Session ID from context
            method: HTTP method
            path: Request path

        Returns:
            True if signature is valid
        """
        try:
            # Check timestamp freshness
            req_timestamp = int(timestamp)
            current_time = int(time.time())

            if abs(current_time - req_timestamp) > self.max_skew_seconds:
                logger.warning(f"HMAC timestamp too old: {req_timestamp}")
                return False

            # Reconstruct payload (must match Kong's format)
            payload = "|".join(
                [
                    user_id or "",
                    session_id or "",
                    timestamp,
                    method,
                    path,
                ]
            )

            # Calculate expected signature
            expected_sig = base64.b64encode(
                hmac.new(
                    self.secret_key,
                    payload.encode("utf-8"),
                    hashlib.sha256,
                ).digest()
            ).decode("utf-8")

            # Constant-time comparison
            return hmac.compare_digest(signature, expected_sig)

        except (ValueError, TypeError) as e:
            logger.error(f"HMAC verification error: {e}")
            return False


# Global validator instance management
_user_validator: Optional[UserValidator] = None


def get_user_validator() -> UserValidator:
    """Get or create user validator instance"""
    global _user_validator
    if _user_validator is None:
        _user_validator = UserValidator()
    return _user_validator


async def cleanup_user_validator():
    """Clean up user validator resources"""
    global _user_validator
    if _user_validator:
        await _user_validator.close()
        _user_validator = None
