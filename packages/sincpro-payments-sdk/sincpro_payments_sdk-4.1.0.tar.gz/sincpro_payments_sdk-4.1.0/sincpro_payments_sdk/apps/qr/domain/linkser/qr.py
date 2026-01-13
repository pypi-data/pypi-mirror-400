"""QR Linkser Domain Models based on PRD specifications."""

from enum import StrEnum
from typing import NewType

from sincpro_framework import DataTransferObject

QRCode = NewType("QRCode", str)


class QRStatus(StrEnum):
    """Status for a QR transaction according to PRD."""

    PENDIENTE = "Pendiente"  # QR generated but not paid
    CONFIRMADO = "Confirmado"  # Payment processed successfully
    RECHAZADO = "Rechazado"  # Payment could not be processed


class QRImageLinkser(DataTransferObject):
    """QR image response from generateQR API."""

    # Response fields from PRD (will be determined from actual API response)
    codigo_qr: QRCode  # QR code identifier
    imagen_qr: str  # Base64 encoded QR image with data:image/png;base64, prefix
    fecha_generacion: str | None = None  # Generation date in DD-MMM-YY HH:MM:SS format
    estado: QRStatus = QRStatus.PENDIENTE


class QRStatusLinkser(DataTransferObject):
    """QR status response from consultQR API."""

    codigo_qr: QRCode
    estado: QRStatus
    fecha_transaccion: str | None = None  # Transaction date in DD-MMM-YY HH:MM:SS format
    importe_pagado: str | None = None  # Amount paid if confirmed
