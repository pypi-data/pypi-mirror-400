from typing import Optional, TypeVar

from sqlalchemy.engine import Dialect
from sqlalchemy.types import LargeBinary, TypeDecorator, TypeEngine

from atlantiscore.types.evm import (
    ByteEncoding as PythonByteEncoding,
    LiteralByteEncoding,
)

T = TypeVar("T", bound=PythonByteEncoding)


class ByteEncoding(TypeDecorator):
    impl: TypeEngine = LargeBinary
    cache_ok: bool = True
    _default_type: LargeBinary = LargeBinary()

    def load_dialect_impl(self, dialect: Dialect) -> TypeEngine[LargeBinary]:
        return dialect.type_descriptor(self._default_type)

    def process_bind_param(
        self,
        value: Optional[T | LiteralByteEncoding],
        dialect: Dialect,
    ) -> bytes:
        if value is None:
            return value
        return bytes(self._parse(value))

    def process_result_value(
        self,
        value: Optional[bytes],
        dialect: Dialect,
    ) -> T:
        if value is None:
            return value
        return self._parse(bytes(value))

    @staticmethod
    def _parse(value: T | LiteralByteEncoding) -> T:
        return PythonByteEncoding(value)
