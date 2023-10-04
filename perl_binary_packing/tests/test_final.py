import json
import struct
import unittest
from typing import TypedDict, Any

from perl_binary_packing import pack, unpack


class TestPackData(TypedDict):
    format: str
    to_pack: list[Any]
    expected_packed: bytes


class TestUnPackData(TypedDict):
    format: str
    to_unpack: bytes
    expected_unpacked: list[Any]

class TestFinal(unittest.TestCase):
    json_test_file = "test_data.json"
    _test_packing: list[TestPackData] = []
    _test_packing: list[TestUnPackData] = []

    @classmethod
    def _binary_hexes_to_bytes(cls, expected_packed_str: list[str]) -> bytes:
        return b''.join([struct.pack('B', int(byte, 16)) for byte in expected_packed_str])

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        with open(cls.json_test_file) as file:
            test_data = json.load(file)

        if "test_pack" in test_data:
            test_packing = test_data["test_pack"]

            cls._test_packing = [
                TestPackData(
                    format=test_pack["format"],
                    to_pack=test_pack["to_pack"],
                    expected_packed=cls._binary_hexes_to_bytes(test_pack["expected_packed"]),
                )
                for test_pack in test_packing
            ]
        if "test_unpack" in test_data:
            test_unpacking = test_data["test_unpack"]

            cls._test_unpacking = [
                TestUnPackData(
                    format=test_unpack["format"],
                    to_unpack=cls._binary_hexes_to_bytes(test_unpack["to_unpack"]),
                    expected_unpacked=test_unpack["expected_unpacked"],
                )
                for test_unpack in test_unpacking
            ]

    def _format_bytes(self, _bin: bytes) -> str:
        result = ""
        for byte in _bin:
            result += hex(byte) + " "
        return result

    def test_packing(self):
        for test_pack in self._test_packing:
            with self.subTest(**test_pack):
                self._subtest_pack(test_pack)

    def _subtest_pack(self, test_pack: TestPackData):
        format = test_pack["format"]
        to_pack = test_pack["to_pack"]
        expected = test_pack["expected_packed"]
        if ("a" in format) or ("A" in format) or ("Z" in format):
            to_pack = [
                item.encode() if isinstance(item, str) else item
                for item in to_pack
            ]
        packed = pack(format, *to_pack)
        to_pack_view = self._format_array(to_pack)
        test_msg = f"Checking: pack({format}, {to_pack_view})/ Expected: \"{self._format_bytes(expected)}\", actual: \"{self._format_bytes(packed)}\""
        self.assertEqual(
            expected,
            packed,
            test_msg,
        )

    def test_unpacking(self):
        for test_unpack in self._test_unpacking:
            with self.subTest(**test_unpack):
                self._subtest_unpack(test_unpack)

    def _format_expected(self, expected_object: dict) -> Any:
        _type = expected_object["type"]
        raw_value = expected_object["value"]
        possible_types = {
            "str": str,
            "bytes": lambda s: s.replace("0x00", "\0").encode(),
            "int": int,
            "float": float,
        }
        return possible_types[_type](raw_value)

    def _subtest_unpack(self, test_unpack: TestUnPackData):
        format = test_unpack["format"]
        to_unpack = test_unpack["to_unpack"]
        expected_objects = test_unpack["expected_unpacked"]
        expected_values = [self._format_expected(expected_object) for expected_object in expected_objects]
        unpacked = list(unpack(format, to_unpack))
        # to_pack_view = "[" + ", ".join(map(lambda s: f'"{s}"', to_pack)) + "]"
        expected_view = self._format_array(expected_values)
        unpacked_view = self._format_array(unpacked)
        test_msg = f"Checking: pack({format}, {self._format_bytes(to_unpack)})/ Expected: \"{expected_view}\", actual: \"{unpacked_view}\""
        self.assertListEqual(
            expected_values,
            unpacked,
            test_msg,
        )

    def _format_array(self, arr):
        return "[" + ", ".join(map(lambda s: f'"{s}"', arr)) + "]"