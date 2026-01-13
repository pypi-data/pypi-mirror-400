"""Check QR status use case for Banco Económico."""

from datetime import datetime

from sincpro_payments_sdk import exceptions
from sincpro_payments_sdk.apps.common.domain import CurrencyType
from sincpro_payments_sdk.apps.qr import DataTransferObject, Feature, qr
from sincpro_payments_sdk.apps.qr.domain.economico import (
    PaymentQR,
    QRId,
    QRStatusCode,
    QRStatusEconomico,
)


class CommandCheckQRStatusEconomico(DataTransferObject):
    """Command to check QR status with Banco Económico."""

    qr_id: str


class ResponseCheckQRStatusEconomico(QRStatusEconomico):
    """Response from checking QR status with Banco Económico."""


@qr.feature(CommandCheckQRStatusEconomico)
class CheckQRStatusEconomico(Feature):
    """Check QR status with Banco Económico."""

    def execute(self, dto: CommandCheckQRStatusEconomico) -> ResponseCheckQRStatusEconomico:
        """Check QR status."""
        adapter_response = self.economico_qr_adapter.get_qr_status(dto.qr_id)

        if adapter_response.response_code != 0:
            raise exceptions.SincproExternalServiceError(
                f"Failed to check QR status: {adapter_response.message}"
            )

        payments = []
        if adapter_response.payment:
            for payment_data in adapter_response.payment:
                payment_datetime = datetime.fromisoformat(payment_data.payment_date)

                payments.append(
                    PaymentQR(
                        qr_id=QRId(payment_data.qr_id),
                        transaction_id=payment_data.transaction_id,
                        payment_date=payment_datetime,
                        payment_time=payment_data.payment_time,
                        currency=CurrencyType(payment_data.currency),
                        amount=payment_data.amount,
                        sender_bank_code=payment_data.sender_bank_code,
                        sender_name=payment_data.sender_name,
                        sender_document_id=payment_data.sender_document_id,
                        sender_account=payment_data.sender_account,
                    )
                )

        status_code = None
        if adapter_response.status_qr_code is not None:
            status_code = QRStatusCode(adapter_response.status_qr_code)

        return ResponseCheckQRStatusEconomico(
            status_qr_code=status_code,
            payments=payments,
        )
