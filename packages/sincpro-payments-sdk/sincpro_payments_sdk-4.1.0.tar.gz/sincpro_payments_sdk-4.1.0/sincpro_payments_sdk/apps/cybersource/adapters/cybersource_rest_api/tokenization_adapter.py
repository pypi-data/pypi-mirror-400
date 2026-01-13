"""Tokenization adapter for CyberSource REST API.

TypedDict Request Payloads:
    - CreateCardRequest: /tms/v1/instrumentidentifiers
    - CreatePaymentMethodRequest: /tms/v1/paymentinstruments
    - CreateCustomerRequest: /tms/v2/customers
    - AssociateCardToCustomerRequest: /tms/v2/customers/{id}/payment-instruments

Composed from common.py:
    - CardRequest: Card details (number, expiration, type)
    - BuyerInformationRequest: Customer info (merchantCustomerID, email)
    - ClientReferenceInfoRequest: Reference code
    - InstrumentIdentifierRequest: Tokenized card ID
"""

from typing import TypedDict

from sincpro_framework import DataTransferObject

from sincpro_payments_sdk.apps.cybersource.domain import (
    CardMonthOrDay,
    CardNumber,
    CardType,
    CardYear4Digits,
)
from sincpro_payments_sdk.infrastructure.client_api import ClientAPI

from .common import (
    BuyerInformationRequest,
    CardRequest,
    ClientReferenceInfoRequest,
    CyberSourceAuth,
    InstrumentIdentifierRequest,
    cybersource_credential_provider,
)


class CreateCardRequest(TypedDict):
    """POST /tms/v1/instrumentidentifiers - Tokenize card number only."""

    card: CardRequest


class CreatePaymentMethodRequest(TypedDict):
    """POST /tms/v1/paymentinstruments - Create payment method with expiration."""

    card: CardRequest
    instrumentIdentifier: InstrumentIdentifierRequest


class CreateCustomerRequest(TypedDict):
    """POST /tms/v2/customers - Create customer profile."""

    buyerInformation: BuyerInformationRequest
    clientReferenceInformation: ClientReferenceInfoRequest


class AssociateCardToCustomerRequest(TypedDict):
    """POST /tms/v2/customers/{id}/payment-instruments - Link card to customer."""

    card: CardRequest
    instrumentIdentifier: InstrumentIdentifierRequest


class InstrumentIdentifierResponse(DataTransferObject):
    """Response from create_card - tokenized card number."""

    id: str
    state: str
    raw_response: dict | None = None


class PaymentInstrumentResponse(DataTransferObject):
    """Response from create_card_payment_method - card with expiration."""

    id: str
    state: str
    instrument_identifier_id: str
    card_type: str
    expiration_month: str
    expiration_year: str
    raw_response: dict | None = None


class CustomerResponse(DataTransferObject):
    """Response from create_customer."""

    id: str
    raw_response: dict | None = None


