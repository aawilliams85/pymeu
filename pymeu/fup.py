import olefile
import os

CONTROL_SIZE = 2
DATA_SIZE = 16
LITERAL_SIZE = 1
PAGE_CONTROL_SIZE_BYTES = 4
PAGE_HEADER_SIZE_BYTES = 4
TOKEN_SIZE = 2

BLACKLISTED_STREAMS = [
    'DIRSIZE_INFORMATION',
    'PRODUCT_VERSION_INFORMATION',
    'VERSION_INFORMATION',
    '__MAPPEE0',
    '__MAPPER0'
]

def get_int8_nibbles(value: int):
    high_nibble = (value >> 4) & 0x0F
    low_nibble = value & 0x0F
    return (low_nibble, high_nibble)

def get_control_values(bytes: bytearray):
    (length, offset_msb) = get_int8_nibbles(bytes[0])
    offset_lsb = bytes[1]
    offset = (offset_msb << 8) + offset_lsb
    length += 1
    return (length, offset)

def get_expected_length(bytes):
    tokens = int.from_bytes(bytes, byteorder='little').bit_count()
    literals = DATA_SIZE - tokens
    length = (tokens * 2) + literals
    return length

def is_token(bytes: bytes, index) -> bool:
    tokens = int.from_bytes(bytes, byteorder='little').bit_count()
    if (tokens & (1 << index)): return True
    return False

def decompress_page(input: bytearray) -> bytearray:
    output = bytearray()
    length = len(input)
    offset = 0
    page_control_bytes = input[offset:offset + PAGE_CONTROL_SIZE_BYTES]
    offset += PAGE_CONTROL_SIZE_BYTES
    #print(page_control_bytes)

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
        control_length = get_expected_length(control_bytes)

        offset += CONTROL_SIZE
        data_bytes = input[offset:offset + control_length]
        actual_length = len(data_bytes)
        #if (actual_length != control_length): print(f'Actual length: {actual_length}')
        offset += control_length

        # Each chunk is comprised of a fixed number of data tokens (some literal, some pointers)
        byte_index = 0
        for data_index in range(DATA_SIZE):
            if control_int & (1 << data_index):
            #if is_token(control_int, data_index):
                token_bytes = data_bytes[byte_index:byte_index+TOKEN_SIZE]
                (token_length, token_offset) = get_control_values(token_bytes)

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

def decompress_stream(input: bytearray) -> bytearray:
    output = bytearray()
    length = len(input)
    offset = 0
    while offset < length:
        # At the start of each page there is an 4 byte header to signify page length
        page_size = int.from_bytes(input[offset:offset + PAGE_HEADER_SIZE_BYTES], byteorder='little')
        offset += PAGE_HEADER_SIZE_BYTES
        page_bytes = input[offset:offset + page_size]
        offset += page_size

        output += decompress_page(page_bytes)

    return output

def extract_fup(file_path: str, output_path: str):
    streams = []
    ole = olefile.OleFileIO(file_path)
    for stream_path in ole.listdir():
        stream_name = '/'.join(stream_path)
        if (ole.exists(stream_name) and not ole.get_type(stream_name) == olefile.STGTY_STORAGE):
            stream_data = ole.openstream(stream_name).read()
            stream_info = {
                'name': stream_name,
                'data': stream_data,
                'path': stream_path,
                'size': len(stream_data)
            }
            streams.append(stream_info)
            print(f'Name: {stream_name}, Path: {stream_path}, Size: {len(stream_data)}')
    ole.close()
    for stream in streams:
        if stream['name'] in BLACKLISTED_STREAMS: continue
        stream_decompressed = decompress_stream(stream['data'])
        stream_output_path = os.path.join(output_path, stream['name'])
        with open(stream_output_path, 'wb') as f:
            f.write(stream_decompressed)