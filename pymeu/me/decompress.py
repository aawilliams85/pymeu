from collections.abc import Callable
import olefile
import os
from typing import Optional

from . import types

CHUNK_CONTROL_SIZE_BYTES = 2
CHUNK_DATA_SIZE_TOKENS = 16
PAGE_CONTEXT_SIZE_BYTES = 4095
PAGE_CONTROL_SIZE_BYTES = 4
PAGE_HEADER_SIZE_BYTES = 4
TOKEN_LITERAL_SIZE_BYTES = 1
TOKEN_POINTER_SIZE_BYTES = 2

STREAM_NAME_MAPPEE = '__MAPPEE'
STREAM_NAME_MAPPER = '__MAPPER'

def _get_int8_nibbles(value: int):
    high_nibble = (value >> 4) & 0x0F
    low_nibble = value & 0x0F
    return (low_nibble, high_nibble)

def _get_pointer_values(bytes: bytearray):
    (length, offset_msb) = _get_int8_nibbles(bytes[0])
    offset_lsb = bytes[1]
    offset = (offset_msb << 8) + offset_lsb
    length += 1
    return (length, offset)

def _get_expected_chunk_length(bytes) -> int:
    tokens = int.from_bytes(bytes, byteorder='little').bit_count()
    literals = CHUNK_DATA_SIZE_TOKENS - tokens
    length = (tokens * 2) + literals
    return length

def _is_pointer(control: int, index: int) -> bool:
    return bool((control >> index) & 1)

def _decompress_chunk(input: bytearray, control: int, data: bytearray, length: int) -> bytearray:
    output = bytearray(input)

    # Each chunk is comprised of a fixed number of tokens (some literal, some pointers)
    byte_index = 0
    for data_index in range(CHUNK_DATA_SIZE_TOKENS):
        if _is_pointer(control, data_index):
            token_bytes = data[byte_index:byte_index+TOKEN_POINTER_SIZE_BYTES]
            (token_length, token_offset) = _get_pointer_values(token_bytes)

            head = len(output)
            token_index = 0
            while (token_index < token_length):
                if (token_offset > 0):
                    # Normally look back and slide forward.
                    # This allows for the case where the length is
                    # greater than the offset, so part of the new bytes
                    # ends up used again within the same substitution.
                    output.append(output[head - token_offset + token_index])
                else:
                    # Offset zero is a special case where the last char
                    # is just repeated.
                    output.append(output[head - 1])
                token_index += 1

            byte_index += TOKEN_POINTER_SIZE_BYTES
        else:
            output.append(data[byte_index])
            byte_index += TOKEN_LITERAL_SIZE_BYTES
        
        if byte_index >= length: break

    return output[len(input):]

def _decompress_page(input: bytearray) -> bytearray:
    output = bytearray()
    length = len(input)
    offset = 0
    page_control_bytes = input[offset:offset + PAGE_CONTROL_SIZE_BYTES]
    offset += PAGE_CONTROL_SIZE_BYTES

    # If page is not compressed, return the rest of the page as-is
    if (page_control_bytes[0] == 0x01):
        output = input[offset:]
        return output

    # Then parse through the rest of the page
    while offset < length:
        # At the start of each chunk is a pair of control bytes
        chunk_control_bytes = input[offset:offset + CHUNK_CONTROL_SIZE_BYTES]
        chunk_control_int = int.from_bytes(chunk_control_bytes, 'little')
        if not chunk_control_bytes: break
        chunk_expected_length = _get_expected_chunk_length(chunk_control_bytes)

        offset += CHUNK_CONTROL_SIZE_BYTES
        chunk_data_bytes = input[offset:offset + chunk_expected_length]
        chunk_actual_length = len(chunk_data_bytes)
        offset += chunk_expected_length

        context = output[-PAGE_CONTEXT_SIZE_BYTES:]
        output += _decompress_chunk(context, chunk_control_int, chunk_data_bytes, chunk_actual_length)

    # Return decompressed page bytes
    return output

