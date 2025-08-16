import os
import struct

from .. import comms
from ..common.validation import get_cip_identity

from . import helper
from . import registry
from . import types

# Known RemoteHelper file version numbers, used to help check that device is a valid terminal.
HELPER_VERSIONS = {
    '5.10.00',
    '6.00.00',
    '6.10.00',
    '7.00.00',
    '8.00.00',
    '8.10.00',
    '8.20.00',
    '9.00.00',
    '10.00.00',
    '11.00.00',
    '12.00.00',
    '12.00.00.414.56',
    '12.00.00.414.73',
    '12.00.00.414.85',
    '12.00.00.414.99',
    '12.00.00.414.106',
    '13.00.00',
    '14.00.00',
    '15.00.00'
}

# Known terminal MEVersion numbers, used to help check that device is a valid terminal.
ME_VERSIONS = {
    '5.10.16.09',
    '6.00.04.16',
    '6.10.17.09',
    '7.00.20.13',
    '7.00.55.13',
    '8.00.67.12',
    '8.10.42.13',
    '8.20.30.10',
    '9.00.17.241',
    '9.00.00.241',
    '10.00.09.290',
    '11.00.00.230',
    '11.00.25.230',
    '12.00.00.414',
    '12.00.00.414.56.47',
    '12.00.00.414.85.414',
    '12.00.00.414.99.414',
    '12.00.00.414.106.414',
    '12.00.77.414',
    '12.00.78.414',
    '13.00.11.413',
    '14.00.00.394',
    '15.00.00.201'
}

# Known terminal product codes, used to help check that device is a valid terminal.
PRODUCT_CODES = {
    13,   #PanelView Plus 700 CE
    14,   #PanelView Plus 700
    15,   #PanelView Plus 400
    16,   #PanelView Plus 600
    17,   #PanelView Plus 1000
    18,   #PanelView Plus 1250
    19,   #PanelView Plus 1500
    20,   #PanelView Plus 1000 CE
    21,   #PanelView Plus 1250 CE
    22,   #PanelView Plus 1500 CE
    40,   #PanelView Plus Compact 400
    42,   #PanelView Plus Compact 600
    44,   #PanelView Plus Compact 1000
    45,   #PanelView Plus 6 700
    46,   #PanelView Plus 6 700 CE
    47,   #PanelView Plus 6 1000
    48,   #PanelView Plus 6 1000 CE
    49,   #PanelView Plus 6 1250
    50,   #PanelView Plus 6 1250 CE
    51,   #PanelView Plus 6 1500
    52,   #PanelView Plus 6 1500 CE
    74,   #PanelView Plus 6 400
    75,   #PanelView Plus 6 400
    77,   #PanelView Plus 6 600
    78,   #PanelView Plus 6 600 Extended
    79,   #PanelView Plus 6 600 Extended
    81,   #PanelView Plus 7 Standard 600
    83,   #PanelView Plus 7 Standard 700
    85,   #PanelView Plus 7 Standard 900W
    87,   #PanelView Plus 7 Standard 1000
    89,   #PanelView Plus 7 Standard 1200W
    91,   #PanelView Plus 7 Standard 1500
    94,   #PanelView Plus 7 Performance 700
    96,   #PanelView Plus 7 Performance 900W
    98,   #PanelView Plus 7 Performance 1000
    100,  #PanelView Plus 7 Performance 1200W
    102,  #PanelView Plus 7 Performance 1500
    104,  #PanelView Plus 7 Performance 1900
    #107, #PanelView Plus 7 Performance Series B DLR Network Switch - not a terminal
    110,  #PanelView Plus 7 Performance 700W
    112,  #PanelView Plus 7 Performance 1000W
    114,  #PanelView Plus 7 Performance 1200W
    116,  #PanelView Plus 7 Performance 1500W
    118,  #PanelView Plus 7 Performance 1900W
    147,  #PanelView Plus 6 Compact 1000
    175,  #PanelView Plus 6 Compact 400
    177,  #PanelView Plus 6 Compact 600
    179,  #PanelView Plus 7 Standard 400W
    180,  #PanelView Plus 7 Standard 400W DLR
    181,  #PanelView Plus 7 Standard 600
    182,  #PanelView Plus 7 Standard 600 DLR
    183,  #PanelView Plus 7 Standard 700
    184,  #PanelView Plus 7 Standard 700 DLR
    185,  #PanelView Plus 7 Standard 900W
    186,  #PanelView Plus 7 Standard 900W DLR
    187,  #PanelView Plus 7 Standard 1000
    188,  #PanelView Plus 7 Standard 1000 DLR
    189,  #PanelView Plus 7 Standard 1200W
    190,  #PanelView Plus 7 Standard 1200W DLR
    191,  #PanelView Plus 7 Standard 1500
    192   #PanelView Plus 7 Standard 1500 DLR
}

# Known product types, used to help check that device is a valid terminal.
PRODUCT_TYPES = {
    24
}

HELPER_FILE_NAME = 'RemoteHelper.DLL'
RUNTIME_PATH = 'Rockwell Software\\RSViewME\\Runtime'
UPLOAD_LIST_PATH = f'{RUNTIME_PATH}\\Results.txt'

