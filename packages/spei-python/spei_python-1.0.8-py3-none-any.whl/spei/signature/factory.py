from spei.signature import payload as signature_payload
from spei.signature import types as signature_types
from spei.signature.payload import SignaturePayloadBuilder
from spei.types import TipoPagoOrdenPago

_BENEFICIARY_EXTRA_ACCOUNT_ATTR = (
    'PAYMENT_TYPES_WITH_BENEFICIARY_AND_ADDITIONAL_BENEFICIARY_ACCOUNT'
)
_BENEFICIARY_EXTRA_ACCOUNT_TYPES = getattr(
    signature_types,
    _BENEFICIARY_EXTRA_ACCOUNT_ATTR,
)

_ORIGIN_BENEFICIARY_EXTRA_ACCOUNT_ATTR = (
    'PAYMENT_TYPES_WITH_ORIGIN_BENEFICIARY_AND_ADDITIONAL_BENEFICIARY_ACCOUNT'
)
_ORIGIN_BENEFICIARY_EXTRA_ACCOUNT_TYPES = getattr(
    signature_types,
    _ORIGIN_BENEFICIARY_EXTRA_ACCOUNT_ATTR,
)

_BUILDER_BY_PAYMENT_GROUP = (
    (
        signature_types.PAYMENT_TYPES_WITH_DEFAULT_FIELDS,
        signature_payload.DefaultSignaturePayloadBuilder,
    ),
    (
        signature_types.PAYMENT_TYPES_WITH_ORIGIN_ACCOUNT,
        signature_payload.OriginSignaturePayloadBuilder,
    ),
    (
        signature_types.PAYMENT_TYPES_WITH_BENEFICIARY_ACCOUNT,
        signature_payload.BeneficiarySignaturePayloadBuilder,
    ),
    (
        signature_types.PAYMENT_TYPES_WITH_ORIGIN_AND_BENEFICIARY_ACCOUNT,
        signature_payload.OriginAndBeneficiarySignaturePayloadBuilder,
    ),
    (
        _BENEFICIARY_EXTRA_ACCOUNT_TYPES,
        signature_payload.BeneficiaryAndAdditionalBeneficiarySignaturePayloadBuilder,
    ),
    (
        signature_types.REMITTANCE_PAYMENT_TYPES,
        signature_payload.RemittanceSignaturePayloadBuilder,
    ),
    (
        signature_types.INDIRECT_PAYMENT_TYPES,
        signature_payload.IndirectSignaturePayloadBuilder,
    ),
    (
        _ORIGIN_BENEFICIARY_EXTRA_ACCOUNT_TYPES,
        signature_payload.EveryFieldSignaturePayloadBuilder,
    ),
)


def get_signature_builder(
    payment_type: TipoPagoOrdenPago,
) -> SignaturePayloadBuilder:
    for payment_group, builder_factory in _BUILDER_BY_PAYMENT_GROUP:
        if payment_type in payment_group:
            return builder_factory()

    if payment_type == TipoPagoOrdenPago.tercero_indirecto_a_participante:
        return signature_payload.IndirectToParticipantSignaturePayloadBuilder()

    raise NotImplementedError


__all__ = ['get_signature_builder']
