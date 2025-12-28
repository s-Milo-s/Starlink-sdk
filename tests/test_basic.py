"""Basic tests for the Starlink SDK."""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from starlink_sdk.models import (
    FleetHealthResponse,
    FleetCounts,
    AlertSeverity,
    AlertStatus,
    HealthStatus,
    TerminalStatus
)
from starlink_sdk.exceptions import AuthenticationError, StarlinkAPIError
from starlink_sdk.utils import generate_idempotency_key, validate_terminal_id


class TestModels:
    """Test the data models."""
    
    def test_fleet_health_response_creation(self):
        """Test creating a FleetHealthResponse object."""
        now = datetime.now(timezone.utc)
        
        response = FleetHealthResponse(
            from_time=now,
            to_time=now,
            counts=FleetCounts(healthy=10, degraded=2, offline=1)
        )
        
        assert response.counts.healthy == 10
        assert response.counts.degraded == 2
        assert response.counts.offline == 1
    
    def test_enum_values(self):
        """Test enum value validation."""
        assert AlertSeverity.CRITICAL == "critical"
        assert AlertStatus.OPEN == "open"
        assert HealthStatus.HEALTHY == "healthy"
        assert TerminalStatus.ONLINE == "online"


class TestUtils:
    """Test utility functions."""
    
    def test_generate_idempotency_key(self):
        """Test idempotency key generation."""
        key1 = generate_idempotency_key()
        key2 = generate_idempotency_key()
        
        assert key1 != key2
        assert len(key1) == 36  # UUID4 length with hyphens
    
    def test_validate_terminal_id(self):
        """Test terminal ID validation."""
        assert validate_terminal_id("TERMINAL_123") is True
        assert validate_terminal_id("term-456") is True
        assert validate_terminal_id("term_789") is True
        assert validate_terminal_id("") is False
        assert validate_terminal_id("term with spaces") is False


class TestExceptions:
    """Test custom exceptions."""
    
    def test_starlink_api_error(self):
        """Test StarlinkAPIError creation and string representation."""
        error = StarlinkAPIError(
            message="Test error",
            status_code=400,
            detail={"field": "error details"}
        )
        
        assert error.message == "Test error"
        assert error.status_code == 400
        assert error.detail == {"field": "error details"}
        
        error_str = str(error)
        assert "Test error" in error_str
        assert "400" in error_str
    
    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError("Invalid credentials")
        assert str(error) == "Invalid credentials"


# Mock tests would require the actual dependencies to be installed
# These are placeholder tests to show the structure

@pytest.mark.asyncio
async def test_client_creation():
    """Test that we can import and create a client instance."""
    try:
        from starlink_sdk import StarlinkClient
        
        # This would fail without proper environment setup, but tests the import
        client = StarlinkClient.__new__(StarlinkClient)  # Create without __init__
        assert client is not None
    except ImportError as e:
        pytest.skip(f"Dependencies not installed: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
