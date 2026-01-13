"""
Flask webhook server example for BlaziumPay Python SDK
"""

from flask import Flask, request, jsonify
from blaziumpay import (
    BlaziumPayClient,
    BlaziumConfig,
    BlaziumEnvironment,
    WebhookEventType,
)

app = Flask(__name__)

# Initialize client with webhook secret
client = BlaziumPayClient(
    BlaziumConfig(
        apiKey="your-api-key-here",
        webhookSecret="your-webhook-secret-here",
        environment=BlaziumEnvironment.PRODUCTION,
    )
)


@app.route("/webhooks/blazium", methods=["POST"])
def handle_webhook():
    """
    Handle incoming webhook from BlaziumPay
    
    CRITICAL: Use raw request body for signature verification
    """
    try:
        # Get signature from header
        signature = request.headers.get("X-Blazium-Signature")
        if not signature:
            return jsonify({"error": "Missing signature"}), 400
        
        # Get raw body (Flask provides this via request.get_data())
        raw_body = request.get_data(as_text=True)
        if not raw_body:
            return jsonify({"error": "Missing body"}), 400
        
        # Verify and parse webhook
        webhook = client.parse_webhook(raw_body, signature)
        
        print(f"📨 Webhook received: {webhook.event.value} - Payment {webhook.payment_id}")
        
        # Handle different events
        if webhook.event == WebhookEventType.PAYMENT_CONFIRMED:
            handle_payment_confirmed(webhook.payment)
        elif webhook.event == WebhookEventType.PAYMENT_FAILED:
            handle_payment_failed(webhook.payment)
        elif webhook.event == WebhookEventType.PAYMENT_EXPIRED:
            handle_payment_expired(webhook.payment)
        elif webhook.event == WebhookEventType.PAYMENT_CREATED:
            handle_payment_created(webhook.payment)
        else:
            print(f"ℹ️ Unhandled event: {webhook.event.value}")
        
        # Always return 200 to acknowledge receipt
        return jsonify({"received": True}), 200
        
    except Exception as e:
        print(f"❌ Webhook processing error: {e}")
        # Return 500 to trigger retry
        return jsonify({"error": "Processing failed"}), 500


def handle_payment_confirmed(payment):
    """
    Handle payment confirmed event.
    
    IMPORTANT: BlaziumPay does NOT automatically grant rewards or premium features.
    You must implement your own logic here to grant premium access, add currency,
    unlock content, or perform any other actions.
    """
    print(f"✅ Payment confirmed: {payment.id}")
    print(f"   Amount: {payment.payAmount} {payment.payCurrency.value}")
    print(f"   TX Hash: {payment.txHash}")
    
    if not payment.metadata or "userId" not in payment.metadata:
        print("   ⚠️ No userId in metadata, skipping reward delivery")
        return
    
    user_id = payment.metadata["userId"]
    
    # YOUR CUSTOM LOGIC HERE - You decide what happens:
    
    # Example 1: Grant premium features
    if payment.rewardCurrency == "premium":
        print(f"   Granting premium access to user: {user_id}")
        # database.users.update(user_id, {"is_premium": True, "premium_expires_at": ...})
        # send_welcome_email(user_id)
        # unlock_premium_features(user_id)
    
    # Example 2: Add in-game currency
    elif payment.rewardCurrency == "coins":
        print(f"   Adding {payment.rewardAmount} coins to user: {user_id}")
        # database.users.increment_coins(user_id, payment.rewardAmount)
    
    # Example 3: Unlock specific content based on metadata
    elif payment.metadata.get("plan") == "premium":
        print(f"   Unlocking premium plan for user: {user_id}")
        # unlock_premium_features(user_id)
        # grant_premium_access(user_id)
    
    # You have full control - implement whatever logic you need!
    print(f"   ✓ Reward logic executed for user: {user_id}")


def handle_payment_failed(payment):
    """Handle payment failed event"""
    print(f"❌ Payment failed: {payment.id}")
    # TODO: Handle failed payment (notify user, etc.)


def handle_payment_expired(payment):
    """Handle payment expired event"""
    print(f"⏰ Payment expired: {payment.id}")
    # TODO: Handle expired payment


def handle_payment_created(payment):
    """Handle payment created event"""
    print(f"🆕 Payment created: {payment.id}")
    # TODO: Handle payment creation (log, notify, etc.)


if __name__ == "__main__":
    # Run on port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)

