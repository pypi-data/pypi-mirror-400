"""Test unverified webhook scenarios"""

import pytest
import json
import hmac
import hashlib
from blaziumpay import (
    BlaziumPayClient,
    BlaziumConfig,
    BlaziumEnvironment,
    ValidationError,
    InvalidSignatureError,
)


def test_verify_webhook_signature_without_secret():
    """Test that verifyWebhookSignature throws error when webhookSecret is not configured"""
    print("\n🧪 Testing verifyWebhookSignature without webhookSecret...")
    
    config = BlaziumConfig(
        apiKey="test-key",
        # webhookSecret is NOT set - simulating unverified webhook
        environment=BlaziumEnvironment.PRODUCTION
    )
    client = BlaziumPayClient(config)
    
    payload = json.dumps({"test": "data"})
    signature = "some-signature"
    
    with pytest.raises(ValidationError) as exc_info:
        client.verify_webhook_signature(payload, signature)
    
    error_message = str(exc_info.value.message)
    # In Python SDK, the specific error code is in details dict
    error_code = exc_info.value.details.get("code", "") if hasattr(exc_info.value, "details") and exc_info.value.details else ""
    assert "WEBHOOK_SECRET_MISSING" in error_code or "WEBHOOK_SECRET_MISSING" in str(exc_info.value.details) if hasattr(exc_info.value, "details") else False
    assert "not configured" in error_message.lower()
    assert "verified" in error_message.lower() or "verify" in error_message.lower()
    assert "dashboard" in error_message.lower()
    
    print("✅ Correctly throws ValidationError with helpful message")
    print(f"   Error code: {error_code or exc_info.value.code}")
    print(f"   Error message: {error_message}")


def test_parse_webhook_without_secret():
    """Test that parseWebhook throws error when webhookSecret is not configured"""
    print("\n🧪 Testing parseWebhook without webhookSecret...")
    
    config = BlaziumConfig(
        apiKey="test-key",
        # webhookSecret is NOT set - simulating unverified webhook
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
    signature = "some-signature"
    
    with pytest.raises(ValidationError) as exc_info:
        client.parse_webhook(payload, signature)
    
    error_message = str(exc_info.value.message)
    # In Python SDK, the specific error code is in details dict
    error_code = exc_info.value.details.get("code", "") if hasattr(exc_info.value, "details") and exc_info.value.details else ""
    assert "WEBHOOK_SECRET_MISSING" in error_code or "WEBHOOK_SECRET_MISSING" in str(exc_info.value.details) if hasattr(exc_info.value, "details") else False
    assert "not configured" in error_message.lower()
    assert "verified" in error_message.lower() or "verify" in error_message.lower()
    
    print("✅ Correctly throws ValidationError when trying to parse without secret")
    print(f"   Error code: {error_code or exc_info.value.code}")
    print(f"   Error message: {error_message}")


def test_parse_webhook_with_invalid_signature():
    """Test that parseWebhook throws InvalidSignatureError with helpful message for invalid signature"""
    print("\n🧪 Testing parseWebhook with invalid signature...")
    
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
    # Use invalid signature (not matching the secret)
    invalid_signature = "sha256=invalid-signature-that-does-not-match"
    
    with pytest.raises(InvalidSignatureError) as exc_info:
        client.parse_webhook(payload, invalid_signature)
    
    error_message = str(exc_info.value.message)
    assert "INVALID_SIGNATURE" in exc_info.value.code
    # Check that error message mentions unverified webhook
    assert "unverified" in error_message.lower() or "invalid" in error_message.lower()
    
    print("✅ Correctly throws InvalidSignatureError with helpful message")
    print(f"   Error code: {exc_info.value.code}")
    print(f"   Error message: {error_message}")


def test_unverified_webhook_scenario():
    """Complete test scenario: Developer tries to use SDK with unverified webhook"""
    print("\n🧪 Testing complete unverified webhook scenario...")
    
    # Simulate: Developer creates webhook but hasn't verified it yet
    # They try to use SDK to verify incoming webhooks (which won't come)
    config = BlaziumConfig(
        apiKey="test-key",
        # No webhookSecret - webhook is unverified
        environment=BlaziumEnvironment.PRODUCTION
    )
    client = BlaziumPayClient(config)
    
    # Simulate receiving a webhook (which shouldn't happen for unverified webhooks)
    # But if developer tries to verify it anyway...
    payload = json.dumps({
        "id": "webhook-123",
        "event": "payment.confirmed",
        "payment_id": "payment-123"
    })
    signature = "sha256=some-signature"
    
    # Should fail with clear error message
    with pytest.raises(ValidationError) as exc_info:
        client.verify_webhook_signature(payload, signature)
    
    error = exc_info.value
    # In Python SDK, the specific error code is in details dict
    error_code = error.details.get("code", "") if hasattr(error, "details") and error.details else ""
    assert "WEBHOOK_SECRET_MISSING" in error_code or "WEBHOOK_SECRET_MISSING" in str(error.details) if hasattr(error, "details") else False
    
    # Check error message contains helpful information
    error_msg = str(error.message).lower()
    assert "not configured" in error_msg
    assert "verified" in error_msg or "verify" in error_msg
    assert "dashboard" in error_msg
    assert "only verified webhooks" in error_msg or "verified webhooks" in error_msg
    
    print("✅ SDK correctly prevents use with unverified webhook")
    print(f"   Error: {error_code or error.code}")
    print(f"   Message: {error.message}")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Unverified Webhook Scenarios")
    print("=" * 60)
    
    test_verify_webhook_signature_without_secret()
    test_parse_webhook_without_secret()
    test_parse_webhook_with_invalid_signature()
    test_unverified_webhook_scenario()
    
    print("\n" + "=" * 60)
    print("✅ All unverified webhook tests passed!")
    print("=" * 60)

