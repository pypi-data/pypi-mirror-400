"""Banco Económico QR API adapter."""

from datetime import date
from enum import StrEnum
from typing import NotRequired, TypedDict

from sincpro_framework import DataTransferObject

from sincpro_payments_sdk import exceptions
from sincpro_payments_sdk.infrastructure.client_api import ClientAPI

from .economico_auth_adapter import BancoEconomicoAuthAdapter
from .economico_common import BearerTokenAuth, economico_credential_provider


class GenerateQRRequest(TypedDict):
    transactionId: str
    accountCredit: str
    currency: str
    amount: float
    dueDate: str
    singleUse: bool
    modifyAmount: bool
    description: NotRequired[str]


class StatusQRRequest(TypedDict):
    qrId: str


class CancelQRRequest(TypedDict):
    qrId: str


class PaidQRRequest(TypedDict):
    paymentDate: str


class GenerateQRResponse(DataTransferObject):
    """Response from /api/qrsimple/generateQR endpoint."""

    response_code: int
    message: str
    qr_id: str | None = None
    qr_image: str | None = None


class PaymentQRResponse(DataTransferObject):
    """PaymentQR object as defined in API documentation."""

    qr_id: str
    transaction_id: str
    payment_date: str
    payment_time: str
    currency: str
    amount: float
    sender_bank_code: str
    sender_name: str
    sender_document_id: str
    sender_account: str


class StatusQRResponse(DataTransferObject):
    """Response from /api/qrsimple/statusQR endpoint."""

    response_code: int
    message: str
    status_qr_code: int | None = None
    payment: list[PaymentQRResponse] | None = None


class CancelQRResponse(DataTransferObject):
    """Response from /api/qrsimple/cancelQR endpoint."""

    response_code: int
    message: str


class PaidQRResponse(DataTransferObject):
    """Response from /api/qrsimple/paidQR endpoint."""

    response_code: int
    message: str
    payment_list: list[PaymentQRResponse] | None = None


def raise_error_if_not_transaction_success(response_code: int, message: str) -> None:
    """Raise an error if the transaction was not successful.

    Args:
        response_code: API response code (0 = success)
        message: Error message from API

    Raises:
        SincproExternalServiceError: If response_code != 0
    """
    if response_code != 0:
        raise exceptions.SincproExternalServiceError(
            f"Banco Económico API error (code {response_code}): {message}"
        )


class QRRoutes(StrEnum):
    """Banco Económico QR API routes."""

    GENERATE_QR = "/ApiGateway/api/qrsimple/generateQR"
    STATUS_QR = "/ApiGateway/api/qrsimple/statusQR"
    CANCEL_QR = "/ApiGateway/api/qrsimple/cancelQR"
    PAID_QR = "/ApiGateway/api/qrsimple/paidQR"


