"""Test error classes"""

import pytest
from blaziumpay import (
    BlaziumError,
    AuthenticationError,
    ValidationError,
    NetworkError,
    RateLimitError,
    TimeoutError,
    APIError,
    PaymentError,
    PaymentNotFoundError,
    PaymentExpiredError,
    InsufficientPaymentError,
    WebhookError,
    InvalidSignatureError,
)


def test_blazium_error():
    """Test base BlaziumError"""
    error = BlaziumError("Test error", "TEST_CODE", {"key": "value"})
    
    assert str(error) == "TEST_CODE: Test error"
    assert error.message == "Test error"
    assert error.code == "TEST_CODE"
    assert error.details == {"key": "value"}
    
    error_dict = error.to_dict()
    assert error_dict["message"] == "Test error"
    assert error_dict["code"] == "TEST_CODE"


def test_authentication_error():
    """Test AuthenticationError"""
    error = AuthenticationError("Invalid API key")
    assert error.code == "AUTHENTICATION_ERROR"
    assert error.message == "Invalid API key"


def test_validation_error():
    """Test ValidationError"""
    error = ValidationError("Invalid input", {"field": "error"})
    assert error.code == "VALIDATION_ERROR"
    assert error.details == {"field": "error"}


def test_network_error():
    """Test NetworkError"""
    error = NetworkError("Connection failed")
    assert error.code == "NETWORK_ERROR"
    assert error.message == "Connection failed"


def test_rate_limit_error():
    """Test RateLimitError"""
    error = RateLimitError("Too many requests", retryAfter=60)
    assert error.code == "RATE_LIMIT_ERROR"
    assert error.retryAfter == 60


def test_timeout_error():
    """Test TimeoutError"""
    error = TimeoutError("Request timeout", "CUSTOM_TIMEOUT")
    assert error.code == "CUSTOM_TIMEOUT"
    assert error.message == "Request timeout"


def test_api_error():
    """Test APIError"""
    error = APIError("Server error", 500, "SERVER_ERROR")
    assert error.code == "SERVER_ERROR"
    assert error.statusCode == 500


def test_payment_not_found_error():
    """Test PaymentNotFoundError"""
    error = PaymentNotFoundError("payment-123")
    assert error.code == "PAYMENT_NOT_FOUND"
    assert error.details["paymentId"] == "payment-123"


def test_payment_expired_error():
    """Test PaymentExpiredError"""
    error = PaymentExpiredError("payment-123")
    assert error.code == "PAYMENT_EXPIRED"
    assert error.details["paymentId"] == "payment-123"


def test_insufficient_payment_error():
    """Test InsufficientPaymentError"""
    error = InsufficientPaymentError(5.0, 10.0)
    assert error.code == "INSUFFICIENT_PAYMENT"
    assert error.details["received"] == 5.0
    assert error.details["expected"] == 10.0


def test_invalid_signature_error():
    """Test InvalidSignatureError"""
    error = InvalidSignatureError()
    assert error.code == "INVALID_SIGNATURE"
    assert "signature" in error.message.lower()

