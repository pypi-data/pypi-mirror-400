"""Banco Económico QR domain models based on API specifications."""

from datetime import date, datetime
from enum import IntEnum
from typing import NewType

from pydantic import Field
from sincpro_framework import DataTransferObject

from sincpro_payments_sdk.apps.common.domain import CurrencyType

QRId = NewType("QRId", str)


class QRStatusCode(IntEnum):
    """QR status codes from Banco Económico API.

    Based on section 7.4 of API documentation.
    """

    ACTIVE_PENDING = 0
    PAID = 1
    CANCELLED = 9


class QRImageEconomico(DataTransferObject):
    """QR image response from generateQR API."""

    qr_id: QRId
    transaction_id: str
    amount: float
    currency: CurrencyType
    due_date: date
    single_use: bool
    modify_amount: bool
    qr_image: str | None = Field(default=None, repr=False)


class PaymentQR(DataTransferObject):
    """Payment information from statusQR API (Anexo - Objeto PaymentQR)."""

    qr_id: QRId
    transaction_id: str
    payment_date: datetime
    payment_time: str
    currency: CurrencyType
    amount: float
    sender_bank_code: str
    sender_name: str
    sender_document_id: str
    sender_account: str

    @property
    def payment_date_only(self) -> date:
        """Get payment date without time."""
        return self.payment_date.date()


class QRStatusEconomico(DataTransferObject):
    """QR status response from statusQR API."""

    status_qr_code: QRStatusCode | None = None
    payments: list[PaymentQR] = []
