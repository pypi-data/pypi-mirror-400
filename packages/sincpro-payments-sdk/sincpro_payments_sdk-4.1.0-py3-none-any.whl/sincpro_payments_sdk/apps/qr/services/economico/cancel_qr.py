"""Cancel QR use case for Banco Económico."""

from sincpro_payments_sdk import exceptions
from sincpro_payments_sdk.apps.qr import DataTransferObject, Feature, qr


class CommandCancelQREconomico(DataTransferObject):
    """Command to cancel a QR code with Banco Económico."""

    qr_id: str


class ResponseCancelQREconomico(DataTransferObject):
    """Response from canceling QR code with Banco Económico."""

    qr_id: str
    message: str


@qr.feature(CommandCancelQREconomico)
class CancelQREconomico(Feature):
    """Cancel QR code with Banco Económico."""

    def execute(self, dto: CommandCancelQREconomico) -> ResponseCancelQREconomico:
        """Cancel QR code."""
        adapter_response = self.economico_qr_adapter.cancel_qr(dto.qr_id)

        if adapter_response.response_code != 0:
            raise exceptions.SincproExternalServiceError(
                f"Failed to cancel QR: {adapter_response.message}"
            )

        return ResponseCancelQREconomico(
            qr_id=dto.qr_id,
            message=adapter_response.message or "QR cancelled successfully",
        )
