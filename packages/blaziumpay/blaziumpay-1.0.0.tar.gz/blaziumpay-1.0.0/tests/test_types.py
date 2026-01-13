"""Test type definitions and enums"""

import pytest
from blaziumpay import (
    BlaziumChain,
    BlaziumFiat,
    PaymentStatus,
    BlaziumEnvironment,
    WithdrawalStatus,
    WebhookEventType,
    Payment,
    CreatePaymentParams,
    BlaziumConfig,
    WithdrawalRequest,
)


def test_enums():
    """Test enum values"""
    assert BlaziumChain.SOL.value == "SOL"
    assert BlaziumChain.TON.value == "TON"
    assert BlaziumChain.BTC.value == "BTC"
    
    assert PaymentStatus.PENDING.value == "PENDING"
    assert PaymentStatus.CONFIRMED.value == "CONFIRMED"
    
    assert BlaziumEnvironment.PRODUCTION.value == "production"
    assert BlaziumEnvironment.SANDBOX.value == "sandbox"


def test_blazium_config():
    """Test BlaziumConfig dataclass"""
    config = BlaziumConfig(
        apiKey="test-key",
        baseUrl="https://api.example.com/api/v1",
        timeout=20000,
        environment=BlaziumEnvironment.PRODUCTION,
        webhookSecret="test-secret"
    )
    
    assert config.apiKey == "test-key"
    assert config.baseUrl == "https://api.example.com/api/v1"
    assert config.timeout == 20000
    assert config.environment == BlaziumEnvironment.PRODUCTION
    assert config.webhookSecret == "test-secret"


def test_create_payment_params():
    """Test CreatePaymentParams dataclass"""
    params = CreatePaymentParams(
        amount=10.0,
        currency="USD",
        description="Test payment",
        metadata={"key": "value"}
    )
    
    assert params.amount == 10.0
    assert params.currency == "USD"
    assert params.description == "Test payment"
    assert params.metadata == {"key": "value"}


def test_payment_dataclass():
    """Test Payment dataclass"""
    payment = Payment(
        id="test-id",
        status=PaymentStatus.PENDING,
        amount=10.0,
        currency="USD",
        checkoutUrl="https://checkout.example.com",
        createdAt="2024-01-01T00:00:00Z",
        expiresAt="2024-01-01T01:00:00Z"
    )
    
    assert payment.id == "test-id"
    assert payment.status == PaymentStatus.PENDING
    assert payment.amount == 10.0
    assert payment.currency == "USD"


def test_withdrawal_request():
    """Test WithdrawalRequest dataclass"""
    request = WithdrawalRequest(
        chain="TON",
        amount=10.5,
        destinationAddress="UQD4f0TZeNio8vgobNhnB9xa1bXptEKgr2Kaxi8zu1JIfzEJ"
    )
    
    assert request.chain == "TON"
    assert request.amount == 10.5
    assert request.destinationAddress == "UQD4f0TZeNio8vgobNhnB9xa1bXptEKgr2Kaxi8zu1JIfzEJ"

