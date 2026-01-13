"""
Tests for authentication middleware with method-specific exclusions
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient

from auth_gate import AuthMiddleware, UserContext
from auth_gate.fastapi_utils import get_optional_user


@pytest.fixture
def app():
    """Create test FastAPI app"""
    app = FastAPI()

    @app.get("/public")
    async def public_get():
        return {"message": "public GET"}

    @app.post("/public")
    async def public_post():
        return {"message": "public POST"}

    @app.get("/protected")
    async def protected_endpoint(request: Request):
        user = request.state.user
        return {"user_id": user.user_id if user else None}

    @app.get("/optional")
    async def optional_get(request: Request):
        user = getattr(request.state, "user", None)
        return {"authenticated": user is not None, "method": "GET"}

    @app.post("/optional")
    async def optional_post(user: UserContext = Depends(get_optional_user)):
        return {"authenticated": user is not None, "method": "POST"}

    @app.get("/api/data")
    async def api_data_get(user: UserContext = Depends(get_optional_user)):
        return {"data": "GET data", "user_id": user.user_id if user else None}

    @app.post("/api/data")
    async def api_data_post(request: Request):
        user = request.state.user
        return {"data": "POST data", "user_id": user.user_id if user else None}

    @app.get("/api/v1/resource")
    async def api_resource(user: UserContext = Depends(get_optional_user)):
        return {"resource": "data", "user_id": user.user_id if user else None}

    return app


class TestAuthMiddleware:
    """Test AuthMiddleware basic functionality"""

    def test_middleware_excludes_paths(self, app, mock_settings):
        """Test middleware excludes configured paths"""
        app.add_middleware(
            AuthMiddleware,
            excluded_paths={"/public", "/health"},
            excluded_prefixes={"/static"},
        )

        client = TestClient(app)

        # Public endpoint should work without auth
        response = client.get("/public")
        assert response.status_code == 200
        assert response.json() == {"message": "public GET"}

    def test_middleware_requires_auth_for_protected(self, app, mock_settings):
        """Test middleware requires auth for protected endpoints"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            app.add_middleware(
                AuthMiddleware,
                excluded_paths={"/public"},
            )

            client = TestClient(app)

            # Protected endpoint should fail without auth
            response = client.get("/protected")
            assert response.status_code == 401
            assert "Authentication required" in response.json()["message"]

    def test_middleware_with_kong_headers(self, app, mock_settings, kong_headers):
        """Test middleware with Kong headers"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            with patch("auth_gate.user_auth.get_settings", return_value=mock_settings):
                app.add_middleware(
                    AuthMiddleware,
                    excluded_paths={"/public"},
                )

                client = TestClient(app)

                # Protected endpoint should work with Kong headers
                response = client.get("/protected", headers=kong_headers)
                assert response.status_code == 200
                assert response.json()["user_id"] == "test-user-123"

    def test_middleware_optional_auth(self, app, mock_settings, kong_headers):
        """Test middleware with optional authentication paths"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            app.add_middleware(
                AuthMiddleware,
                excluded_paths={"/public"},
                optional_auth_paths={"/optional"},
            )

            client = TestClient(app)

            # Optional endpoint should work without auth
            response = client.get("/optional")
            assert response.status_code == 200
            assert response.json()["authenticated"] is False

            # Optional endpoint should detect auth when present
            with patch("auth_gate.user_auth.get_settings", return_value=mock_settings):
                response = client.get("/optional", headers=kong_headers)
                assert response.status_code == 200
                assert response.json()["authenticated"] is True

    def test_middleware_adds_security_headers(self, app, mock_settings):
        """Test middleware adds security headers"""
        app.add_middleware(
            AuthMiddleware,
            excluded_paths={"/public"},
        )

        client = TestClient(app)

        response = client.get("/public")
        assert response.status_code == 200

        # Check security headers
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert "Strict-Transport-Security" in response.headers
        assert "X-Process-Time" in response.headers

    def test_middleware_bypass_mode(self, app, mock_settings):
        """Test middleware in bypass mode"""
        mock_settings.AUTH_MODE = "bypass"

        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            with patch("auth_gate.user_auth.get_settings", return_value=mock_settings):
                app.add_middleware(
                    AuthMiddleware,
                    excluded_paths={"/public"},
                )

                client = TestClient(app)

                # Should work without any auth headers in bypass mode
                response = client.get("/protected")
                assert response.status_code == 200
                assert response.json()["user_id"] == "00000000-0000-0000-0000-000000000000"


