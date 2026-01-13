import base64
import logging
import warnings

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.hashes import SHA256

from spei import exceptions
from spei.errors import spei as errors
from spei.requests import OrdenRequest
from spei.resources import Orden, Respuesta
from spei.responses import RespuestaResponse
from spei.signature.factory import get_signature_builder

logger = logging.getLogger('spei')
logger.setLevel(logging.DEBUG)


_DEPRECATED_FACTORY_ARGUMENT_MESSAGE = (
    'Use signature_builder_factory; checksum_generator_factory is deprecated.'
)
_DEPRECATED_FACTORY_ACCESS_MESSAGE = (
    'checksum_generator_factory is deprecated; use signature_builder_factory.'
)
_DEPRECATED_GENERATE_CHECKSUM_MESSAGE = (
    'generate_checksum is deprecated; use generate_signature instead.'
)


class BaseClient(object):
    def __init__(
        self,
        priv_key,
        priv_key_passphrase,
        host,
        username,
        password,
        verify=False,
        http_client=requests,
        checksum_generator_factory=None,
        signature_builder_factory=None,
        **factories,
    ):
        self.priv_key = priv_key
        self.priv_key_passphrase = priv_key_passphrase or None
        self.host = host
        self.session = http_client.Session()
        self.session.headers.update(
            {
                'Content-Type': 'application/xml; charset=cp850',
                'User-Agent': 'Fondeadora/Karpay/v0.52.0',
            },
        )
        self.session.verify = verify
        self.session.auth = (username, password)

        if priv_key_passphrase:
            self.priv_key_passphrase = priv_key_passphrase.encode('ascii')

        self.pkey = serialization.load_pem_private_key(
            self.priv_key.encode('utf-8'),
            self.priv_key_passphrase,
            default_backend(),
        )

        factories_conflict = (
            signature_builder_factory is not None
            and checksum_generator_factory is not None
        )

        if factories_conflict:
            warnings.warn(
                _DEPRECATED_FACTORY_ARGUMENT_MESSAGE,
                DeprecationWarning,
                stacklevel=2,
            )

        if signature_builder_factory is None:
            if checksum_generator_factory is not None:
                warnings.warn(
                    _DEPRECATED_FACTORY_ACCESS_MESSAGE,
                    DeprecationWarning,
                    stacklevel=2,
                )
                signature_builder_factory = checksum_generator_factory
            else:
                signature_builder_factory = get_signature_builder

        self._signature_builder_factory = signature_builder_factory

        unexpected_factories = set(factories) - {
            'orden_factory',
            'respuesta_response_factory',
        }

        if unexpected_factories:
            unexpected = ', '.join(sorted(unexpected_factories))
            raise TypeError(f'Unexpected factory arguments: {unexpected}')

        self._orden_factory = factories.get('orden_factory', Orden)
        self._respuesta_response_factory = factories.get(
            'respuesta_response_factory',
            RespuestaResponse,
        )

    @property
    def signature_builder_factory(self):
        return self._signature_builder_factory

    @signature_builder_factory.setter
    def signature_builder_factory(self, factory):
        self._signature_builder_factory = factory

    @property
    def checksum_generator_factory(self):
        warnings.warn(
            _DEPRECATED_FACTORY_ACCESS_MESSAGE,
            DeprecationWarning,
            stacklevel=2,
        )
        return self._signature_builder_factory

    @checksum_generator_factory.setter
    def checksum_generator_factory(self, factory):
        warnings.warn(
            _DEPRECATED_FACTORY_ACCESS_MESSAGE,
            DeprecationWarning,
            stacklevel=2,
        )
        self._signature_builder_factory = factory

    @property
    def orden_factory(self):
        return self._orden_factory

    @orden_factory.setter
    def orden_factory(self, factory):
        self._orden_factory = factory

    @property
    def respuesta_response_factory(self):
        return self._respuesta_response_factory

    @respuesta_response_factory.setter
    def respuesta_response_factory(self, factory):
        self._respuesta_response_factory = factory

    def registra_orden(self, orden_data):
        signature = self.generate_signature(orden_data)
        orden = self._orden_factory(op_firma_dig=signature, **orden_data)
        soap_request = OrdenRequest(orden).to_string()
        logger.info(soap_request)

        response = self.session.post(data=soap_request, url=self.host)
        logger.info(response.text)
        response.raise_for_status()

        respuesta = self._respuesta_response_factory(response.text)

        if respuesta.err_codigo != errors.GenericoCodigoError.exitoso:
            self._raise_error(respuesta)

        return respuesta

    def generate_signature(self, message_data):
        orden = Orden(**message_data, op_firma_dig='')
        builder = self.signature_builder_factory(orden.op_tp_clave)
        message_as_bytes = builder.build(orden)

        signed_message = self.pkey.sign(
            message_as_bytes,
            padding.PKCS1v15(),
            SHA256(),
        )

        return base64.b64encode(signed_message)

    def generate_checksum(self, message_data):
        warnings.warn(
            _DEPRECATED_GENERATE_CHECKSUM_MESSAGE,
            DeprecationWarning,
            stacklevel=2,
        )

        return self.generate_signature(message_data)

    def _raise_error(self, respuesta: Respuesta):
        if respuesta.err_codigo == errors.GenericoCodigoError.tipo_pago_invalido:
            raise exceptions.TipoPagoInvalidoError(respuesta)

        if (  # noqa: WPS337
            respuesta.err_codigo
            == errors.OtrosCodigoError.otros_fecha_operacion_incorrecta
        ):
            raise exceptions.FechaOperacionIncorrectaError(respuesta)

        raise exceptions.SPEIError(respuesta)
