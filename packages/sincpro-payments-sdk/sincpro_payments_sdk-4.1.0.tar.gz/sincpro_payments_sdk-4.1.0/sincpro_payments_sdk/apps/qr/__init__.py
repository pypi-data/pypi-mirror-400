"""Framework for QR code generation and payment processing."""

from .infrastructure.framework import (
    ApplicationService,
    DataTransferObject,
    Feature,
    config_framework,
)

qr = config_framework("payment-qr")

from .services import bnb, economico, linkser

__all__ = [
    "qr",
    "bnb",
    "linkser",
    "economico",
    "Feature",
    "ApplicationService",
    "DataTransferObject",
]
