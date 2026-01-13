from __future__ import annotations

import base64
from typing import Any, Self, Type

from coincurve import GLOBAL_CONTEXT, Context, PrivateKey as CoinCurvePrivateKey
from coincurve.utils import hex_to_bytes
from eth_utils import keccak
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic_core import core_schema

from atlantiscore.types.evm import EVMAddress
from atlantiscore.types.evm.base import LiteralByteEncoding

NUMBER_OF_BYTES_IN_ADDRESS = 20
BYTE_COUNT = 32
HEX_LENGTH = BYTE_COUNT * 2
PRIVATE_KEY_HEX_EXAMPLE = (
    "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
)


class PrivateKey(CoinCurvePrivateKey):
    @property
    def public_address(self) -> EVMAddress:
        public_key = self.public_key.format(compressed=False)[1:]
        return EVMAddress(keccak(public_key)[-NUMBER_OF_BYTES_IN_ADDRESS:])

    @classmethod
    def from_der(cls, *args, **kwargs) -> Self:
        return cls.from_hex(CoinCurvePrivateKey.from_der(*args, **kwargs).to_hex())

    @classmethod
    def from_hex(cls, hexed: str, context: Context = GLOBAL_CONTEXT) -> Self:
        return PrivateKey(hex_to_bytes(hexed), context)

    @classmethod
    def from_int(cls, *args, **kwargs) -> Self:
        return cls.from_hex(CoinCurvePrivateKey.from_int(*args, **kwargs).to_hex())

    @classmethod
    def from_pem(cls, *args, **kwargs) -> Self:
        return cls.from_hex(CoinCurvePrivateKey.from_pem(*args, **kwargs).to_hex())

    def to_base64(self) -> str:
        return base64.b64encode(hex_to_bytes(self.to_hex())).decode()

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Type[Any],
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate,
            schema=core_schema.union_schema(
                [
                    core_schema.str_schema(
                        min_length=HEX_LENGTH,
                        max_length=HEX_LENGTH,
                    ),
                    core_schema.int_schema(ge=0),
                    core_schema.bytes_schema(
                        min_length=BYTE_COUNT,
                        max_length=BYTE_COUNT,
                    ),
                    core_schema.is_instance_schema(cls=cls),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda v: v.to_hex(),
                info_arg=False,
                return_schema=core_schema.str_schema(),
            ),
        )

    @classmethod
    def _validate(cls, v: LiteralByteEncoding | PrivateKey) -> Self:
        try:
            if isinstance(v, PrivateKey):
                return v
            if isinstance(v, str):
                return cls.from_hex(v)
            if isinstance(v, int):
                return cls.from_int(v)
            if isinstance(v, bytes):
                return cls.from_hex(v.hex())
        except (ValueError, TypeError) as e:
            raise ValueError(f"{v} is not a valid private key.") from e

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: core_schema.CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> dict:
        json_schema = handler.resolve_ref_schema(handler(core_schema))
        json_schema.update(example=PRIVATE_KEY_HEX_EXAMPLE)
        return json_schema
