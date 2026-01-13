from sincpro_payments_sdk import exceptions
from sincpro_payments_sdk.apps.cybersource import DataTransferObject, Feature, cybersource
from sincpro_payments_sdk.apps.cybersource.domain import (
    CardMonthOrDay,
    CardNumber,
    CardYear4Digits,
)


class CommandCreateCustomerPaymentMethod(DataTransferObject):
    """Create a customer profile with a saved card.

    Use when you want to:
    - Create a customer in CyberSource vault
    - Associate a card to that customer
    - Allow customer to have multiple cards
    """

    external_id: str
    email: str
    card_number: str
    month: str
    year: str


class ResponseCreateCustomerPaymentMethod(DataTransferObject):
    """Response with customer_id and token_id."""

    customer_id: str
    token_id: str
    instrument_identifier_id: str
    card_type: str
    state: str
    raw_response: dict | None = None


@cybersource.feature(CommandCreateCustomerPaymentMethod)
class CreateCustomerPaymentMethod(Feature):
    """Create a customer with a saved card in CyberSource vault.

    Flow:
        1. create_customer() -> customer_id
        2. create_card() -> instrument_identifier_id
        3. associate_card_payment_method_to_customer() -> token_id

    Use Cases:
        - Customer registration with card save
        - Adding cards to customer wallet
    """

    def execute(
        self, dto: CommandCreateCustomerPaymentMethod
    ) -> ResponseCreateCustomerPaymentMethod:
        card_exp_year = self._get_exp_year(dto)
        card_exp_month = CardMonthOrDay(dto.month)
        card_number = CardNumber(dto.card_number)
        card_type = self._define_card_type(card_number)

        customer = self.token_adapter.create_customer(dto.external_id, dto.email)

        tokenized_card = self.token_adapter.create_card(card_number)
        if tokenized_card.state != "ACTIVE":
            raise exceptions.SincproValidationError("Card not active")

        payment_instrument = self.token_adapter.associate_card_payment_method_to_customer(
            tokenized_customer_id=customer.id,
            tokenized_card_id=tokenized_card.id,
            month=card_exp_month,
            year=card_exp_year,
            card_type=card_type,
        )

        return ResponseCreateCustomerPaymentMethod(
            customer_id=customer.id,
            token_id=payment_instrument.id,
            instrument_identifier_id=tokenized_card.id,
            card_type=payment_instrument.card_type,
            state=payment_instrument.state,
            raw_response=payment_instrument.raw_response,
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
