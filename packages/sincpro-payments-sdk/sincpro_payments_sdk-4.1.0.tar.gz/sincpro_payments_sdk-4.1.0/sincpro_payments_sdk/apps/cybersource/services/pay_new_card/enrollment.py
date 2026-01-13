"""Pay with new card - Step 1: Enrollment with 3DS."""

from sincpro_payments_sdk.apps.common.domain import CurrencyType
from sincpro_payments_sdk.apps.cybersource import DataTransferObject, Feature, cybersource
from sincpro_payments_sdk.apps.cybersource.adapters.cybersource_rest_api.common import (
    PayerAuthenticationResponse,
)
from sincpro_payments_sdk.apps.cybersource.domain import (
    BillingInformation,
    Card,
    CardCVV,
    CardMonthOrDay,
    CardNumber,
    CardYear4Digits,
    CityCode,
    CityName,
    CountryCode,
    IndustrySectorOptions,
    LinkSerMMDRequired,
    SourceOptions,
)


class CommandPayNewCardEnrollment(DataTransferObject):
    """Command to pay with new card - Step 1: Enrollment."""

    transaction_ref: str
    amount: float
    currency: str

    card_number: str
    card_month: str
    card_year: str
    card_cvv: str

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

    fingerprint_token: str
    payer_auth_ref_id: str
    return_url: str | None = None
    save_card: bool = False


class ResponsePayNewCardEnrollment(DataTransferObject):
    """Response from pay with new card enrollment.

    If challenge_required=True, show step_up_url iframe to customer,
    then call PayNewCardValidation with auth_transaction_id.

    If save_card=True and payment successful, token_id contains the saved card token.
    """

    transaction_id: str
    status: str
    raw_response: dict | None = None
    challenge_required: bool = False
    auth_transaction_id: str | None = None
    cavv: str | None = None
    step_up_url: str | None = None
    access_token: str | None = None
    tokenized_card: str | None = None


@cybersource.feature(CommandPayNewCardEnrollment)
class PayNewCardEnrollment(Feature):
    """Pay with new card - Step 1: Enrollment with 3DS."""

    def execute(self, dto: CommandPayNewCardEnrollment) -> ResponsePayNewCardEnrollment:
        card = Card(
            card_number=CardNumber(dto.card_number),
            month=CardMonthOrDay(dto.card_month),
            year=CardYear4Digits(dto.card_year),
        )

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

        response = self.payment_adapter.pay_with_new_card_enrollment(
            transaction_ref=dto.transaction_ref,
            card=card,
            cvv=CardCVV(dto.card_cvv),
            amount=dto.amount,
            currency=CurrencyType(dto.currency),
            billing_info=billing_info,
            merchant_defined_data=merchant_defined_data,
            fingerprint_token=dto.fingerprint_token,
            payer_auth_ref_id=dto.payer_auth_ref_id,
            return_url=dto.return_url,
            save_card=dto.save_card,
        )

        if isinstance(response, PayerAuthenticationResponse):
            return ResponsePayNewCardEnrollment(
                transaction_id=response.id,
                status=response.status,
                raw_response=response.raw_response,
                challenge_required=response.challenge_required == "true",
                auth_transaction_id=response.auth_transaction_id,
                cavv=response.cavv,
                step_up_url=response.step_up_url,
                access_token=response.access_token,
            )

        return ResponsePayNewCardEnrollment(
            transaction_id=response.id,
            status=response.status,
            raw_response=response.raw_response,
            challenge_required=False,
            tokenized_card=response.tokenized_card,
        )
