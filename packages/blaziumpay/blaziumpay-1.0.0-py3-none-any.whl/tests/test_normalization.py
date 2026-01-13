"""Test payment data normalization"""

import pytest
from blaziumpay import (
    BlaziumPayClient,
    BlaziumConfig,
    BlaziumEnvironment,
    PaymentStatus,
    BlaziumChain,
)


@pytest.fixture
def client():
    """Create a test client"""
    config = BlaziumConfig(
        apiKey="test-api-key",
        environment=BlaziumEnvironment.PRODUCTION
    )
    return BlaziumPayClient(config)


def test_normalize_payment_string_amounts(client):
    """Test payment normalization handles string amounts"""
    payment_data = {
        "id": "payment-123",
        "status": "CONFIRMED",
        "amount": "10.5",  # String amount
        "currency": "USD",
        "checkoutUrl": "https://checkout.example.com",
        "createdAt": "2024-01-01T00:00:00Z",
        "expiresAt": "2024-01-01T01:00:00Z",
        "payAmount": "0.1",  # String payAmount
        "payCurrency": "TON",
        "networkFee": "0.01"
    }
    
    payment = client._normalize_payment(payment_data)
    
    assert isinstance(payment.amount, float)
    assert payment.amount == 10.5
    assert isinstance(payment.payAmount, float)
    assert payment.payAmount == 0.1
    assert isinstance(payment.networkFee, float)
    assert payment.networkFee == 0.01
    assert payment.payCurrency == BlaziumChain.TON
    assert payment.status == PaymentStatus.CONFIRMED


def test_normalize_payment_numeric_amounts(client):
    """Test payment normalization handles numeric amounts"""
    payment_data = {
        "id": "payment-123",
        "status": "PENDING",
        "amount": 10.5,  # Numeric amount
        "currency": "USD",
        "checkoutUrl": "https://checkout.example.com",
        "createdAt": "2024-01-01T00:00:00Z",
        "expiresAt": "2024-01-01T01:00:00Z",
        "payAmount": 0.1,  # Numeric payAmount
    }
    
    payment = client._normalize_payment(payment_data)
    
    assert isinstance(payment.amount, float)
    assert payment.amount == 10.5
    assert isinstance(payment.payAmount, float)
    assert payment.payAmount == 0.1


def test_normalize_payment_with_partial_payment(client):
    """Test payment normalization with partial payment data"""
    payment_data = {
        "id": "payment-123",
        "status": "PARTIALLY_PAID",
        "amount": "10.0",
        "currency": "USD",
        "checkoutUrl": "https://checkout.example.com",
        "createdAt": "2024-01-01T00:00:00Z",
        "expiresAt": "2024-01-01T01:00:00Z",
        "payAmount": "0.1",
        "metadata": {
            "partial_payment": {
                "amount": "0.05",
                "txHash": "tx-hash-123",
                "detectedAt": "2024-01-01T00:30:00Z",
            }
        }
    }
    
    payment = client._normalize_payment(payment_data)
    
    assert payment.partialPayment is not None
    assert payment.partialPayment.amount == 0.05
    assert payment.partialPayment.txHash == "tx-hash-123"
    assert payment.partialPayment.expectedAmount == 0.1


def test_normalize_payment_optional_fields(client):
    """Test payment normalization handles optional fields"""
    payment_data = {
        "id": "payment-123",
        "status": "PENDING",
        "amount": "10.0",
        "currency": "USD",
        "checkoutUrl": "https://checkout.example.com",
        "createdAt": "2024-01-01T00:00:00Z",
        "expiresAt": "2024-01-01T01:00:00Z",
        # No optional fields
    }
    
    payment = client._normalize_payment(payment_data)
    
    assert payment.description is None
    assert payment.metadata is None
    assert payment.payCurrency is None
    assert payment.payAmount is None
    assert payment.txHash is None
    assert payment.partialPayment is None

