# BlaziumPay Python SDK

Official Python SDK for BlaziumPay - Production-ready crypto payment infrastructure for TON, Solana, and Bitcoin.

## Installation

```bash
pip install blaziumpay
```

## Quick Start

```python
from blaziumpay import BlaziumPayClient, BlaziumConfig, BlaziumEnvironment

# Initialize client
config = BlaziumConfig(
    apiKey="your-api-key",
    environment=BlaziumEnvironment.PRODUCTION,
    webhookSecret="your-webhook-secret"  # Optional, for webhook verification
)

client = BlaziumPayClient(config)

# Create a payment
from blaziumpay import CreatePaymentParams

payment = client.create_payment(
    CreatePaymentParams(
        amount=10.00,
        currency="USD",
        description="Premium subscription",
        metadata={"userId": "12345"},
        rewardAmount=1,  # Optional metadata: 1 premium subscription
        rewardCurrency="premium"  # Optional metadata: Premium access
    )
)

print(f"Payment created: {payment.checkoutUrl}")

# Wait for payment confirmation
confirmed_payment = client.wait_for_payment(payment.id)
print(f"Payment confirmed: {confirmed_payment.txHash}")

# Note: You must implement your own webhook handler to grant
# premium features when payment is confirmed. See Webhook Handling section.
```

## Webhook Handling

**Important:** BlaziumPay does NOT automatically grant rewards or premium features. You must implement your own logic 
in webhook handlers to grant rewards, unlock features, or perform any other actions when a payment is confirmed.

**Webhook Verification:** Only verified webhooks receive events from BlaziumPay. You must verify your webhook endpoint 
in the dashboard before it will receive any events. Unverified webhooks will not receive any webhook events.

```python
from flask import Flask, request
from blaziumpay import BlaziumPayClient, BlaziumConfig, WebhookEventType

app = Flask(__name__)

client = BlaziumPayClient(
    BlaziumConfig(
        apiKey="your-api-key",
        webhookSecret="your-webhook-secret"  # Required for webhook verification
    )
)

@app.route("/webhooks/blazium", methods=["POST"])
def handle_webhook():
    signature = request.headers.get("X-Blazium-Signature")
    raw_body = request.get_data(as_text=True)
    
    # Verify and parse webhook
    # Note: If webhookSecret is not configured, this will raise a ValidationError
    # with a helpful message explaining that webhooks must be verified first
    webhook = client.parse_webhook(raw_body, signature)
    
    if webhook.event == WebhookEventType.PAYMENT_CONFIRMED:
        payment = webhook.payment
        user_id = payment.metadata["userId"]
        
        # YOUR CUSTOM LOGIC HERE - You decide what happens:
        
        # Example: Grant premium features
        if payment.rewardCurrency == "premium":
            database.users.update(user_id, {"is_premium": True})
        
        # Example: Add in-game currency
        if payment.rewardCurrency == "coins":
            database.users.increment_coins(user_id, payment.rewardAmount)
        
        # You have full control - implement whatever logic you need!
    
    return {"received": True}, 200
```

**Webhook Verification Process:**
1. Create a webhook endpoint in the dashboard
2. Verify the endpoint ownership (BlaziumPay will send a challenge token)
3. Save the webhook secret securely (shown only once after verification)
4. Configure the secret in your SDK client
5. Only verified webhooks receive events - unverified webhooks are ignored by BlaziumPay

## API Reference

### Client Methods

#### `create_payment(params, options=None)`

Create a new payment. The `rewardAmount` and `rewardCurrency` fields are optional metadata for your reference. 
BlaziumPay does not automatically grant rewards - you must implement your own logic in webhook handlers.

```python
payment = client.create_payment(
    CreatePaymentParams(
        amount=10.00,
        currency="USD",
        description="Product purchase",
        redirectUrl="https://example.com/success",
        cancelUrl="https://example.com/cancel",
        expiresIn=3600,  # 1 hour
        rewardAmount=1,  # Optional metadata: 1 premium subscription
        rewardCurrency="premium",  # Optional metadata: Premium access
        metadata={"orderId": "123", "userId": "user_456"}
    ),
    CreatePaymentOptions(idempotencyKey="unique-key-123")
)

# Note: rewardAmount is stored as metadata, but you must implement
# your own webhook handler to grant rewards when payment is confirmed
```

