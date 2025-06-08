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

def process_dmk(dmk_file_path: str):
    config = configparser.ConfigParser(allow_unnamed_section=True)
    with zipfile.ZipFile(dmk_file_path, 'r') as zf:
        with zf.open('Content.txt') as file:
            raw_file = file.read().decode('utf-8')
            config.read_string(raw_file)

    dmk_config = deserialize_dmk_content_file(config)
    print(dmk_config)