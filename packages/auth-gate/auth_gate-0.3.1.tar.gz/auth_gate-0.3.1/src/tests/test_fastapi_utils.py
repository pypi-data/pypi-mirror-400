"""
Tests for FastAPI utility functions
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient

from auth_gate import UserContext
from auth_gate.fastapi_utils import (
    get_current_auth,
    get_current_service,
    get_current_user,
    get_optional_auth,
    get_optional_user,
    is_bypass_mode,
    is_using_keycloak,
    is_using_kong,
    require_admin,
    require_roles,
    require_scopes,
    require_service_roles,
    require_user_roles,
    verify_hmac_signature,
)
from auth_gate.schemas import AuthContext, ServiceContext


@pytest.fixture
def test_app():
    """Create test FastAPI application"""
    return FastAPI()


class TestAuthenticationDependencies:
    """Test authentication dependencies"""

    def test_get_current_auth_with_user(self, test_app, sample_user_context, kong_headers):
        """Test get_current_auth with user authentication"""

        @test_app.get("/test")
        async def test_endpoint(auth: AuthContext = Depends(get_current_auth)):
            return {"type": "user" if isinstance(auth, UserContext) else "service"}

        client = TestClient(test_app)

        with patch("auth_gate.fastapi_utils.get_user_validator") as mock_validator:
            mock_validator.return_value.get_current_user = AsyncMock(
                return_value=sample_user_context
            )

            response = client.get("/test", headers=kong_headers)
            assert response.status_code == 200
            assert response.json()["type"] == "user"

    def test_get_current_auth_with_service(self, test_app, service_context, service_headers):
        """Test get_current_auth with service authentication"""

        @test_app.get("/test")
        async def test_endpoint(auth: AuthContext = Depends(get_current_auth)):
            return {"type": "service" if isinstance(auth, ServiceContext) else "user"}

        client = TestClient(test_app)

        with patch("auth_gate.fastapi_utils.get_user_validator") as mock_validator:
            mock_validator.return_value.get_current_user = AsyncMock(return_value=service_context)

            response = client.get("/test", headers=service_headers)
            assert response.status_code == 200
            assert response.json()["type"] == "service"

    def test_get_current_user_success(self, test_app, sample_user_context, kong_headers):
        """Test get_current_user with valid user"""

        @test_app.get("/test")
        async def test_endpoint(user: UserContext = Depends(get_current_user)):
            return {"user_id": user.user_id}

        client = TestClient(test_app)

        with patch("auth_gate.fastapi_utils.get_current_auth", return_value=sample_user_context):
            response = client.get("/test", headers=kong_headers)
            assert response.status_code == 200
            assert response.json()["user_id"] == "test-user-123"

    def test_get_current_user_rejects_service(self, test_app, service_context, service_headers):
        """Test get_current_user rejects service authentication"""

        @test_app.get("/test")
        async def test_endpoint(user: UserContext = Depends(get_current_user)):
            return {"user_id": user.user_id}

        client = TestClient(test_app)

        with patch("auth_gate.fastapi_utils.get_current_auth", return_value=service_context):
            response = client.get("/test", headers=service_headers)
            assert response.status_code == 403
            assert "user authentication" in response.json()["detail"].lower()

    def test_get_current_service_success(self, test_app, service_context, service_headers):
        """Test get_current_service with valid service"""

        @test_app.get("/test")
        async def test_endpoint(service: ServiceContext = Depends(get_current_service)):
            return {"service_name": service.service_name}

        client = TestClient(test_app)

        with patch("auth_gate.fastapi_utils.get_current_auth", return_value=service_context):
            response = client.get("/test", headers=service_headers)
            assert response.status_code == 200
            assert response.json()["service_name"] == "payment-service"

    def test_get_current_service_rejects_user(self, test_app, sample_user_context, kong_headers):
        """Test get_current_service rejects user authentication"""

        @test_app.get("/test")
        async def test_endpoint(service: ServiceContext = Depends(get_current_service)):
            return {"service_name": service.service_name}

        client = TestClient(test_app)

        with patch("auth_gate.fastapi_utils.get_current_auth", return_value=sample_user_context):
            response = client.get("/test", headers=kong_headers)
            assert response.status_code == 403
            assert "service authentication" in response.json()["detail"].lower()

    def test_require_roles_with_user(self, test_app, sample_user_context, kong_headers):
        """Test require_roles with valid user roles"""
        require_editor = require_roles("customer", "editor")

        @test_app.get("/test")
        async def test_endpoint(auth: AuthContext = Depends(require_editor)):
            return {"success": True}

        client = TestClient(test_app)

        with patch("auth_gate.fastapi_utils.get_current_auth", return_value=sample_user_context):
            response = client.get("/test", headers=kong_headers)
            assert response.status_code == 200
            assert response.json()["success"] is True

    def test_require_roles_with_service(self, test_app, service_context, service_headers):
        """Test require_roles with valid service roles"""
        require_processor = require_roles("payment-processor", "admin")

        @test_app.get("/test")
        async def test_endpoint(auth: AuthContext = Depends(require_processor)):
            return {"success": True}

        client = TestClient(test_app)

        with patch("auth_gate.fastapi_utils.get_current_auth", return_value=service_context):
            response = client.get("/test", headers=service_headers)
            assert response.status_code == 200

    def test_require_roles_failure(self, test_app, sample_user_context, kong_headers):
        """Test require_roles with invalid roles"""
        require_admin_only = require_roles("admin")

        @test_app.get("/test")
        async def test_endpoint(auth: AuthContext = Depends(require_admin_only)):
            return {"success": True}

        client = TestClient(test_app)

        with patch("auth_gate.fastapi_utils.get_current_auth", return_value=sample_user_context):
            response = client.get("/test", headers=kong_headers)
            assert response.status_code == 403
            assert "Requires one of roles" in response.json()["detail"]

    def test_require_user_roles_success(self, test_app, sample_user_context, kong_headers):
        """Test require_user_roles with valid user"""
        require_customer = require_user_roles("customer")

        @test_app.get("/test")
        async def test_endpoint(user: UserContext = Depends(require_customer)):
            return {"user_id": user.user_id}

        client = TestClient(test_app)

        with patch("auth_gate.fastapi_utils.get_current_user", return_value=sample_user_context):
            response = client.get("/test", headers=kong_headers)
            assert response.status_code == 200

    def test_require_user_roles_rejects_service(self, test_app, service_context, service_headers):
        """Test require_user_roles rejects services"""
        require_customer = require_user_roles("customer")

        @test_app.get("/test")
        async def test_endpoint(user: UserContext = Depends(require_customer)):
            return {"user_id": user.user_id}

        client = TestClient(test_app)

        # Service is rejected at get_current_user level
        with patch("auth_gate.fastapi_utils.get_current_auth", return_value=service_context):
            response = client.get("/test", headers=service_headers)
            assert response.status_code == 403
            assert "user authentication" in response.json()["detail"].lower()

    def test_require_service_roles_success(self, test_app, service_context, service_headers):
        """Test require_service_roles with valid service"""
        require_processor = require_service_roles("payment-processor")

        @test_app.get("/test")
        async def test_endpoint(service: ServiceContext = Depends(require_processor)):
            return {"service_name": service.service_name}

        client = TestClient(test_app)

        with patch("auth_gate.fastapi_utils.get_current_service", return_value=service_context):
            response = client.get("/test", headers=service_headers)
            assert response.status_code == 200

    def test_require_service_roles_rejects_user(self, test_app, sample_user_context, kong_headers):
        """Test require_service_roles rejects users"""
        require_processor = require_service_roles("payment-processor")

        @test_app.get("/test")
        async def test_endpoint(service: ServiceContext = Depends(require_processor)):
            return {"service_name": service.service_name}

        client = TestClient(test_app)

        # User is rejected at get_current_service level
        with patch("auth_gate.fastapi_utils.get_current_auth", return_value=sample_user_context):
            response = client.get("/test", headers=kong_headers)
            assert response.status_code == 403
            assert "service authentication" in response.json()["detail"].lower()

    def test_require_admin_with_admin_user(self, test_app, admin_user_context, kong_headers):
        """Test require_admin with admin user"""
        kong_headers["X-User-Roles"] = "admin"
        kong_headers["X-User-ID"] = "admin-user-789"
        kong_headers["X-Username"] = "adminuser"
        kong_headers["X-User-Email"] = "admin@example.com"

        @test_app.get("/test")
        async def test_endpoint(auth: AuthContext = Depends(require_admin)):
            return {"success": True}

        client = TestClient(test_app)

        with patch("auth_gate.fastapi_utils.get_current_auth", return_value=admin_user_context):
            response = client.get("/test", headers=kong_headers)
            assert response.status_code == 200

    def test_require_scopes_success(self, test_app, sample_user_context, kong_headers):
        """Test require_scopes with valid scopes"""
        require_read_write = require_scopes("read", "write")

        @test_app.get("/test")
        async def test_endpoint(user: UserContext = Depends(require_read_write)):
            return {"user_id": user.user_id}

        client = TestClient(test_app)

        with patch("auth_gate.fastapi_utils.get_current_user", return_value=sample_user_context):
            response = client.get("/test", headers=kong_headers)
            assert response.status_code == 200

    def test_require_scopes_failure(self, test_app, sample_user_context, kong_headers):
        """Test require_scopes with missing scopes"""
        require_admin_scope = require_scopes("admin")

        @test_app.get("/test")
        async def test_endpoint(user: UserContext = Depends(require_admin_scope)):
            return {"user_id": user.user_id}

        client = TestClient(test_app)

        with patch("auth_gate.fastapi_utils.get_current_user", return_value=sample_user_context):
            response = client.get("/test", headers=kong_headers)
            assert response.status_code == 403
            assert "Requires scopes" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_optional_auth_with_user(self, sample_user_context):
        """Test get_optional_auth with user authentication"""
        mock_request = Mock()

        with patch("auth_gate.fastapi_utils.get_current_auth", return_value=sample_user_context):
            auth = await get_optional_auth(mock_request)
            assert auth is not None
            assert isinstance(auth, UserContext)
            assert auth.user_id == "test-user-123"

    @pytest.mark.asyncio
    async def test_get_optional_auth_with_service(self, service_context):
        """Test get_optional_auth with service authentication"""
        mock_request = Mock()

        with patch("auth_gate.fastapi_utils.get_current_auth", return_value=service_context):
            auth = await get_optional_auth(mock_request)
            assert auth is not None
            assert isinstance(auth, ServiceContext)
            assert auth.service_name == "payment-service"

    @pytest.mark.asyncio
    async def test_get_optional_auth_without_auth(self):
        """Test get_optional_auth without authentication"""
        mock_request = Mock()

        with patch(
            "auth_gate.fastapi_utils.get_current_auth",
            side_effect=HTTPException(status_code=401, detail="Unauthorized"),
        ):
            auth = await get_optional_auth(mock_request)
            assert auth is None

    @pytest.mark.asyncio
    async def test_get_optional_user_with_auth(self, sample_user_context):
        """Test get_optional_user with user authentication"""
        mock_request = Mock()

        with patch("auth_gate.fastapi_utils.get_current_auth", return_value=sample_user_context):
            user = await get_optional_user(mock_request)
            assert user is not None
            assert user.user_id == "test-user-123"

    @pytest.mark.asyncio
    async def test_get_optional_user_with_service(self, service_context):
        """Test get_optional_user returns None for service"""
        mock_request = Mock()

        with patch("auth_gate.fastapi_utils.get_current_auth", return_value=service_context):
            user = await get_optional_user(mock_request)
            assert user is None

    @pytest.mark.asyncio
    async def test_get_optional_user_without_auth(self):
        """Test get_optional_user without authentication"""
        mock_request = Mock()

        with patch(
            "auth_gate.fastapi_utils.get_current_auth",
            side_effect=HTTPException(status_code=401, detail="Unauthorized"),
        ):
            user = await get_optional_user(mock_request)
            assert user is None


class TestHMACVerification:
    """Test HMAC verification dependency"""

    @pytest.mark.asyncio
    async def test_verify_hmac_signature_disabled(self, sample_user_context, mock_settings):
        """Test HMAC verification when disabled"""
        mock_settings.VERIFY_HMAC = False

        with patch("auth_gate.fastapi_utils.get_settings", return_value=mock_settings):
            mock_request = Mock()
            auth = await verify_hmac_signature(
                mock_request, x_authz_signature=None, x_authz_ts=None, auth=sample_user_context
            )
            assert auth == sample_user_context

    @pytest.mark.asyncio
    async def test_verify_hmac_signature_missing_headers(self, sample_user_context, mock_settings):
        """Test HMAC verification with missing headers"""
        mock_settings.VERIFY_HMAC = True

        with patch("auth_gate.fastapi_utils.get_settings", return_value=mock_settings):
            mock_request = Mock()

            with pytest.raises(HTTPException) as exc_info:
                await verify_hmac_signature(
                    mock_request, x_authz_signature=None, x_authz_ts=None, auth=sample_user_context
                )

            assert exc_info.value.status_code == 401
            assert "Missing HMAC headers" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_verify_hmac_signature_with_service(self, service_context, mock_settings):
        """Test HMAC verification with service context"""
        mock_settings.VERIFY_HMAC = False

        with patch("auth_gate.fastapi_utils.get_settings", return_value=mock_settings):
            mock_request = Mock()
            auth = await verify_hmac_signature(
                mock_request, x_authz_signature=None, x_authz_ts=None, auth=service_context
            )
            assert auth == service_context
            assert isinstance(auth, ServiceContext)


class TestUtilityFunctions:
    """Test utility functions"""

    def test_is_using_kong(self, mock_settings):
        """Test is_using_kong utility"""
        mock_settings.AUTH_MODE = "kong_headers"

        with patch("auth_gate.fastapi_utils.get_settings", return_value=mock_settings):
            assert is_using_kong() is True

        mock_settings.AUTH_MODE = "direct_keycloak"
        with patch("auth_gate.fastapi_utils.get_settings", return_value=mock_settings):
            assert is_using_kong() is False

    def test_is_using_keycloak(self, mock_settings):
        """Test is_using_keycloak utility"""
        mock_settings.AUTH_MODE = "direct_keycloak"

        with patch("auth_gate.fastapi_utils.get_settings", return_value=mock_settings):
            assert is_using_keycloak() is True

        mock_settings.AUTH_MODE = "kong_headers"
        with patch("auth_gate.fastapi_utils.get_settings", return_value=mock_settings):
            assert is_using_keycloak() is False

    def test_is_bypass_mode(self, mock_settings):
        """Test is_bypass_mode utility"""
        mock_settings.AUTH_MODE = "bypass"

        with patch("auth_gate.fastapi_utils.get_settings", return_value=mock_settings):
            assert is_bypass_mode() is True

        mock_settings.AUTH_MODE = "kong_headers"
        with patch("auth_gate.fastapi_utils.get_settings", return_value=mock_settings):
            assert is_bypass_mode() is False
