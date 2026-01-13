"""
Tests for configuration management
"""

import os

import pytest

from auth_gate import AuthMode, AuthSettings
from auth_gate.config import get_settings, reset_settings


class TestAuthSettings:
    """Test AuthSettings configuration"""

    def test_default_settings(self):
        """Test default settings initialization"""
        settings = AuthSettings()
        assert settings.AUTH_MODE == "kong_headers"
        assert settings.VERIFY_HMAC is False
        assert settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD == 5
        assert settings.CIRCUIT_BREAKER_RECOVERY_TIMEOUT == 60

    def test_settings_from_env(self):
        """Test settings from environment variables"""
        os.environ["AUTH_MODE"] = "direct_keycloak"
        os.environ["KEYCLOAK_REALM_URL"] = "https://keycloak.custom/realms/test"
        os.environ["VERIFY_HMAC"] = "true"

        settings = AuthSettings()
        assert settings.AUTH_MODE == "direct_keycloak"
        assert settings.KEYCLOAK_REALM_URL == "https://keycloak.custom/realms/test"
        assert settings.VERIFY_HMAC is True

    def test_auth_mode_enum_property(self):
        """Test auth_mode_enum property"""
        settings = AuthSettings(AUTH_MODE="kong_headers")
        assert settings.auth_mode_enum == AuthMode.KONG_HEADERS

        settings = AuthSettings(AUTH_MODE="direct_keycloak")
        assert settings.auth_mode_enum == AuthMode.DIRECT_KEYCLOAK

        settings = AuthSettings(AUTH_MODE="bypass")
        assert settings.auth_mode_enum == AuthMode.BYPASS

    def test_invalid_auth_mode(self):
        """Test invalid auth mode raises error"""
        settings = AuthSettings(AUTH_MODE="invalid")
        with pytest.raises(ValueError, match="Invalid AUTH_MODE"):
            _ = settings.auth_mode_enum

    def test_environment_flags(self):
        """Test environment detection flags"""
        settings = AuthSettings(AUTH_MODE="kong_headers")
        assert settings.is_production is True
        assert settings.is_development is False
        assert settings.is_testing is False

        settings = AuthSettings(AUTH_MODE="direct_keycloak")
        assert settings.is_production is False
        assert settings.is_development is True
        assert settings.is_testing is False

        settings = AuthSettings(AUTH_MODE="bypass")
        assert settings.is_production is False
        assert settings.is_development is False
        assert settings.is_testing is True

    def test_singleton_pattern(self):
        """Test settings singleton pattern"""
        reset_settings()
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

        reset_settings()
        settings3 = get_settings()
        assert settings3 is not settings1
