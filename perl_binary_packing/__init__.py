from typing import Any

from perl_binary_packing.factory import parse_format


def pack(format_str: str, *args) -> bytes:
    # if len(args) == 1 and isinstance(args[0], (list, tuple)):
    #     args = args[0]
    formats = parse_format(format_str)
    packed = b''
    for i, _format in enumerate(formats):
        arg = args[i] if i < len(args) else None
        _packed = _format.pack(arg)
        packed += _packed
    return packed


def unpack(format_str: str, data: bytes) -> tuple[Any]:
    formats = parse_format(format_str)
    result = []
    _data = data
    for _format in formats:
        unpack_result = _format.unpack(_data)
        result.extend(unpack_result.data)
        _data = _data[unpack_result.unpacked_bytes_length]
    return tuple(result)