class TestMethodSpecificExclusions:
    """Test method-specific path exclusions"""

    def test_exclude_specific_methods_only(self, app, mock_settings):
        """Test excluding specific HTTP methods for a path"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            app.add_middleware(
                AuthMiddleware,
                excluded_paths={
                    "/public": {"GET"},  # Only GET is excluded
                },
            )

            client = TestClient(app)

            # GET should work without auth
            response = client.get("/public")
            assert response.status_code == 200
            assert response.json() == {"message": "public GET"}

            # POST should require auth
            response = client.post("/public")
            assert response.status_code == 401
            assert "Authentication required" in response.json()["message"]

    def test_exclude_multiple_methods(self, app, mock_settings, kong_headers):
        """Test excluding multiple specific methods"""
        mock_settings.AUTH_MODE = "kong_headers"
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            with patch("auth_gate.user_auth.get_settings", return_value=mock_settings):
                app.add_middleware(
                    AuthMiddleware,
                    excluded_paths={
                        "/api/data": {"GET", "HEAD", "OPTIONS"},  # Read-only methods excluded
                    },
                )

                client = TestClient(app)

                # GET should work without auth
                response = client.get("/api/data")
                assert response.status_code == 200
                assert response.json()["data"] == "GET data"
                assert response.json()["user_id"] is None

                # POST should require auth
                response = client.post("/api/data")
                assert response.status_code == 401

                # POST with auth should work
                response = client.post("/api/data", headers=kong_headers)
                assert response.status_code == 200
                assert response.json()["user_id"] == "test-user-123"

    def test_mixed_exclusion_formats(self, app, mock_settings):
        """Test mixing set and dict formats for exclusions"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            app.add_middleware(
                AuthMiddleware,
                excluded_paths={
                    "/public": {"GET"},  # Method-specific
                    "/health": None,  # All methods
                },
                excluded_prefixes={
                    "/static": None,  # All methods for prefix
                    "/api/docs": {"GET"},  # Only GET for docs
                },
            )

            client = TestClient(app)

            # Test method-specific exclusion
            response = client.get("/public")
            assert response.status_code == 200

            response = client.post("/public")
            assert response.status_code == 401

    def test_optional_auth_with_methods(self, app, mock_settings, kong_headers):
        """Test optional authentication with method specifications"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            with patch("auth_gate.user_auth.get_settings", return_value=mock_settings):
                app.add_middleware(
                    AuthMiddleware,
                    optional_auth_paths={
                        "/optional": {"GET"},  # Only GET has optional auth
                    },
                )

                client = TestClient(app)

                # GET should work without auth (optional)
                response = client.get("/optional")
                assert response.status_code == 200
                assert response.json()["authenticated"] is False

                # GET with auth should detect it
                response = client.get("/optional", headers=kong_headers)
                assert response.status_code == 200
                assert response.json()["authenticated"] is True

                # POST should require auth (not optional)
                response = client.post("/optional")
                assert response.status_code == 401
                assert "Authentication required" in response.json()["message"]

    def test_prefix_exclusion_with_methods(self, app, mock_settings):
        """Test prefix exclusion with method specifications"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            app.add_middleware(
                AuthMiddleware,
                excluded_prefixes={
                    "/api": {"GET", "HEAD"},  # Only GET/HEAD excluded for /api/*
                },
            )

            client = TestClient(app)
            with patch("auth_gate.fastapi_utils.get_user_validator") as mock_validator:
                mock_validator.return_value.get_current_user = AsyncMock(
                    return_value=UserContext(
                        user_id="test-user",
                        username="testuser",
                        roles=["customer"],
                        auth_source="kong",
                    )
                )
                # GET requests under /api should work without auth
                response = client.get("/api/data")
                assert response.status_code == 200

                response = client.get("/api/v1/resource")
                assert response.status_code == 200

                # POST requests under /api should require auth
                response = client.post("/api/data")
                assert response.status_code == 401

    def test_case_insensitive_methods(self, app, mock_settings):
        """Test that method names are case-insensitive"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            app.add_middleware(
                AuthMiddleware,
                excluded_paths={
                    "/public": {"get", "post"},  # Lowercase methods
                },
            )

            client = TestClient(app)

            # Both GET and POST should work (case-insensitive)
            response = client.get("/public")
            assert response.status_code == 200

            response = client.post("/public")
            assert response.status_code == 200

    def test_backward_compatibility_set_format(self, app, mock_settings):
        """Test backward compatibility with set format"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            # Old format still works
            app.add_middleware(
                AuthMiddleware,
                excluded_paths={"/public", "/health"},  # Set format
                excluded_prefixes={"/static"},  # Set format
                optional_auth_paths={"/optional"},  # Set format
            )

            client = TestClient(app)

            # All methods should be excluded for set format
            response = client.get("/public")
            assert response.status_code == 200

            response = client.post("/public")
            assert response.status_code == 200

            # Optional auth should work for all methods
            response = client.get("/optional")
            assert response.status_code == 200
            assert response.json()["authenticated"] is False

            response = client.post("/optional")
            assert response.status_code == 200
            assert response.json()["authenticated"] is False

    # def test_invalid_path_format_raises_error(self, app, mock_settings):
    #     """Test that invalid path format raises error"""
    #     with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
    #         with pytest.raises(ValueError, match="Invalid type for paths"):
    #             app.add_middleware(
    #                 AuthMiddleware,
    #                 excluded_paths=["/public"],  # List not supported, should be set or dict
    #             )

    # def test_invalid_methods_format_raises_error(self, app, mock_settings):
    #     """Test that invalid methods format raises error"""
    #     with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
    #         with pytest.raises(ValueError, match="Methods must be a set or None"):
    #             app.add_middleware(
    #                 AuthMiddleware,
    #                 excluded_paths={
    #                     "/public": ["GET", "POST"],  # List not supported, should be set
    #                 }
    #             )

    def test_complex_real_world_scenario(self, app, mock_settings, kong_headers):
        """Test a complex real-world configuration"""
        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            with patch("auth_gate.user_auth.get_settings", return_value=mock_settings):
                app.add_middleware(
                    AuthMiddleware,
                    excluded_paths={
                        "/health": None,  # Health check - all methods
                        "/public": {"GET", "HEAD"},  # Public read-only
                    },
                    excluded_prefixes={
                        "/static": None,  # Static files - all methods
                        "/api/docs": {"GET"},  # API docs - GET only
                    },
                    optional_auth_paths={
                        "/api/data": {"GET"},  # Public read, auth for write
                    },
                )

                client = TestClient(app)

                # Test excluded paths
                response = client.get("/public")
                assert response.status_code == 200

                response = client.post("/public")
                assert response.status_code == 401

                # Test optional auth
                response = client.get("/api/data")
                assert response.status_code == 200
                assert response.json()["user_id"] is None

                response = client.get("/api/data", headers=kong_headers)
                assert response.status_code == 200
                assert response.json()["user_id"] == "test-user-123"

                response = client.post("/api/data")
                assert response.status_code == 401

                # Protected endpoints still require auth
                response = client.get("/protected")
                assert response.status_code == 401

                response = client.get("/protected", headers=kong_headers)
                assert response.status_code == 200


