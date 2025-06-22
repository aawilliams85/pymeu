from collections.abc import Callable
import configparser
import struct
import time
from typing import Optional
from warnings import warn
import zipfile

from . import comms
from . import messages
from . import types

def deserialize_dmk_content_header(config: configparser) -> types.DMKContentHeader:
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

def deserialize_dmk_content_catalog(config: configparser, catalog_num: int) -> types.DMKContentCatalog:
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

def deserialize_dmk_content_file(config: configparser) -> types.DMKContentFile:
    header = deserialize_dmk_content_header(config)
    catalogs = []
    for i in range(header.number_catalogs):
        catalogs.append(deserialize_dmk_content_catalog(config, i+1))

    return types.DMKContentFile(
        header=header,
        catalogs=catalogs
    )

def deserialize_dmk_nvs_header(config: configparser) -> types.DMKNvsHeader:
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

def deserialize_dmk_nvs_update(config: configparser, update_num: int) -> types.DMKNvsUpdate:
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

def deserialize_dmk_nvs_file(config: configparser) -> types.DMKNvsFile:
    header = deserialize_dmk_nvs_header(config)
    updates = []
    for i in range(header.number_updates):
        updates.append(deserialize_dmk_nvs_update(config, i+1))

    return types.DMKNvsFile(
        header=header,
        updates=updates
    )

def send_dmk_update_preamble(cip: comms.Driver, serial_number: str, file_size: int) -> int:
    """
    Sends a DMK CAB file preamble message to the remote terminal.
    It responds with the chunk size to use for the actual file
    transfer.

    Args:
        cip (comms.Driver): CIP driver to communicate with the terminal
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
        | Bytes 0->7    | File size in bytes                                  |
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
    req_unk1 = 0x00010007
    req_serial_number = int(serial_number, 16)
    req_data = struct.pack('<QII', file_size, req_unk1, req_serial_number)
    resp = messages.dmk_preamble(cip, req_data)
    if not resp: raise Exception(f'Failed to write file preamble to terminal.')
    resp_unk1, resp_chunk_size, resp_unk2 = struct.unpack('<III', resp.value)
    assert(resp_unk1 == 0)
    assert(resp_unk2 == 0)
    assert(resp_chunk_size > 0)
    return resp_chunk_size

def send_dmk_update_file(cip: comms.Driver, chunk_size: int, source_data: bytearray, progress: Optional[Callable[[str, int, int], None]] = None) -> bool:
    req_chunk_number = 1
    req_offset = 0
    total_bytes = len(source_data)
    while req_offset < total_bytes:
        req_chunk = source_data[req_offset:req_offset + chunk_size]
        req_header = struct.pack('<I', req_offset)
        req_next_chunk_number = req_chunk_number + 1
        req_data = req_header + req_chunk

        # End of file
        if not req_chunk: break

        resp = messages.dmk_chunk(cip, req_data)

        if not resp: raise Exception(f'Failed to write chunk {req_chunk_number} to terminal.')
        resp_offset_last, resp_offset_this, resp_code = struct.unpack('<IIH', resp.value)
        assert((resp_offset_this == req_offset) or (resp_offset_this == 0xFFFFFFFF))
        assert(resp_code == 0x02)

        # Update progress callback
        current_bytes = req_offset + len(req_chunk)
        if progress: progress('Download',total_bytes, current_bytes)

        # Continue to next chunk
        req_chunk_number += 1
        req_offset += len(req_chunk)

def send_dmk_updates(cip: comms.Driver, dmk_file_path: str, nvs: types.DMKNvsFile, progress: Optional[Callable[[str, int, int], None]] = None):
    with zipfile.ZipFile(dmk_file_path, 'r') as zf:
        for update in nvs.updates:
            chunk_size = send_dmk_update_preamble(cip, update.file_size)
            with zf.open(update.data_file_name) as file:
                send_dmk_update_file(cip, chunk_size, bytearray(file.read()), progress)
                time.sleep(update.max_timeout_seconds)

def validate_update_size(dmk_file_path: str, nvs: types.DMKNvsFile):
    with zipfile.ZipFile(dmk_file_path, 'r') as zf:
        for update in nvs.updates:
            actual_size = zf.getinfo(update.data_file_name).file_size
            with zf.open(update.data_file_name) as file:
                if (actual_size != update.file_size):
                    raise Exception(f'File: {update.data_file_name}, Expected Size: {update.file_size}, Actual Size: {actual_size}')

def process_dmk(cip: comms.Driver, dmk_file_path: str, dry_run: bool, progress: Optional[Callable[[str, int, int], None]] = None):
    config_content = configparser.ConfigParser(allow_unnamed_section=True)
    config_nvs = configparser.ConfigParser(allow_unnamed_section=True, allow_no_value=True)
    with zipfile.ZipFile(dmk_file_path, 'r') as zf:
        with zf.open('Content.txt') as file:
            raw_file = file.read().decode('utf-8')
            config_content.read_string(raw_file)
        with zf.open('RA_PVPApps_FTviewME_AllRegions.nvs') as file:
            raw_file = file.read().decode('utf-8', errors='ignore')
            config_nvs.read_string(raw_file)

    dmk_file = types.DMKFile(
        content=deserialize_dmk_content_file(config_content),
        nvs=deserialize_dmk_nvs_file(config_nvs)
    )
    validate_update_size(dmk_file_path, dmk_file.nvs)
    if not(dry_run): send_dmk_updates(cip, dmk_file_path, dmk_file.nvs, progress)
    return dmk_file

def masked_equals(mask: int, a: int, b: int) -> bool:
    return (mask & a) == (mask & b)

def validate_dmk_for_terminal(device: types.MEDeviceInfo, content: types.DMKContentFile) -> bool:
    for catalog in content.catalogs:
        if not(masked_equals(catalog.vendor_id_mask, catalog.vendor_id, device.cip_identity.vendor_id)): continue
        if not(masked_equals(catalog.product_type_mask, catalog.product_type, device.cip_identity.product_type)): continue
        if not(masked_equals(catalog.product_code_mask, catalog.product_code, device.cip_identity.product_code)): continue
        return True # Device matches this catalog
    return False # Device doesn't match any catalogs