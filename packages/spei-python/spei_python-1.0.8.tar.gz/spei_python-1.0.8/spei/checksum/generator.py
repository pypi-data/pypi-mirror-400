import warnings

from spei.signature import payload as signature_payload


def _warn(name: str) -> None:
    warnings.warn(
        f'{name} is deprecated; use spei.signature.payload equivalents instead.',
        DeprecationWarning,
        stacklevel=3,
    )


class ChecksumGenerator(
    signature_payload.SignaturePayloadBuilder,
):
    def __init__(self, *args, **kwargs):
        _warn('ChecksumGenerator')
        super().__init__(*args, **kwargs)


class ChecksumGeneratorRemittance(
    signature_payload.RemittanceSignaturePayloadBuilder,
):
    def __init__(self, *args, **kwargs):
        _warn('ChecksumGeneratorRemittance')
        super().__init__(*args, **kwargs)


class ChecksumGeneratorDefault(
    signature_payload.DefaultSignaturePayloadBuilder,
):
    def __init__(self, *args, **kwargs):
        _warn('ChecksumGeneratorDefault')
        super().__init__(*args, **kwargs)


class ChecksumGeneratorOrigin(
    signature_payload.OriginSignaturePayloadBuilder,
):
    def __init__(self, *args, **kwargs):
        _warn('ChecksumGeneratorOrigin')
        super().__init__(*args, **kwargs)


class ChecksumGeneratorBeneficiary(
    signature_payload.BeneficiarySignaturePayloadBuilder,
):
    def __init__(self, *args, **kwargs):
        _warn('ChecksumGeneratorBeneficiary')
        super().__init__(*args, **kwargs)


class ChecksumGeneratorOriginAndBeneficiary(
    signature_payload.OriginAndBeneficiarySignaturePayloadBuilder,
):
    def __init__(self, *args, **kwargs):
        _warn('ChecksumGeneratorOriginAndBeneficiary')
        super().__init__(*args, **kwargs)


class ChecksumGeneratorBeneficiaryAndAdditionalBeneficiary(
    signature_payload.BeneficiaryAndAdditionalBeneficiarySignaturePayloadBuilder,
):
    def __init__(self, *args, **kwargs):
        _warn('ChecksumGeneratorBeneficiaryAndAdditionalBeneficiary')
        super().__init__(*args, **kwargs)


class ChecksumGeneratorIndirectToParticipant(
    signature_payload.IndirectToParticipantSignaturePayloadBuilder,
):
    def __init__(self, *args, **kwargs):
        _warn('ChecksumGeneratorIndirectToParticipant')
        super().__init__(*args, **kwargs)


class ChecksumGeneratorIndirect(
    signature_payload.IndirectSignaturePayloadBuilder,
):
    def __init__(self, *args, **kwargs):
        _warn('ChecksumGeneratorIndirect')
        super().__init__(*args, **kwargs)


class ChecksumGeneratorEveryField(
    signature_payload.EveryFieldSignaturePayloadBuilder,
):
    def __init__(self, *args, **kwargs):
        _warn('ChecksumGeneratorEveryField')
        super().__init__(*args, **kwargs)


__all__ = [
    'ChecksumGenerator',
    'ChecksumGeneratorBeneficiary',
    'ChecksumGeneratorBeneficiaryAndAdditionalBeneficiary',
    'ChecksumGeneratorDefault',
    'ChecksumGeneratorEveryField',
    'ChecksumGeneratorIndirect',
    'ChecksumGeneratorIndirectToParticipant',
    'ChecksumGeneratorOrigin',
    'ChecksumGeneratorOriginAndBeneficiary',
    'ChecksumGeneratorRemittance',
]
