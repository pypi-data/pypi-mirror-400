import warnings

from spei.signature.factory import get_signature_builder
from spei.signature.payload import SignaturePayloadBuilder
from spei.types import TipoPagoOrdenPago


def get_checksum_generator(payment_type: TipoPagoOrdenPago) -> SignaturePayloadBuilder:
    warnings.warn(
        'get_checksum_generator is deprecated; use spei.signature.factory.get_signature_builder instead.',  # noqa: E501
        DeprecationWarning,
        stacklevel=2,
    )
    return get_signature_builder(payment_type)


__all__ = ['get_checksum_generator']
