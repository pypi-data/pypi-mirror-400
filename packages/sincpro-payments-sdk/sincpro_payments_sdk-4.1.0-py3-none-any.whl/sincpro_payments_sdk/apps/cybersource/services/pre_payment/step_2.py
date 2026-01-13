"""Step 2: Check if require auth with challenge.

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
    IndustrySectorOptions,
    LinkSerMMDRequired,
    SourceOptions,
)

_DEPRECATION_MSG = (
    "CheckRequireAuth is deprecated. "
    "Use PayNewCardEnrollment or PaySavedCardEnrollment instead."
)


class CommandCheckRequireAuth(DataTransferObject):
    """.. deprecated:: 2.0.0 Use PayNewCardEnrollment instead."""

    card_type: CardType | str
    card_number: CardNumber | str
    card_month: CardMonthOrDay | str
    card_year: CardMonthOrDay | str
    transaction_ref: str
    reference_id: str
    amount: str | float
    currency: str

    customer_firstname: str
    customer_lastname: str
    is_logged_user: bool
    source_transaction: SourceOptions
    customer_number_document: str
    customer_phone: str

    industry_sector: IndustrySectorOptions
    company_number_document: str
    company_name: str
    product_description: str


class ResponseCheckRequireAuth(PayerAuthenticationResponse):
    """.. deprecated:: 2.0.0"""


@cybersource.feature(CommandCheckRequireAuth)
class CheckRequireAuth(Feature):
    """.. deprecated:: 2.0.0 Use PayNewCardEnrollment or PaySavedCardEnrollment."""

    def execute(self, dto: CommandCheckRequireAuth) -> ResponseCheckRequireAuth:
        warnings.warn(_DEPRECATION_MSG, DeprecationWarning, stacklevel=2)
        card = CardNumber(dto.card_number)
        month = CardMonthOrDay(dto.card_month)
        year = CardYear4Digits(dto.card_year)
        card_type = CardType(dto.card_type)

        # Required by LINKSER
        merchant_defined_data = LinkSerMMDRequired(
            merchant_defined_data_1="SI" if dto.is_logged_user else "NO",
            merchant_defined_data_7=f"{dto.customer_firstname} {dto.customer_lastname}",
            merchant_defined_data_9=dto.source_transaction,
            merchant_defined_data_11=dto.customer_number_document,
            merchant_defined_data_12=dto.customer_phone,
            merchant_defined_data_14=dto.industry_sector,
            merchant_defined_data_15=dto.company_number_document,
            merchant_defined_data_87=dto.company_number_document,
            merchant_defined_data_88=dto.company_name,
            merchant_defined_data_90=dto.product_description,
        )

        enrollment = self.payer_auth_adapter.auth_enrollment(
            card,
            month,
            year,
            card_type,
            dto.transaction_ref,
            dto.reference_id,
            dto.amount,
            CurrencyType(dto.currency),
            merchant_defined_data,
        )

        if enrollment.status == "AUTHENTICATION_FAILED":
            raise exceptions.SincproValidationError("La autenticación de la tarjeta fallo")

        return ResponseCheckRequireAuth.model_construct(**enrollment.model_dump())
