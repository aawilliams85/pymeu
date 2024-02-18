import pycomm3
import struct
from warnings import warn

from .constants import *
from .messages import *
from .types import *

def terminal_create_directory(cip: pycomm3.CIPDriver, dir: str) -> bool:
    req_args = ['\\Windows\\RemoteHelper.DLL', 'CreateRemDirectory', dir]
    resp_code, resp_data = terminal_run_function(cip, req_args)
    if (resp_code != CREATE_DIR_SUCCESS): raise Exception('Failed to create directory on terminal.')    
    return True

def terminal_create_file_exchange_for_download(cip: pycomm3.CIPDriver, file: MEFile, remote_path: str) -> int:
    # Request format
    #
    # Byte 0 Transfer Type (always 1 for file download?)
    # Byte 1 Overwrite (0 = New File, 1 = Overwrite Existing)
    # Byte 2 to 3 Chunk size in bytes
    # Byte 4 to 7 File size in bytes
    # Byte 8 to N-1 File name
    # Byte N null footer
    req_header = struct.pack('<BBHI', 0x01, int(file.overwrite_required), CHUNK_SIZE, file.get_size())
    req_args = [f'{remote_path}\\{file.name}']
    req_data = req_header + b''.join(arg.encode() + b'\x00' for arg in req_args)

    # Response format
    #
    # Byte 0 to 1 message instance (should match request, 0x00)
    # Byte 2 to 3 unknown purpose
    # Byte 4 to 5 file instance (use this instance for file transfer)
    # Byte 6 to 7 chunk size in bytes
    resp = msg_create_file_exchange(cip, req_data)
    if not resp: raise Exception('Failed to create file exchange on terminal')
    resp_msg_instance, resp_unk1, resp_file_instance, resp_chunk_size = struct.unpack('<HHHH', resp.value)
    if (resp_msg_instance != 0): raise Exception(f'Response message instance {resp_msg_instance} is not zero.  Most likely there was an incomplete transfer.  Reboot terminal and try again.')
    if (resp_unk1 != 0 ): raise Exception(f'Response unknown bytes {resp_unk1} are not zero.  Examine packets.')
    if (resp_file_instance != 1): warn(f'Response file instance {resp_file_instance} is not one.  Examine packets.')
    if (resp_chunk_size != CHUNK_SIZE): raise Exception(f'Response chunk size {resp_chunk_size} did not match request size {CHUNK_SIZE}')
    return resp_file_instance

def terminal_create_file_exchange_for_download_mer(cip: pycomm3.CIPDriver, file: MEFile) -> int:
    return terminal_create_file_exchange_for_download(cip, file, '\\Application Data\\Rockwell Software\\RSViewME\\Runtime')

def terminal_create_file_exchange_for_upload(cip: pycomm3.CIPDriver, remote_path: str) -> int:
    # Request format
    #
    # Byte 0 Transfer Type (always 0 for file upload?)
    # Byte 1 unknown purpose (used for overwrite in download... maybe no purpose here?)
    # Byte 2 to 3 Chunk size in bytes
    # Byte 4 to N-1 File name
    # Byte N null footer
    req_header = struct.pack('<BBH', 0x00, 0x00, CHUNK_SIZE)
    req_args = [f'{remote_path}']
    req_data = req_header + b''.join(arg.encode() + b'\x00' for arg in req_args)

    # Response format
    #
    # Byte 0 to 1 message instance (should match request, 0x00)
    # Byte 2 to 3 unknown purpose
    # Byte 4 to 5 file instance (use this instance for file transfer, increases with each subsequent transfer until Delete is run)
    # Byte 6 to 7 chunk size in bytes
    # Byte 8 to 11 file size in bytes
    resp = msg_create_file_exchange(cip, req_data)
    if not resp: raise Exception('Failed to create file exchange on terminal')
    resp_msg_instance, resp_unk1, resp_file_instance, resp_chunk_size, resp_file_size = struct.unpack('<HHHHI', resp.value)
    if (resp_msg_instance != 0): raise Exception(f'Response message instance {resp_msg_instance} is not zero.  Most likely there was an incomplete transfer.  Reboot terminal and try again.')
    if (resp_unk1 != 0 ): raise Exception(f'Response unknown bytes {resp_unk1} are not zero.  Examine packets.')
    if (resp_file_instance != 1): warn(f'Response file instance {resp_file_instance} is not one.  Examine packets.')
    if (resp_chunk_size != CHUNK_SIZE): raise Exception(f'Response chunk size {resp_chunk_size} did not match request size {CHUNK_SIZE}')
    return resp_file_instance

def terminal_create_file_exchange_for_upload_mer(cip: pycomm3.CIPDriver, file: MEFile) -> int:
    return terminal_create_file_exchange_for_upload(cip, f'\\Application Data\\Rockwell Software\\RSViewME\\Runtime\\{file.name}')

def terminal_create_file_exchange_for_upload_mer_list(cip: pycomm3.CIPDriver) -> int:
    return terminal_create_file_exchange_for_upload(cip, '\\Application Data\\Rockwell Software\\RSViewME\\Runtime\\Results.txt')

