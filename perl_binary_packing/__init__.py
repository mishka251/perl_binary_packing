from typing import Any

from perl_binary_packing.factory import parse_format


def pack(format_str: str, *args) -> bytes:
    # if len(args) == 1 and isinstance(args[0], (list, tuple)):
    #     args = args[0]
    formats = parse_format(format_str)
    packed = b''
    full_args = args
    current_args = args
    for i, _format in enumerate(formats):
        # arg = args[i] if i < len(args) else None
        _packed = _format.pack(current_args)
        packed += _packed.packed
        current_args = current_args[_packed.packed_items_count:] if _packed.packed_items_count < len(
            current_args) else tuple()
    return packed


def unpack(format_str: str, data: bytes) -> tuple[Any]:
    try:
        return _unpack(format_str, data)
    except Exception as ex:
        raise Exception(f"Error while unpacking {data} with {format_str=}") from ex


def _unpack(format_str: str, data: bytes) -> tuple[Any]:
    formats = parse_format(format_str)
    result = []
    _data = data
    for _format in formats:
        needed_len = None
        try:
            needed_len = _format.get_bytes_length()
        except NotImplementedError:
            pass
        if needed_len:
            data_part = _data[0:needed_len]
        else:
            data_part = _data
        unpack_result = _format.unpack(data_part)
        result.extend(unpack_result.data)
        if unpack_result.unpacked_bytes_length < len(data):
            _data = _data[unpack_result.unpacked_bytes_length:]
        else:
            _data = b""
    return tuple(result)
