"""Recurring Payment (MIT) - Merchant Initiated Transaction."""

from sincpro_payments_sdk.apps.common.domain import CurrencyType
from sincpro_payments_sdk.apps.cybersource import DataTransferObject, Feature, cybersource
from sincpro_payments_sdk.apps.cybersource.domain import (
    BillingInformation,
    CityCode,
    CityName,
    CountryCode,
    IndustrySectorOptions,
    LinkSerMMDRequired,
    SourceOptions,
)


class CommandRecurringPayment(DataTransferObject):
    """Command for Merchant Initiated Transaction (MIT).

    NO customer present, NO CVV, NO 3DS.
    For automatic charges like subscriptions, recurring billing, installments.

    Prerequisites:
        - Card must have been saved with customer consent in a previous CIT transaction
        - Original transaction must have used save_card=True
    """

    transaction_ref: str
    amount: float
    currency: str

    token_id: str

    customer_firstname: str
    customer_lastname: str
    customer_email: str
    customer_phone: str
    customer_address: str
    customer_postal_code: str
    city_code: str
    city_name: str
    country_code: str

    is_logged_user: bool
    source_transaction: SourceOptions
    customer_number_document: str
    industry_sector: IndustrySectorOptions
    company_number_document: str
    company_name: str
    product_description: str

    commerce_indicator: str = "recurring"


class ResponseRecurringPayment(DataTransferObject):
    """Response from recurring payment."""

    transaction_id: str
    status: str
    raw_response: dict | None = None


@cybersource.feature(CommandRecurringPayment)
class RecurringPayment(Feature):
    """Recurring Payment (MIT) - Merchant Initiated Transaction.

    For automatic charges without customer present.
    No CVV required, no 3DS challenge.
    """

    def execute(self, dto: CommandRecurringPayment) -> ResponseRecurringPayment:
        billing_info = BillingInformation(
            first_name=dto.customer_firstname,
            last_name=dto.customer_lastname,
            email=dto.customer_email,
            phone=dto.customer_phone,
            address=dto.customer_address,
            city_code=CityCode(dto.city_code),
            city_name=CityName(dto.city_name),
            postal_code=dto.customer_postal_code,
            country_code=CountryCode(dto.country_code),
        )

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

        response = self.payment_adapter.merchant_initiated_payment(
            transaction_ref=dto.transaction_ref,
            token_id=dto.token_id,
            amount=dto.amount,
            currency=CurrencyType(dto.currency),
            billing_info=billing_info,
            merchant_defined_data=merchant_defined_data,
            commerce_indicator=dto.commerce_indicator,
        )

        return ResponseRecurringPayment(
            transaction_id=response.id,
            status=response.status,
            raw_response=response.raw_response,
        )
