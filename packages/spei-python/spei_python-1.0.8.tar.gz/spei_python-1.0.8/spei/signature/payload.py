import warnings
from datetime import date
from decimal import Decimal
from typing import Optional, Tuple

from spei.resources import Orden


class SignaturePayloadBuilder(object):
    """Builds byte payloads to sign or verify SPEI orders."""

    def build(self, orden: Orden) -> bytes:
        raise NotImplementedError

    def format_data(self, orden: Orden) -> bytes:
        warnings.warn(
            'SignaturePayloadBuilder.format_data is deprecated; use build instead.',
            DeprecationWarning,
            stacklevel=2,
        )
        return self.build(orden)

    def split_amount(self, amount: str) -> Tuple[int, int]:
        amount_as_cents = int(Decimal(str(amount)) * 100)
        high = 0
        low = amount_as_cents
        tens_of_millions = amount_as_cents // 10**9
        if tens_of_millions:
            high = tens_of_millions
            low = amount_as_cents - (tens_of_millions * 10**9)
        return high, low

    def _fecha_to_bytearray(self, fecha_operacion: date) -> bytearray:
        day = int.to_bytes(int(fecha_operacion.day), 1, 'big')
        month = int.to_bytes(int(fecha_operacion.month), 1, 'big')
        year = int.to_bytes(int(fecha_operacion.year), 2, 'big')

        return bytearray(day + month + year)

    def _clave_to_bytearray(self, clave: Optional[str]) -> bytearray:
        clave = clave or ''

        return bytearray(int.to_bytes(int(clave), 4, 'big'))

    def _monto_to_bytearray(self, amount: str) -> bytearray:
        high_value, low_value = self.split_amount(amount)
        high_bytes = int.to_bytes(int(high_value), 4, 'big')
        low_bytes = int.to_bytes(int(low_value), 4, 'big')

        return bytearray(high_bytes + low_bytes)

    def _to_byte_array(
        self,
        value: Optional[str],
        add_zero_byte: bool = False,
    ) -> bytearray:
        value = value or ''
        encoded = value.encode('utf-8')
        bytes_ = bytearray(encoded)
        if add_zero_byte:
            bytes_.append(0)

        return bytes_

    def _list_to_bytes(
        self,
        message_data: Tuple[bytearray, ...],
    ) -> bytes:
        res = bytearray()
        for field in message_data:
            for element in field:
                res.append(element)

        return bytes(res)


class RemittanceSignaturePayloadBuilder(
    SignaturePayloadBuilder,
):
    def build(self, orden: Orden) -> bytes:
        message_data = (
            self._fecha_to_bytearray(orden.op_fecha_oper),
            self._clave_to_bytearray(str(orden.op_ins_clave_ord)),
            self._clave_to_bytearray(str(orden.op_ins_clave_ben)),
            self._to_byte_array(orden.op_cve_rastreo, add_zero_byte=True),
            self._monto_to_bytearray(orden.op_monto),
            self._to_byte_array(orden.op_cuenta_ord, add_zero_byte=True),
            self._to_byte_array(orden.op_cuenta_ben, add_zero_byte=True),
            self._to_byte_array(
                orden.op_cuenta_participante_ord,
                add_zero_byte=True,
            ),
        )
        return self._list_to_bytes(message_data)


class DefaultSignaturePayloadBuilder(
    SignaturePayloadBuilder,
):
    def build(self, orden: Orden) -> bytes:
        message_data = (
            self._fecha_to_bytearray(orden.op_fecha_oper),
            self._clave_to_bytearray(str(orden.op_ins_clave_ord)),
            self._clave_to_bytearray(str(orden.op_ins_clave_ben)),
            self._to_byte_array(orden.op_cve_rastreo, add_zero_byte=True),
            self._monto_to_bytearray(orden.op_monto),
        )
        return self._list_to_bytes(message_data)


class OriginSignaturePayloadBuilder(
    SignaturePayloadBuilder,
):
    def build(self, orden: Orden) -> bytes:
        message_data = (
            self._fecha_to_bytearray(orden.op_fecha_oper),
            self._clave_to_bytearray(str(orden.op_ins_clave_ord)),
            self._clave_to_bytearray(str(orden.op_ins_clave_ben)),
            self._to_byte_array(orden.op_cve_rastreo, add_zero_byte=True),
            self._monto_to_bytearray(orden.op_monto),
            self._to_byte_array(orden.op_cuenta_ord, add_zero_byte=True),
        )
        return self._list_to_bytes(message_data)


class BeneficiarySignaturePayloadBuilder(
    SignaturePayloadBuilder,
):
    def build(self, orden: Orden) -> bytes:
        message_data = (
            self._fecha_to_bytearray(orden.op_fecha_oper),
            self._clave_to_bytearray(str(orden.op_ins_clave_ord)),
            self._clave_to_bytearray(str(orden.op_ins_clave_ben)),
            self._to_byte_array(orden.op_cve_rastreo, add_zero_byte=True),
            self._monto_to_bytearray(orden.op_monto),
            self._to_byte_array(orden.op_cuenta_ben, add_zero_byte=True),
        )
        return self._list_to_bytes(message_data)


