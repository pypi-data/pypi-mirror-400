"""Banco Económico credential providers and authentication."""

from requests.auth import AuthBase
from sincpro_framework import logger

from sincpro_payments_sdk.apps.qr.domain.economico import (
    BancoEconomicoCredentials,
    BancoEconomicoEndPoints,
)
from sincpro_payments_sdk.infrastructure.provider_credentials import CredentialProvider


class BearerTokenAuth(AuthBase):
    """Bearer token authentication for Banco Económico API."""

    def __init__(
        self, economico_credential_provider: CredentialProvider[BancoEconomicoCredentials]
    ):
        self._economico_credential_provider = economico_credential_provider
        self.bearer_token: str | None = None

    def _set_credentials_from_callable_ref(self):
        credentials = self._economico_credential_provider.get_credentials()
        self.bearer_token = credentials.bearer_token

    def build_headers(self) -> dict:
        """Build headers for Banco Económico authentication."""
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
        }
        return headers

    def __call__(self, request):
        """Customize the request with Bearer token authentication."""
        self._set_credentials_from_callable_ref()

        headers = self.build_headers()
        request.headers.update(headers)
        logger.debug(f"Request headers: {request.headers}")

        return request


def _get_default_credentials() -> BancoEconomicoCredentials:

    return BancoEconomicoCredentials(
        user_name="26551010",
        password="1234",
        aes_key="40A318B299F245C2B697176723088629",
        endpoint=BancoEconomicoEndPoints.CERTIFICATION,
    )


economico_credential_provider = CredentialProvider[BancoEconomicoCredentials](
    _get_default_credentials
)