class TestParameterizedPathMatching:
    """Test parameterized path matching with UUID v4 patterns"""

    def test_uuid_path_parameter_basic(self, mock_settings, kong_headers):
        """Test basic UUID parameter matching"""
        mock_settings.AUTH_MODE = "kong_headers"

        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            app = FastAPI()

            valid_uuid = "7b5bcc8f-2c99-43c0-9c7d-e27c10881bd2"

            @app.get(f"/api/v1/categories/{valid_uuid}")
            async def get_category():
                return {"id": valid_uuid}

            app.add_middleware(
                AuthMiddleware,
                excluded_paths={
                    "/api/v1/categories/{category_id:uuid}": None,
                },
            )

            client = TestClient(app)

            # Valid UUID should be excluded (no auth needed)
            response = client.get(f"/api/v1/categories/{valid_uuid}")
            assert response.status_code == 200
            assert response.json()["id"] == valid_uuid

    def test_uuid_path_parameter_with_methods(self, mock_settings, kong_headers):
        """Test UUID parameters with method-specific exclusions"""
        mock_settings.AUTH_MODE = "kong_headers"

        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            app = FastAPI()

            valid_uuid = "a1b2c3d4-e5f6-4789-abcd-ef0123456789"

            @app.get(f"/api/v1/products/{valid_uuid}")
            async def get_product():
                return {"id": valid_uuid, "method": "GET"}

            @app.post(f"/api/v1/products/{valid_uuid}")
            async def update_product(request: Request):
                user = request.state.user
                return {"id": valid_uuid, "method": "POST", "user": user.user_id}

            app.add_middleware(
                AuthMiddleware,
                excluded_paths={
                    "/api/v1/products/{product_id:uuid}": {"GET"},  # Only GET excluded
                },
            )

            client = TestClient(app)

            # GET should work without auth (excluded)
            response = client.get(f"/api/v1/products/{valid_uuid}")
            assert response.status_code == 200
            assert response.json()["method"] == "GET"

            # POST should require auth (not excluded)
            response = client.post(f"/api/v1/products/{valid_uuid}")
            assert response.status_code == 401

            # POST with auth should work
            response = client.post(f"/api/v1/products/{valid_uuid}", headers=kong_headers)
            assert response.status_code == 200
            assert response.json()["user"] == "test-user-123"

    def test_uuid_invalid_format_requires_auth(self, mock_settings):
        """Test that invalid UUID formats don't match pattern"""
        mock_settings.AUTH_MODE = "kong_headers"

        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            app = FastAPI()

            @app.get("/api/v1/categories/{category_id}")
            async def get_category(category_id: str):
                return {"id": category_id}

            app.add_middleware(
                AuthMiddleware,
                excluded_paths={
                    "/api/v1/categories/{category_id:uuid}": None,
                },
            )

            client = TestClient(app)

            # Invalid UUIDs should require auth
            invalid_ids = [
                "invalid-id",
                "123",
                "all",
                "not-a-uuid",
                "7b5bcc8f",  # Too short
                "7b5bcc8f-2c99-43c0-9c7d-e27c10881bd2-extra",  # Too long
                "7b5bcc8f-2c99-53c0-9c7d-e27c10881bd2",  # Wrong version (5 instead of 4)
            ]

            for invalid_id in invalid_ids:
                response = client.get(f"/api/v1/categories/{invalid_id}")
                assert response.status_code == 401, f"Expected 401 for {invalid_id}"

    def test_exact_match_takes_precedence_over_pattern(self, mock_settings, kong_headers):
        """Test that exact paths have higher priority than patterns"""
        mock_settings.AUTH_MODE = "kong_headers"

        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            app = FastAPI()

            @app.get("/api/v1/categories/featured")
            async def get_featured():
                return {"type": "featured"}

            @app.post("/api/v1/categories/featured")
            async def update_featured():
                return {"type": "updated"}

            app.add_middleware(
                AuthMiddleware,
                excluded_paths={
                    "/api/v1/categories/featured": None,  # Exact match - all methods
                    "/api/v1/categories/{category_id:uuid}": {"GET"},  # Pattern - GET only
                },
            )

            client = TestClient(app)

            # Exact match should work for all methods (None = all methods)
            response = client.get("/api/v1/categories/featured")
            assert response.status_code == 200

            response = client.post("/api/v1/categories/featured")
            assert response.status_code == 200  # Exact match wins, POST excluded

    def test_multiple_uuid_parameters(self, mock_settings):
        """Test paths with multiple UUID parameters"""
        mock_settings.AUTH_MODE = "kong_headers"

        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            app = FastAPI()

            store_id = "550e8400-e29b-41d4-a716-446655440000"
            product_id = "7b5bcc8f-2c99-43c0-9c7d-e27c10881bd2"

            @app.get(f"/api/v1/stores/{store_id}/products/{product_id}")
            async def get_product():
                return {"store_id": store_id, "product_id": product_id}

            app.add_middleware(
                AuthMiddleware,
                excluded_paths={
                    "/api/v1/stores/{store_id:uuid}/products/{product_id:uuid}": {"GET"},
                },
            )

            client = TestClient(app)

            # Valid UUIDs should match
            response = client.get(f"/api/v1/stores/{store_id}/products/{product_id}")
            assert response.status_code == 200
            assert response.json()["store_id"] == store_id
            assert response.json()["product_id"] == product_id

            # Invalid UUID in either position should require auth
            response = client.get(f"/api/v1/stores/invalid/products/{product_id}")
            assert response.status_code == 401

            response = client.get(f"/api/v1/stores/{store_id}/products/invalid")
            assert response.status_code == 401

    def test_pattern_match_with_optional_auth(self, mock_settings, kong_headers):
        """Test parameterized paths with optional authentication"""
        mock_settings.AUTH_MODE = "kong_headers"

        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            app = FastAPI()

            user_id = "123e4567-e89b-42d3-a456-426614174000"

            @app.get(f"/api/v1/recommendations/{user_id}")
            async def get_recommendations(request: Request):
                user = getattr(request.state, "user", None)
                if user:
                    return {"personalized": True, "user_id": user.user_id}
                return {"personalized": False}

            app.add_middleware(
                AuthMiddleware,
                optional_auth_paths={
                    "/api/v1/recommendations/{user_id:uuid}": {"GET"},
                },
            )

            client = TestClient(app)

            # Without auth - should work but not personalized
            response = client.get(f"/api/v1/recommendations/{user_id}")
            assert response.status_code == 200
            assert response.json()["personalized"] is False

            # With auth - should work and be personalized
            response = client.get(f"/api/v1/recommendations/{user_id}", headers=kong_headers)
            assert response.status_code == 200
            assert response.json()["personalized"] is True
            assert response.json()["user_id"] == "test-user-123"

    def test_prefix_pattern_matching(self, mock_settings):
        """Test parameterized prefix matching"""
        mock_settings.AUTH_MODE = "kong_headers"

        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            app = FastAPI()

            version_id = "f47ac10b-58cc-4372-a567-0e02b2c3d479"

            @app.get(f"/api/{version_id}/docs")
            async def get_docs():
                return {"version": version_id, "type": "docs"}

            @app.get(f"/api/{version_id}/swagger")
            async def get_swagger():
                return {"version": version_id, "type": "swagger"}

            app.add_middleware(
                AuthMiddleware,
                excluded_prefixes={
                    "/api/{version:uuid}": {"GET"},
                },
            )

            client = TestClient(app)

            # Both should be excluded (prefix match)
            response = client.get(f"/api/{version_id}/docs")
            assert response.status_code == 200

            response = client.get(f"/api/{version_id}/swagger")
            assert response.status_code == 200

    def test_backward_compatibility_no_regression(self, mock_settings, kong_headers):
        """Test that existing configurations still work"""
        mock_settings.AUTH_MODE = "kong_headers"

        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            app = FastAPI()

            @app.get("/health")
            async def health():
                return {"status": "ok"}

            @app.get("/api/docs/swagger")
            async def swagger():
                return {"docs": "swagger"}

            @app.get("/protected")
            async def protected(request: Request):
                user = request.state.user
                return {"user_id": user.user_id}

            app.add_middleware(
                AuthMiddleware,
                excluded_paths={"/health"},  # Set format (legacy)
                excluded_prefixes={"/api/docs": {"GET"}},  # Dict with methods
            )

            client = TestClient(app)

            # Exact path exclusion still works
            response = client.get("/health")
            assert response.status_code == 200

            # Prefix exclusion still works
            response = client.get("/api/docs/swagger")
            assert response.status_code == 200

            # Protected endpoint still requires auth
            response = client.get("/protected")
            assert response.status_code == 401

            response = client.get("/protected", headers=kong_headers)
            assert response.status_code == 200

    def test_invalid_pattern_syntax_raises_error(self, mock_settings):
        """Test that invalid patterns raise clear errors"""
        mock_settings.AUTH_MODE = "kong_headers"

        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            with patch("auth_gate.middleware.get_user_validator"):
                # Missing type annotation
                with pytest.raises(ValueError, match="missing type annotation"):
                    AuthMiddleware(
                        app=None,
                        excluded_paths={
                            "/api/{id}": None,  # No :type specified
                        },
                    )

                # Unsupported type
                with pytest.raises(ValueError, match="Unsupported type"):
                    AuthMiddleware(
                        app=None,
                        excluded_paths={
                            "/api/{id:invalid}": None,
                        },
                    )

    def test_case_insensitive_uuid_matching(self, mock_settings):
        """Test that UUID matching is case-insensitive"""
        mock_settings.AUTH_MODE = "kong_headers"

        with patch("auth_gate.middleware.get_settings", return_value=mock_settings):
            app = FastAPI()

            @app.get("/api/v1/items/{item_id}")
            async def get_item(item_id: str):
                return {"id": item_id}

            app.add_middleware(
                AuthMiddleware,
                excluded_paths={
                    "/api/v1/items/{item_id:uuid}": None,
                },
            )

            client = TestClient(app)

            # Test different case variations (all valid UUID v4)
            uuids = [
                "7b5bcc8f-2c99-43c0-9c7d-e27c10881bd2",  # lowercase
                "7B5BCC8F-2C99-43C0-9C7D-E27C10881BD2",  # uppercase
                "7b5bCc8f-2C99-43c0-9C7d-E27c10881bD2",  # mixed case
            ]

            for uuid_val in uuids:
                response = client.get(f"/api/v1/items/{uuid_val}")
                assert response.status_code == 200, f"Failed for UUID: {uuid_val}"
                assert response.json()["id"] == uuid_val
