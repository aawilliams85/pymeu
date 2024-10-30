import pycomm3

from . import files
from . import helper
from . import paths
from . import registry
from .. import types

def create_log(cip: pycomm3.CIPDriver, device: types.MEDeviceInfo):
    device.log.append(f'Terminal storage exists: {helper.get_folder_exists(cip)}.')
    device.log.append(f'Terminal has {helper.get_free_space(cip)} free bytes')
    device.log.append(f'Terminal has files: {upload_mer_list(cip, device)}')
    device.log.append(f'Terminal startup file: {registry.get_startup_mer(cip)}.')

def download_mer_file(cip: pycomm3.CIPDriver, device: types.MEDeviceInfo, file:types. MEFile, run_at_startup: bool, replace_comms: bool, delete_logs: bool) -> bool:
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
    file_instance = files.create_exchange_download(cip, file, paths.storage_path + '\\Rockwell Software\\RSViewME\\Runtime')
    device.log.append(f'Create file exchange {file_instance} for download.')

    # Set attributes
    #
    # Still no clue what this is.  Might be setting file up for write?
    if not(files.is_set_unk_valid(cip)): raise Exception('Invalid response from an unknown attribute.  Check packets.')

    # Transfer *.MER chunk by chunk
    files.download(cip, file_instance, file.path)

    # Mark file exchange as completed on the terminal
    files.end_write(cip, file_instance)
    device.log.append(f'Downloaded {file.path} to {file.name} using file exchange {file_instance}.')

    # Delete file exchange on the terminal
    files.delete_exchange(cip, file_instance)
    device.log.append(f'Deleted file exchange {file_instance}.')

    # Set *.MER to run at startup and then reboot
    if run_at_startup:
        helper.set_startup_mer(cip, file, replace_comms, delete_logs)
        device.log.append(f'Setting file to run at startup.')
        reboot(cip)
        device.log.append(f'Rebooting terminal.')

    return True

def upload_mer_file(cip: pycomm3.CIPDriver, device: types.MEDeviceInfo, file: types.MEFile, rem_file: types.MEFile) -> bool:
    # Verify file exists on terminal
    if not(helper.get_file_exists(cip, rem_file)): raise Exception(f'File {rem_file.name} does not exist on terminal.')

    # Create file exchange
    file_instance = files.create_exchange_upload(cip, paths.storage_path + f'\\Rockwell Software\\RSViewME\\Runtime\\{rem_file.name}')
    device.log.append(f'Create file exchange {file_instance} for upload.')

    # Transfer *.MER chunk by chunk
    files.upload_mer(cip, file_instance, file)
    device.log.append(f'Uploaded {rem_file.name} to {file.path} using file exchange {file_instance}.')

    # Delete file exchange on the terminal
    files.delete_exchange(cip, file_instance)
    device.log.append(f'Deleted file exchange {file_instance}.')

    return True

def upload_mer_list(cip: pycomm3.CIPDriver, device: types.MEDeviceInfo):
    # Create *.MER list
    helper.create_mer_list(cip)

    # Create file exchange on the terminal
    file_instance = files.create_exchange_upload(cip, paths.upload_list_path)
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

def reboot(cip: pycomm3.CIPDriver):
    cip = pycomm3.CIPDriver(cip._cip_path)
    cip._cfg['socket_timeout'] = 0.25
    cip.open()
    helper.reboot(cip)
    cip.close()