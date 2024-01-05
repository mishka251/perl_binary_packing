from typing import ClassVar

from perl_binary_packing.formats import AsciiNullPaddedChar, NullPaddedChar, SpacePaddedChar
from perl_binary_packing.tests.base import BaseTestBinaryFormat, SubTestCase

"""
  DB<31> print unpack("A5", 'zz')
"zz"
  DB<36> print '"'.unpack("a5", 'zz').'"'
"zz"
  DB<37> print '"'.pack("a5", 'zz').'"'
"zz"
  DB<38> print '"'.pack("A5", 'zz').'"'
"zz   "
  DB<39> print '"'.pack("Z5", 'zz').'"'
"zz"
  DB<40>

"""
class TestNullPaddedString(BaseTestBinaryFormat[bytes]):
    _format = NullPaddedChar()
    examples: ClassVar[list[SubTestCase]] = [
        SubTestCase(b"1", b"1"),
        SubTestCase(b"z", b"z"),
        SubTestCase(b"a", b"a"),
        SubTestCase(b"f", b"f"),
        SubTestCase(b"=", b"="),
    ]

    def test_pack_long(self) -> None:
        expected = b"z"
        value = b"zz"
        actual = self._pack(value)
        self.assertEqual(expected, actual)

    def test_unpack_long(self) -> None:
        expected = b"z"
        value = b"z"
        actual = self._unpack(value)
        self.assertEqual(expected, actual)


class TestSpacePaddedString(BaseTestBinaryFormat[bytes]):
    _format = SpacePaddedChar()
    examples: ClassVar[list[SubTestCase]] = [
        SubTestCase(b"1", b"1"),
        SubTestCase(b"z", b"z"),
        SubTestCase(b"a", b"a"),
        SubTestCase(b"f", b"f"),
        SubTestCase(b"=", b"="),
    ]

    def test_pack_long(self) -> None:
        expected = b"z"
        value = b"zz"
        actual = self._pack(value)
        self.assertEqual(expected, actual)

    def test_unpack_long(self) -> None:
        expected = b"z"
        value = b"z"
        actual = self._unpack(value)
        self.assertEqual(expected, actual)


class TestAsciiNullString(BaseTestBinaryFormat[bytes]):
    _format = AsciiNullPaddedChar()
    examples: ClassVar[list[SubTestCase]] = [
        SubTestCase(b"1", b"1"),
        SubTestCase(b"z", b"z"),
        SubTestCase(b"a", b"a"),
        SubTestCase(b"f", b"f"),
        SubTestCase(b"=", b"="),
    ]

    def test_pack_long(self) -> None:
        expected = b"\0"
        value = b"zz"
        actual = self._pack(value)
        self.assertEqual(expected, actual)

    def test_unpack_long(self) -> None:
        expected = b"z"
        value = b"z"
        actual = self._unpack(value)
        self.assertEqual(expected, actual)
