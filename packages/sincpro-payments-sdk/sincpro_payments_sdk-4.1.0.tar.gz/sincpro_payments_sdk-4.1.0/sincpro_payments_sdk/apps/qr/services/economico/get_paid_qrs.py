"""Get paid QRs use case for Banco Económico."""

from datetime import date, datetime

from sincpro_payments_sdk import exceptions
from sincpro_payments_sdk.apps.common.domain import CurrencyType
from sincpro_payments_sdk.apps.qr import DataTransferObject, Feature, qr
from sincpro_payments_sdk.apps.qr.domain.economico import PaymentQR, QRId, QRStatusEconomico


class CommandGetPaidQRsEconomico(DataTransferObject):
    """Command to get paid QRs for a specific date."""

    payment_date: date


class ResponseGetPaidQRsEconomico(QRStatusEconomico):
    """Response from getting paid QRs."""


@qr.feature(CommandGetPaidQRsEconomico)
class GetPaidQRsEconomico(Feature):
    """Get list of paid QRs for reconciliation."""

    def execute(self, dto: CommandGetPaidQRsEconomico) -> ResponseGetPaidQRsEconomico:
        """Get paid QRs."""
        adapter_response = self.economico_qr_adapter.get_paid_qrs(dto.payment_date)

        if adapter_response.response_code != 0:
            raise exceptions.SincproExternalServiceError(
                f"Failed to get paid QRs: {adapter_response.message}"
            )

        payments = []
        if adapter_response.payment_list:
            for payment_data in adapter_response.payment_list:
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

        return ResponseGetPaidQRsEconomico(payments=payments)
