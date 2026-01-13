"""
Pytest fixtures and configuration for testing
"""

import asyncio
import os
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient

from auth_gate import AuthSettings, ServiceContext, UserContext
from auth_gate.config import AuthMode, reset_settings
from auth_gate.s2s_auth import ServiceAuthClient
from auth_gate.subscription import SubscriptionStatus, SubscriptionTier
from auth_gate.user_auth import UserValidator, cleanup_user_validator


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def reset_config():
    """Reset configuration before each test"""
    reset_settings()
    # Reset environment variables
    env_vars = [
        "AUTH_MODE",
        "KEYCLOAK_REALM_URL",
        "KEYCLOAK_CLIENT_ID",
        "KEYCLOAK_CLIENT_SECRET",
        "SERVICE_CLIENT_ID",
        "SERVICE_CLIENT_SECRET",
    ]
    for var in env_vars:
        if var in os.environ:
            del os.environ[var]
    yield
    reset_settings()


@pytest.fixture(scope="function")
def mock_settings():
    """Mock settings for testing"""
    settings = AuthSettings(
        AUTH_MODE="kong_headers",
        KEYCLOAK_REALM_URL="https://keycloak.test/realms/test",
        KEYCLOAK_CLIENT_ID="test-client",
        KEYCLOAK_CLIENT_SECRET="test-secret",
        SERVICE_CLIENT_ID="service-client",
        SERVICE_CLIENT_SECRET="service-secret",
        VERIFY_HMAC=False,
        INTERNAL_HMAC_KEY="test-hmac-key",
        CIRCUIT_BREAKER_FAILURE_THRESHOLD=3,
        CIRCUIT_BREAKER_RECOVERY_TIMEOUT=1,
    )
    with patch("auth_gate.config.get_settings", return_value=settings):
        with patch("auth_gate.user_auth.get_settings", return_value=settings):
            with patch("auth_gate.s2s_auth.get_settings", return_value=settings):
                with patch("auth_gate.middleware.get_settings", return_value=settings):
                    with patch("auth_gate.fastapi_utils.get_settings", return_value=settings):
                        yield settings


@pytest_asyncio.fixture(autouse=True)
async def reset_auth_state():
    """Reset auth state before/after each test to prevent caching issues"""
    await cleanup_user_validator()  # Clears global _user_validator
    yield
    await cleanup_user_validator()


@pytest.fixture
def sample_user_context():
    """Sample user context for testing"""
    return UserContext(
        user_id="test-user-123",
        username="testuser",
        email="test@example.com",
        roles=["customer", "verified"],
        scopes=["read", "write"],
        session_id="session-456",
        client_id="web-app",
        auth_source="kong",
        organization_id="org-456",
        subscription_tier=SubscriptionTier.PROFESSIONAL,
        subscription_status=SubscriptionStatus.ACTIVE,
    )


@pytest.fixture
def service_context():
    """Sample service context for testing"""
    return ServiceContext(
        service_name="payment-service",
        service_id="service-456",
        roles=["service", "payment-processor"],
        session_id="session-789",
        client_id="payment-service",
        auth_source="kong",
        organization_id=None,
        subscription_tier=SubscriptionTier.FREE,
        subscription_status=SubscriptionStatus.ACTIVE,
    )


@pytest.fixture
def admin_service_context():
    """Admin service context for testing"""
    return ServiceContext(
        service_name="admin-service",
        service_id="admin-service-123",
        roles=["admin", "service"],
        session_id="session-admin",
        client_id="admin-service",
        auth_source="kong",
    )


@pytest.fixture
def admin_user_context():
    """Admin user context for testing"""
    return UserContext(
        user_id="admin-user-789",
        username="adminuser",
        email="admin@example.com",
        roles=["admin"],
        scopes=["read", "write", "admin"],
        session_id="session-789",
        client_id="admin-app",
        auth_source="kong",
    )


@pytest.fixture
def service_headers():
    """Sample service headers from Kong"""
    return {
        "X-Token-Verified": "true",
        "X-Auth-Source": "service",
        "X-Service-Name": "payment-service",
        "X-Service-Authenticated": "true",
        "X-Service-Roles": "service,payment-processor",
        "X-Session-ID": "session-789",
        "X-Client-ID": "payment-service",
    }


@pytest.fixture
def kong_headers():
    """Sample Kong headers for testing"""
    return {
        "X-Token-Verified": "true",
        "X-User-ID": "test-user-123",
        "X-Username": "testuser",
        "X-User-Email": "test@example.com",
        "X-User-Roles": "customer,verified",
        "X-User-Scopes": "read write",
        "X-Session-ID": "session-456",
        "X-Client-ID": "web-app",
        "X-Auth-Source": "kong",
    }


