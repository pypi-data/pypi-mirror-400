"""BNB Credentials setup for QR API."""

from enum import StrEnum

from sincpro_framework import DataTransferObject


class BNBEndPoints(StrEnum):
    """BNB credential types."""

    SAND_BOX = "http://test.bnb.com.bo"
    PRODUCTION = "https://marketapi.bnb.com.bo"


class QRBNBCredentials(DataTransferObject):
    """Credentials for BNB QR API."""

    account_id: str
    authorization_id: str
    endpoint: BNBEndPoints
    jwt_token: str | None = None


class UpdateAuthId(DataTransferObject):
    """Update the authorization ID."""

    account_id: str
    current_auth_id: str
    new_auth_id: str
    jwt_token: str
