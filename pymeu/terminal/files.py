
import pycomm3
import struct

from enum import Enum
from warnings import warn

from .. import messages
from .. import types

# When files are transferred, this is the maximum number of bytes
# used per message.  Quick tests up to 2000 bytes did succeed, >2000 bytes failed.
CHUNK_SIZE = 1984

# Known values associated with some file services, with unclear purpose or meaning.
# Further investigation needed.
GET_UNK1_VALUES = {
    b'\x02\x00'
}

# Known values associated with some file services, with unclear purpose or meaning.
# Further investigation needed.
GET_UNK2_VALUES = {
    b'\x01\x60',
    b'\x03\x41'
}

# Known values associated with some file services, with unclear purpose or meaning.
# Further investigation needed.
GET_UNK3_VALUES = {
    b'\x64\x00'
}

class TransferType(Enum):
    DOWNLOAD = int.from_bytes(b'\x01', byteorder='big')
    UPLOAD = int.from_bytes(b'\x00', byteorder='big')

def create_exchange_download(cip: pycomm3.CIPDriver, file: types.MEFile, remote_path: str) -> int:
    """
    Creates a file exchange for downloading from the local device to the remote terminal.

    Args:
        cip (pycomm3.CIPDriver): CIPDriver to communicate with the terminal
        file (MEFile): Identifying metadata for the file to be downloaded.
        remote_path (str): The remote path on the terminal where the file 
        will be downloaded to.

    Returns:
        int: The file exchange instance returned from the device, that can be
        used for subsequent file transfer operations.

    Raises:
        Exception: If the file exchange creation fails or if the response 
        contains unexpected values, indicating potential issues with the 
        transfer.

    Request Format:
        The request consists of the following byte structure:

        | Byte Range    | Description                                         |
        |---------------|-----------------------------------------------------|
        | Byte 0        | Transfer Type (always 1 for file download)          |
        | Byte 1        | Overwrite flag (0 = New File, 1 = Overwrite)        |
        | Bytes 2->3    | Chunk size in bytes                                 |
        | Bytes 4->7    | File size in bytes                                  |
        | Bytes 8->N-1  | File name                                           |
        | Byte N        | Null footer                                         |

    Response Format:
        The response consists of the following byte structure:

        | Byte Range    | Description                                         |
        |---------------|-----------------------------------------------------|
        | Bytes 0->1    | Message instance (should match request, 0x00)       |
        | Bytes 2->3    | Unknown purpose                                     |
        | Bytes 4->5    | File instance (use this instance for file transfer) |
        | Bytes 6->7    | Chunk size in bytes                                 |

    Note:
        If the response message instance or unknown bytes are not zero, it 
        may indicate an incomplete transfer happened previously. In such cases,
        reboot the terminal and try again.
    """
    req_header = struct.pack('<BBHI', TransferType.DOWNLOAD.value, int(file.overwrite_required), CHUNK_SIZE, file.get_size())
    req_args = [f'{remote_path}\\{file.name}']
    req_data = req_header + b''.join(arg.encode() + b'\x00' for arg in req_args)

    resp = messages.create_file_exchange(cip, req_data)
    if not resp: raise Exception('Failed to create file exchange on terminal')
    resp_msg_instance, resp_unk1, resp_file_instance, resp_chunk_size = struct.unpack('<HHHH', resp.value)
    if (resp_msg_instance != 0): raise Exception(f'Response message instance {resp_msg_instance} is not zero.  Most likely there was an incomplete transfer.  Reboot terminal and try again.')
    if (resp_unk1 != 0 ): raise Exception(f'Response unknown bytes {resp_unk1} are not zero.  Examine packets.')
    if (resp_file_instance != 1): warn(f'Response file instance {resp_file_instance} is not one.  Examine packets.')
    if (resp_chunk_size != CHUNK_SIZE): raise Exception(f'Response chunk size {resp_chunk_size} did not match request size {CHUNK_SIZE}')
    return resp_file_instance

