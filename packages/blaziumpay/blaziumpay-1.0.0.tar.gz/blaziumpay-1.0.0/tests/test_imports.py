"""Test that all imports work correctly"""

import pytest


def test_main_imports():
    """Test main package imports"""
    from blaziumpay import (
        BlaziumPayClient,
        BlaziumConfig,
        BlaziumChain,
        BlaziumFiat,
        PaymentStatus,
        BlaziumEnvironment,
        WithdrawalStatus,
        WebhookEventType,
        Payment,
        CreatePaymentParams,
        CreatePaymentOptions,
        WebhookPayload,
        PaymentStats,
        PaginatedResponse,
        ListPaymentsParams,
        MerchantBalance,
        Withdrawal,
        WithdrawalRequest,
    )
    assert BlaziumPayClient is not None
    assert BlaziumConfig is not None


def test_error_imports():
    """Test error class imports"""
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
    assert BlaziumError is not None
    assert AuthenticationError is not None


def test_version():
    """Test version is accessible"""
    import blaziumpay
    assert hasattr(blaziumpay, "__version__")
    assert blaziumpay.__version__ == "1.0.0"

