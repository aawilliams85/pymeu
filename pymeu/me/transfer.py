from collections.abc import Callable
from enum import IntEnum
import os
import struct
from typing import Optional
from warnings import warn

from .. import comms
from . import messages
from . import helper
from . import types
from . import util

END_OF_FILE = b'\x00\x00\x00\x00\x02\x00\xff\xff'

# Known values associated with some file services, with unclear purpose or meaning.
# Further investigation needed.
GET_UNK1_VALUES = {
    b'\x02\x00'
}
GET_UNK2_VALUES = {
    b'\x01\x60',
    b'\x03\x41'
}
GET_UNK3_VALUES = {
    b'\x64\x00'
}

class TransferType(IntEnum):
    DOWNLOAD = int.from_bytes(b'\x01', byteorder='big')
    UPLOAD = int.from_bytes(b'\x00', byteorder='big')

def _create_download(
    cip: comms.Driver, 
    file_path_terminal: str,
    file_size: int,
    overwrite: bool = True,
) -> int:
    '''
    Creates a transfer instance for downloading from the local device to the remote terminal.

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
        | Bytes 4->5    | Transfer instance (use this instance for download)  |
        | Bytes 6->7    | Chunk size in bytes                                 |
    '''
    req_header = struct.pack('<BBHI', TransferType.DOWNLOAD, int(overwrite), cip.me_chunk_size, file_size)
    req_args = [file_path_terminal]
    req_data = req_header + b''.join(arg.encode() + b'\x00' for arg in req_args)

    resp = messages.create_transfer(cip, req_data)
    resp_exception_text = f'Failed to create transfer instance for download of {file_path_terminal}.'
    if not resp: raise Exception(f'{resp_exception_text}.  No message response.')
 
    resp_msg_instance, resp_unk1, resp_transfer_instance, resp_chunk_size = struct.unpack('<HHHH', resp.value)
    if (resp_msg_instance != 0): raise Exception(f'{resp_exception_text}.  Response message instance: {resp_msg_instance}, expected: 0.  There may be an incomplete transfer.  Reboot terminal and try again.')
    if (resp_unk1 != 0 ): raise Exception(f'{resp_exception_text}.  Response UNK1 bytes: {resp_unk1}, expected: 0.  Please file a bug report with all available information.')
    if (resp_chunk_size != cip.me_chunk_size): raise Exception(f'{resp_exception_text}.  Response chunk size: {resp_chunk_size}, expected: {cip.me_chunk_size}.  Please file a bug report with all available information.')
    return resp_transfer_instance

def _create_upload(
    cip: comms.Driver, 
    file_path_terminal: str
) -> tuple[int, int]:
    '''
    Creates a transfer instance for uploading from the remote terminal to the local device.

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
        | Bytes 4->5    | Transfer instance (use this instance for upload)    |
        | Bytes 6->7    | Chunk size in bytes                                 |
        | Bytes 8->11   | File size in bytes                                  |
    '''
    req_header = struct.pack('<BBH', TransferType.UPLOAD, 0x00, cip.me_chunk_size)
    req_args = [f'{file_path_terminal}']
    req_data = req_header + b''.join(arg.encode() + b'\x00' for arg in req_args)

    resp = messages.create_transfer(cip, req_data)
    resp_exception_text = f'Failed to create transfer instance for upload of {file_path_terminal}.'
    if not resp: raise Exception(f'{resp_exception_text}.  No message response.')

    resp_msg_instance, resp_unk1, resp_transfer_instance, resp_chunk_size, resp_file_size = struct.unpack('<HHHHI', resp.value)
    if (resp_msg_instance != 0): raise Exception(f'{resp_exception_text}.  Response message instance: {resp_msg_instance}, expected: 0.  There may be an incomplete transfer.  Reboot terminal and try again.')
    if (resp_unk1 != 0 ): raise Exception(f'{resp_exception_text}.  Response UNK1 bytes: {resp_unk1}, expected: 0.  Please file a bug report with all available information.')
    if (resp_chunk_size != cip.me_chunk_size): raise Exception(f'{resp_exception_text}.  Response chunk size: {resp_chunk_size}, expected: {cip.me_chunk_size}.  Please file a bug report with all available information.')
    return resp_transfer_instance, resp_file_size

def _delete(cip: comms.Driver, instance: int):
    return messages.delete_transfer(cip, instance)