def _decompress_stream(
    input: bytearray,
    progress_desc: str = None,
    progress: Optional[Callable[[str, str, int, int], None]] = None
) -> bytearray:
    output = bytearray()
    length = len(input)
    offset = 0
    while offset < length:
        # At the start of each page there is an 4 byte header to signify page length
        page_size = int.from_bytes(input[offset:offset + PAGE_HEADER_SIZE_BYTES], byteorder='little')
        offset += PAGE_HEADER_SIZE_BYTES
        page_bytes = input[offset:offset + page_size]
        offset += page_size

        output += _decompress_page(page_bytes)
        if progress:
            desc = f'Decompressing'
            if progress_desc: desc += f' {progress_desc}'
            progress(desc, 'bytes', length, offset)

    return output

def _create_subfolders(output_path: str, archive_paths: list[str]):
    folders = archive_paths[:-1]
    current_path = output_path
    for folder in folders:
        current_path = os.path.join(current_path, folder)
        os.makedirs(current_path, exist_ok=True)
    return os.path.join(current_path, archive_paths[-1])

def _get_mapper_filename(input: bytearray) -> str:
    offset = 0
    length = int.from_bytes(input[offset:offset + PAGE_HEADER_SIZE_BYTES], byteorder='little')
    offset += PAGE_HEADER_SIZE_BYTES
    name = input[offset:].decode('utf-16-le').rstrip('\x00')
    return name

def _get_mapper_for_mappee(ole: olefile.OleFileIO, mappee_name: str) -> str:
    # The assumption is that if there are multiple MAPPER/MAPPEE pairs
    # in the archive, that they have unique numbers at end of the stream name.
    mapper_name = mappee_name.replace(STREAM_NAME_MAPPEE, STREAM_NAME_MAPPER)
    mapper_data = ole.openstream(mapper_name).read()
    return _get_mapper_filename(mapper_data)

def decompress_archive(
    ole: olefile.OleFileIO,
    progress: Optional[Callable[[str, str, int, int], None]] = None
) -> list[types.MEArchive]:
    streams = []
    for stream_path in ole.listdir():
        stream_name = '/'.join(stream_path)
        if (ole.exists(stream_name) and not ole.get_type(stream_name) == olefile.STGTY_STORAGE):
            original_name = stream_name
            # If a stream name starts with __MAPPEE it has the content of the file.
            # If a stream name starts with __MAPPER it has the name of the file.
            #
            # This logic restores the name from the MAPPER to the MAPPEE and
            # excludes the MAPPER from the stream list.
            if stream_name.startswith(STREAM_NAME_MAPPEE):
                actual_name = _get_mapper_for_mappee(ole, original_name)
                stream_name = actual_name
                stream_path[-1] = actual_name
            if stream_name.startswith(STREAM_NAME_MAPPER):
                continue
            
            stream_data = ole.openstream(original_name).read()
            try:
                stream_data = _decompress_stream(
                    input=stream_data,
                    progress_desc=stream_name,
                    progress=progress
                )
            except Exception as e:
                # Some streams aren't compressed.
                #
                # Is there a better way to retain them and still
                # print exceptions for failed decompressions?
                #print(e)
                pass

            stream_info = types.MEArchive(
                name=stream_name,
                data=stream_data,
                path=stream_path,
                size=len(stream_data)
            )
                
            streams.append(stream_info)
    return streams

def archive_to_disk(file_path: str, output_path: str):
    # Directly dump archive with no application-specific
    # handling (ex: for *.FUP or *.MER)

    # Create output folder if it doesn't exist yet
    if not(os.path.exists(output_path)): os.makedirs(output_path, exist_ok=True)

    with olefile.OleFileIO(file_path) as ole:
        streams = decompress_archive(ole)
        for stream in streams:
            stream_output_path = _create_subfolders(output_path, stream.path)
            with open(stream_output_path, 'wb') as f:
                f.write(stream.data)