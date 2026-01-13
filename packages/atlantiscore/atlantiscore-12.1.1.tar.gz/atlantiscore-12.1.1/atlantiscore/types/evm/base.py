from __future__ import annotations

from abc import ABCMeta
from typing import Any, Self, Type

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic_core import core_schema

from atlantiscore.lib.exceptions import InvalidByteEncoding

BYTE_ORDER = "big"
NUMBER_OF_BITS_IN_BYTE = 8
PREFIX = "0x"
PREFIX_SIZE = len(PREFIX)

LiteralByteEncoding = str | int | bytes


class ByteEncoding:
    _value: bytes

    def __init__(self, value: ByteEncoding | LiteralByteEncoding) -> None:
        self._value = encoding_to_bytes(value)

    def __bytes__(self) -> bytes:
        return self._value

    def __int__(self) -> int:
        return int.from_bytes(self._value, BYTE_ORDER)

    def __str__(self) -> str:
        return PREFIX + self._value.hex()

    def __eq__(self, other: any) -> bool:
        try:
            return hash(self) == hash(ByteEncoding(other))
        except InvalidByteEncoding:
            return False

    def __ne__(self, other: any) -> bool:
        return not self.__eq__(other)

    def __gt__(self, other: ByteEncoding) -> bool:
        return hash(self) > hash(ByteEncoding(other))

    def __lt__(self, other: ByteEncoding) -> bool:
        return hash(self) < hash(ByteEncoding(other))

    def __hash__(self) -> int:
        return int(self)

    def __bool__(self) -> bool:
        return bool(int(self))

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Type[Any],
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate,
            schema=core_schema.union_schema(cls._get_pydantic_core_schemas()),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda v: str(v),
                info_arg=False,
                return_schema=core_schema.str_schema(),
            ),
        )

    @classmethod
    def _get_pydantic_core_schemas(cls) -> list[core_schema.CoreSchema]:
        return [
            core_schema.str_schema(),
            core_schema.int_schema(ge=0),
            core_schema.bytes_schema(),
            core_schema.is_instance_schema(cls=cls),
        ]

    @classmethod
    def _validate(cls, v: ByteEncoding | LiteralByteEncoding) -> Self:
        try:
            return cls(v)
        except InvalidByteEncoding as e:
            raise ValueError(str(e))

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: core_schema.CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> dict:
        json_schema = handler.resolve_ref_schema(handler(core_schema))
        return json_schema


class RestrictedByteEncoding(ByteEncoding, metaclass=ABCMeta):
    _example: str
    _byte_count: int
    _max_str_length: int
    _min_str_length: int

    @classmethod
    def _get_pydantic_core_schemas(cls) -> list[core_schema.CoreSchema]:
        return [
            core_schema.str_schema(
                min_length=cls._min_str_length,
                max_length=cls._max_str_length,
            ),
            core_schema.int_schema(ge=0),
            core_schema.bytes_schema(
                min_length=cls._byte_count,
                max_length=cls._byte_count,
            ),
            core_schema.is_instance_schema(cls=cls),
        ]

    @classmethod
    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: core_schema.CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> dict:
        json_schema = super().__get_pydantic_json_schema__(core_schema, handler)
        json_schema.update(example=cls._example)
        return json_schema


def encoding_to_bytes(value: ByteEncoding | LiteralByteEncoding) -> bytes:
    try:
        if isinstance(value, ByteEncoding):
            return bytes(value)

        if isinstance(value, str):
            byte_sequence = _hex_to_bytes(value)
        elif isinstance(value, int):
            byte_sequence = _int_to_bytes(value)
        elif isinstance(value, bytes):
            byte_sequence = value
        else:
            raise TypeError

        return byte_sequence
    except (ValueError, TypeError) as e:
        raise InvalidByteEncoding(value) from e


def encoding_to_restricted_bytes(
    value: ByteEncoding | LiteralByteEncoding,
    byte_count: int,
) -> bytes:
    if isinstance(value, int):
        byte_sequence = _int_to_padded_bytes(value, byte_count)
    else:
        byte_sequence = encoding_to_bytes(value)

    try:
        if len(byte_sequence) != byte_count:
            raise ValueError

        return byte_sequence
    except ValueError as e:
        raise InvalidByteEncoding(value) from e


def _hex_to_bytes(hex_str: str) -> bytes:
    if hex_str[:PREFIX_SIZE].lower() == PREFIX:
        hex_str = hex_str[PREFIX_SIZE:]
    return bytes.fromhex(hex_str)


def _int_to_bytes(integer: int) -> bytes:
    return integer.to_bytes(_calculate_required_byte_count(integer), BYTE_ORDER)


def _int_to_padded_bytes(integer: int, byte_count: int) -> bytes:
    return _int_to_bytes(integer).rjust(byte_count, b"\x00")


def _calculate_required_byte_count(integer: int) -> int:
    """Returns the minimum number of bytes required to represent the given int.

    Example:
    0 + 7 would require 0 bytes
    1 + 7 would require 1 byte
    """
    return (integer.bit_length() + 7) // NUMBER_OF_BITS_IN_BYTE
