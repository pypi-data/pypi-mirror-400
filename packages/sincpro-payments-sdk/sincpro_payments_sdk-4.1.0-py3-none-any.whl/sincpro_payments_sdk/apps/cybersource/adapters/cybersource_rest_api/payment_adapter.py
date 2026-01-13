"""CyberSource Adapter Module"""

import warnings
from typing import Literal, NotRequired, TypedDict, Union

from sincpro_framework import logger

from sincpro_payments_sdk.apps.common.domain import CurrencyType
from sincpro_payments_sdk.apps.cybersource.domain import BillingInformation, Card
from sincpro_payments_sdk.apps.cybersource.domain.payments import (
    CaptureState,
    LinkSerMMDRequired,
    PayerAuthenticationStatus,
    PaymentAuthorizationStatus,
)
from sincpro_payments_sdk.infrastructure.client_api import ClientAPI

from .common import (
    AuthorizationOptionsRequest,
    ClientReferenceInfoRequest,
    ConsumerAuthInfoRequest,
    CyberSourceAuth,
    CyberSourceBaseResponse,
    DeviceInfoRequest,
    LinkResponse,
    MerchantDefinedInfoItem,
    OrderInfoRequest,
    PayerAuthenticationResponse,
    PaymentInfoRequest,
    ProcessingInfoRequest,
    create_merchant_def_map,
    cybersource_credential_provider,
)


class PaymentAuthorizationRequest(TypedDict):
    clientReferenceInformation: ClientReferenceInfoRequest
    paymentInformation: PaymentInfoRequest
    orderInformation: OrderInfoRequest
    merchantDefinedInformation: list[MerchantDefinedInfoItem]
    processingInformation: NotRequired[ProcessingInfoRequest]
    consumerAuthenticationInformation: NotRequired[ConsumerAuthInfoRequest]
    deviceInformation: NotRequired[DeviceInfoRequest]


class ReverseAuthRequest(TypedDict):
    clientReferenceInformation: ClientReferenceInfoRequest
    orderInformation: OrderInfoRequest
    reason: str


class CapturePaymentRequest(TypedDict):
    clientReferenceInformation: ClientReferenceInfoRequest
    orderInformation: OrderInfoRequest


class RefundPaymentRequest(TypedDict):
    clientReferenceInformation: ClientReferenceInfoRequest
    orderInformation: OrderInfoRequest


class CancelPaymentRequest(TypedDict):
    clientReferenceInformation: ClientReferenceInfoRequest


class TransactionApiResponse(CyberSourceBaseResponse):
    status: PaymentAuthorizationStatus
    tokenized_card: str | None = None


class PaymentAuthorizationApiResponse(CyberSourceBaseResponse):
    status: PaymentAuthorizationStatus
    order_information: dict
    link_payment_auth: LinkResponse
    link_payment_capture: LinkResponse
    link_reverse_auth: LinkResponse


class ReverseAuthApiResponse(CyberSourceBaseResponse):
    status: Literal["REVERSED",]


class PaymentCaptureApiResponse(CyberSourceBaseResponse):
    status: CaptureState | PaymentAuthorizationStatus
    order_information: dict
    link_payment_capture: LinkResponse
    link_void: LinkResponse
    tokenized_card: str | None = None


class RefundPaymentApiResponse(CyberSourceBaseResponse):
    status: str
    order_information: dict
    link_refund: LinkResponse
    link_void: LinkResponse


class RefundCaptureApiResponse(CyberSourceBaseResponse):
    status: str
    order_information: dict
    link_capture_refund: LinkResponse
    link_void_capture: LinkResponse


class VoidApiResponse(CyberSourceBaseResponse):
    pass