def terminal_create_mer_list(cip: pycomm3.CIPDriver):
    req_args = ['\\Windows\\RemoteHelper.DLL','FileBrowse','\\Application Data\\Rockwell Software\\RSViewME\\Runtime\\*.mer::\\Application Data\\Rockwell Software\\RSViewME\\Runtime\\Results.txt']
    resp_code, resp_data = terminal_run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Response code was not zero.  Examine packets.')
    return True

def terminal_create_runtime_directory(cip: pycomm3.CIPDriver, file: MEFile) -> bool:
    # Create paths
    if not(terminal_create_directory(cip, '\\Application Data')): return False
    if not(terminal_create_directory(cip, '\\Application Data\\Rockwell Software')): return False
    if not(terminal_create_directory(cip, '\\Application Data\\Rockwell Software\\RSViewME')): return False
    if not(terminal_create_directory(cip, '\\Application Data\\Rockwell Software\\RSViewME\\Runtime')): return False
    if not(terminal_create_directory(cip, '\\Application Data\\Rockwell Software\\RSViewME\\Runtime\\')): return False
    return True

def terminal_delete_file_exchange(cip: pycomm3.CIPDriver, instance: int):
    return msg_delete_file_exchange(cip, instance)

def terminal_end_file_write(cip: pycomm3.CIPDriver, instance: int):
    req_data = b'\x00\x00\x00\x00\x02\x00\xff\xff'
    return msg_write_file_chunk(cip, instance, req_data)

def terminal_file_download(cip: pycomm3.CIPDriver, instance: int, file: str):
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
            resp = msg_write_file_chunk(cip, instance, req_data)
            if not resp: raise Exception(f'Failed to write chunk {req_chunk_number} to terminal.')
            resp_unk1, resp_chunk_number, resp_next_chunk_number = struct.unpack('<III', resp.value)
            if (resp_unk1 != 0 ): raise Exception(f'Response unknown bytes {resp_unk1} are not zero.  Examine packets.')
            if (resp_chunk_number != req_chunk_number ): raise Exception(f'Response chunk number {resp_chunk_number} did not match request chunk number {req_chunk_number}.')
            if (resp_next_chunk_number != req_next_chunk_number): raise Exception(f'Response next chunk number {resp_next_chunk_number} did not match expected next chunk number {req_next_chunk_number}.')

            # Continue to next chunk
            req_chunk_number += 1

def terminal_file_download_mer(cip: pycomm3.CIPDriver, instance: int, file: MEFile):
    terminal_file_download(cip, instance, file.path)

def terminal_file_upload(cip: pycomm3.CIPDriver, instance: int):
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
        resp = msg_read_file_chunk(cip, instance, req_data)
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

def terminal_file_upload_mer(cip: pycomm3.CIPDriver, instance: int, file: MEFile):
    resp_binary = terminal_file_upload(cip, instance)
    with open(file.path, 'wb') as dest_file:
        dest_file.write(resp_binary)

def terminal_file_upload_mer_list(cip: pycomm3.CIPDriver, instance: int):
    resp_binary = terminal_file_upload(cip, instance)
    resp_str = "".join([chr(b) for b in resp_binary if b != 0])
    resp_list = resp_str.split(':')
    return resp_list

def terminal_get_file_exists(cip: pycomm3.CIPDriver, file: MEFile) -> bool:
    req_args = ['\\Windows\\RemoteHelper.DLL', 'FileExists', f'\\Application Data\\Rockwell Software\\RSViewME\\Runtime\\{file.name}']
    resp_code, resp_data = terminal_run_function(cip, req_args)
    if (resp_code != 0): return False    
    return bool(int(resp_data))

def terminal_get_file_size(cip: pycomm3.CIPDriver, file: MEFile) -> int:
    req_args = ['\\Windows\\RemoteHelper.DLL', 'FileSize', f'\\Application Data\\Rockwell Software\\RSViewME\\Runtime\\{file.name}']
    resp_code, resp_data = terminal_run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Response code was not zero.  Examine packets.')
    return int(resp_data)

def terminal_get_folder_exists(cip: pycomm3.CIPDriver) -> bool:
    req_args = ['\\Windows\\RemoteHelper.DLL', 'StorageExists', '\\Application Data']
    resp_code, resp_data = terminal_run_function(cip, req_args)
    if (resp_code != 0):
        warn(f'Response code was not zero.  Examine packets.')
        return False
    return bool(int(resp_data))

def terminal_get_free_space(cip: pycomm3.CIPDriver) -> int:
    req_args = ['\\Windows\\RemoteHelper.DLL', 'FreeSpace', '\\Application Data\\Rockwell Software\\RSViewME\\Runtime\\']
    resp_code, resp_data = terminal_run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Response code was not zero.  Examine packets.')
    return int(resp_data)

def terminal_get_helper_version(cip: pycomm3.CIPDriver) -> str:
    req_args = ['\\Windows\\RemoteHelper.DLL', 'GetVersion', '\\Windows\\RemoteHelper.DLL']
    resp_code, resp_data = terminal_run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Response code was not zero.  Examine packets.')
    return str(resp_data)

