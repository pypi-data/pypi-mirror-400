"""Test helper methods"""

import pytest
from blaziumpay import (
    BlaziumPayClient,
    BlaziumConfig,
    BlaziumEnvironment,
    Payment,
    PaymentStatus,
)


@pytest.fixture
def client():
    """Create a test client"""
    config = BlaziumConfig(
        apiKey="test-api-key",
        environment=BlaziumEnvironment.PRODUCTION
    )
    return BlaziumPayClient(config)


def test_is_final():
    """Test is_final helper method"""
    client = BlaziumPayClient(
        BlaziumConfig(apiKey="test-key")
    )
    
    # Final statuses
    confirmed_payment = Payment(
        id="test",
        status=PaymentStatus.CONFIRMED,
        amount=10.0,
        currency="USD",
        checkoutUrl="https://example.com",
        createdAt="2024-01-01T00:00:00Z",
        expiresAt="2024-01-01T01:00:00Z"
    )
    assert client.is_final(confirmed_payment) is True
    
    failed_payment = Payment(
        id="test",
        status=PaymentStatus.FAILED,
        amount=10.0,
        currency="USD",
        checkoutUrl="https://example.com",
        createdAt="2024-01-01T00:00:00Z",
        expiresAt="2024-01-01T01:00:00Z"
    )
    assert client.is_final(failed_payment) is True
    
    # Non-final status
    pending_payment = Payment(
        id="test",
        status=PaymentStatus.PENDING,
        amount=10.0,
        currency="USD",
        checkoutUrl="https://example.com",
        createdAt="2024-01-01T00:00:00Z",
        expiresAt="2024-01-01T01:00:00Z"
    )
    assert client.is_final(pending_payment) is False


def test_is_paid():
    """Test is_paid helper method"""
    client = BlaziumPayClient(
        BlaziumConfig(apiKey="test-key")
    )
    
    # Confirmed payment
    confirmed_payment = Payment(
        id="test",
        status=PaymentStatus.CONFIRMED,
        amount=10.0,
        currency="USD",
        checkoutUrl="https://example.com",
        createdAt="2024-01-01T00:00:00Z",
        expiresAt="2024-01-01T01:00:00Z"
    )
    assert client.is_paid(confirmed_payment) is True
    
    # Pending payment
    pending_payment = Payment(
        id="test",
        status=PaymentStatus.PENDING,
        amount=10.0,
        currency="USD",
        checkoutUrl="https://example.com",
        createdAt="2024-01-01T00:00:00Z",
        expiresAt="2024-01-01T01:00:00Z"
    )
    assert client.is_paid(pending_payment) is False

