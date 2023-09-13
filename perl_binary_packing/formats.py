import dataclasses
import struct
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


# Сопоставление форматов
# перла https://perldoc.perl.org/functions/pack
# и питона https://docs.python.org/3/library/struct.html


@dataclasses.dataclass
class UnpackResult(Generic[T]):
    data: T
    unpacked_bytes_length: int


class BaseBinaryFormat(Generic[T]):
    def pack(self, value: Optional[T]) -> bytes:
        if self._value_is_empty(value):
            return self._pack_none()
        return self._pack(value)

    def _value_is_empty(self,  value: Optional[T]) -> bool:
        return value is None

    def _pack(self, value: T) -> bytes:
        raise NotImplementedError()

    def unpack(self, data: bytes) -> UnpackResult[T]:
        raise NotImplementedError()

    def get_bytes_length(self) -> int:
        raise NotImplementedError()

    def _pack_none(self) -> bytes:
        return b'\0'


class PythonSupportedFormat(BaseBinaryFormat[T]):
    _python_format: str

    def _get_format(self) -> str:
        return self._python_format

    def _pack(self, value: T) -> bytes:
        return struct.pack(self._get_format(), value)

    def unpack(self, data: bytes) -> UnpackResult[T]:
        size = self.get_bytes_length()
        packed_data = struct.pack(self._get_format(), data)
        return UnpackResult(packed_data, size)

    def get_bytes_length(self) -> int:
        return struct.calcsize(self._get_format())



# region strings
class NullPaddedChar(PythonSupportedFormat[bytes]):
    # a
    _python_format = "s"


class SpacePaddedChar(PythonSupportedFormat[bytes]):
    # A
    _python_format = "s"

    def _pack_none(self) -> bytes:
        return b' '

    def _value_is_empty(self,  value: Optional[T]) -> bool:
        return value is None or value == b""


class AsciiNullPaddedChar(PythonSupportedFormat[bytes]):
    # Z
    _python_format = "s"

    def _pack(self, value: T) -> bytes:
        return b'\0'


# endregion strings


# region integers
class SignedChar(PythonSupportedFormat[int]):
    # c
    _python_format = "b"


class UnSignedChar(PythonSupportedFormat[int]):
    # C
    _python_format = "B"


class WideSignedChar(PythonSupportedFormat[int]):
    # w
    # _python_format = "b"
    pass


class SignedShort(PythonSupportedFormat[int]):
    # s
    _python_format = "h"


class UnSignedShort(PythonSupportedFormat[int]):
    # S
    _python_format = "H"


class SignedLong(PythonSupportedFormat[int]):
    # l
    _python_format = "l"


class UnSignedLong(PythonSupportedFormat[int]):
    # L
    _python_format = "L"


class SignedLongLong(PythonSupportedFormat[int]):
    # q
    _python_format = "q"


class UnSignedLongLong(PythonSupportedFormat[int]):
    # Q
    _python_format = "Q"


class SignedInteger(PythonSupportedFormat[int]):
    # i
    _python_format = "i"


class UnSignedInteger(PythonSupportedFormat[int]):
    # I
    _python_format = "I"


class NetWorkUnSignedShort(PythonSupportedFormat[int]):
    # n
    _python_format = "!H"


class VAXUnSignedShort(PythonSupportedFormat[int]):
    # v
    _python_format = "<H"


class NetWorkUnSignedLong(PythonSupportedFormat[int]):
    # N
    _python_format = "!L"


class VAXUnSignedLong(PythonSupportedFormat[int]):
    # V
    _python_format = "<L"


# endregion integers


# region floats

class Float(PythonSupportedFormat[float]):
    # f
    _python_format = "f"


class Double(PythonSupportedFormat[float]):
    # d
    _python_format = "d"


# endregion floats


