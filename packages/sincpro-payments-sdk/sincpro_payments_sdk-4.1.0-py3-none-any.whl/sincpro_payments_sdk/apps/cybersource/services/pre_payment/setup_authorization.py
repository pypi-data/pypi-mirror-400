"""Setup 3DS Authentication for new cards.

Use this before calling PayNewCardEnrollment.
Returns tokens needed for device fingerprinting in the frontend.
"""

from sincpro_payments_sdk.apps.cybersource import DataTransferObject, Feature, cybersource
from sincpro_payments_sdk.apps.cybersource.adapters.cybersource_rest_api.payer_auth_adapter import (
    SetupAuthenticationResponse,
)
from sincpro_payments_sdk.apps.cybersource.domain import (
    CardMonthOrDay,
    CardNumber,
    CardType,
    CardYear4Digits,
)


class CommandSetupAuth(DataTransferObject):
    """Setup 3DS Authentication for a new card.

    The reference_id returned should be passed to PayNewCardEnrollment as payer_auth_ref_id.
    """

    card_type: CardType | str
    card_number: str
    card_month: str
    card_year: str
    transaction_ref: str


class ResponseSetupAuth(SetupAuthenticationResponse):
    """Response with tokens for 3DS device fingerprinting.

    Frontend must:
        1. Render hidden iframe with device_data_collection_url
        2. Pass access_token and reference_id to the iframe
        3. Wait for completion, then call PayNewCardEnrollment
    """


@cybersource.feature(CommandSetupAuth)
class SetupAuthFor(Feature):
    """Setup 3DS Authentication for new cards."""

    def execute(self, dto: CommandSetupAuth) -> ResponseSetupAuth:
        response = self.payer_auth_adapter.setup_payer_auth(
            CardNumber(dto.card_number),
            CardMonthOrDay(dto.card_month),
            CardYear4Digits(dto.card_year),
            CardType(dto.card_type),
            dto.transaction_ref,
        )

        return ResponseSetupAuth.model_construct(**response.model_dump())