class BancoEconomicoQRAdapter(ClientAPI):
    """Adapter for Banco Económico QR API operations."""

    def __init__(self):
        super().__init__(auth=BearerTokenAuth(economico_credential_provider))
        self._auth_adapter = BancoEconomicoAuthAdapter()

    @property
    def base_url(self) -> str:
        """Get the base URL for the Banco Económico API."""
        credentials = economico_credential_provider.get_credentials()
        return credentials.endpoint

    def generate_qr(
        self,
        transaction_id: str,
        account_credit: str,
        currency: str,
        amount: float,
        due_date: date,
        single_use: bool = True,
        modify_amount: bool = False,
        description: str | None = None,
    ) -> GenerateQRResponse:
        """Generate a QR code with Banco Económico.

        Args:
            transaction_id: Unique transaction identifier
            account_credit: Account number (will be encrypted)
            currency: BOB or USD
            amount: Amount with max 2 decimals
            due_date: QR expiration date
            single_use: If True, QR can only be used once
            modify_amount: If True, payer can modify amount
            description: Optional payment description

        Returns:
            GenerateQRResponse with raw API response data
        """
        credentials = economico_credential_provider.get_credentials()

        encrypted_account = self._auth_adapter.encrypt(account_credit, credentials.aes_key)

        payload: GenerateQRRequest = {
            "transactionId": transaction_id,
            "accountCredit": encrypted_account,
            "currency": currency,
            "amount": round(amount, 2),
            "dueDate": due_date.strftime("%Y-%m-%d"),
            "singleUse": single_use,
            "modifyAmount": modify_amount,
        }

        if description:
            payload["description"] = description

        response = self.execute_request(
            QRRoutes.GENERATE_QR,
            "POST",
            data=payload,
            timeout=30,
        )

        response_data = response.json()

        result = GenerateQRResponse(
            response_code=response_data.get("responseCode", 0),
            message=response_data.get("message", ""),
            qr_id=response_data.get("qrId"),
            qr_image=response_data.get("qrImage"),
        )

        raise_error_if_not_transaction_success(result.response_code, result.message)

        return result

    def get_qr_status(self, qr_id: str) -> StatusQRResponse:
        """Get status of a specific QR.

        Args:
            qr_id: QR identifier to check status

        Returns:
            StatusQRResponse with raw API response data
        """
        payload: StatusQRRequest = {"qrId": qr_id}

        response = self.execute_request(
            QRRoutes.STATUS_QR,
            "GET",
            data=payload,
            timeout=30,
        )

        response_data = response.json()

        payments = None
        if response_data.get("payment"):
            payments = [
                PaymentQRResponse(
                    qr_id=p.get("qrId", ""),
                    transaction_id=p.get("transactionId", ""),
                    payment_date=p.get("paymentDate", ""),
                    payment_time=p.get("paymentTime", ""),
                    currency=p.get("currency", ""),
                    amount=p.get("amount", 0.0),
                    sender_bank_code=p.get("senderBankCode", ""),
                    sender_name=p.get("senderName", ""),
                    sender_document_id=p.get("senderDocumentId", ""),
                    sender_account=p.get("senderAccount", ""),
                )
                for p in response_data.get("payment", [])
            ]

        result = StatusQRResponse(
            response_code=response_data.get("responseCode", 0),
            message=response_data.get("message", ""),
            status_qr_code=response_data.get("statusQrCode"),
            payment=payments,
        )

        raise_error_if_not_transaction_success(result.response_code, result.message)

        return result

    def cancel_qr(self, qr_id: str) -> CancelQRResponse:
        """Cancel a generated QR.

        Args:
            qr_id: QR identifier to cancel

        Returns:
            CancelQRResponse with raw API response data
        """
        payload: CancelQRRequest = {"qrId": qr_id}

        response = self.execute_request(
            QRRoutes.CANCEL_QR,
            "DELETE",
            data=payload,
            timeout=30,
        )

        response_data = response.json()

        result = CancelQRResponse(
            response_code=response_data.get("responseCode", 0),
            message=response_data.get("message", ""),
        )

        raise_error_if_not_transaction_success(result.response_code, result.message)

        return result

    def get_paid_qrs(self, payment_date: date) -> PaidQRResponse:
        """Get list of QRs paid on a specific date.

        Args:
            payment_date: Date to retrieve paid QRs (for reconciliation)

        Returns:
            PaidQRResponse with list of payments
        """
        payload: PaidQRRequest = {"paymentDate": payment_date.strftime("%Y-%m-%d")}

        response = self.execute_request(
            QRRoutes.PAID_QR,
            "GET",
            data=payload,
            timeout=30,
        )

        response_data = response.json()

        payment_list = None
        if response_data.get("paymentList"):
            payment_list = [
                PaymentQRResponse(
                    qr_id=p.get("qrId", ""),
                    transaction_id=p.get("transactionId", ""),
                    payment_date=p.get("paymentDate", ""),
                    payment_time=p.get("paymentTime", ""),
                    currency=p.get("currency", ""),
                    amount=p.get("amount", 0.0),
                    sender_bank_code=p.get("senderBankCode", ""),
                    sender_name=p.get("senderName", ""),
                    sender_document_id=p.get("senderDocumentId", ""),
                    sender_account=p.get("senderAccount", ""),
                )
                for p in response_data.get("paymentList", [])
            ]

        result = PaidQRResponse(
            response_code=response_data.get("responseCode", 0),
            message=response_data.get("message", ""),
            payment_list=payment_list,
        )

        raise_error_if_not_transaction_success(result.response_code, result.message)

        return result
