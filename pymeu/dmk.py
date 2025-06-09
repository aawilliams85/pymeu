import configparser
import zipfile

from . import types

DMK_CONTENT_FILE_NAME = 'Content.txt'

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

def process_dmk(dmk_file_path: str):
    config1 = configparser.ConfigParser(allow_unnamed_section=True)
    config2 = configparser.ConfigParser(allow_unnamed_section=True, allow_no_value=True)
    with zipfile.ZipFile(dmk_file_path, 'r') as zf:
        with zf.open('Content.txt') as file:
            raw_file = file.read().decode('utf-8')
            config1.read_string(raw_file)
        with zf.open('RA_PVPApps_FTviewME_AllRegions.nvs') as file:
            raw_file = file.read().decode('utf-8', errors='ignore')
            config2.read_string(raw_file)

    dmk_content = deserialize_dmk_content_file(config1)
    dmk_nvs = deserialize_dmk_nvs_file(config2)
    print(dmk_nvs)
    #print(dmk_config)
    return dmk_content

def masked_equals(mask: int, a: int, b: int) -> bool:
    return (mask & a) == (mask & b)

def validate_dmk_for_terminal(device: types.MEDeviceInfo, content: types.DMKContentFile) -> bool:
    for catalog in content.catalogs:
        if not(masked_equals(catalog.vendor_id_mask, catalog.vendor_id, device.vendor_id)): continue
        if not(masked_equals(catalog.product_type_mask, catalog.product_type, device.product_type)): continue
        if not(masked_equals(catalog.product_code_mask, catalog.product_code, device.product_code)): continue
        return True # Device matches this catalog
    return False # Device doesn't match any catalogs