from collections.abc import Callable
import olefile
import os
import struct
from typing import Optional

from . import types


CHUNK_CONTROL_SIZE_BYTES = 2
CHUNK_DATA_SIZE_TOKENS = 16
PAGE_HEADER_SIZE_BYTES = 4
TOKEN_LITERAL_SIZE_BYTES = 1
TOKEN_POINTER_SIZE_BYTES = 2

STREAM_NAME_MAPPEE = '__MAPPEE'
STREAM_NAME_MAPPER = '__MAPPER'

def _get_int8_nibbles(value: int) -> tuple[int, int]:
    high_nibble = (value >> 4) & 0x0F
    low_nibble = value & 0x0F
    return low_nibble, high_nibble

def _get_pointer_values(input: memoryview) -> tuple[int, int]:
    if len(input) != 2: raise ValueError("Input must be exactly 2 bytes long")
    (length, offset_msb) = _get_int8_nibbles(input[0])
    offset_lsb = input[1]
    offset = (offset_msb << 8) | offset_lsb
    length += 1
    return length, offset

def _get_expected_chunk_length(input: int) -> int:
    # Each chunk is made up of a fixed number of tokens.
    # Some are pointers (2 bytes), the rest are literals (1 byte).
    pointers = int.from_bytes(input, byteorder='little').bit_count()
    literals = CHUNK_DATA_SIZE_TOKENS - pointers
    length = (pointers * TOKEN_POINTER_SIZE_BYTES) + (literals * TOKEN_LITERAL_SIZE_BYTES)
    return length

def _is_pointer(control: int, index: int) -> bool:
    return bool((control >> index) & 1)
'''
def _decompress_chunk(input: bytearray, control: int, data: memoryview, length: int) -> bytearray:
    output = bytearray(input)

    # Each chunk is comprised of a fixed number of tokens (some literal, some pointers)
    byte_index = 0
    for data_index in range(CHUNK_DATA_SIZE_TOKENS):
        if _is_pointer(control, data_index):
            token_bytes = data[byte_index:byte_index+TOKEN_POINTER_SIZE_BYTES]
            (token_length, token_offset) = _get_pointer_values(memoryview(token_bytes))

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
'''

def _decompress_chunk(
    context: memoryview,
    control: int,
    data: memoryview,
    length: int
) -> bytearray:
    output = bytearray()

    chunk_offset = 0
    for token_index in range(CHUNK_DATA_SIZE_TOKENS):
        if _is_pointer(control, token_index):
            (token_length, token_offset) = _get_pointer_values(data[chunk_offset:chunk_offset + TOKEN_POINTER_SIZE_BYTES])
            head = len(output)
            print(f'{token_offset} {token_length}')

            '''
            look_back_length = token_length - head
            if (look_back_length > 0):
                output.append(context[-look_back_length:])
                token_length -= look_back_length

            output.append(output[])
            '''
        else:
            output.append(data[token_index])
    return output

def _decompress_page(
    input: memoryview
) -> bytearray:
    page_offset = 0
    page_length = len(input)
    output = bytearray()

    # If this page is uncompressed, return the data portion as-is
    page_control_bytes = memoryview(input[page_offset:page_offset + PAGE_HEADER_SIZE_BYTES])
    page_offset += PAGE_HEADER_SIZE_BYTES
    if (page_control_bytes[0] == 0x01): return memoryview(input[page_offset:])

    # Otherwise decompress each chunk and append them
    while (page_offset < page_length):
        chunk_control_int = struct.unpack_from('H', input, page_offset)[0]
        page_offset += 2
        chunk_length = _get_expected_chunk_length(chunk_control_int)
        chunk_data_bytes = input[page_offset:page_offset + chunk_length]
        page_offset += chunk_length

        output.append(_decompress_chunk(context=memoryview(output), 
                                        control=chunk_control_int, 
                                        data=chunk_data_bytes, 
                                        length=chunk_length))

    return output

def _decompress_stream(
    input: memoryview,
    progress_desc: str = None,
    progress: Optional[Callable[[str, str, int, int], None]] = None
) -> bytearray:

    # Break the stream into a set of pages
    stream_offset = 0
    stream_length = len(input)
    stream_pages_compressed = []
    stream_pages_length = []
    while (stream_offset < stream_length):
        page_length = struct.unpack_from('I', input, stream_offset)[0]
        stream_offset += 4
        page_mv = memoryview(input[stream_offset:stream_offset + page_length])
        stream_offset += page_length
        stream_pages_compressed.append(page_mv)
        stream_pages_length.append(page_length + 4)

    # Decompress each page separately
    # No context is shared across pages
    stream_pages_decompressed = []
    stream_pages_progress = 0
    print(len(stream_pages_length))
    for (page, length) in zip(stream_pages_compressed, stream_pages_length):
        stream_pages_decompressed.append(_decompress_page(page))
        if progress:
            stream_pages_progress += length
            desc = f'Decompressing'
            if progress_desc: desc += f' {progress_desc}'
            progress(desc, 'bytes', stream_length, stream_pages_progress)

    # Concatenate output
    output = bytearray()
    for page in stream_pages_decompressed: output.extend(page)
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
                print(stream_name)
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

def archive_to_stream(
    input_path: str | bytes,
    progress: Optional[Callable[[str, str, int, int], None]] = None
) -> list[types.MEArchive]:
    with olefile.OleFileIO(input_path) as ole:
        streams = decompress_archive(
            ole=ole,
            progress=progress
        )
        return streams

def archive_to_folder(
    input_path: str | bytes, 
    output_path: str,
    progress: Optional[Callable[[str, str, int, int], None]] = None
):
    if not(os.path.exists(output_path)): os.makedirs(output_path, exist_ok=True)
    streams = archive_to_stream(
        input_path=input_path,
        progress=progress
    )
    for stream in streams:
        stream_output_path = _create_subfolders(output_path, stream.path)
        with open(stream_output_path, 'wb') as f:
            f.write(stream.data)