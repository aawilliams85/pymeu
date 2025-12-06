from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
import olefile
import os
import struct
from typing import Optional

from . import types

PAGE_HEADER_SIZE_BYTES = 4
PAGE_SIZE_BYTES = 32768
CHUNK_SIZE_TOKENS = 16

STREAM_NAME_MAPPEE = '__MAPPEE'
STREAM_NAME_MAPPER = '__MAPPER'

def get_pointer_values(input: memoryview) -> tuple[int, int]:
    if len(input) != 2: raise ValueError("Input must be exactly 2 bytes long")
    length = (input[0] & 0x0F) + 1
    offset = ((input[0] >> 4) << 8) | input[1]
    return length, offset

def is_pointer(input: int, bit: int) -> bool:
    return bool((input >> bit) & 1)

def decompress_token(page_decompressed: bytearray, page_offset: int, token_length: int, token_offset: int):
    # This is a slower but functional decompression that slides byte by byte across
    # the array.
    token_index = 0
    while (token_index < token_length):
        if (token_offset > 0):
            page_decompressed[page_offset + token_index] = page_decompressed[page_offset - token_offset + token_index]
        else:
            page_decompressed[page_offset + token_index] = page_decompressed[page_offset - 1]
        token_index += 1

def decompress_token_fast(page_decompressed: bytearray, page_offset: int, token_length: int, token_offset: int):
    # This is a faster but broken decompression since it copies the data all at once.
    # If the token extends beyond where page_offset started, it is inacurrate.
    if token_offset > 0:
        page_decompressed[page_offset:page_offset + token_length] = page_decompressed[page_offset - token_offset:page_offset - token_offset + token_length]
    else:
        page_decompressed[page_offset:page_offset + token_length] = [page_decompressed[page_offset - 1]] * token_length

def decompress_chunk(page_decompressed: bytearray, chunk_data: memoryview, chunk_control: int, page_offset: int) -> int:
    chunk_offset = 0
    chunk_token_count = len(chunk_data) - chunk_control.bit_count()
    for x in range(chunk_token_count):
        if is_pointer(chunk_control, x):
            token_length, token_offset = get_pointer_values(chunk_data[chunk_offset:chunk_offset + 2])
            chunk_offset += 2

            if (token_length > token_offset):
                decompress_token(page_decompressed=page_decompressed, page_offset=page_offset, token_length=token_length, token_offset=token_offset)
            else:
                decompress_token_fast(page_decompressed=page_decompressed, page_offset=page_offset, token_length=token_length, token_offset=token_offset)
            page_offset += token_length

        else:
            page_decompressed[page_offset] = chunk_data[chunk_offset]
            chunk_offset += 1
            page_offset += 1
    return page_offset

def decompress_page(input: memoryview) -> bytearray:
    page_offset = 0
    page_length = len(input)

    # If the page is too short, return as-is
    if (page_length < 4): return bytearray(input[page_offset:])

    # If the page is uncompressed already, return as-is
    page_control = input[page_offset:page_offset + PAGE_HEADER_SIZE_BYTES]
    page_offset += PAGE_HEADER_SIZE_BYTES
    if (page_control[0] == 0x01): return bytearray(input[page_offset:])

    # Split the page into chunks
    page_decompressed = bytearray(PAGE_SIZE_BYTES)
    page_decompressed_offset = 0
    while (page_offset < page_length):
        # Two bytes for control bits
        chunk_control: int = struct.unpack_from('H', input, page_offset)[0]
        page_offset += 2

        # One byte for each token, plus one byte for each of the pointers
        # since they are two bytes each.
        chunk_length_expected = chunk_control.bit_count() + CHUNK_SIZE_TOKENS
        chunk_data = input[page_offset:page_offset + chunk_length_expected]
        page_offset += len(chunk_data)

        # Decompressed offset is cumulative
        page_decompressed_offset = decompress_chunk(page_decompressed=page_decompressed, chunk_data=chunk_data, chunk_control=chunk_control, page_offset=page_decompressed_offset)

    # Typically the last page of the stream could be less than the preallocated size
    if (page_decompressed_offset < PAGE_SIZE_BYTES): page_decompressed = page_decompressed[:page_decompressed_offset]
    return page_decompressed

def decompress_stream(
    input: memoryview,
    progress_desc: str | None = None,
    progress: Optional[Callable[[str, str, int, int], None]] = None
) -> bytearray:
    stream_offset = 0
    stream_length = len(input)

    # If the stream is too short it can't contain
    # a compressed stream and will be returned directly.
    if (stream_length < 4): return bytearray(input.tobytes())

    # Split compressed stream into pages
    stream_page_compressed: list[memoryview] = []
    while (stream_offset < stream_length):
        # If the stream is too short it can't contain
        # another page definition, the stream doesn't follow
        # the expected format and will be returned directly.
        if (stream_length - stream_offset) < 4: return bytearray(input.tobytes())

        page_length = struct.unpack_from('I', input, stream_offset)[0]
        stream_offset += 4
        page_mv = input[stream_offset:stream_offset + page_length]
        stream_offset += page_length
        stream_page_compressed.append(page_mv)

    # If the offsets don't add up this stream doesn't follow
    # the expected format and will be returned directly.
    if (stream_offset != stream_length): return bytearray(input.tobytes())

    # Decompress each page separately
    workers = os.cpu_count() or 1
    page_bytes_list = [mv.tobytes() for mv in stream_page_compressed]
    completed_bytes = 0
    stream_page_decompressed: list[bytearray] = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        decompressed_iterator = pool.map(decompress_page, page_bytes_list)
        for i, decompressed_page in enumerate(decompressed_iterator):
            stream_page_decompressed.append(decompressed_page)

            # Optional progress indication
            if progress:
                completed_bytes += len(page_bytes_list[i])
                progress(f'Decompressing {progress_desc or 'stream'}', 'bytes', stream_length, completed_bytes)

    # Optional progress indication
    if progress: progress(f'Decompressing {progress_desc or 'stream'}', 'bytes', stream_length, stream_length)

    # Concatenate pages into decompressed stream
    output_length = sum(len(x) for x in stream_page_decompressed)
    output = bytearray(output_length)
    output_offset = 0
    for page in stream_page_decompressed:
        page_len = len(page)
        output[output_offset:output_offset + page_len] = page
        output_offset += page_len

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
            print(stream_name)
            stream_data = decompress_stream(
                input=memoryview(stream_data),
                progress_desc=stream_name,
                progress=progress
            )
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