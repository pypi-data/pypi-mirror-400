"""
Integration tests for the auth client package
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from auth_gate import (
    AuthMiddleware,
    UserContext,
    get_current_auth,
    get_current_service,
    get_current_user,
    get_optional_user,
    require_admin,
    require_supplier_or_admin,
)
from auth_gate.schemas import AuthContext, ServiceContext


@pytest.fixture
def integrated_app():
    """Create fully integrated FastAPI app"""
    app = FastAPI()

    # Add authentication middleware
    app.add_middleware(
        AuthMiddleware,
        excluded_paths={"/health", "/metrics"},
        excluded_prefixes={"/docs"},
        optional_auth_paths={"/api/products"},
    )

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    @app.get("/api/profile")
    async def get_profile(user: UserContext = Depends(get_current_user)):
        return {
            "user_id": user.user_id,
            "username": user.username,
            "roles": user.roles,
        }

    @app.get("/api/admin/users")
    async def list_users(auth: AuthContext = Depends(require_admin)):
        if isinstance(auth, UserContext):
            return {"users": ["user1", "user2"], "requester_type": "user"}
        else:
            return {"users": ["user1", "user2"], "requester_type": "service"}

    @app.get("/api/supplier/products")
    async def supplier_products(user: UserContext = Depends(require_supplier_or_admin)):
        return {"products": ["product1", "product2"]}

    @app.get("/api/products")
    async def public_products(user: UserContext = Depends(get_optional_user)):
        if user:
            return {"products": ["product1", "product2"], "personalized": True}
        return {"products": ["product1"], "personalized": False}

    @app.get("/api/data")
    async def get_data(auth: AuthContext = Depends(get_current_auth)):
        if isinstance(auth, UserContext):
            return {"data": "filtered", "for": "user", "user_id": auth.user_id}
        else:
            return {"data": "full", "for": "service", "service_name": auth.service_name}

    @app.post("/api/internal/sync")
    async def sync_data(service: ServiceContext = Depends(get_current_service)):
        return {"status": "syncing", "service": service.service_name}

    return app


class TestEndToEndIntegration:
    """End-to-end integration tests"""

    def test_health_endpoint_no_auth(self, integrated_app, mock_settings):
        """Test health endpoint requires no authentication"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            client = TestClient(integrated_app)
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"

    def test_protected_endpoint_with_kong_headers(
        self, integrated_app, mock_settings, kong_headers
    ):
        """Test protected endpoint with Kong headers"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            with patch("auth_gate.user_auth.get_settings", return_value=mock_settings):
                with patch("auth_gate.fastapi_utils.get_user_validator") as mock_validator:
                    mock_validator.return_value.get_current_user = AsyncMock(
                        return_value=UserContext(
                            user_id="test-user-123",
                            username="testuser",
                            roles=["customer"],
                        )
                    )

                    client = TestClient(integrated_app)
                    response = client.get("/api/profile", headers=kong_headers)
                    assert response.status_code == 200
                    assert response.json()["user_id"] == "test-user-123"

    def test_service_endpoint_with_service_headers(
        self, integrated_app, mock_settings, service_headers, service_context
    ):
        """Test service-only endpoint with service headers"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            with patch("auth_gate.user_auth.get_settings", return_value=mock_settings):
                with patch("auth_gate.fastapi_utils.get_user_validator") as mock_validator:
                    mock_validator.return_value.get_current_user = AsyncMock(
                        return_value=service_context
                    )

                    client = TestClient(integrated_app)
                    response = client.post("/api/internal/sync", headers=service_headers)
                    assert response.status_code == 200
                    assert response.json()["service"] == "payment-service"

    def test_service_rejected_from_user_endpoint(
        self, integrated_app, mock_settings, service_headers, service_context
    ):
        """Test service is rejected from user-only endpoint"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            with patch("auth_gate.user_auth.get_settings", return_value=mock_settings):
                with patch("auth_gate.fastapi_utils.get_user_validator") as mock_validator:
                    mock_validator.return_value.get_current_user = AsyncMock(
                        return_value=service_context
                    )

                    client = TestClient(integrated_app)
                    response = client.get("/api/profile", headers=service_headers)
                    assert response.status_code == 403
                    assert "user authentication" in response.json()["detail"].lower()

    def test_user_rejected_from_service_endpoint(self, integrated_app, mock_settings, kong_headers):
        """Test user is rejected from service-only endpoint"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            with patch("auth_gate.user_auth.get_settings", return_value=mock_settings):
                with patch("auth_gate.fastapi_utils.get_user_validator") as mock_validator:
                    mock_validator.return_value.get_current_user = AsyncMock(
                        return_value=UserContext(
                            user_id="test-user-123",
                            username="testuser",
                            roles=["customer"],
                        )
                    )

                    client = TestClient(integrated_app)
                    response = client.post("/api/internal/sync", headers=kong_headers)
                    assert response.status_code == 403
                    assert "service authentication" in response.json()["detail"].lower()

    def test_shared_endpoint_with_user(self, integrated_app, mock_settings, kong_headers):
        """Test shared endpoint accessible by user"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            with patch("auth_gate.user_auth.get_settings", return_value=mock_settings):
                with patch("auth_gate.fastapi_utils.get_user_validator") as mock_validator:
                    mock_validator.return_value.get_current_user = AsyncMock(
                        return_value=UserContext(
                            user_id="test-user-123",
                            username="testuser",
                            roles=["customer"],
                        )
                    )

                    client = TestClient(integrated_app)
                    response = client.get("/api/data", headers=kong_headers)
                    assert response.status_code == 200
                    assert response.json()["for"] == "user"
                    assert response.json()["data"] == "filtered"

    def test_shared_endpoint_with_service(
        self, integrated_app, mock_settings, service_headers, service_context
    ):
        """Test shared endpoint accessible by service"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            with patch("auth_gate.user_auth.get_settings", return_value=mock_settings):
                with patch("auth_gate.fastapi_utils.get_user_validator") as mock_validator:
                    mock_validator.return_value.get_current_user = AsyncMock(
                        return_value=service_context
                    )

                    client = TestClient(integrated_app)
                    response = client.get("/api/data", headers=service_headers)
                    assert response.status_code == 200
                    assert response.json()["for"] == "service"
                    assert response.json()["data"] == "full"

    def test_admin_endpoint_with_insufficient_roles(
        self, integrated_app, mock_settings, kong_headers
    ):
        """Test admin endpoint with insufficient roles"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            with patch("auth_gate.user_auth.get_settings", return_value=mock_settings):
                with patch("auth_gate.fastapi_utils.get_user_validator") as mock_validator:
                    mock_validator.return_value.get_current_user = AsyncMock(
                        return_value=UserContext(
                            user_id="test-user-123",
                            username="testuser",
                            roles=["customer"],
                        )
                    )

                    client = TestClient(integrated_app)
                    response = client.get("/api/admin/users", headers=kong_headers)
                    assert response.status_code == 403
                    assert "Requires one of roles" in response.json()["detail"]

    def test_admin_endpoint_with_admin_user(
        self, integrated_app, mock_settings, kong_headers, admin_user_context
    ):
        """Test admin endpoint with admin user"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            with patch("auth_gate.user_auth.get_settings", return_value=mock_settings):
                with patch("auth_gate.fastapi_utils.get_user_validator") as mock_validator:
                    mock_validator.return_value.get_current_user = AsyncMock(
                        return_value=admin_user_context
                    )

                    client = TestClient(integrated_app)
                    response = client.get("/api/admin/users", headers=kong_headers)
                    assert response.status_code == 200
                    assert response.json()["requester_type"] == "user"

    def test_admin_endpoint_with_admin_service(
        self, integrated_app, mock_settings, service_headers, admin_service_context
    ):
        """Test admin endpoint with admin service"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            with patch("auth_gate.user_auth.get_settings", return_value=mock_settings):
                with patch("auth_gate.fastapi_utils.get_user_validator") as mock_validator:
                    mock_validator.return_value.get_current_user = AsyncMock(
                        return_value=admin_service_context
                    )

                    client = TestClient(integrated_app)
                    response = client.get("/api/admin/users", headers=service_headers)
                    assert response.status_code == 200
                    assert response.json()["requester_type"] == "service"

    def test_optional_auth_endpoint(self, integrated_app, mock_settings, kong_headers):
        """Test optional authentication endpoint"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            client = TestClient(integrated_app)

            # Without authentication
            response = client.get("/api/products")
            assert response.status_code == 200
            assert response.json()["personalized"] is False

            # With user authentication
            with patch("auth_gate.user_auth.get_settings", return_value=mock_settings):
                with patch("auth_gate.fastapi_utils.get_user_validator") as mock_validator:
                    mock_validator.return_value.get_current_user = AsyncMock(
                        return_value=UserContext(
                            user_id="test-user-123",
                            username="testuser",
                            roles=["customer"],
                        )
                    )

                    response = client.get("/api/products", headers=kong_headers)
                    assert response.status_code == 200
                    assert response.json()["personalized"] is True

    def test_optional_auth_endpoint_with_service(
        self, integrated_app, mock_settings, service_headers, service_context
    ):
        """Test optional authentication endpoint with service (service is ignored)"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            with patch("auth_gate.user_auth.get_settings", return_value=mock_settings):
                with patch("auth_gate.fastapi_utils.get_user_validator") as mock_validator:
                    mock_validator.return_value.get_current_user = AsyncMock(
                        return_value=service_context
                    )

                    client = TestClient(integrated_app)
                    response = client.get("/api/products", headers=service_headers)
                    assert response.status_code == 200
                    # Service is ignored by get_optional_user
                    assert response.json()["personalized"] is False

    def test_bypass_mode_integration(self, integrated_app, mock_settings):
        """Test bypass mode for testing"""
        # Override for this test only (doesn't affect other tests using the fixture)
        mock_settings.AUTH_MODE = "bypass"

        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            with patch("auth_gate.fastapi_utils.get_settings", return_value=mock_settings):
                with patch("auth_gate.fastapi_utils.get_user_validator") as mock_validator:
                    # Mock the validator's get_current_user to return bypass user
                    mock_validator.return_value.get_current_user = AsyncMock(
                        return_value=UserContext(
                            user_id="00000000-0000-0000-0000-000000000000",
                            username="testuser",
                            roles=["admin"],
                            auth_source="bypass",
                            email="test@example.com",
                            session_id="test_session",
                            client_id="test_client",
                        )
                    )

                    client = TestClient(integrated_app)

                    # Should work without any headers
                    response = client.get("/api/profile")
                    assert response.status_code == 200
                    assert response.json()["user_id"] == "00000000-0000-0000-0000-000000000000"

                    # Admin endpoint should work (due to "admin" role)
                    response = client.get("/api/admin/users")
                    assert response.status_code == 200


class TestMiddlewareIntegration:
    """Test middleware integration specifically"""

    def test_middleware_logs_user_authentication(
        self, integrated_app, mock_settings, kong_headers, caplog
    ):
        """Test that middleware logs user authentication correctly"""
        import logging

        caplog.set_level(logging.INFO)

        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            with patch("auth_gate.user_auth.get_settings", return_value=mock_settings):
                with patch("auth_gate.fastapi_utils.get_user_validator") as mock_validator:
                    mock_validator.return_value.get_current_user = AsyncMock(
                        return_value=UserContext(
                            user_id="test-user-123",
                            username="testuser",
                            roles=["customer"],
                            auth_source="kong",
                        )
                    )

                    client = TestClient(integrated_app)
                    response = client.get("/api/profile", headers=kong_headers)
                    assert response.status_code == 200

                    # Check that user authentication was logged
                    assert any(
                        "Authenticated user request" in record.message for record in caplog.records
                    )

    def test_middleware_logs_service_authentication(
        self, integrated_app, mock_settings, service_headers, service_context, caplog
    ):
        """Test that middleware logs service authentication correctly"""
        import logging

        caplog.set_level(logging.INFO)

        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            with patch("auth_gate.user_auth.get_settings", return_value=mock_settings):
                with patch("auth_gate.fastapi_utils.get_user_validator") as mock_validator:
                    mock_validator.return_value.get_current_user = AsyncMock(
                        return_value=service_context
                    )

                    client = TestClient(integrated_app)
                    response = client.post("/api/internal/sync", headers=service_headers)
                    assert response.status_code == 200

                    # Check that service authentication was logged
                    assert any(
                        "Authenticated service request" in record.message
                        for record in caplog.records
                    )
