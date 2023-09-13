import json
import struct
import unittest
from typing import TypedDict, Any

from perl_binary_packing import pack


class TestPackData(TypedDict):
    format: str
    to_pack: list[Any]
    expected_packed: bytes


class TestFinal(unittest.TestCase):
    json_test_file = "test_data.json"
    _test_packing: list[TestPackData] = []

    @classmethod
    def _process_expected_packed(cls, expected_packed_str: list[str]) -> bytes:
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
                    expected_packed=cls._process_expected_packed(test_pack["expected_packed"]),
                )
                for test_pack in test_packing
            ]

    def test_packing(self):
        for test_pack in self._test_packing:
            with self.subTest(**test_pack):
                format = test_pack["format"]
                to_pack = test_pack["to_pack"]
                expected = test_pack["expected_packed"]
                if ("a" in format) or ("A" in format) or ("Z" in format):
                    to_pack = [
                        item.encode() if isinstance(item, str) else item
                        for item in to_pack
                    ]
                packed = pack(format, *to_pack)
                to_pack_view = "[" + ", ".join(map(lambda s: f'"{s}"', to_pack)) + "]"
                self.assertEqual(
                    expected,
                    packed,
                    f"Checking: pack({format}, {to_pack_view})/ Expected: \"{expected}\", actual: \"{packed}\""
                )
