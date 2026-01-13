"""
Error classes for BlaziumPay SDK
"""


class BlaziumError(Exception):
    """Base exception for all BlaziumPay errors"""
    
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR", details: dict = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def __str__(self) -> str:
        return f"{self.code}: {self.message}"
    
    def to_dict(self) -> dict:
        """Convert error to dictionary"""
        return {
            "name": self.__class__.__name__,
            "message": self.message,
            "code": self.code,
            "details": self.details,
        }


class AuthenticationError(BlaziumError):
    """Authentication error (401/403)"""
    
    def __init__(self, message: str = "Invalid API Key provided"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class ValidationError(BlaziumError):
    """Validation error (400/422)"""
    
    def __init__(self, message: str, errors: dict = None):
        super().__init__(message, "VALIDATION_ERROR", errors or {})


class NetworkError(BlaziumError):
    """Network request failed"""
    
    def __init__(self, message: str = "Network request failed"):
        super().__init__(message, "NETWORK_ERROR")


class RateLimitError(BlaziumError):
    """Rate limit exceeded (429)"""
    
    def __init__(self, message: str = "Too many requests", retryAfter: int = None):
        super().__init__(message, "RATE_LIMIT_ERROR")
        self.retryAfter = retryAfter


class TimeoutError(BlaziumError):
    """Operation timed out"""
    
    def __init__(self, message: str = "Operation timed out", code: str = "TIMEOUT_ERROR"):
        super().__init__(message, code)


class APIError(BlaziumError):
    """Generic API error"""
    
    def __init__(self, message: str, statusCode: int, code: str = "API_ERROR"):
        super().__init__(message, code)
        self.statusCode = statusCode


class PaymentError(BlaziumError):
    """Payment-specific error"""
    
    def __init__(self, message: str, code: str = "PAYMENT_ERROR", details: dict = None):
        super().__init__(message, code, details)


class PaymentNotFoundError(PaymentError):
    """Payment not found"""
    
    def __init__(self, paymentId: str):
        super().__init__(
            f"Payment with ID {paymentId} not found",
            "PAYMENT_NOT_FOUND",
            {"paymentId": paymentId}
        )


class PaymentExpiredError(PaymentError):
    """Payment expired"""
    
    def __init__(self, paymentId: str):
        super().__init__(
            f"Payment {paymentId} has expired",
            "PAYMENT_EXPIRED",
            {"paymentId": paymentId}
        )


class InsufficientPaymentError(PaymentError):
    """Insufficient payment amount"""
    
    def __init__(self, received: float, expected: float):
        super().__init__(
            f"Insufficient payment: received {received}, expected {expected}",
            "INSUFFICIENT_PAYMENT",
            {"received": received, "expected": expected}
        )


class WebhookError(BlaziumError):
    """Webhook-specific error"""
    
    def __init__(self, message: str, code: str = "WEBHOOK_ERROR", details: dict = None):
        super().__init__(message, code, details)


class InvalidSignatureError(WebhookError):
    """Webhook signature verification failed"""
    
    def __init__(self, message: str = None):
        default_message = "Webhook signature verification failed"
        if message:
            super().__init__(message, "INVALID_SIGNATURE")
        else:
            super().__init__(default_message, "INVALID_SIGNATURE")

