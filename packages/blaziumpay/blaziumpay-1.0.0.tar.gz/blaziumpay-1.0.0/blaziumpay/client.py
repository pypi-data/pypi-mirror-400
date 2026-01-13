"""
BlaziumPay Python SDK Client
"""

import json
import time
import hmac
import hashlib
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
try:
    from urllib3.util.retry import Retry
except ImportError:
    from requests.packages.urllib3.util.retry import Retry

from .types import (
    BlaziumConfig,
    BlaziumChain,
    Payment,
    PaymentStatus,
    CreatePaymentParams,
    CreatePaymentOptions,
    WebhookPayload,
    WebhookEventType,
    PaymentStats,
    PaginatedResponse,
    ListPaymentsParams,
    MerchantBalance,
    Withdrawal,
    WithdrawalRequest,
    WithdrawalStatus,
    PartialPayment,
)
from .errors import (
    BlaziumError,
    AuthenticationError,
    ValidationError,
    NetworkError,
    RateLimitError,
    TimeoutError,
    APIError,
)


class BlaziumPayClient:
    """Main client for BlaziumPay API"""
    
    def __init__(self, config: BlaziumConfig):
        """
        Initialize BlaziumPay client
        
        Args:
            config: BlaziumPay configuration
        """
        if not config.apiKey:
            raise ValidationError("API Key is required")
        
        if not config.baseUrl.startswith(("http://", "https://")):
            raise ValidationError("Invalid baseUrl format")
        
        self.config = config
        
        # Create session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "Authorization": f"Bearer {config.apiKey}",
            "Content-Type": "application/json",
            "User-Agent": f"BlaziumPay-Python-SDK/1.0.0 ({config.environment.value})",
            "X-SDK-Version": "1.0.0",
        })
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to API
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            data: Request body
            headers: Additional headers
            
        Returns:
            Response data as dictionary
            
        Raises:
            Various BlaziumError subclasses on failure
        """
        url = f"{self.config.baseUrl.rstrip('/')}/{endpoint.lstrip('/')}"
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=request_headers,
                timeout=self.config.timeout / 1000,  # Convert ms to seconds
            )
            
            # Handle response
            if response.status_code == 401 or response.status_code == 403:
                raise AuthenticationError(
                    response.json().get("error", "Authentication failed")
                )
            elif response.status_code == 400 or response.status_code == 422:
                error_data = response.json()
                raise ValidationError(
                    error_data.get("error", "Validation failed"),
                    error_data.get("details") or error_data.get("issues", {}),
                )
            elif response.status_code == 404:
                error_data = response.json()
                raise APIError(
                    error_data.get("error", "Not found"),
                    response.status_code,
                    "NOT_FOUND",
                )
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                retry_after_int = int(retry_after) if retry_after else None
                raise RateLimitError(
                    response.json().get("error", "Too many requests"),
                    retry_after_int,
                )
            elif response.status_code >= 500:
                error_data = response.json()
                raise APIError(
                    error_data.get("error", "Server error"),
                    response.status_code,
                    "SERVER_ERROR",
                )
            elif not response.ok:
                error_data = response.json()
                raise APIError(
                    error_data.get("error", f"HTTP {response.status_code}"),
                    response.status_code,
                )
            
            return response.json()
            
        except requests.exceptions.Timeout:
            raise TimeoutError("Request timeout")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}")
        except (AuthenticationError, ValidationError, RateLimitError, APIError):
            raise
        except Exception as e:
            if isinstance(e, BlaziumError):
                raise
            raise BlaziumError(f"Unexpected error: {str(e)}")
    
    def create_payment(
        self,
        params: CreatePaymentParams,
        options: Optional[CreatePaymentOptions] = None,
    ) -> Payment:
        """
        Create a new payment.
        
        Note: rewardAmount and rewardCurrency are optional metadata fields for developer reference.
        BlaziumPay does NOT automatically grant rewards - developers must implement their own
        logic in webhook handlers to grant premium features, add currency, or perform other actions.
        
        Args:
            params: Payment creation parameters
            options: Optional payment creation options (e.g., idempotency key)
            
        Returns:
            Created Payment object
        """
        # Validate amount
        if params.amount <= 0:
            raise ValidationError("Amount must be positive")
        
        # Validate currency
        if not params.currency or len(params.currency) < 2 or len(params.currency) > 5:
            raise ValidationError("Invalid currency format")
        
        # Validate expiresIn if provided
        if params.expiresIn is not None:
            if params.expiresIn < 60 or params.expiresIn > 86400:
                raise ValidationError("expiresIn must be between 60 and 86400 seconds")
        
        # Prepare request data
        data = {
            "amount": params.amount,
            "currency": params.currency.upper(),
        }
        
        if params.description:
            if len(params.description) > 500:
                raise ValidationError("Description must be 500 characters or less")
            data["description"] = params.description
        
        if params.metadata:
            data["metadata"] = params.metadata
        
        if params.redirectUrl:
            data["redirectUrl"] = params.redirectUrl
        
        if params.cancelUrl:
            data["cancelUrl"] = params.cancelUrl
        
        if params.expiresIn:
            data["expiresIn"] = params.expiresIn
        
        if params.rewardAmount:
            data["rewardAmount"] = params.rewardAmount
        
        if params.rewardCurrency:
            data["rewardCurrency"] = params.rewardCurrency
        
        if params.rewardData:
            data["rewardData"] = params.rewardData
        
        # Add idempotency key if provided
        headers = {}
        if options and options.idempotencyKey:
            headers["Idempotency-Key"] = options.idempotencyKey
        
        response_data = self._request("POST", "/payments", data=data, headers=headers)
        return self._normalize_payment(response_data)
    
    def get_payment(self, paymentId: str) -> Payment:
        """
        Get payment details
        
        Args:
            paymentId: Payment ID
            
        Returns:
            Payment object
        """
        if not paymentId:
            raise ValidationError("Payment ID is required")
        
        response_data = self._request("GET", f"/payments/{paymentId}")
        return self._normalize_payment(response_data)
    
    def list_payments(self, params: Optional[ListPaymentsParams] = None) -> PaginatedResponse:
        """
        List payments with filters
        
        Args:
            params: Optional filter parameters
            
        Returns:
            Paginated response with payment list
        """
        query_params = {}
        
        if params:
            if params.status:
                query_params["status"] = params.status.value
            if params.currency:
                query_params["currency"] = params.currency
            if params.page:
                query_params["page"] = params.page
            if params.pageSize:
                query_params["pageSize"] = params.pageSize
            if params.startDate:
                query_params["startDate"] = params.startDate
            if params.endDate:
                query_params["endDate"] = params.endDate
        
        response_data = self._request("GET", "/payments", params=query_params)
        
        return PaginatedResponse(
            data=[self._normalize_payment(p) for p in response_data["data"]],
            pagination=response_data["pagination"],
        )
    
    def cancel_payment(self, paymentId: str) -> Payment:
        """
        Cancel a payment
        
        Args:
            paymentId: Payment ID
            
        Returns:
            Updated Payment object
        """
        if not paymentId:
            raise ValidationError("Payment ID is required")
        
        response_data = self._request("POST", f"/payments/{paymentId}/cancel")
        return self._normalize_payment(response_data)
    
    def get_stats(self) -> PaymentStats:
        """
        Get payment statistics
        
        Returns:
            PaymentStats object
        """
        response_data = self._request("GET", "/payments/stats")
        return PaymentStats(**response_data)
    
    def get_balance(self, chain: str) -> MerchantBalance:
        """
        Get merchant balance for a specific chain
        
        Args:
            chain: Blockchain chain (e.g., "TON", "SOL", "BTC")
            
        Returns:
            MerchantBalance object
        """
        if not chain:
            raise ValidationError("Chain is required")
        
        response_data = self._request("GET", "/balance", params={"chain": chain.upper()})
        return MerchantBalance(**response_data)
    
    def request_withdrawal(self, request: WithdrawalRequest) -> Withdrawal:
        """
        Request a withdrawal
        
        Args:
            request: Withdrawal request parameters
            
        Returns:
            Created Withdrawal object
        """
        if not request.chain:
            raise ValidationError("Chain is required")
        
        if not request.amount or request.amount <= 0:
            raise ValidationError("Amount must be positive")
        
        if not request.destinationAddress:
            raise ValidationError("Destination address is required")
        
        response_data = self._request(
            "POST",
            "/withdrawals",
            data={
                "chain": request.chain.upper(),
                "amount": request.amount,
                "destinationAddress": request.destinationAddress,
            },
        )
        return Withdrawal(**response_data)
    
    def list_withdrawals(self) -> List[Withdrawal]:
        """
        List withdrawal history
        
        Returns:
            List of Withdrawal objects
        """
        response_data = self._request("GET", "/withdrawals")
        return [Withdrawal(**w) for w in response_data["data"]]
    
    def get_withdrawal(self, withdrawalId: str) -> Withdrawal:
        """
        Get specific withdrawal status
        
        Args:
            withdrawalId: Withdrawal ID
            
        Returns:
            Withdrawal object
        """
        if not withdrawalId:
            raise ValidationError("Withdrawal ID is required")
        
        response_data = self._request("GET", f"/withdrawals/{withdrawalId}")
        return Withdrawal(**response_data)
    
    def wait_for_payment(
        self,
        paymentId: str,
        timeoutMs: int = 300000,
        pollIntervalMs: int = 3000,
    ) -> Payment:
        """
        Wait for a payment to be confirmed (Long Polling helper)
        
        Args:
            paymentId: Payment ID
            timeoutMs: Maximum time to wait in milliseconds
            pollIntervalMs: Polling interval in milliseconds
            
        Returns:
            Confirmed Payment object
            
        Raises:
            TimeoutError: If payment doesn't confirm within timeout
            BlaziumError: If payment ends in a non-confirmed state
        """
        start_time = time.time() * 1000  # Convert to milliseconds
        
        while (time.time() * 1000) - start_time < timeoutMs:
            try:
                payment = self.get_payment(paymentId)
                
                if payment.status == PaymentStatus.CONFIRMED:
                    return payment
                
                final_statuses = [
                    PaymentStatus.FAILED,
                    PaymentStatus.EXPIRED,
                    PaymentStatus.CANCELLED,
                ]
                
                if payment.status in final_statuses:
                    raise BlaziumError(
                        f"Payment ended with status: {payment.status.value}",
                        "PAYMENT_NOT_CONFIRMED",
                    )
                
                time.sleep(pollIntervalMs / 1000)  # Convert to seconds
                
            except (NetworkError, TimeoutError):
                # Retry on network/timeout errors
                time.sleep(pollIntervalMs / 1000)
            except BlaziumError as e:
                if e.code == "PAYMENT_NOT_CONFIRMED":
                    raise
                # Retry on other errors
                time.sleep(pollIntervalMs / 1000)
        
        raise TimeoutError(
            f"Payment confirmation timed out after {timeoutMs}ms",
            "PAYMENT_TIMEOUT",
        )
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verify webhook signature
        
        Args:
            payload: Raw JSON string of webhook payload
            signature: Signature from HTTP header 'X-Blazium-Signature'
            
        Returns:
            True if signature is valid, False otherwise
            
        Raises:
            ValidationError: If webhook secret is not configured
            
        Note:
            Only verified webhooks receive events. Unverified webhooks will not receive
            any webhook events from BlaziumPay. You must verify your webhook endpoint in the
            dashboard before it will receive events and require signature verification.
        """
        if not self.config.webhookSecret:
            raise ValidationError(
                "Webhook secret not configured. Set webhookSecret in config. "
                "Note: Webhooks must be verified in the dashboard before they receive events. "
                "Only verified webhooks are sent events by BlaziumPay.",
                {"code": "WEBHOOK_SECRET_MISSING"}
            )
        
        try:
            # Remove 'sha256=' prefix if present
            if signature.startswith("sha256="):
                signature = signature[7:]
            
            # Calculate expected signature
            expected_signature = hmac.new(
                self.config.webhookSecret.encode("utf-8"),
                payload.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            
            # Use constant-time comparison to prevent timing attacks
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception:
            return False
    
    def parse_webhook(self, rawPayload: str, signature: str) -> WebhookPayload:
        """
        Parse and verify webhook payload
        
        Args:
            rawPayload: Raw JSON string of webhook payload
            signature: Signature from HTTP header 'X-Blazium-Signature'
            
        Returns:
            Parsed and verified WebhookPayload object
            
        Raises:
            InvalidSignatureError: If signature verification fails
            ValidationError: If payload format is invalid
            
        Note:
            Only verified webhooks receive events. Unverified webhooks will not receive
            any webhook events from BlaziumPay.
        """
        from .errors import InvalidSignatureError
        
        if not self.verify_webhook_signature(rawPayload, signature):
            raise InvalidSignatureError(
                "Invalid webhook signature. This webhook may be from an unverified endpoint. "
                "Only verified webhooks receive events from BlaziumPay."
            )
        
        try:
            payload_data = json.loads(rawPayload)
            
            return WebhookPayload(
                id=payload_data["id"],
                webhook_id=payload_data["webhook_id"],
                event=WebhookEventType(payload_data["event"]),
                payment_id=payload_data["payment_id"],
                payment=self._normalize_payment(payload_data["payment"]),
                timestamp=payload_data["timestamp"],
                createdAt=payload_data["createdAt"],
            )
            
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            raise ValidationError(
                "Invalid webhook payload format",
                {"error": str(e)},
            )
    
    def is_final(self, payment: Payment) -> bool:
        """
        Check if payment is in a final state
        
        Args:
            payment: Payment object
            
        Returns:
            True if payment is in final state
        """
        final_statuses = [
            PaymentStatus.CONFIRMED,
            PaymentStatus.FAILED,
            PaymentStatus.EXPIRED,
            PaymentStatus.CANCELLED,
        ]
        return payment.status in final_statuses
    
    def is_paid(self, payment: Payment) -> bool:
        """
        Check if payment is confirmed/paid
        
        Args:
            payment: Payment object
            
        Returns:
            True if payment is confirmed
        """
        return payment.status == PaymentStatus.CONFIRMED

    def is_partially_paid(self, payment: Payment) -> bool:
        """
        Check if payment is partially paid
        
        Args:
            payment: Payment object
            
        Returns:
            True if payment is partially paid
        """
        return payment.status == PaymentStatus.PARTIALLY_PAID

    def is_expired(self, payment: Payment) -> bool:
        """
        Check if payment has expired
        
        Args:
            payment: Payment object
            
        Returns:
            True if payment is expired
        """
        return payment.status == PaymentStatus.EXPIRED

    def get_payment_progress(self, payment: Payment) -> float:
        """
        Get payment progress as a percentage
        
        Args:
            payment: Payment object
            
        Returns:
            Progress percentage (0-100)
        """
        if not payment.payAmount or payment.amount <= 0:
            return 0.0
        
        # If there's a partial payment, use that amount
        if payment.partialPayment:
            progress = (payment.partialPayment.amount / payment.payAmount) * 100
            return min(100.0, max(0.0, progress))
        
        # If payment is confirmed, it's 100%
        if payment.status == PaymentStatus.CONFIRMED:
            return 100.0
        
        # Otherwise calculate based on payAmount vs expected amount
        # Note: This is approximate as we don't have real-time payment tracking
        return 0.0

    def format_amount(self, amount: float, currency: str) -> str:
        """
        Format crypto amount with appropriate decimals
        
        Args:
            amount: Amount to format
            currency: Currency code (TON, SOL, BTC)
            
        Returns:
            Formatted amount string
        """
        # Format crypto amounts with appropriate decimals
        decimals = {
            'TON': 4,
            'SOL': 4,
            'BTC': 8,
        }
        
        decimal_places = decimals.get(currency.upper(), 4)
        return f"{amount:.{decimal_places}f} {currency.upper()}"

    def _normalize_payment(self, data: Dict[str, Any]) -> Payment:
        """
        Normalize payment data from API response
        
        Args:
            data: Raw payment data from API
            
        Returns:
            Normalized Payment object
        """
        metadata = data.get("metadata") or {}
        partial_payment_data = metadata.get("partial_payment")
        
        partial_payment = None
        if partial_payment_data:
            partial_payment = PartialPayment(
                amount=float(partial_payment_data["amount"]),
                txHash=partial_payment_data["txHash"],
                detectedAt=partial_payment_data["detectedAt"],
                expectedAmount=float(data.get("payAmount", 0)),
            )
        
        return Payment(
            id=str(data["id"]),
            status=PaymentStatus(data["status"]),
            amount=float(data["amount"]) if isinstance(data["amount"], str) else data["amount"],
            currency=str(data["currency"]),
            checkoutUrl=str(data["checkoutUrl"]),
            createdAt=str(data["createdAt"]),
            expiresAt=str(data["expiresAt"]),
            description=data.get("description"),
            metadata=data.get("metadata"),
            updatedAt=data.get("updatedAt"),
            payCurrency=BlaziumChain(data["payCurrency"]) if data.get("payCurrency") else None,
            payAmount=float(data["payAmount"]) if data.get("payAmount") else None,
            payAddress=data.get("payAddress"),
            txHash=data.get("txHash"),
            networkFee=float(data["networkFee"]) if data.get("networkFee") else None,
            blockHeight=str(data["blockHeight"]) if data.get("blockHeight") else None,
            confirmedAt=data.get("confirmedAt"),
            addressIndex=data.get("addressIndex"),
            quotedRate=float(data["quotedRate"]) if data.get("quotedRate") else None,
            quoteExpiresAt=data.get("quoteExpiresAt"),
            rewardAmount=float(data["rewardAmount"]) if data.get("rewardAmount") else None,
            rewardCurrency=data.get("rewardCurrency"),
            rewardData=data.get("rewardData"),
            rewardDelivered=data.get("rewardDelivered"),
            partialPayment=partial_payment,
        )

