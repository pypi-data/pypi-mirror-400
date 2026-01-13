"""Linkser credentials model."""

from sincpro_framework import DataTransferObject


class LinkserCredentials(DataTransferObject):
    """Linkser API credentials for JWT authentication."""

    codigo_comercio: str  # 7-digit merchant code
    jwt_token: str  # JWT token for LINKSER-KEY header
    endpoint: str
    production_mode: bool = False
