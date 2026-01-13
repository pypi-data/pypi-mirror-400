"""
Basic usage example for BlaziumPay Python SDK
"""

from blaziumpay import (
    BlaziumPayClient,
    BlaziumConfig,
    BlaziumEnvironment,
    CreatePaymentParams,
    PaymentStatus,
)

# Initialize client
config = BlaziumConfig(
    apiKey="your-api-key-here",
    environment=BlaziumEnvironment.PRODUCTION,
)

client = BlaziumPayClient(config)

# Create a payment
payment = client.create_payment(
    CreatePaymentParams(
        amount=10.00,
        currency="USD",
        description="Premium subscription",
        metadata={"userId": "12345", "plan": "premium"},
        redirectUrl="https://example.com/success",
        cancelUrl="https://example.com/cancel",
        expiresIn=3600,  # 1 hour
    )
)

print(f"Payment created: {payment.id}")
print(f"Checkout URL: {payment.checkoutUrl}")
print(f"Status: {payment.status.value}")

# Wait for payment confirmation
try:
    confirmed_payment = client.wait_for_payment(payment.id, timeoutMs=300000)
    print(f"Payment confirmed!")
    print(f"Transaction Hash: {confirmed_payment.txHash}")
    print(f"Amount Paid: {confirmed_payment.payAmount} {confirmed_payment.payCurrency.value}")
except Exception as e:
    print(f"Error waiting for payment: {e}")

# Get payment details
payment = client.get_payment(payment.id)
print(f"Payment status: {payment.status.value}")

# List payments
response = client.list_payments()
print(f"Total payments: {response.pagination.totalItems}")

# Get statistics
stats = client.get_stats()
print(f"Total: {stats.total}, Confirmed: {stats.confirmed}, Pending: {stats.pending}")

# Get balance
balance = client.get_balance("TON")
print(f"Available Balance: {balance.availableBalance} TON")

