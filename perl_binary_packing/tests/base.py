import dataclasses
import unittest
from typing import Generic

from perl_binary_packing.formats import BaseBinaryFormat, T


@dataclasses.dataclass
class SubTestCase(Generic[T]):
    value: T
    binary: bytes

    def __str__(self):
        return f"{self.value}"


class BaseTestBinaryFormat(unittest.TestCase, Generic[T]):
    examples: list[SubTestCase[T]] = []
    _format: BaseBinaryFormat[T]

    def _get_format(self) -> BaseBinaryFormat[T]:
        return self._format

    def test_simple_packing(self):
        for example in self.examples:
            with self.subTest(example.value):
                packed = self._pack(example.value)
                self.assertEqual(packed, example.binary)

    def test_simple_unpacking(self):
        for example in self.examples:
            with self.subTest(example.value):
                unpacked = self._unpack(example.binary)
                self.assertEqual(unpacked, example.value)

    def _pack(self, value: T) -> bytes:
        format = self._get_format()
        return format._pack(value)

    def _unpack(self, data: bytes) -> T:
        format = self._get_format()
        return format.unpack(data).data[0]
