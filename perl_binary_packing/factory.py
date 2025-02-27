import re
from typing import Any

from perl_binary_packing.formats import (
    AsciiNullPaddedChar,
    AsciiNullPaddedStr,
    BaseBinaryFormat,
    Double,
    DynamicLenArray,
    FirstHighNibbleCounteddArray,
    FirstHighNibbleUnlimitedArray,
    FirstLowNibbleCountedArray,
    FirstLowNibbleUnlimitedArray,
    FixedLenNullPaddedStr,
    FixedLenSpacePaddedStr,
    Float,
    GroupFormat,
    HexStringHighNybbleFirst,
    HexStringLowNybbleFirst,
    NetWorkUnSignedLong,
    NetWorkUnSignedShort,
    NullPaddedChar,
    SignedChar,
    SignedInteger,
    SignedLong,
    SignedLongLong,
    SignedShort,
    SpacePaddedChar,
    UnlimitedAsciiString,
    UnlimitedAsciiZString,
    UnlimitedLenArray,
    UnSignedChar,
    UnSignedInteger,
    UnSignedLong,
    UnSignedLongLong,
    UnSignedShort,
    VAXUnSignedLong,
    VAXUnSignedShort,
)

simple_formats: dict[str, BaseBinaryFormat[Any]] = {
    "h": HexStringLowNybbleFirst(),
    "H": HexStringHighNybbleFirst(),
    "a": NullPaddedChar(),
    "A": SpacePaddedChar(),
    "Z": AsciiNullPaddedChar(),
    "c": SignedChar(),
    "C": UnSignedChar(),
    "s": SignedShort(),
    "S": UnSignedShort(),
    "l": SignedLong(),
    "L": UnSignedLong(),
    "q": SignedLongLong(),
    "Q": UnSignedLongLong(),
    "i": SignedInteger(),
    "I": UnSignedInteger(),
    "n": NetWorkUnSignedShort(),
    "v": VAXUnSignedShort(),
    "N": NetWorkUnSignedLong(),
    "V": VAXUnSignedLong(),
    "f": Float(),
    "d": Double(),
}


def get_repeat_count_str(format_str: str) -> str:
    if rm := re.match(r"^\d+", format_str):
        return format_str[rm.regs[0][0] : rm.regs[0][1]]
    return ""


def _parse_format_simple(format_str: str) -> BaseBinaryFormat[Any]:
    return simple_formats[format_str]


def _parse_format(  # noqa: PLR0915,C901,PLR0912
    format_str: str,
) -> list[BaseBinaryFormat[Any]]:
    with_dynamic_count_format_re = r"^(?P<count_format>.)/(?P<item_format>.)"
    with_dynamic_count_group_format_re = r"^(?P<count_format>.)/\((?P<item_format>.*)\)"
    with_static_count_format_re = r"^(?P<item_format>.)\[?(?P<count>\d+)\]?"
    group_with_static_count_format_re = r"^\((?P<item_format>.*)\)\[?(?P<count>\d+)\]?"
    with_unknown_count_format_re = r"^(?P<item_format>.)\*"

    format_str_tmp = format_str
    formats: list[BaseBinaryFormat[Any]] = []
    current_format: BaseBinaryFormat[Any]
    item_format: BaseBinaryFormat[Any]
    while format_str_tmp:
        if match := re.match(with_dynamic_count_group_format_re, format_str_tmp):
            count_format_str = match.group("count_format")
            item_format_str = match.group("item_format")
            cont_format = _parse_format_simple(count_format_str)
            item_formats = _parse_format(item_format_str)
            item_format = (
                item_formats[0]
                if len(item_formats) == 1
                else GroupFormat(tuple(item_formats))
            )
            current_format = DynamicLenArray(item_format, cont_format)
            formats.append(current_format)
            format_len = match.regs[0][1] - match.regs[0][0]
            format_str_tmp = format_str_tmp[format_len:]
        elif match := re.match(with_dynamic_count_format_re, format_str_tmp):
            count_format_str = match.group("count_format")
            item_format_str = match.group("item_format")
            cont_format = _parse_format_simple(count_format_str)
            item_format = _parse_format_simple(item_format_str)
            current_format = DynamicLenArray(item_format, cont_format)
            formats.append(current_format)
            format_len = match.regs[0][1] - match.regs[0][0]
            format_str_tmp = format_str_tmp[format_len:]
        elif match := re.match(with_static_count_format_re, format_str_tmp):
            count_str = match.group("count")
            count = int(count_str)
            item_format_str = match.group("item_format")
            if item_format_str == "a":
                current_format = FixedLenNullPaddedStr(count)
                formats.append(current_format)
            elif item_format_str == "A":
                current_format = FixedLenSpacePaddedStr(count)
                formats.append(current_format)
            elif item_format_str == "Z":
                current_format = AsciiNullPaddedStr(count)
                formats.append(current_format)
            elif item_format_str == "h":
                current_format = FirstLowNibbleCountedArray(count)
                formats.append(current_format)
            elif item_format_str == "H":
                current_format = FirstHighNibbleCounteddArray(count)
                formats.append(current_format)
            else:
                item_format = _parse_format_simple(item_format_str)
                current_formats = [item_format] * count
                formats.extend(current_formats)
            format_len = match.regs[0][1] - match.regs[0][0]
            format_str_tmp = format_str_tmp[format_len:]
        elif match := re.match(group_with_static_count_format_re, format_str_tmp):
            count_str = match.group("count")
            count = int(count_str)
            item_format_str = match.group("item_format")
            if item_format_str == "a":
                current_format = FixedLenNullPaddedStr(count)
                formats.append(current_format)
            elif item_format_str == "A":
                current_format = FixedLenSpacePaddedStr(count)
                formats.append(current_format)
            elif item_format_str == "Z":
                current_format = AsciiNullPaddedStr(count)
                formats.append(current_format)
            elif item_format_str == "h":
                current_format = FirstLowNibbleCountedArray(count)
                formats.append(current_format)
            elif item_format_str == "H":
                current_format = FirstHighNibbleCounteddArray(count)
                formats.append(current_format)
            else:
                item_format = _parse_format(item_format_str)[0]
                current_formats = [item_format] * count
                formats.extend(current_formats)
            format_len = match.regs[0][1] - match.regs[0][0]
            format_str_tmp = format_str_tmp[format_len:]
        elif match := re.match(with_unknown_count_format_re, format_str_tmp):
            item_format_str = match.group("item_format")
            binary_string_formats = {"a", "A"}
            if item_format_str == "Z":
                current_format = UnlimitedAsciiZString()
            elif item_format_str == "h":
                current_format = FirstLowNibbleUnlimitedArray()
            elif item_format_str == "H":
                current_format = FirstHighNibbleUnlimitedArray()
            elif item_format_str in binary_string_formats:
                current_format = UnlimitedAsciiString()
            else:
                item_format = _parse_format_simple(item_format_str)
                current_format = UnlimitedLenArray(item_format)
            formats.append(current_format)
            format_len = len(item_format_str) + 1
            format_str_tmp = format_str_tmp[format_len:]
        else:
            _format_str = format_str_tmp[0]
            current_format = _parse_format_simple(_format_str)
            formats.append(current_format)
            format_str_tmp = format_str_tmp[1:]

    return formats


def parse_format(format_str: str) -> GroupFormat:
    formats = _parse_format(format_str)
    return GroupFormat(tuple(formats))