#### `get_payment(paymentId)`

Get payment details by ID.

```python
payment = client.get_payment("payment-id-123")
```

#### `list_payments(params=None)`

List payments with optional filters.

```python
from blaziumpay import ListPaymentsParams, PaymentStatus

response = client.list_payments(
    ListPaymentsParams(
        status=PaymentStatus.CONFIRMED,
        currency="USD",
        page=1,
        pageSize=20
    )
)

for payment in response.data:
    print(f"{payment.id}: {payment.amount} {payment.currency}")
```

#### `cancel_payment(paymentId)`

Cancel a pending payment.

```python
payment = client.cancel_payment("payment-id-123")
```

#### `get_stats()`

Get payment statistics.

```python
stats = client.get_stats()
print(f"Total: {stats.total}, Confirmed: {stats.confirmed}")
```

#### `get_balance(chain)`

Get merchant balance for a specific chain.

```python
balance = client.get_balance("TON")
print(f"Available: {balance.availableBalance} TON")
```

#### `request_withdrawal(request)`

Request a withdrawal.

```python
from blaziumpay import WithdrawalRequest

withdrawal = client.request_withdrawal(
    WithdrawalRequest(
        chain="TON",
        amount=10.5,
        destinationAddress="UQD4f0TZeNio8vgobNhnB9xa1bXptEKgr2Kaxi8zu1JIfzEJ"
    )
)
```

#### `list_withdrawals()`

List withdrawal history.

```python
withdrawals = client.list_withdrawals()
for w in withdrawals:
    print(f"{w.id}: {w.amount} {w.chain}")
```

#### `wait_for_payment(paymentId, timeoutMs=300000, pollIntervalMs=3000)`

Wait for a payment to be confirmed (long polling helper).

```python
# Wait up to 5 minutes, polling every 3 seconds
payment = client.wait_for_payment("payment-id-123")
```

#### `verify_webhook_signature(payload, signature)`

Verify webhook signature.

```python
is_valid = client.verify_webhook_signature(raw_body, signature)
```

#### `parse_webhook(rawPayload, signature)`

Parse and verify webhook payload.

```python
webhook = client.parse_webhook(raw_body, signature)
```

#### Utility Methods

```python
client.is_paid(payment)              # True if CONFIRMED
client.is_partially_paid(payment)     # True if underpaid
client.is_expired(payment)            # True if expired
client.is_final(payment)              # True if no more updates
client.get_payment_progress(payment)  # % of amount paid (0-100)
client.format_amount(1.5, 'TON')      # "1.5000 TON"
```

## Error Handling

The SDK provides specific error classes for different scenarios:

```python
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
)

try:
    payment = client.create_payment(...)
except ValidationError as e:
    print(f"Validation failed: {e.message}")
    print(f"Details: {e.details}")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retryAfter} seconds")
except NetworkError:
    print("Network error occurred")
```

## Type Hints

The SDK is fully typed with Python type hints:

```python
from blaziumpay import Payment, PaymentStatus, BlaziumChain

def process_payment(payment: Payment) -> bool:
    if payment.status == PaymentStatus.CONFIRMED:
        return True
    return False
```

## Security Best Practices

1. **Never trust frontend signals** - Always verify payments server-side
2. **Verify webhook signatures** - Use `verify_webhook_signature()` - CRITICAL for security
3. **Use idempotency keys** - Prevent duplicate payments
4. **Implement your own reward logic** - BlaziumPay does NOT automatically grant rewards. You must implement webhook handlers to grant premium features, add currency, or perform other actions
5. **Use rewardAmount as metadata** - Store what you promise users, but implement your own logic to grant it
6. **Store API keys securely** - Use environment variables
7. **Implement timeout handling** - Network issues happen
8. **Log webhook failures** - Monitor for issues
9. **Make webhook handlers idempotent** - Handle duplicate webhook deliveries gracefully

## Requirements

- Python 3.8+
- `requests` library

## License

MIT

## Support

- Documentation: https://docs.blaziumpay.com
- Issues: https://github.com/blaziumpay/python-sdk/issues
- Email: support@blaziumpay.com