class TokenizationAdapter(ClientAPI):
    """CyberSource Tokenization API adapter.

    Tokenization allows storing card data securely in CyberSource vault.
    Use tokens instead of raw card numbers for payments.

    Use Cases:

        1. One-time tokenization (guest checkout):
            create_card(card_number) -> instrument_id
            Use instrument_id in PaymentAdapter with token_id param

        2. Save card for later (returning customer):
            a. create_card(card_number) -> instrument_id
            b. create_card_payment_method(instrument_id, month, year, type) -> payment_method_id
            Store payment_method_id in your DB for future payments

        3. Customer vault (multiple cards per customer):
            a. create_customer(external_id, email) -> customer_id
            b. create_card(card_number) -> instrument_id
            c. associate_card_payment_method_to_customer(customer_id, instrument_id, ...)
            d. list_customer_payment_methods(customer_id) -> all saved cards

    Token Hierarchy:
        Customer (optional)
            └── Payment Instrument (card with expiration)
                    └── Instrument Identifier (card number token)

    PCI Compliance:
        - Only instrument_id touches raw card number
        - After tokenization, never store or transmit raw card data
        - Tokens are merchant-specific, useless if stolen
    """

    ROUTE_INSTRUMENT_IDENTIFICATION = "/tms/v1/instrumentidentifiers"
    ROUTE_PAYMENT_INSTRUMENTS = "/tms/v1/paymentinstruments"
    ROUTE_CUSTOMERS = "/tms/v2/customers"
    ROUTE_CUSTOMER_PAYMENT_INSTRUMENTS = "/tms/v2/customers/{customerId}/payment-instruments"

    def __init__(self):
        """Initialize with a CyberSource client."""
        super().__init__(auth=CyberSourceAuth(cybersource_credential_provider))

    @property
    def base_url(self):
        """Get the base URL for the CyberSource API."""
        updated_credentials = cybersource_credential_provider.get_credentials()
        return f"https://{updated_credentials.endpoint}"

    def create_card(self, card_number: CardNumber) -> InstrumentIdentifierResponse:
        """Tokenize card number only (Step 1 of any tokenization flow).

        Returns instrument_id that replaces the raw card number.
        This is the only method that receives the actual card number.

        Use instrument_id for:
            - One-time payment: Pass to PaymentAdapter.direct_payment(token_id=instrument_id)
            - Save for later: Pass to create_card_payment_method()
        """
        body: CreateCardRequest = {
            "card": {
                "number": card_number,
            },
        }

        response = self.execute_request(
            self.ROUTE_INSTRUMENT_IDENTIFICATION, "POST", data=body
        )
        res_py_obj = response.json()

        return InstrumentIdentifierResponse(
            id=res_py_obj["id"],
            state=res_py_obj["state"],
            raw_response=res_py_obj,
        )

    def create_card_payment_method(
        self,
        tokenized_card_id: str,
        month: CardMonthOrDay,
        year: CardYear4Digits,
        card_type: str,
    ) -> PaymentInstrumentResponse:
        """Create payment method with expiration details (Step 2 for saved cards).

        Adds expiration date and card type to a tokenized card.
        Required to save card for future use without re-entering expiration.

        Args:
            tokenized_card_id: instrument_id from create_card()

        Returns payment_method_id to store in your database.
        """
        body: CreatePaymentMethodRequest = {
            "card": {"expirationMonth": month, "expirationYear": year, "type": card_type},
            "instrumentIdentifier": {"id": tokenized_card_id},
        }

        response = self.execute_request(
            self.ROUTE_PAYMENT_INSTRUMENTS,
            "POST",
            data=body,
        )
        res_py_obj = response.json()

        return PaymentInstrumentResponse(
            id=res_py_obj["id"],
            state=res_py_obj["state"],
            instrument_identifier_id=tokenized_card_id,
            card_type=res_py_obj["card"]["type"],
            expiration_month=res_py_obj["card"]["expirationMonth"],
            expiration_year=res_py_obj["card"]["expirationYear"],
            raw_response=res_py_obj,
        )

    def create_customer(self, external_id: str, email: str) -> CustomerResponse:
        """Create customer profile in CyberSource vault.

        Use when customer needs to save multiple cards.
        Link your internal customer ID (external_id) to CyberSource customer_id.

        Args:
            external_id: Your internal customer/user ID
            email: Customer email for CyberSource records

        Returns customer_id to use in associate_card_payment_method_to_customer().
        """
        payload: CreateCustomerRequest = {
            "buyerInformation": {
                "merchantCustomerID": external_id,
                "email": email,
            },
            "clientReferenceInformation": {"code": external_id},
        }
        response = self.execute_request(
            self.ROUTE_CUSTOMERS,
            data=payload,
        )
        res_py_obj = response.json()

        return CustomerResponse(
            id=res_py_obj["id"],
            raw_response=res_py_obj,
        )

    def associate_card_payment_method_to_customer(
        self,
        tokenized_customer_id: str,
        tokenized_card_id: str,
        month: CardMonthOrDay,
        year: CardYear4Digits,
        card_type: CardType,
    ) -> PaymentInstrumentResponse:
        """Link a tokenized card to a customer profile.

        Allows customer to have multiple saved cards.
        Cards linked to customer appear in list_customer_payment_methods().

        Args:
            tokenized_customer_id: customer_id from create_customer()
            tokenized_card_id: instrument_id from create_card()
        """
        payload: AssociateCardToCustomerRequest = {
            "card": {"expirationMonth": month, "expirationYear": year, "type": card_type},
            "instrumentIdentifier": {"id": tokenized_card_id},
        }
        response = self.execute_request(
            self.ROUTE_CUSTOMER_PAYMENT_INSTRUMENTS.format(customerId=tokenized_customer_id),
            data=payload,
        )
        res_py_obj = response.json()

        return PaymentInstrumentResponse(
            id=res_py_obj["id"],
            state=res_py_obj["state"],
            instrument_identifier_id=tokenized_card_id,
            card_type=res_py_obj["card"]["type"],
            expiration_month=res_py_obj["card"]["expirationMonth"],
            expiration_year=res_py_obj["card"]["expirationYear"],
            raw_response=res_py_obj,
        )

    def list_customer_payment_methods(self, tokenized_customer_id: str) -> list[dict]:
        """List all cards saved for a customer.

        Use to display "saved cards" UI for returning customers.

        Returns list of payment instruments with masked card numbers.
        """
        response = self.execute_request(
            self.ROUTE_CUSTOMER_PAYMENT_INSTRUMENTS.format(customerId=tokenized_customer_id),
            "GET",
        )
        res_py_obj = response.json()
        return res_py_obj.get("_embedded", {}).get("paymentInstruments", [])
