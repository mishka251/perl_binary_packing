from typing import Any

from perl_binary_packing.factory import parse_format


class PackError(Exception):
    pass


class UnPackError(Exception):
    pass

def pack(format_str: str, *args: Any) -> bytes:
    try:
        return _pack(format_str, *args)
    except Exception as ex:
        msg = f"Error while packing {args} with {format_str=}"
        raise PackError(msg) from ex


def _pack(format_str: str, *args: Any) -> bytes:
    formats = parse_format(format_str)
    packed = b""
    current_args = args
    for _format in formats:
        try:
            _packed = _format.pack(current_args)
        except Exception as ex:
            msg = f"Error pack {_format=} {current_args=}"
            raise PackError(msg) from ex
        packed += _packed.packed
        current_args = (
            current_args[_packed.packed_items_count:]
            if _packed.packed_items_count < len(current_args)
            else tuple()  # noqa: C408
        )
    return packed


def unpack(format_str: str, data: bytes) -> tuple[Any]:
    try:
        return _unpack(format_str, data)
    except Exception as ex:
        msg = f"Error while unpacking {data} with {format_str=}"
        raise UnPackError(msg) from ex


def _unpack(format_str: str, data: bytes) -> tuple[Any]:
    formats = parse_format(format_str)
    result = []
    _data = data
    for _format in formats:
        try:
            needed_len = _format.get_bytes_length()
        except NotImplementedError:
            needed_len = None
        data_part = _data[0:needed_len] if needed_len else _data
        try:
            unpack_result = _format.unpack(data_part)
        except Exception as ex:
            msg = f"Unpack error {_format=}, {data_part=}"
            raise UnPackError(msg) from ex
        result.extend(unpack_result.data)
        _data = _data[unpack_result.unpacked_bytes_length:] if unpack_result.unpacked_bytes_length < len(data) else b""
    return tuple(result)
