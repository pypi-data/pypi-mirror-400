"""
Tests for authentication schemas
"""

from auth_gate import UserContext
from auth_gate.schemas import AuthContext, ServiceContext


class TestBaseAuthContext:
    """Test BaseAuthContext common functionality"""

    def test_base_has_role(self):
        """Test has_role method on base context"""
        user = UserContext(user_id="user-123", roles=["customer", "verified"])

        assert user.has_role("customer") is True
        assert user.has_role("verified") is True
        assert user.has_role("admin") is False

    def test_base_has_any_role(self):
        """Test has_any_role method on base context"""
        user = UserContext(user_id="user-123", roles=["customer"])

        assert user.has_any_role(["customer", "admin"]) is True
        assert user.has_any_role(["admin", "supplier"]) is False

    def test_base_has_all_roles(self):
        """Test has_all_roles method on base context"""
        user = UserContext(user_id="user-123", roles=["customer", "verified"])

        assert user.has_all_roles(["customer", "verified"]) is True
        assert user.has_all_roles(["customer", "admin"]) is False


class TestUserContext:
    """Test UserContext model"""

    def test_user_context_creation(self):
        """Test creating user context"""
        user = UserContext(
            user_id="user-123",
            username="testuser",
            email="test@example.com",
            roles=["customer"],
            scopes=["read"],
            session_id="session-123",
            client_id="web-app",
            auth_source="kong",
        )

        assert user.user_id == "user-123"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.roles == ["customer"]
        assert user.scopes == ["read"]
        assert user.is_service is False

    def test_minimal_user_context(self):
        """Test creating user context with minimal data"""
        user = UserContext(user_id="user-123")

        assert user.user_id == "user-123"
        assert user.username is None
        assert user.email is None
        assert user.roles == []
        assert user.scopes == []
        assert user.auth_source == "unknown"
        assert user.is_service is False

    def test_is_admin_property(self):
        """Test is_admin property"""
        user = UserContext(user_id="user-123", roles=["customer"])
        assert user.is_admin is False

        admin = UserContext(user_id="admin-123", roles=["admin"])
        assert admin.is_admin is True

    def test_is_supplier_property(self):
        """Test is_supplier property"""
        user = UserContext(user_id="user-123", roles=["customer"])
        assert user.is_supplier is False

        supplier = UserContext(user_id="supplier-123", roles=["supplier"])
        assert supplier.is_supplier is True

        admin = UserContext(user_id="admin-123", roles=["admin"])
        assert admin.is_supplier is True  # Admin has supplier access

    def test_is_customer_property(self):
        """Test is_customer property"""
        user = UserContext(user_id="user-123", roles=["customer"])
        assert user.is_customer is True

        supplier = UserContext(user_id="supplier-123", roles=["supplier"])
        assert supplier.is_customer is False

    def test_is_moderator_property(self):
        """Test is_moderator property"""
        user = UserContext(user_id="user-123", roles=["customer"])
        assert user.is_moderator is False

        moderator = UserContext(user_id="mod-123", roles=["moderator"])
        assert moderator.is_moderator is True

        admin = UserContext(user_id="admin-123", roles=["admin"])
        assert admin.is_moderator is True  # Admin has moderator access

    def test_has_role(self):
        """Test has_role method"""
        user = UserContext(user_id="user-123", roles=["customer", "verified"])

        assert user.has_role("customer") is True
        assert user.has_role("verified") is True
        assert user.has_role("admin") is False
        assert user.has_role("supplier") is False

    def test_has_any_role(self):
        """Test has_any_role method"""
        user = UserContext(user_id="user-123", roles=["customer", "verified"])

        assert user.has_any_role(["customer", "admin"]) is True
        assert user.has_any_role(["verified"]) is True
        assert user.has_any_role(["admin", "supplier"]) is False
        assert user.has_any_role([]) is False

    def test_has_all_roles(self):
        """Test has_all_roles method"""
        user = UserContext(user_id="user-123", roles=["customer", "verified"])

        assert user.has_all_roles(["customer", "verified"]) is True
        assert user.has_all_roles(["customer"]) is True
        assert user.has_all_roles(["customer", "admin"]) is False
        assert user.has_all_roles([]) is True

    def test_has_scope(self):
        """Test has_scope method"""
        user = UserContext(user_id="user-123", scopes=["read", "write"])

        assert user.has_scope("read") is True
        assert user.has_scope("write") is True
        assert user.has_scope("admin") is False

    def test_has_any_scope(self):
        """Test has_any_scope method"""
        user = UserContext(user_id="user-123", scopes=["read", "write"])

        assert user.has_any_scope(["read", "admin"]) is True
        assert user.has_any_scope(["write"]) is True
        assert user.has_any_scope(["admin", "delete"]) is False
        assert user.has_any_scope([]) is False

    def test_admin_role_privileges(self):
        """Test admin role has special privileges"""
        admin = UserContext(user_id="admin-123", roles=["admin"])

        # Admin should pass all role checks
        assert admin.has_role("customer") is True
        assert admin.has_role("supplier") is True
        assert admin.has_role("moderator") is True
        assert admin.has_any_role(["customer", "supplier"]) is True