@pytest.fixture
def keycloak_token_response():
    """Sample Keycloak token introspection response"""
    return {
        "active": True,
        "sub": "test-user-123",
        "username": "testuser",
        "email": "test@example.com",
        "realm_access": {"roles": ["customer", "verified"]},
        "scope": "read write",
        "sid": "session-456",
        "client_id": "web-app",
    }


@pytest.fixture
def service_token_response():
    """Sample service token response from Keycloak"""
    return {
        "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test",
        "token_type": "Bearer",
        "expires_in": 300,
    }


@pytest_asyncio.fixture
async def mock_http_client():
    """Mock HTTP client for testing"""
    client = AsyncMock(spec=AsyncClient)
    return client


@pytest_asyncio.fixture
async def kc_validator():
    """Fixture to create and clean up UserValidator instance"""
    # Reset settings to ensure clean state
    reset_settings()

    # Create validator with DIRECT_KEYCLOAK mode
    validator = UserValidator(mode=AuthMode.DIRECT_KEYCLOAK)
    yield validator

    # Clean up after each test
    await validator.close()


@pytest_asyncio.fixture
async def kh_validator():
    """Fixture to create and clean up UserValidator instance"""
    # Reset settings to ensure clean state
    reset_settings()

    # Create validator with DIRECT_KEYCLOAK mode
    validator = UserValidator(mode=AuthMode.KONG_HEADERS)
    yield validator

    # Clean up after each test
    await validator.close()


@pytest_asyncio.fixture
async def bypass_validator():
    """Fixture to create and clean up UserValidator instance"""
    # Reset settings to ensure clean state
    reset_settings()

    # Create validator with DIRECT_KEYCLOAK mode
    validator = UserValidator(mode=AuthMode.BYPASS)
    yield validator

    # Clean up after each test
    await validator.close()


@pytest_asyncio.fixture
async def service_auth_client():
    """Fixture to create and clean up UserValidator instance"""
    # Reset settings to ensure clean state
    reset_settings()

    # Create validator with DIRECT_KEYCLOAK mode
    auth_client = ServiceAuthClient()
    yield auth_client

    # Clean up after each test
    await auth_client.close()


# ============================================================================
# Subscription-related fixtures
# ============================================================================


@pytest.fixture
def user_context_free():
    """User with free tier subscription."""
    return UserContext(
        user_id="user-123",
        username="testuser",
        email="test@example.com",
        roles=["customer"],
        scopes=["read"],
        organization_id="org-456",
        subscription_tier=SubscriptionTier.FREE,
        subscription_status=SubscriptionStatus.ACTIVE,
        auth_source="kong",
    )


@pytest.fixture
def user_context_professional():
    """User with professional tier subscription."""
    return UserContext(
        user_id="user-pro-123",
        username="prouser",
        email="pro@example.com",
        roles=["customer", "verified"],
        scopes=["read", "write"],
        organization_id="org-789",
        subscription_tier=SubscriptionTier.PROFESSIONAL,
        subscription_status=SubscriptionStatus.ACTIVE,
        auth_source="kong",
    )


@pytest.fixture
def user_context_enterprise():
    """User with enterprise tier subscription."""
    return UserContext(
        user_id="user-ent-123",
        username="entuser",
        email="ent@example.com",
        roles=["customer", "verified", "enterprise"],
        scopes=["read", "write", "admin"],
        organization_id="org-enterprise",
        subscription_tier=SubscriptionTier.ENTERPRISE,
        subscription_status=SubscriptionStatus.ACTIVE,
        auth_source="kong",
    )


@pytest.fixture
def user_context_suspended():
    """User with suspended subscription."""
    return UserContext(
        user_id="user-suspended",
        username="suspended",
        email="suspended@example.com",
        roles=["customer"],
        scopes=["read"],
        organization_id="org-456",
        subscription_tier=SubscriptionTier.PROFESSIONAL,
        subscription_status=SubscriptionStatus.SUSPENDED,
        auth_source="kong",
    )


@pytest.fixture
def user_context_past_due():
    """User with past due subscription."""
    return UserContext(
        user_id="user-past-due",
        username="pastdue",
        email="pastdue@example.com",
        roles=["customer"],
        scopes=["read"],
        organization_id="org-456",
        subscription_tier=SubscriptionTier.BASIC,
        subscription_status=SubscriptionStatus.PAST_DUE,
        auth_source="kong",
    )


@pytest.fixture
def kong_headers_with_subscription():
    """Kong headers including subscription context."""
    return {
        "X-Token-Verified": "true",
        "X-Auth-Source": "kong",
        "X-User-ID": "user-123",
        "X-Username": "testuser",
        "X-User-Email": "test@example.com",
        "X-User-Roles": "customer,verified",
        "X-User-Scopes": "read write",
        "X-Organization-ID": "org-456",
        "X-Subscription-Tier": "professional",
        "X-Subscription-Status": "active",
        "X-Session-ID": "session-123",
        "X-Client-ID": "web-app",
    }