def create_exchange_upload(cip: pycomm3.CIPDriver, remote_path: str) -> int:
    """
    Creates a file exchange for uploading from the remote terminal to the local device.

    Args:
        cip (pycomm3.CIPDriver): CIPDriver to communicate with the terminal
        remote_path (str): The remote path on the terminal where the file 
        will be uploaded from.

    Returns:
        int: The file exchange instance returned from the device, that can be
        used for subsequent file transfer operations.

    Raises:
        Exception: If the file exchange creation fails or if the response 
        contains unexpected values, indicating potential issues with the 
        transfer.

    Request Format:
        The request consists of the following byte structure:

        | Byte Range    | Description                                         |
        |---------------|-----------------------------------------------------|
        | Byte 0        | Transfer Type (always 0 for file upload)            |
        | Byte 1        | Unknown purpose (overwrite in download, N/A?)       |
        | Bytes 2->3    | Chunk size in bytes                                 |
        | Bytes 4->N-1  | File name                                           |
        | Byte N        | Null footer                                         |

    Response Format:
        The response consists of the following byte structure:

        | Byte Range    | Description                                         |
        |---------------|-----------------------------------------------------|
        | Bytes 0->1    | Message instance (should match request, 0x00)       |
        | Bytes 2->3    | Unknown purpose                                     |
        | Bytes 4->5    | File instance (use this instance for file transfer) |
        | Bytes 6->7    | Chunk size in bytes                                 |
        | Bytes 8->11   | File size in bytes                                  |

    Note:
        If the response message instance or unknown bytes are not zero, it 
        may indicate an incomplete transfer happened previously. In such cases,
        reboot the terminal and try again.
    """
    req_header = struct.pack('<BBH', TransferType.UPLOAD.value, 0x00, CHUNK_SIZE)
    req_args = [f'{remote_path}']
    req_data = req_header + b''.join(arg.encode() + b'\x00' for arg in req_args)

    resp = messages.create_file_exchange(cip, req_data)
    if not resp: raise Exception('Failed to create file exchange on terminal')
    resp_msg_instance, resp_unk1, resp_file_instance, resp_chunk_size, resp_file_size = struct.unpack('<HHHHI', resp.value)
    if (resp_msg_instance != 0): raise Exception(f'Response message instance {resp_msg_instance} is not zero.  Most likely there was an incomplete transfer.  Reboot terminal and try again.')
    if (resp_unk1 != 0 ): raise Exception(f'Response unknown bytes {resp_unk1} are not zero.  Examine packets.')
    if (resp_file_instance != 1): warn(f'Response file instance {resp_file_instance} is not one.  Examine packets.')
    if (resp_chunk_size != CHUNK_SIZE): raise Exception(f'Response chunk size {resp_chunk_size} did not match request size {CHUNK_SIZE}')
    return resp_file_instance

def delete_exchange(cip: pycomm3.CIPDriver, instance: int):
    return messages.delete_file_exchange(cip, instance)

def download(cip: pycomm3.CIPDriver, instance: int, source_data: bytearray) -> bool:
    """
    Downloads a file from the local device to the remote terminal.
    The transfer happens by breaking the file down into one or more
    chunks, with each chunk being sent via a CIP message and reassembled
    on the remote terminal.

    Args:
        cip (pycomm3.CIPDriver): CIPDriver to communicate with the terminal
        instance (int): The previously created file transfer instance.
        source_data (bytearray): The binary data of the file to be transferred.

    Returns:
        bool: True when transfer is complete.

    Raises:
        Exception: If the file transfer fails or if the response contains
        unexpected values, indicating potential issues with the transfer.

    Request Format:
        The request consists of the following byte structure:

        | Byte Range    | Description                                         |
        |---------------|-----------------------------------------------------|
        | Bytes 0->3    | Chunk number                                        |
        | Bytes 4->5    | Chunk size in bytes                                 |
        | Bytes 6->N    | Chunk data                                          |

    Response Format:
        The response consists of the following byte structure:

        | Byte Range    | Description                                         |
        |---------------|-----------------------------------------------------|
        | Bytes 0->3    | Unknown purpose                                     |
        | Bytes 4->7    | Chunk number echo                                   |
        | Bytes 8->11   | Next chunk number expected                          |

    Note:
        If the response message instance or unknown bytes are not zero, it 
        may indicate an incomplete transfer happened previously. In such cases,
        reboot the terminal and try again.
    """
    req_chunk_number = 1
    req_offset = 0
    while req_offset < len(source_data):
        req_chunk = source_data[req_offset:req_offset + CHUNK_SIZE]
        req_header = struct.pack('<IH', req_chunk_number, len(req_chunk))
        req_next_chunk_number = req_chunk_number + 1
        req_data = req_header + req_chunk

        # End of file
        if not req_chunk: break

        resp = messages.write_file_chunk(cip, instance, req_data)
        if not resp: raise Exception(f'Failed to write chunk {req_chunk_number} to terminal.')
        resp_unk1, resp_chunk_number, resp_next_chunk_number = struct.unpack('<III', resp.value)
        if (resp_unk1 != 0 ): raise Exception(f'Response unknown bytes {resp_unk1} are not zero.  Examine packets.')
        if (resp_chunk_number != req_chunk_number ): raise Exception(f'Response chunk number {resp_chunk_number} did not match request chunk number {req_chunk_number}.')
        if (resp_next_chunk_number != req_next_chunk_number): raise Exception(f'Response next chunk number {resp_next_chunk_number} did not match expected next chunk number {req_next_chunk_number}.')

        # Continue to next chunk
        req_chunk_number += 1
        req_offset += len(req_chunk)

    # Close out file
    req_data = b'\x00\x00\x00\x00\x02\x00\xff\xff'
    resp = messages.write_file_chunk(cip, instance, req_data)
    return True