def get_me_identity(cip: comms.Driver, paths: types.MEPaths) -> types.MEIdentity:
    me_version = registry.get_me_version(cip)
    helper_version = helper.get_version(cip, paths, paths.helper_file)

    major_rev = registry.get_version_major(cip)
    minor_rev = registry.get_version_minor(cip)
    product_code = registry.get_product_code(cip)
    product_name = registry.get_product_name(cip)
    product_type = registry.get_product_type(cip)
    serial_number = registry.get_serial_number(cip)
    vendor_id = registry.get_vendor_id(cip)

    return types.MEIdentity(
        helper_version=helper_version,
        me_version=me_version,
        major_rev=major_rev,
        minor_rev=minor_rev,
        product_code=product_code,
        product_name=product_name,
        product_type=product_type,
        serial_number=serial_number,
        vendor_id=vendor_id
    )

def get_me_paths(cip: comms.Driver) -> types.MEPaths:
    me_version = registry.get_me_version(cip)
    major_rev = int(me_version.split(".")[0])

    if major_rev <= 5:
        helper_path = '\\Storage Card\\Rockwell Software\\RSViewME'
        storage_path = '\\Storage Card'
    else:
        helper_path = '\\Windows'
        storage_path = '\\Application Data'

    fuwhelper_file_path = '\\Storage Card\\FUWhelper.dll'
    helper_file_path = f'{helper_path}\\{HELPER_FILE_NAME}'
    runtime_path = f'{storage_path}\\{RUNTIME_PATH}'
    upload_list_path = f'{storage_path}\\{UPLOAD_LIST_PATH}'

    return types.MEPaths(
        helper_file=helper_file_path,
        storage=storage_path,
        upload_list=upload_list_path,
        runtime=runtime_path,
        fuwhelper_file=fuwhelper_file_path)

def get_terminal_info(cip: comms.Driver) -> types.MEDeviceInfo:
    cip_identity = get_cip_identity(cip)
    try:
        me_paths = get_me_paths(cip)
        me_identity = get_me_identity(cip, me_paths)
    except:
        me_paths = types.MEPaths(None,None,None,None,None)
        me_identity = types.MEIdentity(None,None,None,None,None,None,None,None,None)
        
    return types.MEDeviceInfo(
        comms_path=cip._original_path,
        cip_identity=cip_identity,
        me_identity=me_identity,
        log=[],
        files=[],
        running_med_file=None,
        startup_mer_file=None,
        me_paths=me_paths)

def extract_version_prefix(version: str) -> str:
    """Extracts the major and minor version (e.g., '12.00') from a version string."""
    return '.'.join(version.split('.')[:2])

def is_native_me_terminal(device: types.MEDeviceInfo) -> bool:
    """Indicate whether the terminal is a native ME terminal (PVP5,6,7A) or not (PVP7B)"""
    if (device.cip_identity.hardware_rev is not None): return False
    if (device.cip_identity.minor_rev >= 100): return False
    return True

def is_version_matched(device_version: str, known_versions: set) -> bool:
    """Checks if the device version prefix matches any of the known version prefixes."""
    device_version_prefix = extract_version_prefix(device_version)
    return any(extract_version_prefix(known_version) == device_version_prefix for known_version in known_versions)

def is_valid_me_terminal(device: types.MEDeviceInfo) -> bool:
    if device.me_identity.product_type not in PRODUCT_TYPES: return False
    if device.me_identity.product_code not in PRODUCT_CODES: return False
    if not is_version_matched(device.me_identity.helper_version, HELPER_VERSIONS): return False
    if not is_version_matched(device.me_identity.me_version, ME_VERSIONS): return False
    return True

def is_valid_download(
    cip: comms.Driver, 
    device: types.MEDeviceInfo, 
    file_path_local: str, 
    file_name_terminal: str,
    overwrite: bool
) -> bool:
    file_name_local = os.path.basename(file_path_local)
    file_size_local = os.path.getsize(file_path_local)
    file_path_terminal = f'{device.me_paths.runtime}\\{file_name_terminal}'

    # Check that file is correct extension
    if (os.path.splitext(file_path_local)[1].lower() != '.mer'):
        device.log.append(f'File {file_path_local} is not a *.mer file')
        return False

    # Check that storage folder exists
    resp_storage_exists = helper.get_folder_exists(cip, device.me_paths, device.me_paths.storage)
    if not(resp_storage_exists):
        device.log.append(f'Storage folder does not exist on terminal')
        return False

    # Check free space
    resp_free_space = helper.get_free_space_runtime(cip, device.me_paths)
    if (resp_free_space > file_size_local):
        device.log.append(f'File {file_name_local} requires {file_size_local} byes.  Free space on terminal {resp_free_space} bytes.')
    else:
        device.log.append(f'File {file_name_local} requires {file_size_local} bytes.  Free space on terminal {resp_free_space} bytes is insufficient.')
        return False

    # Check if file name already exists
    resp_file_exists = helper.get_file_exists(cip, device.me_paths, file_path_terminal)
    if (resp_file_exists and not overwrite):
        device.log.append(f'File {file_name_local} already exists on terminal, and overwrite was NOT requested.  Use overwrite=True to overwrite existing.')
        return False

    # Check space consumed by file if it exists
    if resp_file_exists:
        resp_file_size = helper.get_file_size(cip, device.me_paths, file_path_terminal)
        device.log.append(f'File {file_name_local} on terminal is {resp_file_size} bytes.')

    return True