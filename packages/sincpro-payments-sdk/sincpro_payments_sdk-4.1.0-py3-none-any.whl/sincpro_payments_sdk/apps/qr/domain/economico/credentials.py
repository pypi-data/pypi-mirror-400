"""Banco Económico credentials model."""

from enum import StrEnum

from sincpro_framework import DataTransferObject


class BancoEconomicoEndPoints(StrEnum):
    """Banco Económico endpoint types."""

    CERTIFICATION = "https://apimktdesa.baneco.com.bo"
    PRODUCTION = "https://apimkt.bancavive.com.bo"


class BancoEconomicoCredentials(DataTransferObject):
    """Credentials for Banco Económico API."""

    user_name: str  # Username for authentication
    password: str  # Password (will be encrypted before sending)
    aes_key: str  # AES-256 key provided by the bank (32 bytes)
    endpoint: BancoEconomicoEndPoints
    bearer_token: str | None = None  # JWT token obtained after authentication
