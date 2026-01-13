"""Payer Auth API adapter.

TypedDict Request Payloads:
    - SetupPayerAuthRequest: /risk/v1/authentication-setups
    - AuthEnrollmentRequest: /risk/v1/authentications
    - ValidateAuthRequest: /risk/v1/authentication-results

Composed from common.py:
    - ClientReferenceInfoRequest: Client reference code
    - PaymentInfoRequest: Payment info (card)
    - ConsumerAuthInfoRequest: 3DS authentication info
    - OrderInfoRequest: Order info (amount, currency)
    - MerchantDefinedInfoItem: Custom merchant data (LinkSer)
"""

from typing import Literal, NotRequired, TypedDict

from sincpro_payments_sdk import exceptions
from sincpro_payments_sdk.apps.cybersource.domain import (
    CardMonthOrDay,
    CardNumber,
    CardType,
    CardYear4Digits,
    LinkSerMMDRequired,
)
from sincpro_payments_sdk.infrastructure.client_api import ClientAPI

from .common import (
    ClientReferenceInfoRequest,
    ConsumerAuthInfoRequest,
    CyberSourceAuth,
    CyberSourceBaseResponse,
    MerchantDefinedInfoItem,
    OrderInfoRequest,
    PayerAuthenticationResponse,
    PaymentInfoRequest,
    create_merchant_def_map,
    cybersource_credential_provider,
)


class SetupPayerAuthRequest(TypedDict):
    """POST /risk/v1/authentication-setups - Starts 3DS process."""

    clientReferenceInformation: ClientReferenceInfoRequest
    paymentInformation: PaymentInfoRequest


class AuthEnrollmentRequest(TypedDict):
    """POST /risk/v1/authentications - 3DS Enrollment with order data."""

    paymentInformation: PaymentInfoRequest
    clientReferenceInformation: ClientReferenceInfoRequest
    consumerAuthenticationInformation: ConsumerAuthInfoRequest
    orderInformation: OrderInfoRequest
    merchantDefinedInformation: NotRequired[list[MerchantDefinedInfoItem]]


class ValidateAuthRequest(TypedDict):
    """POST /risk/v1/authentication-results - Validates 3DS authentication."""

    paymentInformation: PaymentInfoRequest
    consumerAuthenticationInformation: ConsumerAuthInfoRequest
    orderInformation: OrderInfoRequest


class SetupAuthenticationResponse(CyberSourceBaseResponse):
    client_ref_info: str
    access_token: str
    device_data_collection_url: str
    reference_id: str
    token: str
    status: Literal["COMPLETED", "FAILED"]


