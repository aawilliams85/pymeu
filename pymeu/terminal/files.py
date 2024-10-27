from enum import Enum
import pycomm3
import struct
from warnings import warn

from .. import messages
from ..types import *
from .paths import *

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

def create_exchange_download(cip: pycomm3.CIPDriver, file: MEFile, remote_path: str) -> int:
    # Request format
    #
    # Byte 0 Transfer Type (always 1 for file download?)
    # Byte 1 Overwrite (0 = New File, 1 = Overwrite Existing)
    # Byte 2 to 3 Chunk size in bytes
    # Byte 4 to 7 File size in bytes
    # Byte 8 to N-1 File name
    # Byte N null footer
    req_header = struct.pack('<BBHI', TransferType.DOWNLOAD.value, int(file.overwrite_required), CHUNK_SIZE, file.get_size())
    req_args = [f'{remote_path}\\{file.name}']
    req_data = req_header + b''.join(arg.encode() + b'\x00' for arg in req_args)

    # Response format
    #
    # Byte 0 to 1 message instance (should match request, 0x00)
    # Byte 2 to 3 unknown purpose
    # Byte 4 to 5 file instance (use this instance for file transfer)
    # Byte 6 to 7 chunk size in bytes
    resp = messages.create_file_exchange(cip, req_data)
    if not resp: raise Exception('Failed to create file exchange on terminal')
    resp_msg_instance, resp_unk1, resp_file_instance, resp_chunk_size = struct.unpack('<HHHH', resp.value)
    if (resp_msg_instance != 0): raise Exception(f'Response message instance {resp_msg_instance} is not zero.  Most likely there was an incomplete transfer.  Reboot terminal and try again.')
    if (resp_unk1 != 0 ): raise Exception(f'Response unknown bytes {resp_unk1} are not zero.  Examine packets.')
    if (resp_file_instance != 1): warn(f'Response file instance {resp_file_instance} is not one.  Examine packets.')
    if (resp_chunk_size != CHUNK_SIZE): raise Exception(f'Response chunk size {resp_chunk_size} did not match request size {CHUNK_SIZE}')
    return resp_file_instance

def create_exchange_upload(cip: pycomm3.CIPDriver, remote_path: str) -> int:
    # Request format
    #
    # Byte 0 Transfer Type (always 0 for file upload?)
    # Byte 1 unknown purpose (used for overwrite in download... maybe no purpose here?)
    # Byte 2 to 3 Chunk size in bytes
    # Byte 4 to N-1 File name
    # Byte N null footer
    req_header = struct.pack('<BBH', TransferType.UPLOAD.value, 0x00, CHUNK_SIZE)
    req_args = [f'{remote_path}']
    req_data = req_header + b''.join(arg.encode() + b'\x00' for arg in req_args)

    # Response format
    #
    # Byte 0 to 1 message instance (should match request, 0x00)
    # Byte 2 to 3 unknown purpose
    # Byte 4 to 5 file instance (use this instance for file transfer, increases with each subsequent transfer until Delete is run)
    # Byte 6 to 7 chunk size in bytes
    # Byte 8 to 11 file size in bytes
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

def end_write(cip: pycomm3.CIPDriver, instance: int):
    req_data = b'\x00\x00\x00\x00\x02\x00\xff\xff'
    return messages.write_file_chunk(cip, instance, req_data)

def download(cip: pycomm3.CIPDriver, instance: int, file: str):
    req_chunk_number = 1
    with open(file, 'rb') as source_file:
        while True:
            # Request format
            #
            # Byte 0 to 3 chunk number
            # Byte 4 to 5 chunk size in bytes
            # Byte 6 to N chunk data
            req_chunk = source_file.read(CHUNK_SIZE)
            req_header = struct.pack('<IH', req_chunk_number, len(req_chunk))
            req_next_chunk_number = req_chunk_number + 1
            req_data = req_header + req_chunk

            # End of file
            if not req_chunk:
                #print(f'File downloaded from: {file.path}')
                break

            # Response format
            #
            # Byte 0 to 3 unknown purpose
            # Byte 4 to 7 req chunk number echo
            # Byte 8 to 11 next chunk number
            resp = messages.write_file_chunk(cip, instance, req_data)
            if not resp: raise Exception(f'Failed to write chunk {req_chunk_number} to terminal.')
            resp_unk1, resp_chunk_number, resp_next_chunk_number = struct.unpack('<III', resp.value)
            if (resp_unk1 != 0 ): raise Exception(f'Response unknown bytes {resp_unk1} are not zero.  Examine packets.')
            if (resp_chunk_number != req_chunk_number ): raise Exception(f'Response chunk number {resp_chunk_number} did not match request chunk number {req_chunk_number}.')
            if (resp_next_chunk_number != req_next_chunk_number): raise Exception(f'Response next chunk number {resp_next_chunk_number} did not match expected next chunk number {req_next_chunk_number}.')

            # Continue to next chunk
            req_chunk_number += 1

def upload(cip: pycomm3.CIPDriver, instance: int):
    req_chunk_number = 1
    resp_binary = bytearray()
    while True:
        # Request format
        #
        # Byte 0 to 3 chunk number
        req_data = struct.pack('<I', req_chunk_number)

        # Response format
        #
        # Byte 0 to 3 unknown purpose
        # Byte 4 to 7 req chunk number echo
        # Byte 8 to 9 chunk size in bytes
        # Byte 10 to N chunk data
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

def upload_mer(cip: pycomm3.CIPDriver, instance: int, file: MEFile):
    resp_binary = upload(cip, instance)
    with open(file.path, 'wb') as dest_file:
        dest_file.write(resp_binary)

def upload_mer_list(cip: pycomm3.CIPDriver, instance: int):
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