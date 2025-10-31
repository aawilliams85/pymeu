import struct

from . import types

def _lookahead_bytes(input: types.MEBinStream, length: int) -> bytes:
    if ((input.offset + length) > len(input.data)): raise MemoryError(f'Memory bounds exceeded.  Size: {len(input.data):0X}, Offset: {input.offset:0X}, Length: {length:0X}.')
    value = input.data[input.offset:input.offset + length]
    return value

def _lookahead_bool(input: types.MEBinStream) -> bool:
    value = bool(int.from_bytes(_lookahead_bytes(input=input, length=1), 'little'))
    return value

def _lookahead_int(input: types.MEBinStream, length: int = 4) -> int:
    value = int.from_bytes(_lookahead_bytes(input=input, length=length), 'little')
    return value

def _seek_forward(input: types.MEBinStream, length: int):
    # Anywhere this is called, basically means that I don't
    # understand what a range of bytes means and want to skip
    # past it.
    _seek_bytes(input=input, length=length)

def _seek_bytes(input: types.MEBinStream, length: int = 4) -> bytes:
    if ((input.offset + length) > len(input.data)): raise MemoryError(f'Memory bounds exceeded.  Size: {len(input.data):0X}, Offset: {input.offset:0X}, Length: {length:0X}.')
    value = input.data[input.offset:input.offset + length]
    input.offset += length
    return value

def _seek_float(input: types.MEBinStream) -> float:
    length = 4
    value = struct.unpack('<f', input.data[input.offset:input.offset + length])[0]
    input.offset += length
    return value

def _seek_double(input: types.MEBinStream) -> float:
    length = 8
    value = struct.unpack('<d', input.data[input.offset:input.offset + length])[0]
    input.offset += length
    return value

def _seek_int(input: types.MEBinStream, length: int = 4) -> int:
    value = int.from_bytes(input.data[input.offset:input.offset + length], 'little')
    input.offset += length
    return value

def _seek_string(input: types.MEBinStream, length: int = 64, decode: str = 'utf-16le') -> str:
    data = _seek_bytes(input=input, length=length)
    value = data.decode(decode).rstrip('\x00')
    return value

def _seek_string_var_len(input: types.MEBinStream, length: int = 4, mult: int = 1, decode: str = 'utf-16le') -> str:
    # Some variable-length string fields start with 4 bytes to specify the length in bytes.
    # Other use 2 bytes to specify the length in characters.  For the latter specify length=2, mult=2.
    str_len = int.from_bytes(input.data[input.offset: input.offset + length], 'little')
    input.offset += length
    length = str_len * mult
    data = _seek_bytes(input=input, length=length)
    value = data.decode(decode).rstrip('\x00')
    return value
