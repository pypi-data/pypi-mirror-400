"""Banco Económico authentication and encryption adapter."""

from enum import StrEnum
from typing import TypedDict

from sincpro_payments_sdk.apps.qr.domain.economico import BancoEconomicoCredentials
from sincpro_payments_sdk.infrastructure.client_api import ClientAPI

from .economico_common import economico_credential_provider


class AuthenticateRequest(TypedDict):
    userName: str
    password: str


class AuthRoutes(StrEnum):
    """Banco Económico authentication routes."""

    ENCRYPT = "/ApiGateway/api/authentication/encrypt"
    DECRYPT = "/ApiGateway/api/authentication/decrypt"
    AUTHENTICATE = "/ApiGateway/api/authentication/authenticate"


class BancoEconomicoAuthAdapter(ClientAPI):
    """Adapter for Banco Económico authentication and encryption operations."""

    def __init__(self):
        """Initialize without auth since these endpoints don't require Bearer token."""
        super().__init__(auth=None)

    @property
    def base_url(self) -> str:
        """Get the base URL for the Banco Económico API."""
        credentials = economico_credential_provider.get_credentials()
        return credentials.endpoint

    def encrypt(self, text: str, aes_key: str) -> str:
        """Encrypt text using Banco Económico encryption API.

        Args:
            text: Text to encrypt
            aes_key: AES-256 key (32 bytes)

        Returns:
            Encrypted text
        """
        response = self.execute_request(
            AuthRoutes.ENCRYPT,
            "GET",
            params={"text": text, "aesKey": aes_key},
            timeout=30,
        )
        return response.json()

    def decrypt(self, text: str, aes_key: str) -> str:
        """Decrypt text using Banco Económico decryption API.

        Args:
            text: Encrypted text
            aes_key: AES-256 key (32 bytes)

        Returns:
            Decrypted text
        """
        response = self.execute_request(
            AuthRoutes.DECRYPT,
            "GET",
            params={"text": text, "aesKey": aes_key},
            timeout=30,
        )
        return response.json()

    def authenticate(
        self, credentials: BancoEconomicoCredentials
    ) -> BancoEconomicoCredentials:
        """Authenticate with Banco Económico and obtain Bearer token.

        Args:
            credentials: Banco Económico credentials with username and password

        Returns:
            Updated credentials with bearer_token
        """
        encrypted_password = self.encrypt(credentials.password, credentials.aes_key)

        payload: AuthenticateRequest = {
            "userName": credentials.user_name,
            "password": encrypted_password,
        }

        response = self.execute_request(
            AuthRoutes.AUTHENTICATE,
            "POST",
            data=payload,
            timeout=30,
        )

        response_data = response.json()

        bearer_token = (
            response_data.get("token")
            or response_data.get("bearerToken")
            or response_data.get("access_token")
        )

        if not bearer_token:
            bearer_token = response_data.get("data", {}).get("token")

        return BancoEconomicoCredentials(
            user_name=credentials.user_name,
            password=credentials.password,
            aes_key=credentials.aes_key,
            endpoint=credentials.endpoint,
            bearer_token=bearer_token,
        )