class OriginAndBeneficiarySignaturePayloadBuilder(
    SignaturePayloadBuilder,
):
    def build(self, orden: Orden) -> bytes:
        message_data = (
            self._fecha_to_bytearray(orden.op_fecha_oper),
            self._clave_to_bytearray(str(orden.op_ins_clave_ord)),
            self._clave_to_bytearray(str(orden.op_ins_clave_ben)),
            self._to_byte_array(orden.op_cve_rastreo, add_zero_byte=True),
            self._monto_to_bytearray(orden.op_monto),
            self._to_byte_array(orden.op_cuenta_ord, add_zero_byte=True),
            self._to_byte_array(orden.op_cuenta_ben, add_zero_byte=True),
        )
        return self._list_to_bytes(message_data)


class BeneficiaryAndAdditionalBeneficiarySignaturePayloadBuilder(
    SignaturePayloadBuilder,
):
    def build(self, orden: Orden) -> bytes:
        message_data = (
            self._fecha_to_bytearray(orden.op_fecha_oper),
            self._clave_to_bytearray(str(orden.op_ins_clave_ord)),
            self._clave_to_bytearray(str(orden.op_ins_clave_ben)),
            self._to_byte_array(orden.op_cve_rastreo, add_zero_byte=True),
            self._monto_to_bytearray(orden.op_monto),
            self._to_byte_array(orden.op_cuenta_ben, add_zero_byte=True),
            self._to_byte_array(orden.op_cuenta_ben_2, add_zero_byte=True),
        )
        return self._list_to_bytes(message_data)


class IndirectToParticipantSignaturePayloadBuilder(
    SignaturePayloadBuilder,
):
    def build(self, orden: Orden) -> bytes:
        message_data = (
            self._fecha_to_bytearray(orden.op_fecha_oper),
            self._clave_to_bytearray(str(orden.op_ins_clave_ord)),
            self._clave_to_bytearray(str(orden.op_ins_clave_ben)),
            self._to_byte_array(orden.op_cve_rastreo, add_zero_byte=True),
            self._monto_to_bytearray(orden.op_monto),
            self._to_byte_array(orden.op_cuenta_ord, add_zero_byte=True),
            self._to_byte_array(
                orden.op_cuenta_participante_ord,
                add_zero_byte=True,
            ),
        )
        return self._list_to_bytes(message_data)


class IndirectSignaturePayloadBuilder(
    SignaturePayloadBuilder,
):
    def build(self, orden: Orden) -> bytes:
        message_data = (
            self._fecha_to_bytearray(orden.op_fecha_oper),
            self._clave_to_bytearray(str(orden.op_ins_clave_ord)),
            self._clave_to_bytearray(str(orden.op_ins_clave_ben)),
            self._to_byte_array(orden.op_cve_rastreo, add_zero_byte=True),
            self._monto_to_bytearray(orden.op_monto),
            self._to_byte_array(orden.op_cuenta_ord, add_zero_byte=True),
            self._to_byte_array(orden.op_cuenta_ben, add_zero_byte=True),
            self._to_byte_array(orden.op_cuenta_participante_ord, add_zero_byte=True),
        )
        return self._list_to_bytes(message_data)


class EveryFieldSignaturePayloadBuilder(
    SignaturePayloadBuilder,
):
    def build(self, orden: Orden) -> bytes:
        message_data = (
            self._fecha_to_bytearray(orden.op_fecha_oper),
            self._clave_to_bytearray(str(orden.op_ins_clave_ord)),
            self._clave_to_bytearray(str(orden.op_ins_clave_ben)),
            self._to_byte_array(orden.op_cve_rastreo, add_zero_byte=True),
            self._monto_to_bytearray(orden.op_monto),
            self._to_byte_array(orden.op_cuenta_ord, add_zero_byte=True),
            self._to_byte_array(orden.op_cuenta_ben, add_zero_byte=True),
            self._to_byte_array(orden.op_cuenta_ben_2, add_zero_byte=True),
        )
        return self._list_to_bytes(message_data)


__all__ = [
    'SignaturePayloadBuilder',
    'RemittanceSignaturePayloadBuilder',
    'DefaultSignaturePayloadBuilder',
    'OriginSignaturePayloadBuilder',
    'BeneficiarySignaturePayloadBuilder',
    'OriginAndBeneficiarySignaturePayloadBuilder',
    'BeneficiaryAndAdditionalBeneficiarySignaturePayloadBuilder',
    'IndirectToParticipantSignaturePayloadBuilder',
    'IndirectSignaturePayloadBuilder',
    'EveryFieldSignaturePayloadBuilder',
]
