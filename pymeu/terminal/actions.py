import pycomm3

from ..types import *
from . import files
from . import helper

def download_mer_file(cip: pycomm3.CIPDriver, device: MEDeviceInfo, file: MEFile) -> bool:
    # Create runtime folder
    #
    # TODO: Can we check if this already exists and skip?
    if not(helper.create_runtime_directory(cip, file)): raise Exception('Failed to create runtime path on terminal.')

    # Get attributes
    #
    # Still no clue on what these are, or when/how they would change.
    # If they aren't changed by creating paths, could be moved ahead
    # to is_download_valid().
    if not(files.is_get_unk_valid(cip)): raise Exception('Invalid response from an unknown attribute.  Check packets.')

    # Create a file exchange on the terminal
    file_instance = files.create_exchange_download_mer(cip, file)
    device.log.append(f'Create file exchange {file_instance} for download.')

    # Set attributes
    #
    # Still no clue what this is.  Might be setting file up for write?
    if not(files.is_set_unk_valid(cip)): raise Exception('Invalid response from an unknown attribute.  Check packets.')

    # Transfer *.MER chunk by chunk
    files.download_mer(cip, file_instance, file)

    # Mark file exchange as completed on the terminal
    files.end_write(cip, file_instance)
    device.log.append(f'Downloaded {file.path} to {file.name} using file exchange {file_instance}.')

    # Delete file exchange on the terminal
    files.delete_exchange(cip, file_instance)
    device.log.append(f'Deleted file exchange {file_instance}.')

    return True

def upload_mer_file(cip: pycomm3.CIPDriver, device: MEDeviceInfo, file: MEFile, rem_file: MEFile) -> bool:
    # Verify file exists on terminal
    if not(helper.get_file_exists(cip, rem_file)): raise Exception(f'File {rem_file.name} does not exist on terminal.')

    # Create file exchange
    file_instance = files.create_exchange_upload_mer(cip, rem_file)
    device.log.append(f'Create file exchange {file_instance} for upload.')

    # Transfer *.MER chunk by chunk
    files.upload_mer(cip, file_instance, file)
    device.log.append(f'Uploaded {rem_file.name} to {file.path} using file exchange {file_instance}.')

    # Delete file exchange on the terminal
    files.delete_exchange(cip, file_instance)
    device.log.append(f'Deleted file exchange {file_instance}.')

    return True


def upload_mer_list(cip: pycomm3.CIPDriver, device: MEDeviceInfo):
    # Create *.MER list
    helper.create_mer_list(cip)

    # Create file exchange on the terminal
    file_instance = files.create_exchange_upload_mer_list(cip)
    device.log.append(f'Create file exchange {file_instance} for upload.')

    # Transfer *.MER list chunk by chunk
    file_list = files.upload_mer_list(cip, file_instance)
    device.log.append(f'Uploaded *.MER list using file exchange {file_instance}.')
    device.files = file_list

    # Delete file exchange on the terminal
    files.delete_exchange(cip, file_instance)
    device.log.append(f'Deleted file exchange {file_instance}.')

    # Delete *.MER list on the terminal
    helper.delete_file_mer_list(cip)
    device.log.append(f'Delete *.MER list on terminal.')

    return file_list

def reboot(cip: pycomm3.CIPDriver, comms_path: str):
    cip = pycomm3.CIPDriver(comms_path)
    cip._cfg['socket_timeout'] = 0.25
    cip.open()
    helper.reboot(cip)
    cip.close()