def terminal_get_me_version(cip: pycomm3.CIPDriver) -> str:
    return terminal_get_registry_value(cip, ['HKEY_LOCAL_MACHINE\\SOFTWARE\\Rockwell Software\\RSView Enterprise\\MEVersion'])

def terminal_get_product_code(cip: pycomm3.CIPDriver) -> str:
    return terminal_get_registry_value(cip, ['HKEY_LOCAL_MACHINE\\SOFTWARE\\Rockwell Software\\RSLinxNG\\CIP Identity\\ProductCode'])

def terminal_get_product_type(cip: pycomm3.CIPDriver) -> str:
    return terminal_get_registry_value(cip, ['HKEY_LOCAL_MACHINE\\SOFTWARE\\Rockwell Software\\RSLinxNG\\CIP Identity\\ProductType'])

def terminal_get_registry_value(cip: pycomm3.CIPDriver, key: str) -> str:
    req_data = b''.join(arg.encode() + b'\x00' for arg in key)

    # Response format
    #
    # Byte 0 to 3 response code (0 = function ran, otherwise failed)
    # Byte 4 to 7 unknown purpose
    # Byte 8 to N-1 product type string
    # Byte N null footer
    resp = msg_read_registry(cip, req_data)
    if not resp: raise Exception(f'Failed to read registry key: {key}')
    resp_code = int.from_bytes(resp.value[:4], byteorder='little', signed=False)
    if (resp_code != 0): raise Exception(f'Read registry response code was not zero.  Examine packets.')

    resp_unk1 = int.from_bytes(resp.value[4:8], byteorder='little', signed=False)
    resp_value = str(resp.value[8:].decode('utf-8').strip('\x00'))
    return resp_value

def terminal_get_startup_mer(cip: pycomm3.CIPDriver) -> str:
    return terminal_get_registry_value(cip, ['HKEY_LOCAL_MACHINE\\SOFTWARE\\Rockwell Software\\RSViewME\\Startup Options\\CurrentApp'])

def terminal_is_get_unk_valid(cip: pycomm3.CIPDriver) -> bool:
    # I don't know what any of these three attributes are for yet.
    # It may be checking that the file exchange is available.
    resp = msg_get_attr_unk(cip, b'\x30\x01')
    if not resp: return False
    if resp.value not in GET_UNK1_VALUES:
        warn(f'Invalid UNK1 value.  Examine packets.')
        return False

    resp = msg_get_attr_unk(cip, b'\x30\x08')
    if not resp: return False
    if resp.value not in GET_UNK2_VALUES:
        warn(f'Invalid UNK2 value.  Examine packets.')
        return False

    resp = msg_get_attr_unk(cip, b'\x30\x09')
    if not resp: return False
    if resp.value not in GET_UNK3_VALUES:
        warn(f'Invalid UNK3 value.  Examine packets.')
        return False

    return True

def terminal_is_set_unk_valid(cip: pycomm3.CIPDriver) -> bool:
    # I don't know what setting this attribute does yet.
    # It may be marking the file exchange as in use.
    #
    resp = msg_set_attr_unk(cip, b'\x30\x01\xff\xff')
    if not resp: return False

    return True

def terminal_reboot(cip: pycomm3.CIPDriver):
    # For some reason this one has an extra trailing byte.
    # Not sure if it has some other purpose yet
    req_args = ['\\Windows\\RemoteHelper.DLL', 'BootTerminal','']
    req_data = b''.join(arg.encode() + b'\x00' for arg in req_args)

    try:
        resp = msg_run_function(cip, req_data)
        
        #Should never get here
        raise Exception(resp)
    except pycomm3.exceptions.CommError as e:
        # Unlike most CIP messages, this one is always expected to
        # create an exception.  When it is received by the terminal,
        # the device reboots and breaks the socket.
        if (str(e) != 'failed to receive reply'): raise e

def terminal_run_function(cip: pycomm3.CIPDriver, req_args):
    req_data = b''.join(arg.encode() + b'\x00' for arg in req_args)

    # Response format
    #
    # Byte 0 to 3 response code (typically 0 = function ran, otherwise failed, not all functions follow this)
    # Byte 4 to N-1 response data
    # Byte N null footer
    resp = msg_run_function(cip, req_data)
    if not resp: raise Exception(f'Failed to run function: {req_args}.')
    resp_code = int.from_bytes(resp.value[:4], byteorder='little', signed=False)
    resp_data = resp.value[4:].decode('utf-8').strip('\x00')
    return resp_code, resp_data

def terminal_set_startup_mer(cip: pycomm3.CIPDriver, file: MEFile, replace_comms: bool, delete_logs: bool) -> bool:
    req_args = ['\\Windows\\RemoteHelper.DLL', 'CreateRemMEStartupShortcut', f'\\Application Data:{file.name}: /r /delay']
    if replace_comms: req_args = [req_args[1], req_args[2], req_args[3] + ' /o']
    if delete_logs: req_args = [req_args[1], req_args[2], req_args[3] + ' /d']
    resp_code, resp_data = terminal_run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Response code was not zero.  Examine packets.')
    return True