class FixedLenArray(BaseBinaryFormat[list[T]], Generic[T]):
    # FORMAT[COUNT]
    def __init__(self, inner_format: BaseBinaryFormat[T], count: int):
        self._count = count
        self._item_format = inner_format

    def _pack(self, value: list[T]) -> bytes:
        packed = b''
        # assert len(value) == self._count
        for item in value:
            packed += self._item_format._pack(item)
        return packed

    def unpack(self, data: bytes) -> UnpackResult[list[T]]:
        result = []
        total_bytes = 0
        items_data = data
        for _ in range(self._count):
            data_part = items_data
            unpacked_item, bytes_len = self._item_format.unpack(data_part)
            result.append(unpacked_item)
            total_bytes += bytes_len
            items_data = items_data[bytes_len:]
        return UnpackResult(result, total_bytes)

    def get_bytes_length(self) -> int:
        return self._item_format.get_bytes_length() * self._count


class DynamicLenArray(BaseBinaryFormat[list[T]], Generic[T]):
    # LENGTH_TYPE/ITEM_TYPE
    def __init__(self, inner_format: BaseBinaryFormat[T], count_format: BaseBinaryFormat[int]):
        self._count_format = count_format
        self._item_format = inner_format

    def _pack(self, value: list[T]) -> bytes:
        packed = b''
        packed += self._count_format._pack(len(value))
        for item in value:
            packed += self._item_format._pack(item)
        return packed

    def unpack(self, data: bytes) -> UnpackResult[list[T]]:
        result = []
        total_bytes = 0
        count_unpack_result = self._count_format.unpack(data[0:self._count_format.get_bytes_length()])
        count = count_unpack_result.data

        items_data = data[count_unpack_result.unpacked_bytes_length:]
        for _ in range(count):
            data_part = items_data
            unpacked_item, bytes_len = self._item_format.unpack(data_part)
            result.append(unpacked_item)
            total_bytes += bytes_len
            items_data = items_data[bytes_len:]
        return UnpackResult(result, total_bytes)

    def get_bytes_length(self) -> int:
        raise NotImplementedError("Нельзя определить не распаковав данные")


class UnlimitedLenArray(BaseBinaryFormat[list[T]], Generic[T]):
    # ITEM_TYPE*
    def __init__(self, inner_format: BaseBinaryFormat[T]):
        self._item_format = inner_format

    def _pack(self, value: list[T]) -> bytes:
        packed = b''
        for item in value:
            packed += self._item_format._pack(item)
        return packed

    def unpack(self, data: bytes) -> UnpackResult[list[T]]:
        result = []
        total_bytes = 0

        items_data = data
        while items_data:
            data_part = items_data
            unpacked_item, bytes_len = self._item_format.unpack(data_part)
            result.append(unpacked_item)
            total_bytes += bytes_len
            items_data = items_data[bytes_len:]
        return UnpackResult(result, total_bytes)

    def get_bytes_length(self) -> int:
        raise NotImplementedError("Нельзя определить не распаковав данные")

    def _pack_none(self) -> bytes:
        return b''


class FixedLenNullPaddedStr(PythonSupportedFormat[bytes]):
    # 10a
    _python_format = "s"

    def __init__(self, count: int):
        self._count = count

    def _get_format(self) -> str:
        return f"{self._count}{self._python_format}"

class FixedLenSpacePaddedStr(PythonSupportedFormat[bytes]):
    # 10A
    _python_format = "s"

    def __init__(self, count: int):
        self._count = count

    def _get_format(self) -> str:
        return f"{self._count}{self._python_format}"


class AsciiNullPaddedStr(PythonSupportedFormat[bytes]):
    # 10Z
    _python_format = "s"

    def __init__(self, count: int):
        self._count = count

    def _get_format(self) -> str:
        return f"{self._count - 1}{self._python_format}"

    def _pack(self, value: list[bytes]) -> bytes:
        return super()._pack(value) + b'\0'


class UnlimitedAsciiZString(UnlimitedLenArray[bytes]):
    def __init__(self):
        super().__init__(SignedChar())

    def _pack(self, value: list[bytes]) -> bytes:
        return super()._pack(value) + b'\0'

    def _pack_none(self) -> bytes:
        return b'\0'