class PayerAuthenticationAdapter(ClientAPI):
    """Adapter for CyberSource Payer Authentication API requests.

    Steps to execute the process Payer Authentication:
        - Setup Payer Authentication
        - Authenticate Enrollment
        - Validate Authentication
    """

    ROUTE_SETUP_PAYER_AUTH = "/risk/v1/authentication-setups"
    ROUTE_AUTH_ENROLLMENT = "/risk/v1/authentications"
    ROUTE_VALIDATE_AUTH = "/risk/v1/authentication-results"

    def __init__(self):
        """Initialize with a CyberSource client."""
        super().__init__(auth=CyberSourceAuth(cybersource_credential_provider))

    @property
    def base_url(self):
        """Get the base URL for the CyberSource API."""
        updated_credentials = cybersource_credential_provider.get_credentials()
        return f"https://{updated_credentials.endpoint}"

    def setup_payer_auth(
        self,
        card_number: CardNumber,
        month: CardMonthOrDay,
        year: CardYear4Digits,
        card_type: CardType,
        transaction_ref: str,
    ) -> SetupAuthenticationResponse:
        """Step 1 of 3DS flow - Setup Payer Authentication.

        3DS Authentication Flow (3 steps):
            1. setup_payer_auth -> Get device fingerprint token
            2. auth_enrollment -> Check if card enrolled in 3DS, may require challenge
            3. validate_auth -> Validate after challenge (only if challenge_required=True)

        When to use this adapter vs direct payment:
            - Use this: When you need granular control of each 3DS step
            - Use PaymentAdapter.direct_payment_with_3ds_enrollment: All-in-one payment

        Returns:
            SetupAuthenticationResponse with access_token and reference_id for next step
        """
        payload: SetupPayerAuthRequest = {
            "clientReferenceInformation": {"code": transaction_ref},
            "paymentInformation": {
                "card": {
                    "type": card_type,
                    "expirationMonth": month,
                    "expirationYear": year,
                    "number": card_number,
                }
            },
        }

        response = self.execute_request(
            self.ROUTE_SETUP_PAYER_AUTH,
            "POST",
            data=payload,
        )
        dict_response = response.json()
        if "errorInformation" in dict_response:
            raise exceptions.SincproValidationError(str(dict_response["errorInformation"]))

        return SetupAuthenticationResponse(
            raw_response=dict_response,
            id=dict_response.get("id"),
            client_ref_info=dict_response["clientReferenceInformation"]["code"],
            access_token=dict_response["consumerAuthenticationInformation"]["accessToken"],
            device_data_collection_url=dict_response["consumerAuthenticationInformation"][
                "deviceDataCollectionUrl"
            ],
            reference_id=dict_response["consumerAuthenticationInformation"]["referenceId"],
            token=dict_response["consumerAuthenticationInformation"]["token"],
            status=dict_response.get("status"),
        )

    def auth_enrollment(
        self,
        card_number: CardNumber,
        month: CardMonthOrDay,
        year: CardYear4Digits,
        card_type: CardType,
        transaction_ref: str,
        reference_id: str,
        amount: str | float,
        currency: str,
        linkser_merchant_def: LinkSerMMDRequired | None = None,
    ) -> PayerAuthenticationResponse:
        """Step 2 of 3DS flow - Check enrollment and get authentication.

        This step checks if the card is enrolled in 3DS and initiates authentication.

        Response scenarios:
            - challenge_required=False, cavv present: Card authenticated, proceed to payment
            - challenge_required=True: Must show step_up_url iframe to user, then call validate_auth

        Args:
            reference_id: From setup_payer_auth response
            linkser_merchant_def: Required for LinkSer payments (merchant defined data)
        """
        payload: AuthEnrollmentRequest = {
            "paymentInformation": {
                "card": {
                    "type": card_type,
                    "expirationMonth": month,
                    "expirationYear": year,
                    "number": card_number,
                }
            },
            "clientReferenceInformation": {"code": transaction_ref},
            "consumerAuthenticationInformation": {
                "referenceId": reference_id,
                "deviceChannel": "Browser",
            },
            "orderInformation": {
                "amountDetails": {
                    "totalAmount": str(amount),
                    "currency": currency,
                },
            },
        }

        if linkser_merchant_def:
            payload["merchantDefinedInformation"] = create_merchant_def_map(
                linkser_merchant_def
            )

        response = self.execute_request(
            self.ROUTE_AUTH_ENROLLMENT,
            "POST",
            data=payload,
        )
        dict_response = response.json()

        return PayerAuthenticationResponse(
            raw_response=dict_response,
            id=dict_response.get("id"),
            status=dict_response.get("status"),
            auth_transaction_id=dict_response["consumerAuthenticationInformation"][
                "authenticationTransactionId"
            ],
            client_ref_info=dict_response["clientReferenceInformation"]["code"],
            cavv=dict_response["consumerAuthenticationInformation"].get("cavv", None),
            challenge_required=dict_response["consumerAuthenticationInformation"].get(
                "challengeRequired", None
            ),
            access_token=dict_response["consumerAuthenticationInformation"].get(
                "accessToken", None
            ),
            step_up_url=dict_response["consumerAuthenticationInformation"].get(
                "stepUpUrl", None
            ),
            authorization_token=dict_response["consumerAuthenticationInformation"].get(
                "token", None
            ),
        )

    def validate_auth(
        self,
        card_number: CardNumber,
        month: CardMonthOrDay,
        year: CardMonthOrDay,
        card_type: CardType,
        auth_transaction_id: str,
        amount: str | float,
        currency: str,
    ) -> PayerAuthenticationResponse:
        """Step 3 of 3DS flow - Validate after challenge completion.

        Only call this if auth_enrollment returned challenge_required=True.
        Call after user completes the challenge in the step_up_url iframe.

        Args:
            auth_transaction_id: From auth_enrollment response

        Returns:
            PayerAuthenticationResponse with cavv for payment authorization
        """
        payload: ValidateAuthRequest = {
            "paymentInformation": {
                "card": {
                    "type": card_type,
                    "expirationMonth": month,
                    "expirationYear": year,
                    "number": card_number,
                }
            },
            "consumerAuthenticationInformation": {
                "authenticationTransactionId": auth_transaction_id
            },
            "orderInformation": {
                "amountDetails": {
                    "totalAmount": str(amount),
                    "currency": currency,
                },
            },
        }

        response = self.execute_request(
            self.ROUTE_VALIDATE_AUTH,
            "POST",
            data=payload,
        )

        dict_response = response.json()
        if "errorInformation" in dict_response:
            raise exceptions.SincproValidationError(str(dict_response["errorInformation"]))

        return PayerAuthenticationResponse(
            raw_response=dict_response,
            id=dict_response.get("id"),
            status=dict_response.get("status"),
            auth_transaction_id=dict_response["consumerAuthenticationInformation"][
                "authenticationTransactionId"
            ],
            client_ref_info=dict_response["clientReferenceInformation"]["code"],
        )
