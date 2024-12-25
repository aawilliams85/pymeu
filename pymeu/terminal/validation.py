import pycomm3

from . import helper
from . import paths
from . import registry
from .. import types

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
    17,   #PanelView Plus
    47,   #PanelView Plus 6 1000
    48,   #PanelView Plus 6
    51,   #PanelView Plus 6
    94,   #PanelView Plus 7 700 Perf
    98,   #PanelView Plus 7 1000 Perf
    102,  #PanelView Plus 7
    187,  #PanelView Plus 7 1000 Standard
    189   #PanelView Plus 7 1200 Standard
}

# Known product types, used to help check that device is a valid terminal.
PRODUCT_TYPES = {
    24
}

def get_terminal_info(cip: pycomm3.CIPDriver) -> types.MEDeviceInfo:
    me_version = registry.get_me_version(cip)
    major_rev = int(me_version.split(".")[0])

    if major_rev <= 5:
        paths.helper_path = '\\Storage Card\\Rockwell Software\\RSViewME'
        paths.storage_path = '\\Storage Card'
    else:
        paths.helper_path = '\\Windows'
        paths.storage_path = '\\Application Data'

    paths.upload_list_path = paths.storage_path + '\\' + paths.UPLOAD_LIST_PATH
    paths.helper_file_path = paths.helper_path + '\\' + paths.HELPER_FILE_NAME

    return types.MEDeviceInfo(cip._cip_path, 
                               helper.get_helper_version(cip),
                               me_version,
                               registry.get_version_major(cip),
                               registry.get_version_minor(cip),
                               registry.get_product_code(cip),
                               registry.get_product_type(cip),
                               [],
                               [])


def extract_version_prefix(version: str) -> str:
    """Extracts the major and minor version (e.g., '12.00') from a version string."""
    return '.'.join(version.split('.')[:2])

def is_version_matched(device_version: str, known_versions: set) -> bool:
    """Checks if the device version prefix matches any of the known version prefixes."""
    device_version_prefix = extract_version_prefix(device_version)
    return any(extract_version_prefix(known_version) == device_version_prefix for known_version in known_versions)

def is_terminal_valid(device: types.MEDeviceInfo) -> bool:
    if device.product_type not in PRODUCT_TYPES: return False
    if device.product_code not in PRODUCT_CODES: return False
    if not is_version_matched(device.helper_version, HELPER_VERSIONS): return False
    if not is_version_matched(device.me_version, ME_VERSIONS): return False
    return True

def is_download_valid(cip: pycomm3.CIPDriver, device: types.MEDeviceInfo, file: types.MEFile) -> bool:
    # Check that file is correct extension
    if (file.get_ext() != '.mer'):
        device.log.append(f'File {file.name} is not a *.mer file')
        return False

    # Check that storage folder exists
    resp_storage_exists = helper.get_folder_exists(cip)
    if not(resp_storage_exists):
        device.log.append(f'Storage folder does not exist on terminal')
        return False

    # Check free space
    resp_free_space = helper.get_free_space(cip)
    if (resp_free_space > file.get_size()):
        device.log.append(f'File {file.name} requires {file.get_size()} byes.  Free space on terminal {resp_free_space} bytes.')
    else:
        device.log.append(f'File {file.name} requires {file.get_size()} bytes.  Free space on terminal {resp_free_space} bytes is insufficient.')
        return False

    # Check if file name already exists
    resp_file_exists = helper.get_file_exists(cip, file)
    file.overwrite_required = False
    if (resp_file_exists and file.overwrite_requested):
        device.log.append(f'File {file.name} already exists on terminal, and overwrite was requested.  Setting overwrite to required.')
        file.overwrite_required = True
    if (resp_file_exists and not(file.overwrite_requested)):
        device.log.append(f'File {file.name} already exists on terminal, and overwrite was NOT requested.  Use kwarg overwrite_requested=True to overwrite existing.')
        return False
    if not(resp_file_exists):
        device.log.append(f'File {file.name} does not exist on terminal.  Setting overwrite to not required.')

    # Check space consumed by file if it exists
    if resp_file_exists:
        resp_file_size = helper.get_file_size(cip, file)
        device.log.append(f'File {file.name} on terminal is {resp_file_size} bytes.')

    return True