def _write_download(
    cip: comms.Driver, 
    file_data: bytearray, 
    instance: int, 
    progress_desc: str = None, 
    progress: Optional[Callable[[str, str, int, int], None]] = None
) -> bool:
    """
    Downloads a file from the local device to the remote terminal.
    The transfer happens by breaking the file down into one or more
    chunks, with each chunk being sent via a CIP message and reassembled
    on the remote terminal.

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
    """
    req_chunk_number = 1
    req_offset = 0
    total_bytes = len(file_data)
    while req_offset < total_bytes:
        req_chunk = file_data[req_offset:req_offset + cip.me_chunk_size]
        req_header = struct.pack('<IH', req_chunk_number, len(req_chunk))
        req_next_chunk_number = req_chunk_number + 1
        req_data = req_header + req_chunk

        # End of file
        if not req_chunk: break

        resp = messages.write_file_chunk(cip, instance, req_data)
        if not resp: raise Exception(f'Failed to write chunk {req_chunk_number} to terminal.')
        resp_unk1, resp_chunk_number, resp_next_chunk_number = struct.unpack('<III', resp.value)
        if (resp_unk1 != 0 ): raise Exception(f'Response unknown bytes: {resp_unk1}, expected: 0.')
        if (resp_chunk_number != req_chunk_number ): raise Exception(f'Response chunk number: {resp_chunk_number}, expected: {req_chunk_number}.')
        if (resp_next_chunk_number != req_next_chunk_number): raise Exception(f'Response next chunk number: {resp_next_chunk_number}, expected: {req_next_chunk_number}.')

        # Update progress callback
        current_bytes = req_offset + len(req_chunk)
        if progress: progress(f'Download {progress_desc}','bytes', total_bytes, current_bytes)

        # Continue to next chunk
        req_chunk_number += 1
        req_offset += len(req_chunk)

    # Close out file
    req_data = END_OF_FILE
    resp = messages.write_file_chunk(cip, instance, req_data)
    return True

