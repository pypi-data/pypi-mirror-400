"""Step 3: Validate if challenge was completed.

.. deprecated:: 2.0.0
    For granular 3DS control only. Use `pay_new_card` or `pay_saved_card` services instead.
"""

import warnings

from sincpro_payments_sdk import exceptions
from sincpro_payments_sdk.apps.common.domain.payments import CurrencyType
from sincpro_payments_sdk.apps.cybersource import DataTransferObject, Feature, cybersource
from sincpro_payments_sdk.apps.cybersource.adapters.cybersource_rest_api.common import (
    PayerAuthenticationResponse,
)
from sincpro_payments_sdk.apps.cybersource.domain import (
    CardMonthOrDay,
    CardNumber,
    CardType,
    CardYear4Digits,
)

_DEPRECATION_MSG = (
    "ValidateAuth is deprecated. "
    "Use PayNewCardValidation or PaySavedCardValidation instead."
)


class CommandValidateAuth(DataTransferObject):
    """.. deprecated:: 2.0.0 Use PayNewCardValidation instead."""

    card_type: CardType | str
    card_number: CardNumber | str
    card_month: CardMonthOrDay | str
    card_year: CardYear4Digits | str
    transaction_ref: str
    amount: str | float
    currency: str


class ResponseValidateAuth(PayerAuthenticationResponse):
    """.. deprecated:: 2.0.0"""


@cybersource.feature(CommandValidateAuth)
class ValidateAuth(Feature):
    """.. deprecated:: 2.0.0 Use PayNewCardValidation or PaySavedCardValidation."""

    def execute(self, dto: CommandValidateAuth) -> ResponseValidateAuth:
        warnings.warn(_DEPRECATION_MSG, DeprecationWarning, stacklevel=2)
        card = CardNumber(dto.card_number)
        month = CardMonthOrDay(dto.card_month)
        year = CardYear4Digits(dto.card_year)
        card_type = CardType(dto.card_type)

        enrollment = self.payer_auth_adapter.validate_auth(
            card,
            month,
            year,
            card_type,
            dto.transaction_ref,
            dto.amount,
            CurrencyType(dto.currency),
        )

        if enrollment.status == "AUTHENTICATION_FAILED":
            raise exceptions.SincproValidationError(
                "El banco no permite realizar transacion por falta de autenticacion"
            )

        return ResponseValidateAuth.model_construct(**enrollment.model_dump())
