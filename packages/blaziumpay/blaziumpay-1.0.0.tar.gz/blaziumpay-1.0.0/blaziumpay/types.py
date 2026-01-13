"""
Type definitions for BlaziumPay SDK
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime


class BlaziumChain(str, Enum):
    """Supported blockchain networks"""
    SOL = "SOL"
    TON = "TON"
    BTC = "BTC"


class BlaziumFiat(str, Enum):
    """Supported fiat currencies"""
    USD = "USD"
    EUR = "EUR"
    TRY = "TRY"


class PaymentStatus(str, Enum):
    """Payment status values"""
    CREATED = "CREATED"
    PENDING = "PENDING"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class BlaziumEnvironment(str, Enum):
    """API environment"""
    PRODUCTION = "production"
    SANDBOX = "sandbox"


class WithdrawalStatus(str, Enum):
    """Withdrawal status values"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class WebhookEventType(str, Enum):
    """Webhook event types"""
    PAYMENT_CREATED = "payment.created"
    PAYMENT_PENDING = "payment.pending"
    PAYMENT_CONFIRMED = "payment.confirmed"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_EXPIRED = "payment.expired"
    PAYMENT_PARTIALLY_PAID = "payment.partially_paid"


@dataclass
class PartialPayment:
    """Partial payment information"""
    amount: float
    txHash: str
    detectedAt: str
    expectedAmount: float


@dataclass
class Payment:
    """Payment object"""
    id: str
    status: PaymentStatus
    amount: float
    currency: str
    checkoutUrl: str
    createdAt: str
    expiresAt: str
    
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    updatedAt: Optional[str] = None
    
    payCurrency: Optional[BlaziumChain] = None
    payAmount: Optional[float] = None
    payAddress: Optional[str] = None
    txHash: Optional[str] = None
    networkFee: Optional[float] = None
    blockHeight: Optional[str] = None
    confirmedAt: Optional[str] = None
    addressIndex: Optional[int] = None
    
    quotedRate: Optional[float] = None
    quoteExpiresAt: Optional[str] = None
    
    # Reward metadata (optional - for developer reference only)
    # Note: BlaziumPay does NOT automatically grant rewards.
    # Developers must implement their own logic in webhook handlers.
    rewardAmount: Optional[float] = None
    rewardCurrency: Optional[str] = None
    rewardData: Optional[Dict[str, Any]] = None
    rewardDelivered: Optional[bool] = None  # Flag from API indicating if developer has marked reward as delivered
    
    partialPayment: Optional[PartialPayment] = None


@dataclass
class CreatePaymentParams:
    """Parameters for creating a payment"""
    amount: float
    currency: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    redirectUrl: Optional[str] = None
    cancelUrl: Optional[str] = None
    expiresIn: Optional[int] = None
    # Reward metadata (optional - for developer reference only)
    # Note: BlaziumPay does NOT automatically grant rewards.
    rewardAmount: Optional[float] = None
    rewardCurrency: Optional[str] = None
    rewardData: Optional[Dict[str, Any]] = None


@dataclass
class CreatePaymentOptions:
    """Options for creating a payment"""
    idempotencyKey: Optional[str] = None


@dataclass
class WebhookPayload:
    """Webhook payload structure"""
    id: str
    webhook_id: str
    event: WebhookEventType
    payment_id: str
    payment: Payment
    timestamp: str
    createdAt: str


@dataclass
class PaymentStats:
    """Payment statistics"""
    total: int
    confirmed: int
    pending: int
    failed: int
    totalVolume: float
    currency: str


@dataclass
class Pagination:
    """Pagination information"""
    page: int
    pageSize: int
    totalPages: int
    totalItems: int


@dataclass
class PaginatedResponse:
    """Paginated response"""
    data: List[Payment]
    pagination: Pagination


@dataclass
class ListPaymentsParams:
    """Parameters for listing payments"""
    status: Optional[PaymentStatus] = None
    currency: Optional[str] = None
    page: Optional[int] = None
    pageSize: Optional[int] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None


@dataclass
class MerchantBalance:
    """Merchant balance information"""
    chain: str
    totalEarned: str
    availableBalance: str
    pendingBalance: str
    totalWithdrawn: str
    holdAmount: str
    settlementPeriodDays: int


@dataclass
class Withdrawal:
    """Withdrawal object"""
    id: str
    status: WithdrawalStatus
    amount: str
    chain: str
    destinationAddress: str
    requestedAt: str
    txHash: Optional[str] = None
    networkFee: Optional[str] = None
    finalAmount: Optional[str] = None
    errorMessage: Optional[str] = None
    completedAt: Optional[str] = None


@dataclass
class WithdrawalRequest:
    """Request for creating a withdrawal"""
    chain: str
    amount: float
    destinationAddress: str


@dataclass
class BlaziumConfig:
    """BlaziumPay client configuration"""
    apiKey: str
    baseUrl: str = "https://api.blaziumpay.com/api/v1"
    timeout: int = 15000
    environment: BlaziumEnvironment = BlaziumEnvironment.PRODUCTION
    webhookSecret: Optional[str] = None

