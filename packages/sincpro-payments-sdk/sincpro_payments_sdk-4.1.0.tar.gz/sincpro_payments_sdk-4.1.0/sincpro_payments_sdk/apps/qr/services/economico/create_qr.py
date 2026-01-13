"""Create QR use case for Banco Económico."""

from datetime import date, timedelta

from pydantic import Field

from sincpro_payments_sdk import exceptions
from sincpro_payments_sdk.apps.common.domain import CurrencyType
from sincpro_payments_sdk.apps.qr import DataTransferObject, Feature, qr
from sincpro_payments_sdk.apps.qr.domain.economico import QRId, QRImageEconomico


class CommandCreateQREconomico(DataTransferObject):
    """Command to create a QR code with Banco Económico."""

    transaction_id: str
    account_credit: str
    currency: str | CurrencyType
    amount: float
    description: str
    due_date: date = Field(default_factory=lambda: date.today() + timedelta(days=1))
    single_use: bool = True
    modify_amount: bool = False


class ResponseCreateQREconomico(QRImageEconomico):
    """Response from creating QR code with Banco Económico."""


@qr.feature(CommandCreateQREconomico)
class CreateQREconomico(Feature):
    """Create QR code with Banco Económico."""

    def execute(self, dto: CommandCreateQREconomico) -> ResponseCreateQREconomico:
        """Create QR code."""
        adapter_response = self.economico_qr_adapter.generate_qr(
            transaction_id=dto.transaction_id,
            account_credit=dto.account_credit,
            currency=str(dto.currency),
            amount=dto.amount,
            due_date=dto.due_date,
            single_use=dto.single_use,
            modify_amount=dto.modify_amount,
            description=dto.description,
        )

        if adapter_response.response_code != 0:
            raise exceptions.SincproExternalServiceError(
                f"Failed to create QR: {adapter_response.message}"
            )

        if not adapter_response.qr_id or not adapter_response.qr_image:
            raise exceptions.SincproExternalServiceError(
                "QR generation returned empty qr_id or qr_image"
            )

        return ResponseCreateQREconomico(
            qr_id=QRId(adapter_response.qr_id),
            transaction_id=dto.transaction_id,
            amount=dto.amount,
            currency=(
                CurrencyType(dto.currency) if isinstance(dto.currency, str) else dto.currency
            ),
            due_date=dto.due_date,
            single_use=dto.single_use,
            modify_amount=dto.modify_amount,
            qr_image=adapter_response.qr_image,
        )
