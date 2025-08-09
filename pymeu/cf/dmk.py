from collections.abc import Callable
import configparser
import struct
import time
from typing import Optional
from warnings import warn
import zipfile

from .. import comms
from ..common.messages import reset

from . import messages
from . import types

FILE_NANE_CONTENT = 'Content.txt'
FILE_NAME_NVS = 'RA_PVPApps_FTviewME_AllRegions.nvs'

def _deserialize_dmk_content_header(config: configparser) -> types.DMKContentHeader:
    section_name = 'Content'
    if section_name not in config:
        raise ValueError(f"Section '{section_name}' not found in configuration.")

    section = config[section_name]
    return types.DMKContentHeader(
        dmk_type=section.get('DMKType', ''),
        family_name=section.get('FamilyName',''),
        revision=section.get('Revision',''),
        number_catalogs=section.getint('NumberCatalogs',0)
    )

def _deserialize_dmk_content_catalog(config: configparser, catalog_num: int) -> types.DMKContentCatalog:
    section_name = f'Catalog{catalog_num}'
    if section_name not in config:
        raise ValueError(f"Section '{section_name}' not found in configuration.")

    section = config[section_name]
    return types.DMKContentCatalog(
        catalog=section.get('Catalog',''),
        revision=section.get('Revision',''),
        vendor_id=int(section.get('VendorId',0),16),
        vendor_id_mask=int(section.get('VendorIdMask',0),16),
        product_type=int(section.get('ProductType',0),16),
        product_type_mask=int(section.get('ProductTypeMask',0),16),
        product_code=int(section.get('ProductCode',0),16),
        product_code_mask=int(section.get('ProductCodeMask',0),16),
        device_instance=section.getint('DeviceInstance',0),
        disable_sub_minor=section.getint('DisableSubminor',0),
        driver_name=section.get('DriverName','')
    )

def _deserialize_dmk_content_file(config: configparser) -> types.DMKContentFile:
    header = _deserialize_dmk_content_header(config)
    catalogs = []
    for i in range(header.number_catalogs):
        catalogs.append(_deserialize_dmk_content_catalog(config, i+1))

    return types.DMKContentFile(
        header=header,
        catalogs=catalogs
    )

def _deserialize_dmk_nvs_header(config: configparser) -> types.DMKNvsHeader:
    section_name = 'Device'
    if section_name not in config:
        raise ValueError(f"Section '{section_name}' not found in configuration.")

    section = config[section_name]
    return types.DMKNvsHeader(
        description=section.get('Description',''),
        programming_protocol=section.get('ProgrammingProtocol',''),
        disable_sub_minor=section.getint('DisableSubminor',0),
        new_revision=section.get('NewRevision',''),
        number_updates=section.getint('NumberUpdates',0),
        connection_type=section.get('ConnectionType',''),
        max_power_up_seconds=section.getint('MaxPowerupSeconds',0),
        number_identities=section.getint('NumberIdentities',0),
        family_name=section.get('FamilyName',''),
        release_notes_file_name=section.get('ReleaseNotesFileName','')
    )

def _deserialize_dmk_nvs_update(config: configparser, update_num: int) -> types.DMKNvsUpdate:
    section_name = f'Update{update_num}'
    if section_name not in config:
        raise ValueError(f"Section '{section_name}' not found in configuration.")

    section = config[section_name]
    return types.DMKNvsUpdate(
        nvs_instance=section.getint('NVSInstance',0),
        major_revision=section.getint('MajorRevision',0),
        minor_revision=section.getint('MinorRevision',0),
        tftp_timeout_seconds=section.getint('TFTPTimeOutSeconds',0),
        max_timeout_seconds=section.getint('MaxTimeoutSeconds',0),
        starting_location=int(section.get('StartingLocation',0),16),
        file_size=section.getint('FileSize',0),
        data_file_name=section.get('DataFileName',''),
        rename_data_file=section.get('RenameDataFile',''),
        update_reset=section.getint('UpdateReset',0),
        auto_reset_on_error=section.getint('AutoResetOnError',0),
        first_transfer_delay=section.getint('FirstTransferDelay',0),
        last_transfer_delay=section.getint('LastTransferDelay',0),
        error_instructions=section.get('ErrorInstructions')
    )

