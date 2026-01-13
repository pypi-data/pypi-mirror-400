"""Domain module for payments."""

from enum import StrEnum
from typing import Literal

from sincpro_framework import DataTransferObject

from sincpro_payments_sdk.apps.common.domain import CurrencyType


class PayerAuthenticationStatus(StrEnum):
    """Payer auth status enumeration."""

    AUTHENTICATION_SUCCESSFUL = "AUTHENTICATION_SUCCESSFUL"
    PENDING_AUTHENTICATION = "PENDING_AUTHENTICATION"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"


class PaymentAuthorizationStatus(StrEnum):
    """Status response enumeration."""

    AUTHORIZED = "AUTHORIZED"
    PARTIAL_AUTHORIZED = "PARTIAL_AUTHORIZED"
    AUTHORIZED_PENDING_REVIEW = "AUTHORIZED_PENDING_REVIEW"
    AUTHORIZED_RISK_DECLINED = "AUTHORIZED_RISK_DECLINED"
    PENDING_AUTHENTICATION = "PENDING_AUTHENTICATION"
    PENDING_REVIEW = "PENDING_REVIEW"
    DECLINED = "DECLINED"
    INVALID_REQUEST = "INVALID_REQUEST"


class CaptureState(StrEnum):
    """Capture state enumeration."""

    PENDING = "PENDING"
    TRANSMITTED = "TRANSMITTED"


class AmountDetails(DataTransferObject):
    """Amount details."""

    total_amount: float
    currency: CurrencyType


SourceOptions = str  # Valid: "WEB", "APP", "POS", "PLUGIN"
IndustrySectorOptions = str  # Valid: "SERVICIOS DE SOFTWARE", "SERVICIO PROFESIONAL"


class LinkSerMMDRequired(DataTransferObject):
    """LinkSer MMD Required."""

    #: Is user logged in?
    merchant_defined_data_1: Literal["SI", "NO"]

    #: Customer name TODO: Check if this is required
    merchant_defined_data_7: str

    #: Source of the transaction
    merchant_defined_data_9: SourceOptions

    #: CI/NIT Customer
    merchant_defined_data_11: str

    #: Customer Phone
    merchant_defined_data_12: str

    #: Industry sector
    merchant_defined_data_14: IndustrySectorOptions

    #: Customer external ID (From software)
    merchant_defined_data_15: str

    #: CI/NIT Company supplier
    merchant_defined_data_87: str

    #: Company name supplier
    merchant_defined_data_88: str

    #: Product description
    merchant_defined_data_90: str


class PaymentMethod(DataTransferObject):
    """Payment method information."""

    type: str
    detail: dict
    token: str


class Payment(DataTransferObject):
    """General payment information."""

    amount: float
    currency: str
    payment_method: PaymentMethod
    status: str