def download_mer(cip: pycomm3.CIPDriver, instance: int, file: str):
    with open(file, 'rb') as source_file:
        return download(cip, instance, bytearray(source_file.read()))

def upload(cip: pycomm3.CIPDriver, instance: int) -> bytearray:
    """
    Uploads a file from the remote terminal to the local device.
    The transfer happens by breaking the file down into one or more
    chunks, with each chunk being sent via a CIP message and reassembled
    on the local device.

    Args:
        cip (pycomm3.CIPDriver): CIPDriver to communicate with the terminal
        instance (int): The previously created file transfer instance.

    Returns:
        bytearray: The raw binary data uploaded from the remote terminal.

    Raises:
        Exception: If the file transfer fails or if the response contains
        unexpected values, indicating potential issues with the transfer.

    Request Format:
        The request consists of the following byte structure:

        | Byte Range    | Description                                         |
        |---------------|-----------------------------------------------------|
        | Bytes 0->3    | Chunk number                                        |

    Response Format:
        The response consists of the following byte structure:

        | Byte Range    | Description                                         |
        |---------------|-----------------------------------------------------|
        | Bytes 0->3    | Unknown purpose                                     |
        | Bytes 4->7    | Chunk number echo                                   |
        | Bytes 8->9    | Chunk size in bytes                                 |
        | Bytes 10->N   | Chunk data                                          |

    Note:
        If the response message instance or unknown bytes are not zero, it 
        may indicate an incomplete transfer happened previously. In such cases,
        reboot the terminal and try again.
    """
    req_chunk_number = 1
    resp_binary = bytearray()
    while True:
        req_data = struct.pack('<I', req_chunk_number)

        resp = messages.read_file_chunk(cip, instance, req_data)
        if not resp: raise Exception(f'Failed to read chunk {req_chunk_number} to terminal.')
        resp_unk1 = int.from_bytes(resp.value[:4], byteorder='little', signed=False)
        resp_chunk_number = int.from_bytes(resp.value[4:8], byteorder='little', signed=False)
        resp_chunk_size = int.from_bytes(resp.value[8:9], byteorder='little', signed=False)
        resp_data = bytes(resp.value[10:])

        if (resp_unk1 != 0 ): raise Exception(f'Response unknown bytes {resp_unk1} are not zero.  Examine packets.')
        if (resp_chunk_number != req_chunk_number) and (resp_chunk_number != 0): raise Exception(f'Response chunk number {resp_chunk_number} did not match request chunk number {req_chunk_number}.')

        # End of file
        if (resp_chunk_number == 0) and (resp_chunk_size == 2) and (resp_data == b'\xff\xff'):
            #print('End of file')
            break

        # Write to mer list
        resp_binary += resp_data

        # Continue to next chunk
        req_chunk_number += 1

    return resp_binary

def upload_mer(cip: pycomm3.CIPDriver, instance: int, file: types.MEFile):
    resp_binary = upload(cip, instance)
    with open(file.path, 'wb') as dest_file:
        dest_file.write(resp_binary)

def upload_list(cip: pycomm3.CIPDriver, instance: int):
    resp_binary = upload(cip, instance)
    resp_str = "".join([chr(b) for b in resp_binary if b != 0])
    resp_list = resp_str.split(':')
    return resp_list

def is_get_unk_valid(cip: pycomm3.CIPDriver) -> bool:
    # I don't know what any of these three attributes are for yet.
    # It may be checking that the file exchange is available.
    resp = messages.get_attr_unk(cip, b'\x30\x01')
    if not resp: return False
    if resp.value not in GET_UNK1_VALUES:
        warn(f'Invalid UNK1 value.  Examine packets.')
        return False

    resp = messages.get_attr_unk(cip, b'\x30\x08')
    if not resp: return False
    if resp.value not in GET_UNK2_VALUES:
        warn(f'Invalid UNK2 value.  Examine packets.')
        return False

    resp = messages.get_attr_unk(cip, b'\x30\x09')
    if not resp: return False
    if resp.value not in GET_UNK3_VALUES:
        warn(f'Invalid UNK3 value.  Examine packets.')
        return False

    return True

def is_set_unk_valid(cip: pycomm3.CIPDriver) -> bool:
    # I don't know what setting this attribute does yet.
    # It may be marking the file exchange as in use.
    #
    resp = messages.set_attr_unk(cip, b'\x30\x01\xff\xff')
    if not resp: return False

    return True