"""Setup 3DS Authentication for new cards.

.. deprecated:: 2.0.0
    Use SetupAuthForNewCard (CommandSetupAuthForNewCard) from setup_new_card instead.
"""

import warnings

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

_DEPRECATION_MSG = (
    "StartMonitorAuth is deprecated. "
    "Use SetupAuthForNewCard (CommandSetupAuthForNewCard) from setup_new_card instead."
)


class CommandStartMonitorAuth(DataTransferObject):
    """Setup 3DS Authentication for a new card.

    .. deprecated:: 2.0.0
        Use CommandSetupAuthForNewCard instead.
    """

    card_type: CardType | str
    card_number: str
    card_month: str
    card_year: str
    transaction_ref: str


class ResponseStartMonitorAuth(SetupAuthenticationResponse):
    """Response with tokens for 3DS device fingerprinting.

    .. deprecated:: 2.0.0
        Use ResponseSetupAuthForNewCard instead.
    """


@cybersource.feature(CommandStartMonitorAuth)
class StartMonitorAuth(Feature):
    """Setup 3DS Authentication for new cards.

    .. deprecated:: 2.0.0
        Use SetupAuthForNewCard instead.
    """

    def execute(self, dto: CommandStartMonitorAuth) -> ResponseStartMonitorAuth:
        warnings.warn(_DEPRECATION_MSG, DeprecationWarning, stacklevel=2)
        response = self.payer_auth_adapter.setup_payer_auth(
            CardNumber(dto.card_number),
            CardMonthOrDay(dto.card_month),
            CardYear4Digits(dto.card_year),
            CardType(dto.card_type),
            dto.transaction_ref,
        )

        return ResponseStartMonitorAuth.model_construct(**response.model_dump())
