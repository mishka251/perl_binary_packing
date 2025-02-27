from perl_binary_packing.factory import parse_format
from perl_binary_packing.formats import UnpackResult


class PackError(Exception):
    pass


class UnPackError(Exception):
    pass


def pack(format_str: str, *args: object) -> bytes:
    try:
        return _pack(format_str, *args)
    except Exception as ex:
        msg = f"Error while packing {args} with {format_str=}"
        raise PackError(msg) from ex


def _pack(format_str: str, *args: object) -> bytes:
    _format = parse_format(format_str)
    current_args = args
    try:
        _packed = _format.pack(current_args)
    except Exception as ex:
        msg = f"Error pack {_format=} {current_args=}"
        raise PackError(msg) from ex
    return _packed.packed


def unpack(format_str: str, data: bytes, pos: int = 0) -> tuple[object, ...]:
    try:
        result = _unpack(format_str, data, pos)
    except Exception as ex:
        msg = f"Error while unpacking {data!r} with {format_str=}"
        raise UnPackError(msg) from ex
    return tuple(result.data)


def unpack_with_length(
    format_str: str,
    data: bytes,
    pos: int = 0,
) -> UnpackResult[tuple[object, ...]]:
    try:
        return _unpack(format_str, data, pos)
    except Exception as ex:
        msg = f"Error while unpacking {data!r} with {format_str=}"
        raise UnPackError(msg) from ex


def _unpack(
    format_str: str,
    data: bytes,
    pos: int = 0,
) -> UnpackResult[tuple[object, ...]]:
    _format = parse_format(format_str)
    try:
        unpack_result = _format.unpack(data, pos)
    except Exception as ex:
        msg = f"Unpack error {_format=}, {data!r}"
        raise UnPackError(msg) from ex
    return unpack_result
