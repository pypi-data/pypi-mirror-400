from sincpro_payments_sdk import exceptions
from sincpro_payments_sdk.apps.cybersource import DataTransferObject, Feature, cybersource
from sincpro_payments_sdk.apps.cybersource.domain import (
    CardMonthOrDay,
    CardNumber,
    CardYear4Digits,
)


class CommandCreatePaymentMethod(DataTransferObject):
    """Tokenize a card for future payments.

    This creates a payment instrument that can be used for:
    - PaySavedCardEnrollment (CIT with CVV)
    - RecurringPayment (MIT without CVV)
    """

    card_number: str
    month: str
    year: str


class ResponseCreatePaymentMethod(DataTransferObject):
    """Response with token_id to save in your database."""

    id: str
    state: str
    instrument_identifier_id: str
    card_type: str
    expiration_month: str
    expiration_year: str
    raw_response: dict | None = None


@cybersource.feature(CommandCreatePaymentMethod)
class CreatePaymentMethod(Feature):
    """Tokenize a card for future payments (without charging).

    Use Cases:
        1. Save card during registration (no payment)
        2. Add new card to customer wallet

    Flow:
        1. create_card() -> instrument_identifier_id (tokenized card number)
        2. create_card_payment_method() -> payment_instrument_id (with expiration)

    The returned id is the token_id to use in:
        - PaySavedCardEnrollment (CIT)
        - RecurringPayment (MIT)
    """

    def execute(self, dto: CommandCreatePaymentMethod) -> ResponseCreatePaymentMethod:
        card_exp_year = self._get_exp_year(dto)
        card_exp_month = CardMonthOrDay(dto.month)
        card_number = CardNumber(dto.card_number)
        card_type = self._define_card_type(card_number)

        tokenized_card = self.token_adapter.create_card(card_number)

        if tokenized_card.state != "ACTIVE":
            raise exceptions.SincproValidationError("Card not active")

        payment_method = self.token_adapter.create_card_payment_method(
            tokenized_card.id,
            card_exp_month,
            card_exp_year,
            card_type,
        )

        return ResponseCreatePaymentMethod(
            id=payment_method.id,
            state=payment_method.state,
            instrument_identifier_id=payment_method.instrument_identifier_id,
            card_type=payment_method.card_type,
            expiration_month=payment_method.expiration_month,
            expiration_year=payment_method.expiration_year,
            raw_response=payment_method.raw_response,
        )

    def _get_exp_year(self, dto) -> CardYear4Digits:
        card_exp_year = dto.year
        if len(dto.year) == 2:
            card_exp_year = f"20{dto.year}"
        return CardYear4Digits(card_exp_year)

    def _define_card_type(self, card_number: str) -> str:
        if card_number.startswith("4"):
            return "visa"
        if card_number.startswith("5"):
            return "mastercard"
        return "visa"
