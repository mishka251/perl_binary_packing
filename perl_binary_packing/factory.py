import re

from perl_binary_packing.formats import (
    BaseBinaryFormat,
    NullPaddedChar,
    SpacePaddedChar,
    AsciiNullPaddedChar,
    SignedChar,
    UnSignedChar,
    SignedShort,
    UnSignedShort,
    SignedLong,
    UnSignedLong,
    SignedLongLong,
    UnSignedLongLong,
    SignedInteger,
    UnSignedInteger,
    NetWorkUnSignedShort,
    NetWorkUnSignedLong,
    VAXUnSignedLong,
    VAXUnSignedShort,
    Float,
    Double,
    DynamicLenArray,
    FixedLenArray,
    UnlimitedLenArray, FixedLenNullPaddedStr, FixedLenSpacePaddedStr, AsciiNullPaddedStr, UnlimitedAsciiZString,
    UnlimitedAsciiString, HexStringLowNybbleFirst, HexStringHighNybbleFirst, FirstLowNibbleUnlimitedArray,
    FirstHighNibbleUnlimitedArray, FirstLowNibbleCountedArray, FirstHighNibbleCounteddArray, GroupFormat,
)

simple_formats = {
    "h": HexStringLowNybbleFirst(),
    "H": HexStringHighNybbleFirst(),


    "a": NullPaddedChar(),
    "A": SpacePaddedChar(),
    "Z": AsciiNullPaddedChar(),

    "c": SignedChar(),
    "C": UnSignedChar(),
    # "w": AsciiNullPaddedString(),

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
    if rm := re.match("^\d+", format_str):
        return format_str[rm.regs[0][0]: rm.regs[0][1]]
    return ""


def get_next_format(format_str: str) -> str:
    with_count_format_re = r"^./."
    if re.match(with_count_format_re, format_str):
        return format_str[:3]
    if format_str[0] == 'V' or format_str[0] == 'v':
        count = get_repeat_count_str(format_str[1:])
        return format_str[0] + count
    if format_str.startswith('Z*'):
        return 'Z*'
    if format_str.startswith('a*'):
        return 'a*'
    if format_str.startswith('a['):
        end_index = format_str.find(']')
        return format_str[0:end_index + 1]
    if format_str[0] == 'C':
        count = get_repeat_count_str(format_str[1:])
        return format_str[0] + count
    if format_str.startswith("f"):
        count = get_repeat_count_str(format_str[1:])
        return format_str[0] + count
    if format_str.startswith("l"):
        count = get_repeat_count_str(format_str[1:])
        return format_str[0] + count

    raise NotImplementedError(f'format={format_str}')


def _parse_format_simple(format_str: str) -> BaseBinaryFormat:
    return simple_formats[format_str]


def parse_format(format_str: str) -> list[BaseBinaryFormat]:
    with_dynamic_count_format_re = r"^(?P<count_format>.)/(?P<item_format>.)"
    with_dynamic_count_group_format_re = r"^(?P<count_format>.)/\((?P<item_format>.*)\)"
    with_static_count_format_re = r"^(?P<item_format>.)\[?(?P<count>\d+)\]?"
    with_unknown_count_format_re = r"^(?P<item_format>.)\*"

    format_str_tmp = format_str
    formats = []
    while format_str_tmp:
        if match := re.match(with_dynamic_count_group_format_re, format_str_tmp):
            count_format_str = match.group("count_format")
            item_format_str = match.group("item_format")
            cont_format = _parse_format_simple(count_format_str)
            item_format = parse_format(item_format_str)[0]
            current_format = DynamicLenArray(item_format, cont_format)
            formats.append(current_format)
            format_len = match.regs[0][1]-match.regs[0][0]
            format_str_tmp = format_str_tmp[format_len:]
        elif match := re.match(with_dynamic_count_format_re, format_str_tmp):
            count_format_str = match.group("count_format")
            item_format_str = match.group("item_format")
            cont_format = _parse_format_simple(count_format_str)
            item_format = _parse_format_simple(item_format_str)
            current_format = DynamicLenArray(item_format, cont_format)
            formats.append(current_format)
            format_len = match.regs[0][1]-match.regs[0][0]
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
                # current_format = FixedLenArray(item_format, count)
                current_formats = [item_format]*count
                formats.extend(current_formats)
            format_len = match.regs[0][1]-match.regs[0][0]
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
                item_format = UnSignedChar()
                current_format = UnlimitedAsciiString(item_format)
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
    group = GroupFormat(tuple(formats))
    return [group]
    # return formats
