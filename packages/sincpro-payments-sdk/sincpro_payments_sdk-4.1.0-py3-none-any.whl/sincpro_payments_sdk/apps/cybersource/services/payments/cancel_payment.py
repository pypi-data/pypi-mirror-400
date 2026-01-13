"""Use case to cancel a payment.

.. deprecated:: 2.0.0
    Use CancelOrRefund from cancel_or_refund instead.
"""

import warnings

from sincpro_payments_sdk.apps.cybersource import DataTransferObject, Feature, cybersource

_DEPRECATION_MSG = (
    "CancelPayment is deprecated. Use CancelOrRefund from cancel_or_refund instead."
)


class CmdCancelPayment(DataTransferObject):
    """.. deprecated:: 2.0.0"""

    payment_id: str
    transaction_ref: str


class ResCancelPayment(DataTransferObject):
    """.. deprecated:: 2.0.0"""

    id: str
    raw_response: dict


@cybersource.feature(CmdCancelPayment)
class CancelPayment(Feature):
    """.. deprecated:: 2.0.0 Use CancelOrRefund instead."""

    def execute(self, dto: CmdCancelPayment) -> ResCancelPayment:
        warnings.warn(_DEPRECATION_MSG, DeprecationWarning, stacklevel=2)
        void_payment = self.payment_adapter.cancel_payment(
            dto.payment_id,
            dto.transaction_ref,
        )

        return ResCancelPayment(
            id=void_payment.id,
            raw_response=void_payment.raw_response,
        )
