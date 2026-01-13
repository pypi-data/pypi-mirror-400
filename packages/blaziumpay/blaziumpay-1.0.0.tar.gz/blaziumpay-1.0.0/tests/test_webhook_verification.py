"""Test webhook signature verification"""

import pytest
import hmac
import hashlib
import json
from blaziumpay import (
    BlaziumPayClient,
    BlaziumConfig,
    BlaziumEnvironment,
    InvalidSignatureError,
    ValidationError,
    BlaziumError,
    WebhookEventType,
)


def test_webhook_verification_valid():
    """Test valid webhook signature verification"""
    secret = "test-webhook-secret"
    config = BlaziumConfig(
        apiKey="test-key",
        webhookSecret=secret,
        environment=BlaziumEnvironment.PRODUCTION
    )
    client = BlaziumPayClient(config)
    
    payload = json.dumps({"test": "data"})
    signature = hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    # Test with sha256= prefix
    assert client.verify_webhook_signature(payload, f"sha256={signature}") is True
    
    # Test without prefix
    assert client.verify_webhook_signature(payload, signature) is True


def test_webhook_verification_invalid():
    """Test invalid webhook signature verification"""
    config = BlaziumConfig(
        apiKey="test-key",
        webhookSecret="test-secret",
        environment=BlaziumEnvironment.PRODUCTION
    )
    client = BlaziumPayClient(config)
    
    payload = json.dumps({"test": "data"})
    invalid_signature = "invalid-signature"
    
    assert client.verify_webhook_signature(payload, invalid_signature) is False


def test_webhook_verification_missing_secret():
    """Test webhook verification raises error when secret is missing"""
    config = BlaziumConfig(
        apiKey="test-key",
        webhookSecret=None,
        environment=BlaziumEnvironment.PRODUCTION
    )
    client = BlaziumPayClient(config)
    
    with pytest.raises(BlaziumError) as exc_info:
        client.verify_webhook_signature("payload", "signature")
    
    assert "WEBHOOK_SECRET_MISSING" in exc_info.value.code


def test_parse_webhook_valid():
    """Test parsing valid webhook payload"""
    secret = "test-webhook-secret"
    config = BlaziumConfig(
        apiKey="test-key",
        webhookSecret=secret,
        environment=BlaziumEnvironment.PRODUCTION
    )
    client = BlaziumPayClient(config)
    
    webhook_data = {
        "id": "webhook-123",
        "webhook_id": "webhook-123",
        "event": "payment.confirmed",
        "payment_id": "payment-123",
        "payment": {
            "id": "payment-123",
            "status": "CONFIRMED",
            "amount": "10.0",
            "currency": "USD",
            "checkoutUrl": "https://checkout.example.com",
            "createdAt": "2024-01-01T00:00:00Z",
            "expiresAt": "2024-01-01T01:00:00Z"
        },
        "timestamp": "2024-01-01T00:00:00Z",
        "createdAt": "2024-01-01T00:00:00Z"
    }
    
    payload = json.dumps(webhook_data)
    signature = hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    webhook = client.parse_webhook(payload, f"sha256={signature}")
    
    assert webhook.id == "webhook-123"
    assert webhook.webhook_id == "webhook-123"
    assert webhook.event == WebhookEventType.PAYMENT_CONFIRMED
    assert webhook.payment_id == "payment-123"
    assert webhook.payment.id == "payment-123"


def test_parse_webhook_invalid_signature():
    """Test parsing webhook with invalid signature"""
    config = BlaziumConfig(
        apiKey="test-key",
        webhookSecret="test-secret",
        environment=BlaziumEnvironment.PRODUCTION
    )
    client = BlaziumPayClient(config)
    
    payload = json.dumps({"test": "data"})
    
    with pytest.raises(InvalidSignatureError):
        client.parse_webhook(payload, "invalid-signature")


def test_parse_webhook_invalid_payload():
    """Test parsing webhook with invalid payload format"""
    secret = "test-webhook-secret"
    config = BlaziumConfig(
        apiKey="test-key",
        webhookSecret=secret,
        environment=BlaziumEnvironment.PRODUCTION
    )
    client = BlaziumPayClient(config)
    
    payload = json.dumps({"invalid": "payload"})
    signature = hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    with pytest.raises(ValidationError) as exc_info:
        client.parse_webhook(payload, f"sha256={signature}")
    
    assert "Invalid webhook payload" in str(exc_info.value)

