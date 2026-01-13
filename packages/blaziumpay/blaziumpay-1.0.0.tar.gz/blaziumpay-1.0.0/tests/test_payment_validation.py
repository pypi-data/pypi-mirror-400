"""Test payment creation validation"""

import pytest
from blaziumpay import (
    BlaziumPayClient,
    BlaziumConfig,
    BlaziumEnvironment,
    CreatePaymentParams,
    ValidationError,
)


@pytest.fixture
def client():
    """Create a test client"""
    config = BlaziumConfig(
        apiKey="test-api-key",
        environment=BlaziumEnvironment.PRODUCTION
    )
    return BlaziumPayClient(config)


def test_create_payment_validation_amount_positive(client):
    """Test payment amount must be positive"""
    with pytest.raises(ValidationError) as exc_info:
        client.create_payment(
            CreatePaymentParams(amount=-10.0, currency="USD")
        )
    assert "Amount must be positive" in str(exc_info.value)


def test_create_payment_validation_amount_zero(client):
    """Test payment amount cannot be zero"""
    with pytest.raises(ValidationError) as exc_info:
        client.create_payment(
            CreatePaymentParams(amount=0, currency="USD")
        )
    assert "Amount must be positive" in str(exc_info.value)


def test_create_payment_validation_currency_format(client):
    """Test currency format validation"""
    with pytest.raises(ValidationError) as exc_info:
        client.create_payment(
            CreatePaymentParams(amount=10.0, currency="U")
        )
    assert "Invalid currency" in str(exc_info.value)


def test_create_payment_validation_expires_in_range(client):
    """Test expiresIn must be in valid range"""
    with pytest.raises(ValidationError) as exc_info:
        client.create_payment(
            CreatePaymentParams(
                amount=10.0,
                currency="USD",
                expiresIn=30  # Too short
            )
        )
    assert "expiresIn must be between 60 and 86400" in str(exc_info.value)
    
    with pytest.raises(ValidationError) as exc_info:
        client.create_payment(
            CreatePaymentParams(
                amount=10.0,
                currency="USD",
                expiresIn=100000  # Too long
            )
        )
    assert "expiresIn must be between 60 and 86400" in str(exc_info.value)


def test_create_payment_validation_description_length(client):
    """Test description length validation"""
    long_description = "x" * 501  # 501 characters
    
    with pytest.raises(ValidationError) as exc_info:
        client.create_payment(
            CreatePaymentParams(
                amount=10.0,
                currency="USD",
                description=long_description
            )
        )
    assert "Description must be 500 characters" in str(exc_info.value)


def test_get_payment_validation_missing_id(client):
    """Test get_payment requires payment ID"""
    with pytest.raises(ValidationError) as exc_info:
        client.get_payment("")
    assert "Payment ID is required" in str(exc_info.value)


def test_cancel_payment_validation_missing_id(client):
    """Test cancel_payment requires payment ID"""
    with pytest.raises(ValidationError) as exc_info:
        client.cancel_payment("")
    assert "Payment ID is required" in str(exc_info.value)


def test_get_balance_validation_missing_chain(client):
    """Test get_balance requires chain"""
    with pytest.raises(ValidationError) as exc_info:
        client.get_balance("")
    assert "Chain is required" in str(exc_info.value)


def test_request_withdrawal_validation(client):
    """Test withdrawal request validation"""
    from blaziumpay import WithdrawalRequest
    
    # Missing chain
    with pytest.raises(ValidationError) as exc_info:
        client.request_withdrawal(
            WithdrawalRequest(chain="", amount=10.0, destinationAddress="address")
        )
    assert "Chain is required" in str(exc_info.value)
    
    # Invalid amount
    with pytest.raises(ValidationError) as exc_info:
        client.request_withdrawal(
            WithdrawalRequest(chain="TON", amount=0, destinationAddress="address")
        )
    assert "Amount must be positive" in str(exc_info.value)
    
    # Missing destination
    with pytest.raises(ValidationError) as exc_info:
        client.request_withdrawal(
            WithdrawalRequest(chain="TON", amount=10.0, destinationAddress="")
        )
    assert "Destination address is required" in str(exc_info.value)


def test_get_withdrawal_validation_missing_id(client):
    """Test get_withdrawal requires withdrawal ID"""
    with pytest.raises(ValidationError) as exc_info:
        client.get_withdrawal("")
    assert "Withdrawal ID is required" in str(exc_info.value)

