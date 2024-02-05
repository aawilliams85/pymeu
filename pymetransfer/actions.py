import pycomm3

from .constants import *
from .terminal import *
from .types import *

def is_download_valid(cip: pycomm3.CIPDriver, file:MEFile) -> bool:
    # Check that file is correct extension
    if (file.get_ext() != '.mer'):
        print(f'File {file.name} is not a *.mer file')
        return False

    # Check that storage folder exists
    resp_storage_exists = terminal_get_folder_exists(cip)
    if not(resp_storage_exists):
        print(f'Storage folder does not exist on terminal')
        return False

    # Check free space
    resp_free_space = terminal_get_free_space(cip)
    if (resp_free_space > file.get_size()):
        print(f'File {file.name} requires {file.get_size()} byes.  Free space on terminal {resp_free_space} bytes.')
    else:
        print(f'File {file.name} requires {file.get_size()} bytes.  Free space on terminal {resp_free_space} bytes is insufficient.')
        return False

    # Check if file name already exists
    resp_file_exists = terminal_get_file_exists(cip, file)
    file.overwrite_required = False
    if (resp_file_exists and file.overwrite_requested):
        print(f'File {file.name} already exists on terminal, and overwrite was requested.  Setting overwrite to required.')
        file.overwrite_required = True
    if (resp_file_exists and not(file.overwrite_requested)):
        print(f'File {file.name} already exists on terminal, and overwrite was NOT requested.  Use kwarg overwrite_requested=True to overwrite existing.')
        return False
    if not(resp_file_exists):
        print(f'File {file.name} does not exist on terminal.  Setting overwrite to not required.')

    # Check space consumed by file if it exists
    if resp_file_exists:
        resp_file_size = terminal_get_file_size(cip, file)
        print(f'File {file.name} on terminal is {resp_file_size} bytes.')

    return True

def is_terminal_valid(cip: pycomm3.CIPDriver) -> bool:
    resp = terminal_get_helper_version(cip)
    if resp not in PYMET_HELPER_VERSIONS:
        print(f'Invalid helper version: {resp}')
        return False
    else:
        print(f'Valid helper version: {resp}')

    resp = terminal_get_me_version(cip)
    if resp not in PYMET_ME_VERSIONS:
        print(f'Invalid ME version: {resp}')
        return False
    else:
        print(f'Valid ME version: {resp}')

    resp = terminal_get_product_code(cip)
    if resp not in PYMET_PRODUCT_CODES: 
        print(f'Invalid product code: {resp}')
        return False
    else:
        print(f'Valid product code: {resp}')

    resp = terminal_get_product_type(cip)
    if resp not in PYMET_PRODUCT_TYPES:
        print(f'Invalid product type: {resp}')
        return False
    else:
        print(f'Valid product type: {resp}')

    return True

def download_to_terminal(cip: pycomm3.CIPDriver, file: MEFile) -> bool:
    # Create runtime folder
    #
    # TODO: Can we check if this already exists and skip?
    if not(terminal_create_runtime_directory(cip, file)): raise Exception('Failed to create runtime path on terminal.')

    # Get attributes
    #
    # Still no clue on what these are, or when/how they would change.
    # If they aren't changed by creating paths, could be moved ahead
    # to is_download_valid().
    if not(terminal_is_get_unk_valid(cip)): raise Exception('Invalid response from an unknown attribute.  Check packets.')

    # Create a file exchange on the terminal
    file_instance = terminal_create_file_exchange_for_download(cip, file)

    # Set attributes
    #
    # Still no clue what this is.  Might be setting file up for write?
    if not(terminal_is_set_unk_valid(cip)): raise Exception('Invalid response from an unknown attribute.  Check packets.')

    # Transfer *.MER chunk by chunk
    terminal_file_download(cip, file_instance, file)

    # Mark file exchange as completed on the terminal
    terminal_end_file_write(cip, file_instance)

    # Delete file exchange on the terminal
    terminal_delete_file_exchange(cip, file_instance)

    return True

def reboot(comms_path: str):        
    cip = pycomm3.CIPDriver(comms_path)
    cip._cfg['socket_timeout'] = 0.25
    cip.open()
    terminal_reboot(cip)
    cip.close()