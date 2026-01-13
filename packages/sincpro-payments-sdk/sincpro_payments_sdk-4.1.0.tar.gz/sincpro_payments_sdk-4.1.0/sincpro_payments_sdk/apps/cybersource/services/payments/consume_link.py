"""Consume generated link.

.. deprecated:: 2.0.0
    This is an internal utility. Use specific service methods instead.
"""

import warnings

from sincpro_payments_sdk.apps.cybersource import DataTransferObject, Feature, cybersource

_DEPRECATION_MSG = (
    "ConsumeLink is deprecated. Use specific service methods instead of raw link consumption."
)


class CommandConsumeLink(DataTransferObject):
    """.. deprecated:: 2.0.0"""

    resource: str


class ResponseConsumeLink(DataTransferObject):
    """.. deprecated:: 2.0.0"""

    raw_response: dict | None = None


@cybersource.feature(CommandConsumeLink)
class ConsumeLink(Feature):
    """.. deprecated:: 2.0.0"""

    def execute(self, dto: CommandConsumeLink) -> ResponseConsumeLink:
        warnings.warn(_DEPRECATION_MSG, DeprecationWarning, stacklevel=2)
        response = self.payment_adapter.execute_request(dto.resource, "GET")
        return ResponseConsumeLink(raw_response=response.json())
