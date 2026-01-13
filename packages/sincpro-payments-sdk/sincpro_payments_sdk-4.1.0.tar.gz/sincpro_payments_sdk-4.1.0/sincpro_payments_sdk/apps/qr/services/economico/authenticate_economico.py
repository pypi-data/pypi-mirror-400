"""Authenticate with Banco Económico API."""

from sincpro_payments_sdk import exceptions
from sincpro_payments_sdk.apps.qr import DataTransferObject, Feature, qr
from sincpro_payments_sdk.apps.qr.domain.economico import (
    BancoEconomicoCredentials,
    BancoEconomicoEndPoints,
)


class CommandAuthenticateEconomico(DataTransferObject):
    """Authenticate Banco Económico."""

    user_name: str
    password: str
    aes_key: str
    production_mode: bool = False


class ResponseAuthenticateEconomico(BancoEconomicoCredentials):
    """Authenticate Banco Económico response."""


@qr.feature(CommandAuthenticateEconomico)
class AuthenticateEconomico(Feature):
    """Authenticate with Banco Económico and obtain Bearer token."""

    def execute(self, dto: CommandAuthenticateEconomico) -> ResponseAuthenticateEconomico:
        """Authenticate Banco Económico."""
        credentials = BancoEconomicoCredentials(
            user_name=dto.user_name,
            password=dto.password,
            aes_key=dto.aes_key,
            endpoint=(
                BancoEconomicoEndPoints.CERTIFICATION
                if not dto.production_mode
                else BancoEconomicoEndPoints.PRODUCTION
            ),
        )

        authenticated_credentials = self.economico_auth_adapter.authenticate(credentials)

        if not authenticated_credentials.bearer_token:
            raise exceptions.SincproValidationError(
                "Could not authenticate Banco Económico account"
            )

        qr.logger.info(
            f"Authenticated Banco Económico account {dto.user_name}",
            production=dto.production_mode,
        )

        self.economico_credential_provider.set_loader_credentials(
            lambda: authenticated_credentials
        )

        return ResponseAuthenticateEconomico.model_construct(
            **authenticated_credentials.model_dump()
        )