def _deserialize_dmk_nvs_file(config: configparser) -> types.DMKNvsFile:
    header = _deserialize_dmk_nvs_header(config)
    updates = []
    for i in range(header.number_updates):
        updates.append(_deserialize_dmk_nvs_update(config, i+1))

    return types.DMKNvsFile(
        header=header,
        updates=updates
    )

def _send_dmk_update_preamble(cip: comms.Driver, instance: int, serial_number: str, file_size: int) -> int:
    """
    Sends a DMK CAB file preamble message to the remote terminal.
    It responds with the chunk size to use for the actual file
    transfer.

    Args:
        cip (comms.Driver): CIP driver to communicate with the terminal
        instance (int): File instance
        serial_number (str): The terminal serial number as an 8-character hex string 'FFFFFFFF'
        file_size (int): File size in byte to that will be transferred

    Returns:
        int: The chunk size to use with DMK file transfer.

    Raises:
        Exception: If the file transfer fails or if the response contains
        unexpected values, indicating potential issues with the transfer.

    Request Format:
        The request consists of the following byte structure:

        | Byte Range    | Description                                         |
        |---------------|-----------------------------------------------------|
        | Bytes 0->3    | File size in bytes                                  |
        | Bytes 4->7    | Unknown purpose (reserved?)                         |
        | Bytes 8->11   | Unknown purpose                                     |
        | Bytes 12->15  | Target device serial number                         |

    Response Format:
        The response consists of the following byte structure:

        | Byte Range    | Description                                         |
        |---------------|-----------------------------------------------------|
        | Bytes 0->3    | Unknown purpose                                     |
        | Bytes 4->7    | Chunk size in bytes                                 |
        | Bytes 8->11   | Unknown purpose                                     |
    """
    warn('Preamble using static UNK1 values')
    req_unk1 = 0
    req_unk2 = 0x00010007
    req_serial_number = int(serial_number, 16)
    req_data = struct.pack('<IIII', file_size, req_unk1, req_unk2, req_serial_number)

    resp = messages.dmk_preamble(cip, instance, req_data)

    if not resp.value: raise Exception(f'Failed to write file preamble to terminal.')
    resp_unk1, resp_chunk_size, resp_unk2 = struct.unpack('<III', resp.value)
    if (resp_unk1 != 0): raise Exception(f'Response UNK1: {resp_unk1}.  Update failed.')
    if (resp_chunk_size <= 0): raise Exception(f'Response chunk size: {resp_chunk_size}.  Update failed.')
    if (resp_unk2 != 0): raise Exception(f'Response UNK2: {resp_unk2}.  Update failed.')
    return resp_chunk_size

def _send_dmk_update_file(
    cip: comms.Driver, 
    instance: int, 
    chunk_size: int, 
    source_data: bytearray, 
    description: str, 
    progress: Optional[Callable[[str, str, int, int], None]] = None
):
    req_offset = 0
    current_bytes = 0
    total_bytes = len(source_data)
    if progress: progress(f'{description}', 'bytes', total_bytes, current_bytes)
    while current_bytes < total_bytes:
        req_chunk = source_data[req_offset:req_offset + chunk_size]
        req_header = struct.pack('<I', req_offset)
        req_data = req_header + req_chunk

        resp = messages.dmk_chunk(cip, instance, req_data)

        if not resp: raise Exception(f'Failed to write chunk to terminal.')
        resp_offset, resp_offset_next, resp_code = struct.unpack('<IIH', resp.value)
        if (resp_offset != req_offset): raise Exception(f'Response offset: {resp_offset} does not match request offset: {req_offset}.  Update failed.')
        if (resp_code != 0x02): raise Exception(f'Response code: {resp_code}.  Update failed.')

        if (resp_offset_next == 0xFFFFFFFF):
            # End of file
            current_bytes = total_bytes
        else:
            # Next chunk
            current_bytes = resp_offset_next

        # Update progress callback
        if progress: progress(f'{description}','bytes', total_bytes, current_bytes)
            
        # Continue to next chunk
        req_offset = resp_offset_next
        #req_offset += len(req_chunk)