class TestServiceContext:
    """Test ServiceContext model"""

    def test_service_context_creation(self):
        """Test creating service context"""
        service = ServiceContext(
            service_name="payment-service",
            service_id="service-123",
            roles=["service", "payment-processor"],
            session_id="session-456",
            client_id="payment-service",
            auth_source="kong",
        )

        assert service.service_name == "payment-service"
        assert service.service_id == "service-123"
        assert service.roles == ["service", "payment-processor"]
        assert service.session_id == "session-456"
        assert service.client_id == "payment-service"
        assert service.auth_source == "kong"
        assert service.is_service is True

    def test_minimal_service_context(self):
        """Test creating service context with minimal data"""
        service = ServiceContext(service_name="test-service")

        assert service.service_name == "test-service"
        assert service.service_id is None
        assert service.roles == []
        assert service.auth_source == "unknown"
        assert service.is_service is True

    def test_service_is_admin_property(self):
        """Test is_admin property for services"""
        service = ServiceContext(service_name="test-service", roles=["service"])
        assert service.is_admin is False

        admin_service = ServiceContext(service_name="admin-service", roles=["admin"])
        assert admin_service.is_admin is True

    def test_service_role_methods(self):
        """Test role checking methods for services"""
        service = ServiceContext(service_name="test-service", roles=["service", "data-processor"])

        assert service.has_role("service") is True
        assert service.has_role("data-processor") is True
        assert service.has_role("admin") is False

        assert service.has_any_role(["service", "admin"]) is True
        assert service.has_any_role(["admin", "supplier"]) is False

        assert service.has_all_roles(["service", "data-processor"]) is True
        assert service.has_all_roles(["service", "admin"]) is False

    def test_service_properties_return_false(self):
        """Test that user-specific properties return False for services"""
        service = ServiceContext(service_name="test-service")

        assert service.is_supplier is False
        assert service.is_customer is False
        assert service.is_moderator is False

    def test_service_scope_methods_return_false(self):
        """Test that scope methods return False for services"""
        service = ServiceContext(service_name="test-service")

        assert service.has_scope("read") is False
        assert service.has_scope("write") is False
        assert service.has_any_scope(["read", "write"]) is False

    def test_service_moderator_with_role(self):
        """Test that service with moderator role returns True"""
        service = ServiceContext(service_name="moderation-service", roles=["service", "moderator"])

        assert service.is_moderator is True

    def test_service_admin_privileges(self):
        """Test admin service has special privileges"""
        admin_service = ServiceContext(service_name="admin-service", roles=["admin", "service"])

        # Admin should pass role checks
        assert admin_service.has_role("any-role") is True
        assert admin_service.has_any_role(["customer", "supplier"]) is True


class TestAuthContextUnion:
    """Test AuthContext union type"""

    def test_auth_context_with_user(self):
        """Test AuthContext can hold UserContext"""
        user: AuthContext = UserContext(user_id="user-123")

        assert isinstance(user, UserContext)
        assert user.is_service is False

    def test_auth_context_with_service(self):
        """Test AuthContext can hold ServiceContext"""
        service: AuthContext = ServiceContext(service_name="test-service")

        assert isinstance(service, ServiceContext)
        assert service.is_service is True

    def test_type_checking_user(self):
        """Test type checking for user context"""
        auth: AuthContext = UserContext(user_id="user-123")

        if isinstance(auth, UserContext):
            assert auth.user_id == "user-123"
            assert hasattr(auth, "email")
            assert hasattr(auth, "username")
        else:
            raise AssertionError("Should be UserContext")

    def test_type_checking_service(self):
        """Test type checking for service context"""
        auth: AuthContext = ServiceContext(service_name="test-service")

        if isinstance(auth, ServiceContext):
            assert auth.service_name == "test-service"
            assert hasattr(auth, "service_id")
        else:
            raise AssertionError("Should be ServiceContext")

    def test_is_service_property_discrimination(self):
        """Test using is_service property to discriminate types"""
        user: AuthContext = UserContext(user_id="user-123")
        service: AuthContext = ServiceContext(service_name="test-service")

        assert user.is_service is False
        assert service.is_service is True
