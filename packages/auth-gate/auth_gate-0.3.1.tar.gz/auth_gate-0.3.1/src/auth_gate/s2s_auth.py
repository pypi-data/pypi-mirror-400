"""
Service-to-service authentication with resilience patterns
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional, Tuple, Type, Union

import httpx
from fastapi import HTTPException, status

from .config import get_settings

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open"""

    pass


class CircuitBreaker:
    """
    Circuit breaker implementation for fault tolerance.

    States:
    - CLOSED: Normal operation, calls pass through
    - OPEN: Service is failing, calls are rejected
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
        name: Optional[str] = None,
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to catch
            name: Circuit breaker name for logging
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.name = name or "CircuitBreaker"

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        """Get current circuit state"""
        return self._state

    @property
    def is_open(self) -> bool:
        """Check if circuit is open"""
        return self._state == CircuitState.OPEN

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed"""
        return self._state == CircuitState.CLOSED

    async def __aenter__(self):
        """Context manager entry"""
        await self._before_call()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if exc_type is None:
            await self._on_success()
        elif issubclass(exc_type, self.expected_exception):
            await self._on_failure()
        # Don't suppress the exception
        return False

    async def _before_call(self):
        """Check circuit state before allowing call"""
        async with self._lock:
            if self._state == CircuitState.OPEN:
                # Check if recovery timeout has passed
                if self._last_failure_time and datetime.now(
                    timezone.utc
                ) - self._last_failure_time > timedelta(seconds=self.recovery_timeout):
                    logger.info(f"{self.name}: Attempting recovery (HALF_OPEN)")
                    self._state = CircuitState.HALF_OPEN
                else:
                    raise CircuitBreakerOpenError(f"{self.name}: Circuit is OPEN, rejecting call")

    async def _on_success(self):
        """Handle successful call"""
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                logger.info(f"{self.name}: Recovery successful, closing circuit")
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                self._last_failure_time = None
            elif self._state == CircuitState.CLOSED:
                # Reset failure count on success
                self._failure_count = 0

    async def _on_failure(self):
        """Handle failed call"""
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = datetime.now(timezone.utc)

            if self._state == CircuitState.HALF_OPEN:
                logger.warning(f"{self.name}: Recovery failed, reopening circuit")
                self._state = CircuitState.OPEN
            elif self._state == CircuitState.CLOSED:
                if self._failure_count >= self.failure_threshold:
                    logger.error(
                        f"{self.name}: Failure threshold reached ({self._failure_count}), "
                        f"opening circuit"
                    )
                    self._state = CircuitState.OPEN
                else:
                    logger.warning(
                        f"{self.name}: Failure {self._failure_count}/{self.failure_threshold}"
                    )

    def reset(self):
        """Manually reset circuit breaker"""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = None
        logger.info(f"{self.name}: Circuit manually reset")

    async def call(self, func, *args, **kwargs):
        """
        Execute a function with circuit breaker protection.

        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of func

        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Any exception raised by func
        """
        async with self:
            return await func(*args, **kwargs)


@dataclass
class ServiceToken:
    """Service account token"""

    access_token: str
    token_type: str
    expires_in: int
    created_at: datetime = datetime.now(timezone.utc)  # Default to current time

    @property
    def is_expired(self) -> bool:
        """Check if token is expired (with buffer)"""
        settings = get_settings()
        expiry_time = self.created_at + timedelta(
            seconds=self.expires_in - settings.TOKEN_REFRESH_BUFFER
        )
        return datetime.now(timezone.utc) > expiry_time

    @property
    def authorization_header(self) -> str:
        """Get authorization header value"""
        return f"{self.token_type} {self.access_token}"


class ServiceAuthClient:
    """
    Client for obtaining and managing service account tokens from Keycloak.
    Includes circuit breaker for resilience against Keycloak failures.
    """

    def __init__(self):
        """Initialize service auth client with circuit breaker"""
        settings = get_settings()
        self.token_url = f"{settings.KEYCLOAK_REALM_URL}/protocol/openid-connect/token"
        self.client_id = settings.SERVICE_CLIENT_ID
        self.client_secret = settings.SERVICE_CLIENT_SECRET
        self._token: Optional[ServiceToken] = None
        self._lock = asyncio.Lock()
        self._http_client: Optional[httpx.AsyncClient] = None

        # Initialize circuit breaker
        self._circuit_breaker: CircuitBreaker = CircuitBreaker(
            failure_threshold=settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD,
            recovery_timeout=settings.CIRCUIT_BREAKER_RECOVERY_TIMEOUT,
            expected_exception=(httpx.RequestError, HTTPException),
            name="ServiceAuthCircuit",
        )

    @property
    async def http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._http_client is None:
            settings = get_settings()
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(settings.HTTP_TIMEOUT),
                limits=httpx.Limits(max_keepalive_connections=5),
            )
        return self._http_client

    async def _fetch_token(self) -> ServiceToken:
        """
        Internal method to fetch token from Keycloak.

        Returns:
            ServiceToken

        Raises:
            HTTPException: If token fetch fails
        """
        client = await self.http_client
        response = await client.post(
            self.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "openid profile",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code != 200:
            logger.error(f"Failed to get service token: {response.status_code} - {response.text}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to authenticate service",
            )

        token_data = response.json()
        return ServiceToken(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in", 300),
        )

    async def get_service_token(self) -> str:
        """
        Get service account token for service-to-service calls.
        Uses circuit breaker for resilience against Keycloak failures.

        Returns:
            Authorization header value (e.g., "Bearer token")

        Raises:
            CircuitBreakerOpenError: If circuit is open due to repeated failures
            HTTPException: If token fetch fails
        """
        async with self._lock:
            # Return cached token if still valid
            if self._token and not self._token.is_expired:
                return self._token.authorization_header

            # Get new token with circuit breaker protection
            try:
                self._token = await self._circuit_breaker.call(self._fetch_token)
                if self._token is not None:
                    logger.info(
                        f"Obtained new service token for {self.client_id}, "
                        f"expires in {self._token.expires_in} seconds"
                    )
                    return self._token.authorization_header
                else:
                    logger.error("Failed to obtain service token: token is None")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to authenticate service",
                    )

            except CircuitBreakerOpenError:
                logger.error("Circuit breaker is open - Keycloak is unavailable")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Authentication service temporarily unavailable",
                )
            except httpx.RequestError as e:
                logger.error(f"Failed to connect to Keycloak: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Authentication service unavailable",
                )
            except Exception as e:
                logger.error(f"Unexpected error getting service token: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to authenticate service",
                )

    @property
    def circuit_state(self) -> CircuitState:
        """Get current circuit breaker state"""
        return self._circuit_breaker.state

    def reset_circuit(self):
        """Manually reset circuit breaker"""
        self._circuit_breaker.reset()

    async def close(self):
        """Close HTTP client and clean up resources"""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None


# Global instance management
_service_auth_client: Optional[ServiceAuthClient] = None


def get_service_auth_client() -> ServiceAuthClient:
    """Get or create service auth client"""
    global _service_auth_client
    if _service_auth_client is None:
        _service_auth_client = ServiceAuthClient()
    return _service_auth_client


async def cleanup_service_auth():
    """Cleanup service auth resources"""
    global _service_auth_client
    if _service_auth_client:
        await _service_auth_client.close()
        _service_auth_client = None