class PaymentAdapter(ClientAPI):
    """CyberSource Payment API adapter.

    Card Types (Card Not Present - CNP):
        All payments in this adapter are Card Not Present (e-commerce).

        - New card: Pass card=Card(...) with full card details
        - Saved card (token): Pass token_id=instrument_id from TokenizationAdapter

        When using saved card:
            - Pass token_id instead of card
            - CVV still required for security (cvv param)
            - Use with_stored_token=True for recurring/stored credential

        When saving card during payment:
            - Pass card with full details
            - Set store_card=True to tokenize for future use

    Payment Methods (choose based on your flow):
        - direct_payment_with_3ds_enrollment: All-in-one payment with 3DS, returns challenge if needed
        - direct_payment_with_3ds_validation: Complete payment after 3DS challenge
        - direct_payment: Simple payment with optional 3DS credentials
        - payment_authorization: Authorize only, capture later

    Payment Flow Options:

        Option A - All-in-one with 3DS (recommended for e-commerce):
            1. direct_payment_with_3ds_enrollment -> if challenge, show iframe
            2. direct_payment_with_3ds_validation -> complete after challenge
            Result: Payment authorized + captured in one step

        Option B - Granular 3DS control (use PayerAuthenticationAdapter):
            1. PayerAuthAdapter.setup_payer_auth
            2. PayerAuthAdapter.auth_enrollment
            3. PayerAuthAdapter.validate_auth (if challenge)
            4. direct_payment with auth_transaction_id/cavv
            Result: Payment authorized + captured in one step

        Option C - Authorize then Capture (for delayed fulfillment):
            1. payment_authorization -> Holds funds, returns payment_id
            2. [Ship product or fulfill service]
            3. capture_payment(payment_id) -> Charges the card
            Use when: Pre-orders, ship-then-charge, hotels, rentals
            Cancel with: reverse_auth_payment (before capture)

    Post-Payment Operations Timeline:

        SAME DAY (before settlement ~11pm):
            ┌─────────────────┐
            │  Authorization  │ ──> reverse_auth_payment (cancel auth)
            └────────┬────────┘
                     │ capture_payment
                     ▼
            ┌─────────────────┐
            │    Captured     │ ──> cancel_payment (void, no fees)
            └────────┬────────┘
                     │ settlement (~11pm)
                     ▼
        NEXT DAY+ (after settlement):
            ┌─────────────────┐
            │    Settled      │ ──> refund_payment (incurs fees)
            └─────────────────┘

    Operation Rules:
        - reverse_auth: Before capture only, releases hold on funds
        - capture: Within 7 days of auth, can be partial
        - void (cancel): Same day only, no fees
        - refund: After settlement, incurs fees, can be partial/multiple
    """

    ROUTE_AUTH_PAYMENTS = "/pts/v2/payments"
    ROUTE_AUTH_PAYMENT = "/pts/v2/payments/{id}"
    ROUTE_REVERSE_AUTH = "/pts/v2/payments/{id}/reversals"
    ROUTE_PAYMENT_CAPTURE = "/pts/v2/payments/{id}/captures"
    ROUTE_REFUND_PAYMENT = "/pts/v2/payments/{id}/refunds"
    ROUTE_REFUND_CAPTURE = "/pts/v2/captures/{id}/refunds"
    ROUTE_VOID_PAYMENT = "/pts/v2/payments/{id}/voids"
    ROUTE_CAPTURE = "/pts/v2/captures/{id}"
    ROUTE_CHECK_STATUS_PAYMENT = "/pts/v2/refresh-payment-status/{id}"

    def __init__(self):
        super().__init__(auth=CyberSourceAuth(cybersource_credential_provider))

    @property
    def base_url(self):
        updated_credentials = cybersource_credential_provider.get_credentials()
        return f"https://{updated_credentials.endpoint}"

    def direct_payment_with_3ds_enrollment(
        self,
        transaction_ref: str,
        card: Card | None,
        token_id: str | None,
        cvv: str,
        amount: float,
        currency: CurrencyType,
        billing_info: BillingInformation,
        merchant_defined_data: LinkSerMMDRequired,
        fingerprint_token: str,
        payer_auth_ref_id: str | None = None,
        return_url: str | None = None,
        store_card: bool = False,
        with_stored_token: bool = False,
    ) -> Union[PaymentCaptureApiResponse, PayerAuthenticationResponse]:
        """All-in-one payment with 3DS enrollment.

        .. deprecated:: 2.0.0
            Use pay_with_new_card_enrollment() or pay_with_saved_card_enrollment() instead.
        """
        warnings.warn(
            "direct_payment_with_3ds_enrollment is deprecated. "
            "Use pay_with_new_card_enrollment() or pay_with_saved_card_enrollment().",
            DeprecationWarning,
            stacklevel=2,
        )
        payment_info: PaymentInfoRequest
        if token_id:
            payment_info = {
                "card": {"securityCode": cvv},
                "paymentInstrument": {"id": token_id},
            }
        elif card:
            payment_info = {
                "card": {
                    "number": card.card_number,
                    "securityCode": cvv,
                    "expirationMonth": card.month,
                    "expirationYear": card.year,
                    "type": card.card_type,
                }
            }
        else:
            raise ValueError("Either card or token_id must be provided")

        processing_info: ProcessingInfoRequest = {
            "capture": True,
            "actionList": ["CONSUMER_AUTHENTICATION"],
            "fingerprintSessionId": fingerprint_token,
        }
        if store_card:
            processing_info["actionList"].append("TOKEN_CREATE")
            processing_info["actionTokenTypes"] = ["paymentInstrument"]
            processing_info["authorizationOptions"] = AuthorizationOptionsRequest(
                initiator={"credentialStoredOnFile": True}
            )
        if with_stored_token:
            processing_info["authorizationOptions"] = AuthorizationOptionsRequest(
                initiator={"storedCredentialUsed": with_stored_token}
            )

        payload: PaymentAuthorizationRequest = {
            "clientReferenceInformation": {"code": transaction_ref},
            "paymentInformation": payment_info,
            "orderInformation": {
                "amountDetails": {"totalAmount": str(amount), "currency": currency},
                "billTo": {
                    "firstName": billing_info.first_name,
                    "lastName": billing_info.last_name,
                    "address1": billing_info.address,
                    "locality": billing_info.city_name,
                    "administrativeArea": billing_info.city_code,
                    "postalCode": billing_info.postal_code,
                    "country": billing_info.country_code,
                    "email": billing_info.email,
                    "phoneNumber": billing_info.phone,
                },
            },
            "merchantDefinedInformation": create_merchant_def_map(merchant_defined_data),
            "processingInformation": processing_info,
            "deviceInformation": {"fingerprintSessionId": fingerprint_token},
        }

        if payer_auth_ref_id:
            consumer_auth: ConsumerAuthInfoRequest = {"referenceId": payer_auth_ref_id}
            if return_url:
                consumer_auth["returnUrl"] = return_url
            payload["consumerAuthenticationInformation"] = consumer_auth

        response = self.execute_request(self.ROUTE_AUTH_PAYMENTS, "POST", data=payload)
        res_py_obj = response.json()

        status = PaymentAuthorizationStatus(res_py_obj.get("status"))
        if status == PaymentAuthorizationStatus.PENDING_AUTHENTICATION:
            return PayerAuthenticationResponse(
                raw_response=res_py_obj,
                id=res_py_obj.get("id"),
                status=PayerAuthenticationStatus.PENDING_AUTHENTICATION,
                auth_transaction_id=res_py_obj["consumerAuthenticationInformation"][
                    "authenticationTransactionId"
                ],
                client_ref_info=res_py_obj["clientReferenceInformation"]["code"],
                cavv=res_py_obj["consumerAuthenticationInformation"].get("cavv"),
                challenge_required=res_py_obj["consumerAuthenticationInformation"].get(
                    "challengeRequired"
                ),
                access_token=res_py_obj["consumerAuthenticationInformation"].get(
                    "accessToken"
                ),
                step_up_url=res_py_obj["consumerAuthenticationInformation"].get("stepUpUrl"),
                authorization_token=res_py_obj["consumerAuthenticationInformation"].get(
                    "token"
                ),
            )

        return PaymentCaptureApiResponse(
            id=res_py_obj["id"],
            status=status,
            order_information=res_py_obj.get("orderInformation", {}),
            link_payment_capture=LinkResponse(**res_py_obj["_links"]["self"]),
            link_void=LinkResponse(**res_py_obj["_links"]["void"]),
            raw_response=res_py_obj,
        )

    def direct_payment_with_3ds_validation(
        self,
        transaction_ref: str,
        card: Card | None,
        token_id: str | None,
        cvv: str,
        amount: float,
        currency: CurrencyType,
        billing_info: BillingInformation,
        merchant_defined_data: LinkSerMMDRequired,
        fingerprint_token: str,
        auth_transaction_id: str | None = None,
        cavv: str | None = None,
        store_card: bool = False,
        with_stored_token: bool = False,
    ) -> TransactionApiResponse:
        """Complete payment after 3DS challenge.

        .. deprecated:: 2.0.0
            Use pay_with_new_card_validation() or pay_with_saved_card_validation() instead.
        """
        warnings.warn(
            "direct_payment_with_3ds_validation is deprecated. "
            "Use pay_with_new_card_validation() or pay_with_saved_card_validation().",
            DeprecationWarning,
            stacklevel=2,
        )
        payment_info: PaymentInfoRequest
        if token_id:
            payment_info = {
                "card": {"securityCode": cvv},
                "paymentInstrument": {"id": token_id},
            }
        elif card:
            payment_info = {
                "card": {
                    "number": card.card_number,
                    "securityCode": cvv,
                    "expirationMonth": card.month,
                    "expirationYear": card.year,
                    "type": card.card_type,
                }
            }
        else:
            raise ValueError("Either card or token_id must be provided")

        processing_info: ProcessingInfoRequest = {
            "capture": True,
            "actionList": ["VALIDATE_CONSUMER_AUTHENTICATION"],
            "fingerprintSessionId": fingerprint_token,
        }
        if store_card:
            processing_info["authorizationOptions"] = AuthorizationOptionsRequest(
                initiator={"credentialStoredOnFile": store_card}
            )

        if with_stored_token:
            processing_info["authorizationOptions"] = AuthorizationOptionsRequest(
                initiator={"storedCredentialUsed": with_stored_token}
            )

        payload: PaymentAuthorizationRequest = {
            "clientReferenceInformation": {"code": transaction_ref},
            "paymentInformation": payment_info,
            "orderInformation": {
                "amountDetails": {"totalAmount": str(amount), "currency": currency},
                "billTo": {
                    "firstName": billing_info.first_name,
                    "lastName": billing_info.last_name,
                    "address1": billing_info.address,
                    "locality": billing_info.city_name,
                    "administrativeArea": billing_info.city_code,
                    "postalCode": billing_info.postal_code,
                    "country": billing_info.country_code,
                    "email": billing_info.email,
                    "phoneNumber": billing_info.phone,
                },
            },
            "merchantDefinedInformation": create_merchant_def_map(merchant_defined_data),
            "processingInformation": processing_info,
        }

        if auth_transaction_id or cavv:
            consumer_auth: ConsumerAuthInfoRequest = {}
            if auth_transaction_id:
                consumer_auth["authenticationTransactionId"] = auth_transaction_id
            if cavv:
                consumer_auth["cavv"] = cavv
            payload["consumerAuthenticationInformation"] = consumer_auth
            logger.debug(
                f"Adding Consumer Authentication Information [{auth_transaction_id=}, {cavv=}]"
            )

        response = self.execute_request(self.ROUTE_AUTH_PAYMENTS, "POST", data=payload)
        res_py_obj = response.json()

        return TransactionApiResponse(
            id=res_py_obj["id"],
            status=res_py_obj["status"],
            raw_response=res_py_obj,
        )

    def direct_payment(
        self,
        transaction_ref: str,
        card: Card | None,
        token_id: str | None,
        cvv: str,
        amount: float,
        currency: CurrencyType,
        billing_info: BillingInformation,
        merchant_defined_data: LinkSerMMDRequired,
        fingerprint_token: str,
        auth_transaction_id: str | None = None,
        cavv: str | None = None,
    ) -> PaymentCaptureApiResponse:
        """Simple payment with optional 3DS credentials.

        .. deprecated:: 2.0.0
            Use pay_with_new_card_enrollment/validation, pay_with_saved_card_enrollment/validation,
            or merchant_initiated_payment instead.
        """
        warnings.warn(
            "direct_payment is deprecated. Use the new declarative methods instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        payment_info: PaymentInfoRequest
        if token_id:
            payment_info = {
                "card": {"securityCode": cvv},
                "paymentInstrument": {"id": token_id},
            }
        elif card:
            payment_info = {
                "card": {
                    "number": card.card_number,
                    "securityCode": cvv,
                    "expirationMonth": card.month,
                    "expirationYear": card.year,
                    "type": card.card_type,
                }
            }
        else:
            raise ValueError("Either card or token_id must be provided")

        payload: PaymentAuthorizationRequest = {
            "clientReferenceInformation": {"code": transaction_ref},
            "paymentInformation": payment_info,
            "orderInformation": {
                "amountDetails": {"totalAmount": str(amount), "currency": currency},
                "billTo": {
                    "firstName": billing_info.first_name,
                    "lastName": billing_info.last_name,
                    "address1": billing_info.address,
                    "locality": billing_info.city_name,
                    "administrativeArea": billing_info.city_code,
                    "postalCode": billing_info.postal_code,
                    "country": billing_info.country_code,
                    "email": billing_info.email,
                    "phoneNumber": billing_info.phone,
                },
            },
            "merchantDefinedInformation": create_merchant_def_map(merchant_defined_data),
            "processingInformation": {"capture": True},
            "deviceInformation": {"fingerprintSessionId": fingerprint_token},
        }

        if auth_transaction_id or cavv:
            consumer_auth: ConsumerAuthInfoRequest = {}
            if auth_transaction_id:
                consumer_auth["authenticationTransactionId"] = auth_transaction_id
            if cavv:
                consumer_auth["cavv"] = cavv
            payload["consumerAuthenticationInformation"] = consumer_auth

        response = self.execute_request(self.ROUTE_AUTH_PAYMENTS, "POST", data=payload)
        res_py_obj = response.json()

        return PaymentCaptureApiResponse(
            id=res_py_obj["id"],
            status=res_py_obj["status"],
            order_information=res_py_obj["orderInformation"],
            link_payment_capture=LinkResponse(**res_py_obj["_links"]["self"]),
            link_void=LinkResponse(**res_py_obj["_links"]["void"]),
            raw_response=res_py_obj,
        )

    def payment_authorization(
        self,
        transaction_ref: str,
        card: Card | None,
        token_id: str | None,
        cvv: str,
        amount: float,
        currency: CurrencyType,
        billing_info: BillingInformation,
        merchant_defined_data: LinkSerMMDRequired,
        transaction_session_id: str,
        auth_transaction_id: str | None,
        cavv: str | None,
    ) -> PaymentAuthorizationApiResponse:
        """Authorize payment only (capture separately with capture_payment).

        Two-step payment flow:
            1. payment_authorization -> Holds funds, returns payment_id
            2. capture_payment(payment_id) -> Actually charges the card

        Card vs Token (mutually exclusive):
            - New card: card=Card(...), token_id=None
            - Saved card: card=None, token_id=instrument_id from TokenizationAdapter

        Use this when:
            - Need to verify funds before fulfilling order
            - Want to capture later (e.g., after shipping)
            - Need ability to cancel before capture (reverse_auth_payment)

        Args:
            cvv: Required even with token
            transaction_session_id: Device fingerprint session ID
        """
        payment_info: PaymentInfoRequest
        if token_id:
            payment_info = {
                "card": {"securityCode": cvv},
                "paymentInstrument": {"id": token_id},
            }
        elif card:
            payment_info = {
                "card": {
                    "number": card.card_number,
                    "securityCode": cvv,
                    "expirationMonth": card.month,
                    "expirationYear": card.year,
                    "type": card.card_type,
                }
            }
        else:
            raise ValueError("Either card or token_id must be provided")

        payload: PaymentAuthorizationRequest = {
            "clientReferenceInformation": {"code": transaction_ref},
            "paymentInformation": payment_info,
            "orderInformation": {
                "amountDetails": {"totalAmount": str(amount), "currency": currency},
                "billTo": {
                    "firstName": billing_info.first_name,
                    "lastName": billing_info.last_name,
                    "address1": billing_info.address,
                    "locality": billing_info.city_name,
                    "administrativeArea": billing_info.city_code,
                    "postalCode": billing_info.postal_code,
                    "country": billing_info.country_code,
                    "email": billing_info.email,
                    "phoneNumber": billing_info.phone,
                },
            },
            "merchantDefinedInformation": create_merchant_def_map(merchant_defined_data),
            "deviceInformation": {"fingerprintSessionId": transaction_session_id},
        }

        if auth_transaction_id or cavv:
            consumer_auth: ConsumerAuthInfoRequest = {}
            if auth_transaction_id:
                consumer_auth["authenticationTransactionId"] = auth_transaction_id
            if cavv:
                consumer_auth["cavv"] = cavv
            payload["consumerAuthenticationInformation"] = consumer_auth

        response = self.execute_request(self.ROUTE_AUTH_PAYMENTS, "POST", data=payload)
        res_py_obj = response.json()

        return PaymentAuthorizationApiResponse(
            id=res_py_obj["id"],
            status=res_py_obj["status"],
            order_information=res_py_obj["orderInformation"],
            link_payment_auth=LinkResponse(**res_py_obj["_links"]["self"]),
            link_payment_capture=LinkResponse(**res_py_obj["_links"]["capture"]),
            link_reverse_auth=LinkResponse(**res_py_obj["_links"]["authReversal"]),
            raw_response=res_py_obj,
        )

    def get_auth_payment(self, payment_id: str) -> CyberSourceBaseResponse:
        """Get payment authorization details by ID."""
        response = self.execute_request(self.ROUTE_AUTH_PAYMENT.format(id=payment_id), "GET")
        res_py_obj = response.json()
        return CyberSourceBaseResponse(id=res_py_obj["id"], raw_response=res_py_obj)

    def reverse_auth_payment(
        self,
        payment_id: str,
        reason: str,
        transaction_ref: str,
        amount: float,
        currency: CurrencyType,
    ) -> ReverseAuthApiResponse:
        """Cancel authorization BEFORE capture.

        Use this when:
            - Customer cancels order before shipment
            - Payment was authorized but you don't want to capture
            - Need to release the hold on customer's funds

        Timeline constraint:
            - Must be called BEFORE capture_payment
            - After capture, use refund_payment instead

        reverse_auth vs cancel_payment (void):
            - reverse_auth: Cancels authorization, releases hold
            - cancel_payment: Voids a captured payment same day
        """
        payload: ReverseAuthRequest = {
            "clientReferenceInformation": {"code": transaction_ref},
            "orderInformation": {
                "amountDetails": {"totalAmount": str(amount), "currency": currency}
            },
            "reason": reason,
        }
        response = self.execute_request(
            self.ROUTE_REVERSE_AUTH.format(id=payment_id), "POST", data=payload
        )
        res_py_obj = response.json()

        return ReverseAuthApiResponse(
            id=res_py_obj["id"],
            status=res_py_obj["status"],
            raw_response=res_py_obj,
        )

    def capture_payment(
        self, payment_id: str, transaction_ref: str, amount: float, currency: CurrencyType
    ) -> PaymentCaptureApiResponse:
        """Capture a previously authorized payment.

        Use this after payment_authorization to actually charge the card.

        Timeline constraint:
            - Must capture within 7 days of authorization (bank dependent)
            - After 7 days, authorization expires and funds are released

        Partial capture:
            - Can capture less than authorized amount
            - Remaining authorization is automatically reversed
        """
        payload: CapturePaymentRequest = {
            "clientReferenceInformation": {"code": transaction_ref},
            "orderInformation": {
                "amountDetails": {"totalAmount": str(amount), "currency": currency}
            },
        }
        response = self.execute_request(
            self.ROUTE_PAYMENT_CAPTURE.format(id=payment_id), method="POST", data=payload
        )
        res_py_obj = response.json()

        return PaymentCaptureApiResponse(
            id=res_py_obj["id"],
            status=res_py_obj["status"],
            order_information=res_py_obj["orderInformation"],
            link_payment_capture=LinkResponse(**res_py_obj["_links"]["self"]),
            link_void=LinkResponse(**res_py_obj["_links"]["void"]),
            raw_response=res_py_obj,
        )

    def get_capture_payment(self, capture_id: str) -> CyberSourceBaseResponse:
        """Get capture details by ID."""
        res = self.execute_request(self.ROUTE_CAPTURE.format(id=capture_id), method="GET")
        res_py_obj = res.json()
        return CyberSourceBaseResponse(id=res_py_obj["id"], raw_response=res_py_obj)

    def refund_payment(
        self, capture_id: str, transaction_ref: str, amount: float, currency: CurrencyType
    ) -> RefundPaymentApiResponse:
        """Refund a captured payment (use capture_id from direct_payment response).

        Refund vs Void (cancel_payment):
            - refund_payment: Returns money AFTER settlement (next day+), incurs fees
            - cancel_payment: Cancels BEFORE settlement (same day), no fees

        Use refund when:
            - Payment was captured and settled (next day after capture)
            - Customer returns product
            - Partial refund needed

        Partial refund:
            - Can refund less than captured amount
            - Can do multiple partial refunds until total reached
        """
        payload: RefundPaymentRequest = {
            "clientReferenceInformation": {"code": transaction_ref},
            "orderInformation": {
                "amountDetails": {"totalAmount": str(amount), "currency": currency}
            },
        }
        response = self.execute_request(
            self.ROUTE_REFUND_PAYMENT.format(id=capture_id), method="POST", data=payload
        )
        res_py_obj = response.json()

        return RefundPaymentApiResponse(
            id=res_py_obj["id"],
            status=res_py_obj["status"],
            order_information=res_py_obj["orderInformation"],
            link_refund=LinkResponse(**res_py_obj["_links"]["self"]),
            link_void=LinkResponse(**res_py_obj["_links"]["void"]),
            raw_response=res_py_obj,
        )

    def capture_refund(
        self,
        capture_payment_id: str,
        transaction_ref: str,
        amount: float,
        currency: CurrencyType,
    ) -> RefundCaptureApiResponse:
        """Refund using capture_payment_id (from capture_payment response).

        Same as refund_payment but uses different ID:
            - refund_payment: Uses capture_id from direct_payment (auth+capture)
            - capture_refund: Uses capture_payment_id from capture_payment (separate capture)
        """
        payload: RefundPaymentRequest = {
            "clientReferenceInformation": {"code": transaction_ref},
            "orderInformation": {
                "amountDetails": {"totalAmount": str(amount), "currency": currency}
            },
        }
        response = self.execute_request(
            self.ROUTE_REFUND_CAPTURE.format(id=capture_payment_id), "POST", data=payload
        )
        res_py_obj = response.json()

        return RefundCaptureApiResponse(
            raw_response=res_py_obj,
            id=res_py_obj["id"],
            status=res_py_obj["status"],
            order_information=res_py_obj["orderInformation"],
            link_capture_refund=LinkResponse(**res_py_obj["_links"]["self"]),
            link_void_capture=LinkResponse(**res_py_obj["_links"]["void"]),
        )

    def cancel_payment(
        self,
        payment_id: str,
        transaction_ref: str,
    ) -> VoidApiResponse:
        """Void a payment BEFORE settlement (same day only).

        Timeline constraint:
            - Must void SAME DAY before batch settlement (usually end of day)
            - After settlement, use refund_payment instead

        Void vs Refund:
            - void (cancel_payment): Same day, no fees, instant
            - refund: After settlement, incurs fees, takes days

        When to use:
            - Customer cancels order same day
            - Duplicate transaction detected
            - Error in payment amount
        """
        payload: CancelPaymentRequest = {
            "clientReferenceInformation": {"code": transaction_ref},
        }
        response = self.execute_request(
            self.ROUTE_VOID_PAYMENT.format(id=payment_id), method="POST", data=payload
        )
        res_py_obj = response.json()

        return VoidApiResponse(
            id=res_py_obj["id"],
            raw_response=res_py_obj,
        )

    def _extract_tokenized_card_id(self, response: dict) -> str | None:
        """Extract token_id from CyberSource response when card is saved.

        CyberSource returns token in different locations:
        - tokenInformation.paymentInstrument.id (preferred)
        """
        token_info = response.get("tokenInformation", {})
        if token_info:
            payment_instrument = token_info.get("paymentInstrument", {})
            if payment_instrument.get("id"):
                return payment_instrument["id"]

        return None

    def pay_with_new_card_enrollment(
        self,
        transaction_ref: str,
        card: Card,
        cvv: str,
        amount: float,
        currency: CurrencyType,
        billing_info: BillingInformation,
        merchant_defined_data: LinkSerMMDRequired,
        fingerprint_token: str,
        payer_auth_ref_id: str,
        return_url: str | None = None,
        save_card: bool = False,
    ) -> Union[PaymentCaptureApiResponse, PayerAuthenticationResponse]:
        """Pay with new card - Step 1: Enrollment with 3DS.

        For e-commerce payment with new card (not previously saved).

        Flow:
            1. Call this method
            2. If response is PaymentCaptureApiResponse -> Payment complete
            3. If response is PayerAuthenticationResponse with challenge_required=True:
               - Show step_up_url iframe to customer
               - After challenge, call pay_with_new_card_validation()

        Args:
            save_card: If True, card will be tokenized for future use
        """
        payment_info: PaymentInfoRequest = {
            "card": {
                "number": card.card_number,
                "securityCode": cvv,
                "expirationMonth": card.month,
                "expirationYear": card.year,
                "type": card.card_type,
            }
        }

        processing_info: ProcessingInfoRequest = {
            "capture": True,
            "actionList": ["CONSUMER_AUTHENTICATION"],
            "fingerprintSessionId": fingerprint_token,
        }
        if save_card:
            processing_info["actionList"].append("TOKEN_CREATE")
            processing_info["actionTokenTypes"] = ["paymentInstrument"]
            processing_info["authorizationOptions"] = AuthorizationOptionsRequest(
                initiator={
                    "type": "customer",
                    "credentialStoredOnFile": True,
                    "storedCredentialUsed": False,
                }
            )

        payload: PaymentAuthorizationRequest = {
            "clientReferenceInformation": {"code": transaction_ref},
            "paymentInformation": payment_info,
            "orderInformation": {
                "amountDetails": {"totalAmount": str(amount), "currency": currency},
                "billTo": {
                    "firstName": billing_info.first_name,
                    "lastName": billing_info.last_name,
                    "address1": billing_info.address,
                    "locality": billing_info.city_name,
                    "administrativeArea": billing_info.city_code,
                    "postalCode": billing_info.postal_code,
                    "country": billing_info.country_code,
                    "email": billing_info.email,
                    "phoneNumber": billing_info.phone,
                },
            },
            "merchantDefinedInformation": create_merchant_def_map(merchant_defined_data),
            "processingInformation": processing_info,
            "deviceInformation": {"fingerprintSessionId": fingerprint_token},
            "consumerAuthenticationInformation": {"referenceId": payer_auth_ref_id},
        }

        if return_url:
            payload["consumerAuthenticationInformation"]["returnUrl"] = return_url

        response = self.execute_request(self.ROUTE_AUTH_PAYMENTS, "POST", data=payload)
        res_py_obj = response.json()

        status = PaymentAuthorizationStatus(res_py_obj.get("status"))
        if status == PaymentAuthorizationStatus.PENDING_AUTHENTICATION:
            return PayerAuthenticationResponse(
                raw_response=res_py_obj,
                id=res_py_obj.get("id"),
                status=PayerAuthenticationStatus.PENDING_AUTHENTICATION,
                auth_transaction_id=res_py_obj["consumerAuthenticationInformation"][
                    "authenticationTransactionId"
                ],
                client_ref_info=res_py_obj["clientReferenceInformation"]["code"],
                cavv=res_py_obj["consumerAuthenticationInformation"].get("cavv"),
                challenge_required=res_py_obj["consumerAuthenticationInformation"].get(
                    "challengeRequired"
                ),
                access_token=res_py_obj["consumerAuthenticationInformation"].get(
                    "accessToken"
                ),
                step_up_url=res_py_obj["consumerAuthenticationInformation"].get("stepUpUrl"),
                authorization_token=res_py_obj["consumerAuthenticationInformation"].get(
                    "token"
                ),
            )

        return PaymentCaptureApiResponse(
            id=res_py_obj["id"],
            status=status,
            order_information=res_py_obj.get("orderInformation", {}),
            link_payment_capture=LinkResponse(**res_py_obj["_links"]["self"]),
            link_void=LinkResponse(**res_py_obj["_links"]["void"]),
            raw_response=res_py_obj,
            tokenized_card=self._extract_tokenized_card_id(res_py_obj),
        )

    def pay_with_new_card_validation(
        self,
        transaction_ref: str,
        card: Card,
        cvv: str,
        amount: float,
        currency: CurrencyType,
        billing_info: BillingInformation,
        merchant_defined_data: LinkSerMMDRequired,
        fingerprint_token: str,
        auth_transaction_id: str,
        cavv: str | None = None,
        save_card: bool = False,
    ) -> TransactionApiResponse:
        """Pay with new card - Step 2: Validation after 3DS challenge.

        Call this ONLY after customer completes challenge from pay_with_new_card_enrollment().

        Args:
            auth_transaction_id: From PayerAuthenticationResponse.auth_transaction_id
            cavv: From PayerAuthenticationResponse.cavv (if available)
            save_card: Must match value from enrollment call
        """
        payment_info: PaymentInfoRequest = {
            "card": {
                "number": card.card_number,
                "securityCode": cvv,
                "expirationMonth": card.month,
                "expirationYear": card.year,
                "type": card.card_type,
            }
        }

        processing_info: ProcessingInfoRequest = {
            "capture": True,
            "actionList": ["VALIDATE_CONSUMER_AUTHENTICATION"],
            "fingerprintSessionId": fingerprint_token,
        }
        if save_card:
            processing_info["actionList"].append("TOKEN_CREATE")
            processing_info["actionTokenTypes"] = ["paymentInstrument"]
            processing_info["authorizationOptions"] = AuthorizationOptionsRequest(
                initiator={"credentialStoredOnFile": True}
            )

        payload: PaymentAuthorizationRequest = {
            "clientReferenceInformation": {"code": transaction_ref},
            "paymentInformation": payment_info,
            "orderInformation": {
                "amountDetails": {"totalAmount": str(amount), "currency": currency},
                "billTo": {
                    "firstName": billing_info.first_name,
                    "lastName": billing_info.last_name,
                    "address1": billing_info.address,
                    "locality": billing_info.city_name,
                    "administrativeArea": billing_info.city_code,
                    "postalCode": billing_info.postal_code,
                    "country": billing_info.country_code,
                    "email": billing_info.email,
                    "phoneNumber": billing_info.phone,
                },
            },
            "merchantDefinedInformation": create_merchant_def_map(merchant_defined_data),
            "processingInformation": processing_info,
            "consumerAuthenticationInformation": {
                "authenticationTransactionId": auth_transaction_id
            },
        }

        if cavv:
            payload["consumerAuthenticationInformation"]["cavv"] = cavv

        response = self.execute_request(self.ROUTE_AUTH_PAYMENTS, "POST", data=payload)
        res_py_obj = response.json()

        return TransactionApiResponse(
            id=res_py_obj["id"],
            status=res_py_obj["status"],
            raw_response=res_py_obj,
            tokenized_card=self._extract_tokenized_card_id(res_py_obj),
        )

    def pay_with_saved_card_enrollment(
        self,
        transaction_ref: str,
        token_id: str,
        cvv: str,
        amount: float,
        currency: CurrencyType,
        billing_info: BillingInformation,
        merchant_defined_data: LinkSerMMDRequired,
        fingerprint_token: str,
        payer_auth_ref_id: str,
        return_url: str | None = None,
    ) -> Union[PaymentCaptureApiResponse, PayerAuthenticationResponse]:
        """Pay with saved card (CIT) - Step 1: Enrollment with 3DS.

        Customer Initiated Transaction with previously saved card.
        Customer must be present to enter CVV.

        Flow:
            1. Call this method
            2. If response is PaymentCaptureApiResponse -> Payment complete
            3. If response is PayerAuthenticationResponse with challenge_required=True:
               - Show step_up_url iframe to customer
               - After challenge, call pay_with_saved_card_validation()
        """
        payment_info: PaymentInfoRequest = {
            "card": {"securityCode": cvv},
            "paymentInstrument": {"id": token_id},
        }

        processing_info: ProcessingInfoRequest = {
            "capture": True,
            "actionList": ["CONSUMER_AUTHENTICATION"],
            "fingerprintSessionId": fingerprint_token,
            "authorizationOptions": AuthorizationOptionsRequest(
                initiator={"type": "customer", "storedCredentialUsed": True}
            ),
        }

        payload: PaymentAuthorizationRequest = {
            "clientReferenceInformation": {"code": transaction_ref},
            "paymentInformation": payment_info,
            "orderInformation": {
                "amountDetails": {"totalAmount": str(amount), "currency": currency},
                "billTo": {
                    "firstName": billing_info.first_name,
                    "lastName": billing_info.last_name,
                    "address1": billing_info.address,
                    "locality": billing_info.city_name,
                    "administrativeArea": billing_info.city_code,
                    "postalCode": billing_info.postal_code,
                    "country": billing_info.country_code,
                    "email": billing_info.email,
                    "phoneNumber": billing_info.phone,
                },
            },
            "merchantDefinedInformation": create_merchant_def_map(merchant_defined_data),
            "processingInformation": processing_info,
            "deviceInformation": {"fingerprintSessionId": fingerprint_token},
            "consumerAuthenticationInformation": {"referenceId": payer_auth_ref_id},
        }

        if return_url:
            payload["consumerAuthenticationInformation"]["returnUrl"] = return_url

        response = self.execute_request(self.ROUTE_AUTH_PAYMENTS, "POST", data=payload)
        res_py_obj = response.json()

        status = PaymentAuthorizationStatus(res_py_obj.get("status"))
        if status == PaymentAuthorizationStatus.PENDING_AUTHENTICATION:
            return PayerAuthenticationResponse(
                raw_response=res_py_obj,
                id=res_py_obj.get("id"),
                status=PayerAuthenticationStatus.PENDING_AUTHENTICATION,
                auth_transaction_id=res_py_obj["consumerAuthenticationInformation"][
                    "authenticationTransactionId"
                ],
                client_ref_info=res_py_obj["clientReferenceInformation"]["code"],
                cavv=res_py_obj["consumerAuthenticationInformation"].get("cavv"),
                challenge_required=res_py_obj["consumerAuthenticationInformation"].get(
                    "challengeRequired"
                ),
                access_token=res_py_obj["consumerAuthenticationInformation"].get(
                    "accessToken"
                ),
                step_up_url=res_py_obj["consumerAuthenticationInformation"].get("stepUpUrl"),
                authorization_token=res_py_obj["consumerAuthenticationInformation"].get(
                    "token"
                ),
            )

        return PaymentCaptureApiResponse(
            id=res_py_obj["id"],
            status=status,
            order_information=res_py_obj.get("orderInformation", {}),
            link_payment_capture=LinkResponse(**res_py_obj["_links"]["self"]),
            link_void=LinkResponse(**res_py_obj["_links"]["void"]),
            raw_response=res_py_obj,
        )

    def pay_with_saved_card_validation(
        self,
        transaction_ref: str,
        token_id: str,
        cvv: str,
        amount: float,
        currency: CurrencyType,
        billing_info: BillingInformation,
        merchant_defined_data: LinkSerMMDRequired,
        fingerprint_token: str,
        auth_transaction_id: str,
        cavv: str | None = None,
    ) -> TransactionApiResponse:
        """Pay with saved card (CIT) - Step 2: Validation after 3DS challenge.

        Call this ONLY after customer completes challenge from pay_with_saved_card_enrollment().
        """
        payment_info: PaymentInfoRequest = {
            "card": {"securityCode": cvv},
            "paymentInstrument": {"id": token_id},
        }

        processing_info: ProcessingInfoRequest = {
            "capture": True,
            "actionList": ["VALIDATE_CONSUMER_AUTHENTICATION"],
            "fingerprintSessionId": fingerprint_token,
            "authorizationOptions": AuthorizationOptionsRequest(
                initiator={"type": "customer", "storedCredentialUsed": True}
            ),
        }

        payload: PaymentAuthorizationRequest = {
            "clientReferenceInformation": {"code": transaction_ref},
            "paymentInformation": payment_info,
            "orderInformation": {
                "amountDetails": {"totalAmount": str(amount), "currency": currency},
                "billTo": {
                    "firstName": billing_info.first_name,
                    "lastName": billing_info.last_name,
                    "address1": billing_info.address,
                    "locality": billing_info.city_name,
                    "administrativeArea": billing_info.city_code,
                    "postalCode": billing_info.postal_code,
                    "country": billing_info.country_code,
                    "email": billing_info.email,
                    "phoneNumber": billing_info.phone,
                },
            },
            "merchantDefinedInformation": create_merchant_def_map(merchant_defined_data),
            "processingInformation": processing_info,
            "consumerAuthenticationInformation": {
                "authenticationTransactionId": auth_transaction_id
            },
        }

        if cavv:
            payload["consumerAuthenticationInformation"]["cavv"] = cavv

        response = self.execute_request(self.ROUTE_AUTH_PAYMENTS, "POST", data=payload)
        res_py_obj = response.json()

        return TransactionApiResponse(
            id=res_py_obj["id"],
            status=res_py_obj["status"],
            raw_response=res_py_obj,
        )

    def merchant_initiated_payment(
        self,
        transaction_ref: str,
        token_id: str,
        amount: float,
        currency: CurrencyType,
        billing_info: BillingInformation,
        merchant_defined_data: LinkSerMMDRequired,
        commerce_indicator: str = "recurring",
    ) -> PaymentCaptureApiResponse:
        """Merchant Initiated Transaction (MIT) - Recurring/Subscription payment.

        NO customer present, NO CVV, NO 3DS.
        For automatic charges like subscriptions, recurring billing, installments.

        Args:
            commerce_indicator: "recurring" for subscriptions, "installment" for split payments

        Prerequisites:
            - Card must have been saved with customer consent in a previous CIT transaction
            - Original transaction must have used store_card=True or credentialStoredOnFile=True
        """
        payment_info: PaymentInfoRequest = {
            "paymentInstrument": {"id": token_id},
        }

        processing_info: ProcessingInfoRequest = {
            "capture": True,
            "commerceIndicator": commerce_indicator,
            "authorizationOptions": AuthorizationOptionsRequest(
                initiator={"type": "merchant", "storedCredentialUsed": True}
            ),
        }

        payload: PaymentAuthorizationRequest = {
            "clientReferenceInformation": {"code": transaction_ref},
            "paymentInformation": payment_info,
            "orderInformation": {
                "amountDetails": {"totalAmount": str(amount), "currency": currency},
                "billTo": {
                    "firstName": billing_info.first_name,
                    "lastName": billing_info.last_name,
                    "address1": billing_info.address,
                    "locality": billing_info.city_name,
                    "administrativeArea": billing_info.city_code,
                    "postalCode": billing_info.postal_code,
                    "country": billing_info.country_code,
                    "email": billing_info.email,
                    "phoneNumber": billing_info.phone,
                },
            },
            "merchantDefinedInformation": create_merchant_def_map(merchant_defined_data),
            "processingInformation": processing_info,
        }

        response = self.execute_request(self.ROUTE_AUTH_PAYMENTS, "POST", data=payload)
        res_py_obj = response.json()

        return PaymentCaptureApiResponse(
            id=res_py_obj["id"],
            status=res_py_obj["status"],
            order_information=res_py_obj.get("orderInformation", {}),
            link_payment_capture=LinkResponse(**res_py_obj["_links"]["self"]),
            link_void=LinkResponse(**res_py_obj["_links"]["void"]),
            raw_response=res_py_obj,
        )
