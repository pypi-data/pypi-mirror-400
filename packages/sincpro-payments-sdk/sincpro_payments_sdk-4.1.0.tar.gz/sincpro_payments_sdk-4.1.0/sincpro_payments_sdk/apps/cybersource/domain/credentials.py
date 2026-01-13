"""Domain module for Cybersource credentials."""

from enum import StrEnum

from sincpro_framework import DataTransferObject


class CybersourceEndPoints(StrEnum):
    """Cybersource credential types."""

    SAND_BOX = "apitest.cybersource.com"
    PRODUCTION = "api.cybersource.com"


class CybersourceCredential(DataTransferObject):
    """Base class for Cybersource credentials."""

    key_id: str
    secret_key: str
    merchant_id: str
    endpoint: CybersourceEndPoints
    profile_id: str | None = None
