import olefile
import os

from . import types

CONTROL_SIZE = 2
DATA_SIZE = 16
LITERAL_SIZE = 1
PAGE_CONTROL_SIZE_BYTES = 4
PAGE_HEADER_SIZE_BYTES = 4
TOKEN_SIZE = 2

STREAM_NAME_MAPPEE = '__MAPPEE'
STREAM_NAME_MAPPER = '__MAPPER'

def _get_int8_nibbles(value: int):
    high_nibble = (value >> 4) & 0x0F
    low_nibble = value & 0x0F
    return (low_nibble, high_nibble)

def _get_control_values(bytes: bytearray):
    (length, offset_msb) = _get_int8_nibbles(bytes[0])
    offset_lsb = bytes[1]
    offset = (offset_msb << 8) + offset_lsb
    length += 1
    return (length, offset)

def _get_expected_length(bytes) -> int:
    tokens = int.from_bytes(bytes, byteorder='little').bit_count()
    literals = DATA_SIZE - tokens
    length = (tokens * 2) + literals
    return length

def _is_token(bytes: bytes, index) -> bool:
    tokens = int.from_bytes(bytes, byteorder='little').bit_count()
    if (tokens & (1 << index)): return True
    return False

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
        control_bytes = input[offset:offset + CONTROL_SIZE]
        if not control_bytes: break
        control_int = int.from_bytes(control_bytes, byteorder='little')
        control_length = _get_expected_length(control_bytes)

        offset += CONTROL_SIZE
        data_bytes = input[offset:offset + control_length]
        actual_length = len(data_bytes)
        offset += control_length

        # Each chunk is comprised of a fixed number of data tokens (some literal, some pointers)
        byte_index = 0
        for data_index in range(DATA_SIZE):
            if control_int & (1 << data_index):
            #if is_token(control_int, data_index):
                token_bytes = data_bytes[byte_index:byte_index+TOKEN_SIZE]
                (token_length, token_offset) = _get_control_values(token_bytes)

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

                byte_index += TOKEN_SIZE
            else:
                output.append(data_bytes[byte_index])
                byte_index += LITERAL_SIZE
            
            if byte_index >= actual_length: break

    # Return decompressed page bytes
    return output

def _decompress_stream(input: bytearray) -> bytearray:
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

def decompress_archive(ole: olefile.OleFileIO, output_path: str) -> list[types.MEArchive]:
    streams = []
    for stream_path in ole.listdir():
        stream_name = '/'.join(stream_path)
        if (ole.exists(stream_name) and not ole.get_type(stream_name) == olefile.STGTY_STORAGE):
            # If a stream name starts with __MAPPEE it has the content of the file.
            # If a stream name starts with __MAPPER it has the name of the file.
            #
            # This logic restores the name from the MAPPER to the MAPPEE and
            # excludes the MAPPER from the stream list.
            if stream_name.startswith(STREAM_NAME_MAPPEE):
                stream_path[-1] = _get_mapper_for_mappee(ole, stream_name)
            if stream_name.startswith(STREAM_NAME_MAPPER):
                continue
            
            stream_data = ole.openstream(stream_name).read()
            try:
                stream_data = _decompress_stream(stream_data)
            except Exception as e:
                # Some streams aren't compressed AND 
                print(e)

            stream_info = types.MEArchive(
                name=stream_name,
                data=stream_data,
                path=stream_path,
                size=len(stream_data)
            )
                
            streams.append(stream_info)
            print(f'Name: {stream_name}, Path: {stream_path}, Size: {len(stream_data)}')
    return streams

def archive_to_disk(file_path: str, output_path: str):
    # Directly dump archive with no application-specific
    # handling (ex: for *.FUP or *.MER)

    # Create output folder if it doesn't exist yet
    if not(os.path.exists(output_path)): os.makedirs(output_path, exist_ok=True)

    with olefile.OleFileIO(file_path) as ole:
        streams = decompress_archive(ole, output_path)
        for stream in streams:
            stream_output_path = _create_subfolders(output_path, stream.path)
            with open(stream_output_path, 'wb') as f:
                f.write(stream.data)