def _read_upload(
    cip: comms.Driver, 
    file_size: int, 
    instance: int, 
    progress_desc: str = None,
    progress: Optional[Callable[[str, str, int, int], None]] = None
) -> bytearray:
    """
    Uploads a file from the remote terminal to the local device.
    The transfer happens by breaking the file down into one or more
    chunks, with each chunk being sent via a CIP message and reassembled
    on the local device.

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

        if (resp_unk1 != 0 ): raise Exception(f'Response unknown bytes: {resp_unk1}, expected: 0.')
        if (resp_chunk_number != req_chunk_number) and (resp_chunk_number != 0): raise Exception(f'Response chunk number: {resp_chunk_number}. expected: {req_chunk_number}.')

        # End of file
        if (resp_chunk_number == 0) and (resp_chunk_size == 2) and (resp_data == b'\xff\xff'):
            #print('End of file')
            break

        # Write to mer list
        resp_binary += resp_data

        # Update progress callback
        if progress: progress(f'Upload {progress_desc}','bytes', file_size,len(resp_binary))

        # Continue to next chunk
        req_chunk_number += 1

    return resp_binary

def _is_ready(cip: comms.Driver) -> bool:
    # I don't know what any of these three attributes are for yet.
    # It may be checking that the file exchange is available.
    resp = messages.read_file_ready(cip, b'\x30\x01')
    if not resp: return False
    if resp.value not in GET_UNK1_VALUES:
        warn(f'Invalid UNK1 value.  Please file a bug report with all available information.')
        return False

    resp = messages.read_file_ready(cip, b'\x30\x08')
    if not resp: return False
    if resp.value not in GET_UNK2_VALUES:
        warn(f'Invalid UNK2 value.  Please file a bug report with all available information.')
        return False

    resp = messages.read_file_ready(cip, b'\x30\x09')
    if not resp: return False
    if resp.value not in GET_UNK3_VALUES:
        warn(f'Invalid UNK3 value.  Please file a bug report with all available information.')
        return False

    return True

def _set_ready(cip: comms.Driver) -> bool:
    # I don't know what setting this attribute does yet.
    # It may be marking the file exchange as in use.
    #
    resp = messages.write_file_ready(cip, b'\x30\x01\xff\xff')
    if not resp: return False

    return True

def download(
    cip: comms.Driver, 
    device: types.MEDeviceInfo, 
    file_data: bytearray, 
    file_path_terminal: str, 
    overwrite: bool = False,
    progress: Optional[Callable[[str, str, int, int], None]] = None
) -> bool:
    instance = None
    try:
        dirname, basename = util.split_file_path(file_path_terminal)
        try:
            # Attempt to ensure the directory exists
            # Still having trouble with some directories
            helper.create_folders(cip, device.me_paths, dirname)
        except Exception as e:
            print(e)

        file_exists = helper.get_file_exists(cip, device.me_paths, file_path_terminal)
        if (overwrite and not file_exists): overwrite = False
        if (file_exists and not overwrite): raise FileExistsError(f'File {file_path_terminal} exists on terminal already and overwrite was not specified.')

        if not(_is_ready(cip)): raise Exception('Terminal not ready for file transfer lock.')
        instance = _create_download(
            cip=cip,
            file_path_terminal=file_path_terminal,
            file_size=len(file_data),
            overwrite=overwrite
        )

        if not(_set_ready(cip)): raise Exception('Terminal refused file transfer lock.')
        _write_download(
            cip=cip,
            file_data=file_data,
            instance=instance,
            progress_desc=file_path_terminal,
            progress=progress
        )
        device.log.append(f'Downloaded {file_path_terminal} using transfer instance {instance}.')

        _delete(
            cip=cip,
            instance=instance
        )
    except Exception as e:
        if instance is not None: _delete(cip=cip, instance=instance)
        raise Exception(f'Download {file_path_terminal} failed: {str(e)}')

    return True

def download_file(
    cip: comms.Driver, 
    device: types.MEDeviceInfo, 
    file_path_local: str,
    file_path_terminal: str,
    overwrite: bool = True,
    progress: Optional[Callable[[str, str, int, int], None]] = None
) -> bool:
    with open(file_path_local, 'rb') as source_file:
        return download(
            cip=cip,
            device=device,
            file_data=bytearray(source_file.read()),
            file_path_terminal=file_path_terminal,
            overwrite=overwrite,
            progress=progress
        )
    
def download_file_mer(
    cip: comms.Driver, 
    device: types.MEDeviceInfo, 
    file_path_local: str,
    file_name_terminal: str,
    overwrite: bool,
    run_at_startup: bool,
    replace_comms: bool,
    delete_logs: bool,
    progress: Optional[Callable[[str, str, int, int], None]] = None
) -> bool:
    file_path_terminal = f'{device.me_paths.runtime}\\{file_name_terminal}'
    download_file(
        cip=cip,
        device=device,
        file_path_local=file_path_local,
        file_path_terminal=file_path_terminal,
        overwrite=overwrite,
        progress=progress
    )
    if run_at_startup:
        helper.create_me_shortcut(
            cip=cip,
            paths=device.me_paths,
            file=file_name_terminal,
            replace_comms=replace_comms,
            delete_logs=delete_logs
        )
        util.reboot(cip, device)
    return True

def upload(
    cip: comms.Driver, 
    device: types.MEDeviceInfo, 
    file_path_terminal: str, 
    progress: Optional[Callable[[str, str, int, int], None]] = None
) -> bytearray:
    instance = None
    try:
        file_exists = helper.get_file_exists(cip=cip, paths=device.me_paths, file_path=file_path_terminal)
        if file_exists:
            instance, file_size = _create_upload(cip=cip, file_path_terminal=file_path_terminal)
            resp_binary = _read_upload(
                cip=cip,
                file_size=file_size,
                instance=instance,
                progress_desc=file_path_terminal,
                progress=progress
            )
            _delete(cip=cip, instance=instance)
            return resp_binary
        raise FileNotFoundError(f'File {file_path_terminal} does not exist on terminal.')
    except Exception as e:
        if instance is not None: _delete(cip=cip, instance=instance)
        raise Exception(f'Upload {file_path_terminal} failed: {str(e)}')

def upload_file(
    cip: comms.Driver, 
    device: types.MEDeviceInfo, 
    file_path_local: str,
    file_path_terminal: str,
    progress: Optional[Callable[[str, str, int, int], None]] = None
):
    resp_binary = upload(
        cip=cip,
        device=device,
        file_path_terminal=file_path_terminal,
        progress=progress
    )
    if not(os.path.exists(file_path_local)): os.makedirs(os.path.dirname(file_path_local), exist_ok=True)
    with open(file_path_local, 'wb') as dest_file:
        dest_file.write(resp_binary)

def upload_file_mer(
    cip: comms.Driver, 
    device: types.MEDeviceInfo, 
    file_path_local,
    file_name_terminal,
    progress: Optional[Callable[[str, str, int, int], None]] = None
) -> bool:
    file_path_terminal = f'{device.me_paths.runtime}\\{file_name_terminal}'
    upload_file(
        cip=cip,
        device=device,
        file_path_local=file_path_local,
        file_path_terminal=file_path_terminal,
        progress=progress
    )
    return True

def upload_list(
    cip: comms.Driver,
    device: types.MEDeviceInfo,
    file_path_terminal: str
) -> list[str]:
    resp_binary = upload(
        cip=cip,
        device=device,
        file_path_terminal=file_path_terminal,
        progress=None
    )
    resp_str = "".join([chr(b) for b in resp_binary if b != 0])
    resp_list = resp_str.split(':')
    return resp_list

def upload_list_med(
    cip: comms.Driver, 
    device: types.MEDeviceInfo
) -> list[str]:
    try:
        helper.create_file_list_med(cip, device.me_paths)
        file_list = upload_list(
            cip=cip,
            device=device,
            file_path_terminal=f'{device.me_paths.upload_list}'
        )
        helper.delete_file_list(cip, device.me_paths)        
        return file_list
    except Exception as e:
        return None
    
def upload_list_mer(
    cip: comms.Driver, 
    device: types.MEDeviceInfo
) -> list[str]:
    try:
        helper.create_file_list_mer(cip, device.me_paths)
        file_list = upload_list(
            cip=cip,
            device=device,
            file_path_terminal=f'{device.me_paths.upload_list}'
        )
        helper.delete_file_list(cip, device.me_paths)
        return file_list
    except Exception as e:
        return None