def send_dmk_reset(cip: comms.Driver):
    """
    Sends a reset after DMK is transferred to the rmote terminal..

    Args:
        cip (comms.Driver): CIP driver to communicate with the terminal
    """
    req_data = struct.pack('<B', 0x00)
    resp = reset(cip, req_data)
    if not resp: raise Exception(f'Failed to reset terminal.')

def send_dmk_updates(
    cip: comms.Driver,
    device: types.CFDeviceInfo,
    dmk_file_path: str,
    nvs: types.DMKNvsFile,
    progress: Optional[Callable[[str, str, int, int], None]] = None
):
    cip.close()
    with zipfile.ZipFile(dmk_file_path, 'r') as zf:
        instance = 0
        cip.connection_size = 1400
        for update in nvs.updates:
            instance += 1
            cip.forward_open()
            cip.sequence_reset()

            chunk_size = _send_dmk_update_preamble(
                cip=cip,
                instance=instance,
                serial_number=device.cip_identity.serial_number,
                file_size=update.file_size
            )
            with zf.open(update.data_file_name) as file:
                _send_dmk_update_file(
                    cip=cip,
                    instance=instance,
                    chunk_size=chunk_size,
                    source_data=bytearray(file.read()),
                    description=f'Updating {instance} of {len(nvs.updates)} {file.name}',
                    progress=progress
                )
            cip.forward_close()
            if update.update_reset: send_dmk_reset(cip)

def validate_update_size(dmk_file_path: str, nvs: types.DMKNvsFile):
    with zipfile.ZipFile(dmk_file_path, 'r') as zf:
        for update in nvs.updates:
            actual_size = zf.getinfo(update.data_file_name).file_size
            with zf.open(update.data_file_name) as file:
                if (actual_size != update.file_size):
                    raise Exception(f'File: {update.data_file_name}, Expected Size: {update.file_size}, Actual Size: {actual_size}')

def process_dmk(
    cip: comms.Driver,
    device: types.CFDeviceInfo,
    dmk_path_local: str,
    dry_run: bool,
    progress: Optional[Callable[[str, str, int, int], None]] = None
):
    config_content = configparser.ConfigParser(allow_unnamed_section=True)
    config_nvs = configparser.ConfigParser(allow_unnamed_section=True, allow_no_value=True)
    with zipfile.ZipFile(dmk_path_local, 'r') as zf:
        with zf.open(FILE_NANE_CONTENT) as file:
            raw_file = file.read().decode('utf-8')
            config_content.read_string(raw_file)
        with zf.open(FILE_NAME_NVS) as file:
            raw_file = file.read().decode('utf-8', errors='ignore')
            config_nvs.read_string(raw_file)

    dmk_file = types.DMKFile(
        content=_deserialize_dmk_content_file(config_content),
        nvs=_deserialize_dmk_nvs_file(config_nvs)
    )
    validate_update_size(dmk_path_local, dmk_file.nvs)
    validate_dmk_for_terminal(device, dmk_file.content)
    if not(dry_run):
        send_dmk_updates(
            cip=cip,
            device=device,
            dmk_file_path=dmk_path_local,
            nvs=dmk_file.nvs,
            progress=progress
        )
    return dmk_file

def masked_equals(mask: int, a: int, b: int) -> bool:
    return (mask & a) == (mask & b)

def validate_dmk_for_terminal(device: types.CFDeviceInfo, content: types.DMKContentFile):
    for catalog in content.catalogs:
        if not(masked_equals(catalog.vendor_id_mask, catalog.vendor_id, device.cip_identity.vendor_id)): continue
        if not(masked_equals(catalog.product_type_mask, catalog.product_type, device.cip_identity.product_type)): continue
        if not(masked_equals(catalog.product_code_mask, catalog.product_code, device.cip_identity.product_code)): continue
        return # Device matches this catalog
    raise Exception(f'Device catalog does not match DMK file.  Device: {device}, DMK: {content}')