"""Cancel or Refund Payment - Intelligent service that chooses the right operation.

This service encapsulates the complexity of CyberSource post-payment operations.

IDs you receive from different operations:
    - payment_id: From PaymentCaptureApiResponse.id (direct_payment, enrollment)
    - capture_id: Same as payment_id for direct payments (auth+capture in one)
    - capture_payment_id: From capture_payment() when using separate auth+capture flow

Operations and when to use:
    - reverse_auth: Before capture, releases hold on funds
    - void (cancel): Same day before settlement (~11pm), no fees
    - refund: After settlement, incurs fees

This service tries operations in order until one succeeds.
"""

from enum import StrEnum

from sincpro_payments_sdk.apps.common.domain import CurrencyType
from sincpro_payments_sdk.apps.cybersource import DataTransferObject, Feature, cybersource


class CancelRefundOperation(StrEnum):
    VOID = "VOID"
    REFUND = "REFUND"
    REVERSE_AUTH = "REVERSE_AUTH"


class CommandCancelOrRefund(DataTransferObject):
    """Command to cancel or refund a payment.

    Args:
        payment_id: The payment ID from the original transaction response
        transaction_ref: Your reference for this cancellation/refund
        amount: Amount to cancel/refund
        currency: Currency code (USD, BOB, etc)
        reason: Reason for cancellation (optional, used for reverse_auth)
        preferred_operation: Hint which operation to try first
            - VOID: Try void first (same day)
            - REFUND: Try refund first (after settlement)
            - REVERSE_AUTH: Try reverse auth first (before capture)
    """

    payment_id: str
    transaction_ref: str
    amount: float
    currency: str
    reason: str = "Customer requested cancellation"
    preferred_operation: CancelRefundOperation = CancelRefundOperation.VOID


class ResponseCancelOrRefund(DataTransferObject):
    """Response from cancel or refund operation."""

    transaction_id: str
    status: str
    operation_used: CancelRefundOperation
    raw_response: dict | None = None


@cybersource.feature(CommandCancelOrRefund)
class CancelOrRefund(Feature):
    """Cancel or Refund a payment.

    Tries operations based on preferred_operation, falls back to alternatives.

    Decision flow:
        VOID preferred:
            1. Try cancel_payment (void)
            2. If fails, try refund_payment

        REFUND preferred:
            1. Try refund_payment
            2. If fails, try cancel_payment (void)

        REVERSE_AUTH preferred:
            1. Try reverse_auth_payment
            2. If fails, try cancel_payment (void)
            3. If fails, try refund_payment
    """

    def execute(self, dto: CommandCancelOrRefund) -> ResponseCancelOrRefund:
        currency = CurrencyType(dto.currency)

        if dto.preferred_operation == CancelRefundOperation.REVERSE_AUTH:
            return self._try_reverse_auth_first(dto, currency)
        elif dto.preferred_operation == CancelRefundOperation.REFUND:
            return self._try_refund_first(dto, currency)
        else:
            return self._try_void_first(dto, currency)

    def _try_void_first(
        self, dto: CommandCancelOrRefund, currency: CurrencyType
    ) -> ResponseCancelOrRefund:
        try:
            response = self.payment_adapter.cancel_payment(
                payment_id=dto.payment_id,
                transaction_ref=dto.transaction_ref,
            )
            return ResponseCancelOrRefund(
                transaction_id=response.id,
                status="VOIDED",
                operation_used=CancelRefundOperation.VOID,
                raw_response=response.raw_response,
            )
        except Exception:
            return self._do_refund(dto, currency)

    def _try_refund_first(
        self, dto: CommandCancelOrRefund, currency: CurrencyType
    ) -> ResponseCancelOrRefund:
        try:
            return self._do_refund(dto, currency)
        except Exception:
            response = self.payment_adapter.cancel_payment(
                payment_id=dto.payment_id,
                transaction_ref=dto.transaction_ref,
            )
            return ResponseCancelOrRefund(
                transaction_id=response.id,
                status="VOIDED",
                operation_used=CancelRefundOperation.VOID,
                raw_response=response.raw_response,
            )

    def _try_reverse_auth_first(
        self, dto: CommandCancelOrRefund, currency: CurrencyType
    ) -> ResponseCancelOrRefund:
        try:
            response = self.payment_adapter.reverse_auth_payment(
                payment_id=dto.payment_id,
                reason=dto.reason,
                transaction_ref=dto.transaction_ref,
                amount=dto.amount,
                currency=currency,
            )
            return ResponseCancelOrRefund(
                transaction_id=response.id,
                status=response.status,
                operation_used=CancelRefundOperation.REVERSE_AUTH,
                raw_response=response.raw_response,
            )
        except Exception:
            return self._try_void_first(dto, currency)

    def _do_refund(
        self, dto: CommandCancelOrRefund, currency: CurrencyType
    ) -> ResponseCancelOrRefund:
        response = self.payment_adapter.refund_payment(
            capture_id=dto.payment_id,
            transaction_ref=dto.transaction_ref,
            amount=dto.amount,
            currency=currency,
        )
        return ResponseCancelOrRefund(
            transaction_id=response.id,
            status=response.status,
            operation_used=CancelRefundOperation.REFUND,
            raw_response=response.raw_response,
        )
