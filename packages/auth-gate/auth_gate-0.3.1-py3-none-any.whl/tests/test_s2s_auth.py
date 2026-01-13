"""
Tests for service-to-service authentication
"""

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi import HTTPException

from auth_gate.s2s_auth import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
    ServiceToken,
)


class TestCircuitBreaker:
    """Test CircuitBreaker implementation"""

    @pytest.mark.asyncio
    async def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in closed state allows calls"""
        breaker = CircuitBreaker(failure_threshold=3)

        assert breaker.state == CircuitState.CLOSED
        assert breaker.is_closed is True

        # Successful calls should pass through
        async with breaker:
            pass  # Successful operation

        assert breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_threshold(self):
        """Test circuit breaker opens after failure threshold"""
        breaker = CircuitBreaker(failure_threshold=3)

        # Simulate failures
        for i in range(3):
            try:
                async with breaker:
                    raise ValueError("Test failure")
            except ValueError:
                pass

        assert breaker.state == CircuitState.OPEN
        assert breaker.is_open is True

    @pytest.mark.asyncio
    async def test_circuit_breaker_rejects_calls_when_open(self):
        """Test circuit breaker rejects calls when open"""
        breaker = CircuitBreaker(failure_threshold=2)

        # Open the circuit
        for i in range(2):
            try:
                async with breaker:
                    raise ValueError("Test failure")
            except ValueError:
                pass

        # Should reject calls when open
        with pytest.raises(CircuitBreakerOpenError):
            async with breaker:
                pass

    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_recovery(self):
        """Test circuit breaker recovery through half-open state"""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0)  # Instant recovery

        # Open the circuit
        for i in range(2):
            try:
                async with breaker:
                    raise ValueError("Test failure")
            except ValueError:
                pass

        assert breaker.state == CircuitState.OPEN

        # Wait a tiny bit for recovery timeout
        await asyncio.sleep(0.01)

        # Should transition to half-open and allow one call
        async with breaker:
            pass  # Successful call

        assert breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_failure(self):
        """Test circuit breaker reopens on half-open failure"""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0)

        # Open the circuit
        for i in range(2):
            try:
                async with breaker:
                    raise ValueError("Test failure")
            except ValueError:
                pass

        # Wait for recovery
        await asyncio.sleep(0.01)

        # Fail during half-open
        try:
            async with breaker:
                raise ValueError("Recovery failure")
        except ValueError:
            pass

        assert breaker.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_circuit_breaker_call_wrapper(self):
        """Test circuit breaker call wrapper method"""
        breaker = CircuitBreaker(failure_threshold=3)

        async def successful_func(x, y):
            return x + y

        result = await breaker.call(successful_func, 2, 3)
        assert result == 5

        async def failing_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            await breaker.call(failing_func)

    def test_circuit_breaker_reset(self):
        """Test manual circuit breaker reset"""
        breaker = CircuitBreaker(failure_threshold=1)

        # Open the circuit by causing a failure
        with pytest.raises(ValueError):
            asyncio.run(breaker.call(lambda: (_ for _ in ()).throw(ValueError("Test error"))))

        # At this point, the circuit should be open
        assert breaker.state == CircuitState.OPEN

        # Reset manually
        breaker.reset()

        assert breaker.state == CircuitState.CLOSED
        assert breaker._failure_count == 0
        assert breaker._last_failure_time is None


class TestServiceToken:
    """Test ServiceToken model"""

    def test_service_token_not_expired(self):
        """Test service token expiration check"""
        token = ServiceToken(
            access_token="test-token",
            token_type="Bearer",
            expires_in=300,
            created_at=datetime.now(timezone.utc),
        )

        assert token.is_expired is False
        assert token.authorization_header == "Bearer test-token"

    def test_service_token_expired(self):
        """Test expired service token"""
        token = ServiceToken(
            access_token="test-token",
            token_type="Bearer",
            expires_in=300,
            created_at=datetime.now(timezone.utc) - timedelta(seconds=400),
        )

        assert token.is_expired is True


class TestServiceAuthClient:
    """Test ServiceAuthClient"""

    @pytest.mark.asyncio
    async def test_get_service_token_success(
        self, mock_settings, service_auth_client, service_token_response
    ):
        """Test successful service token acquisition"""
        with patch.object(httpx.AsyncClient, "post", new=AsyncMock()) as mock_post:
            mock_post.return_value = httpx.Response(status_code=200, json=service_token_response)
            token = await service_auth_client.get_service_token()

            assert token == "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test"
            assert service_auth_client._token is not None
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_service_token_cached(
        self, mock_settings, service_auth_client, service_token_response
    ):
        """Test service token caching"""
        with patch.object(httpx.AsyncClient, "post", new=AsyncMock()) as mock_post:
            mock_post.return_value = httpx.Response(status_code=200, json=service_token_response)
            # First call
            token1 = await service_auth_client.get_service_token()

            # Second call should use cache
            token2 = await service_auth_client.get_service_token()

            assert token1 == token2
            # HTTP client should only be called once
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_service_token_refresh_on_expiry(
        self, mock_settings, service_auth_client, service_token_response
    ):
        """Test service token refresh on expiry"""
        # Set an already expired token
        service_auth_client._token = ServiceToken(
            access_token="old-token",
            token_type="Bearer",
            expires_in=300,
            created_at=datetime.now(timezone.utc) - timedelta(seconds=400),
        )

        with patch.object(httpx.AsyncClient, "post", new=AsyncMock()) as mock_post:
            mock_post.return_value = httpx.Response(status_code=200, json=service_token_response)

            token = await service_auth_client.get_service_token()

            assert token == "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test"
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_service_token_circuit_breaker_open(self, mock_settings, service_auth_client):
        """Test service token with open circuit breaker"""
        # Manually open the circuit breaker
        service_auth_client._circuit_breaker._state = CircuitState.OPEN
        service_auth_client._circuit_breaker._last_failure_time = datetime.now(timezone.utc)

        with pytest.raises(HTTPException) as exc_info:
            await service_auth_client.get_service_token()

        assert exc_info.value.status_code == 503
        assert "temporarily unavailable" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_service_token_connection_error(self, mock_settings, service_auth_client):
        """Test service token with connection error"""
        with patch.object(httpx.AsyncClient, "post", new=AsyncMock()) as mock_post:
            mock_post.side_effect = httpx.RequestError("Connection failed")

            with pytest.raises(HTTPException) as exc_info:
                await service_auth_client.get_service_token()

            assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_get_service_token_circuit_breaker_integration(
        self, mock_settings, service_auth_client
    ):
        """Test circuit breaker integration with service token"""
        # Simulate multiple failures to open circuit
        with patch.object(httpx.AsyncClient, "post", new=AsyncMock()) as mock_post:
            mock_post.side_effect = httpx.RequestError("Connection failed")

            # First few failures should be allowed
            for i in range(mock_settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD):
                with pytest.raises(HTTPException):
                    await service_auth_client.get_service_token()

            # Circuit should now be open
            assert service_auth_client.circuit_state == CircuitState.OPEN

            # Next call should be rejected immediately
            with pytest.raises(HTTPException) as exc_info:
                await service_auth_client.get_service_token()

            assert "temporarily unavailable" in exc_info.value.detail

    def test_circuit_state_property(self, service_auth_client):
        """Test circuit state property"""
        assert service_auth_client.circuit_state == CircuitState.CLOSED

    def test_reset_circuit(self, service_auth_client):
        """Test manual circuit reset"""
        service_auth_client._circuit_breaker._state = CircuitState.OPEN

        service_auth_client.reset_circuit()

        assert service_auth_client.circuit_state == CircuitState.CLOSED
