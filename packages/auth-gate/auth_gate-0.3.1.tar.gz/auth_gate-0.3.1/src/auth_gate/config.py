"""
Configuration management for Tradelink Auth Client
"""

from enum import Enum
from typing import Optional

from pydantic_settings import BaseSettings


class AuthMode(Enum):
    """Authentication modes for different environments"""

    KONG_HEADERS = "kong_headers"  # Production: Kong validates tokens
    DIRECT_KEYCLOAK = "direct_keycloak"  # Development: Direct Keycloak validation
    BYPASS = "bypass"  # Testing only - NEVER use in production


class AuthSettings(BaseSettings):
    """
    Centralized configuration for authentication client.
    All settings can be overridden via environment variables.
    """

    model_config = {
        "env_file": (".env", ".env.test", ".env.prod"),
        "extra": "ignore",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }

    # Authentication Mode
    AUTH_MODE: str = "kong_headers"

    # Keycloak Configuration
    KEYCLOAK_REALM_URL: str = "http://localhost:8080/realms/master"
    KEYCLOAK_CLIENT_ID: str = "backend-service"
    KEYCLOAK_CLIENT_SECRET: str = ""

    # Service Account Configuration (for S2S)
    SERVICE_CLIENT_ID: str = "service-account"
    SERVICE_CLIENT_SECRET: str = ""

    # HMAC Verification (optional)
    VERIFY_HMAC: bool = False
    INTERNAL_HMAC_KEY: str = ""

    # Circuit Breaker Settings
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = 60

    # Token Settings
    TOKEN_CACHE_TTL: int = 300  # seconds
    TOKEN_REFRESH_BUFFER: int = 30  # seconds before expiry

    # HTTP Client Settings
    HTTP_TIMEOUT: float = 10.0
    HTTP_MAX_KEEPALIVE_CONNECTIONS: int = 10

    @property
    def auth_mode_enum(self) -> AuthMode:
        """Get AUTH_MODE as enum"""
        try:
            return AuthMode(self.AUTH_MODE.lower())
        except ValueError:
            raise ValueError(f"Invalid AUTH_MODE: {self.AUTH_MODE}")

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.auth_mode_enum == AuthMode.KONG_HEADERS

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.auth_mode_enum == AuthMode.DIRECT_KEYCLOAK

    @property
    def is_testing(self) -> bool:
        """Check if running in testing/bypass mode"""
        return self.auth_mode_enum == AuthMode.BYPASS


# Global settings instance
_settings: Optional[AuthSettings] = None


def get_settings() -> AuthSettings:
    """Get or create settings instance"""
    global _settings
    if _settings is None:
        _settings = AuthSettings()
    return _settings


def reset_settings() -> None:
    """Reset settings (useful for testing)"""
    global _settings
    _settings = None
