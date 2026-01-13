"""Test client initialization and validation"""

import pytest
from blaziumpay import (
    BlaziumPayClient,
    BlaziumConfig,
    BlaziumEnvironment,
    ValidationError,
)


def test_client_initialization():
    """Test client can be initialized with valid config"""
    config = BlaziumConfig(
        apiKey="test-api-key",
        environment=BlaziumEnvironment.PRODUCTION
    )
    
    client = BlaziumPayClient(config)
    assert client is not None
    assert client.config.apiKey == "test-api-key"


def test_client_missing_api_key():
    """Test client raises error when API key is missing"""
    config = BlaziumConfig(
        apiKey="",
        environment=BlaziumEnvironment.PRODUCTION
    )
    
    with pytest.raises(ValidationError) as exc_info:
        BlaziumPayClient(config)
    
    assert "API Key is required" in str(exc_info.value)


def test_client_invalid_base_url():
    """Test client raises error for invalid base URL"""
    config = BlaziumConfig(
        apiKey="test-key",
        baseUrl="invalid-url",
        environment=BlaziumEnvironment.PRODUCTION
    )
    
    with pytest.raises(ValidationError) as exc_info:
        BlaziumPayClient(config)
    
    assert "Invalid baseUrl" in str(exc_info.value)


def test_client_with_webhook_secret():
    """Test client can be initialized with webhook secret"""
    config = BlaziumConfig(
        apiKey="test-api-key",
        webhookSecret="test-webhook-secret",
        environment=BlaziumEnvironment.PRODUCTION
    )
    
    client = BlaziumPayClient(config)
    assert client.config.webhookSecret == "test-webhook-secret"


def test_client_default_values():
    """Test client uses default values correctly"""
    config = BlaziumConfig(apiKey="test-key")
    
    client = BlaziumPayClient(config)
    assert client.config.baseUrl == "https://api.blaziumpay.com/api/v1"
    assert client.config.timeout == 15000
    assert client.config.environment == BlaziumEnvironment.PRODUCTION

