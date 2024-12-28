import os
import pycomm3

from . import files
from . import helper
from . import paths
from . import registry
from .. import types

def create_log(cip: pycomm3.CIPDriver, device: types.MEDeviceInfo):
    device.log.append(f'Terminal storage exists: {helper.get_folder_exists(cip)}.')
    device.log.append(f'Terminal has {helper.get_free_space(cip)} free bytes')
    device.log.append(f'Terminal has MED files: {upload_med_list(cip, device)}')
    device.log.append(f'Terminal has MER files: {upload_mer_list(cip, device)}')

    try:
        device.log.append(f'Terminal startup file: {registry.get_startup_mer(cip)}.')
    except:
        major_rev = int(device.me_version.split(".")[0])
        if major_rev <= 5:
            # For PanelView Plus 5.10 and earlier this registry key appears to be unavailable.
            device.log.append(f'Terminal startup file: could not be determined due to hardware version.')
        else:
            # If no startup app has been defined, it will also fail. 
            device.log.append(f'Terminal startup file: not configured.')

def download_mer_file(cip: pycomm3.CIPDriver, device: types.MEDeviceInfo, file:types.MEFile, run_at_startup: bool, replace_comms: bool, delete_logs: bool) -> bool:
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
    files.download_mer(cip, file_instance, file.path)

    # Delete file exchange on the terminal
    files.delete_exchange(cip, file_instance)
    device.log.append(f'Deleted file exchange {file_instance}.')

    # Set *.MER to run at startup and then reboot
    if run_at_startup:
        device.log.append(f'Setting file: {file.name} to run at startup with Replace Comms: {replace_comms}, Delete Logs: {delete_logs}.')
        helper.create_me_shortcut(cip, file.name, replace_comms, delete_logs)
        device.log.append(f'Setting file to run at startup.')
        reboot(cip, device)
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

def upload_med_list(cip: pycomm3.CIPDriver, device: types.MEDeviceInfo):
    # Create list on the terminal
    helper.create_med_list(cip)

    # Create file exchange on the terminal
    file_instance = files.create_exchange_upload(cip, paths.upload_list_path)
    device.log.append(f'Create file exchange {file_instance} for upload.')

    # Transfer list chunk by chunk
    file_list = files.upload_list(cip, file_instance)
    device.log.append(f'Uploaded *.MED list using file exchange {file_instance}.')

    # Delete file exchange on the terminal
    files.delete_exchange(cip, file_instance)
    device.log.append(f'Deleted file exchange {file_instance}.')

    # Delete list on the terminal
    helper.delete_file_list(cip)
    device.log.append(f'Delete *.MER list on terminal.')

    return file_list

def upload_mer_list(cip: pycomm3.CIPDriver, device: types.MEDeviceInfo):
    # Create *.MER list
    helper.create_mer_list(cip)

    # Create file exchange on the terminal
    file_instance = files.create_exchange_upload(cip, paths.upload_list_path)
    device.log.append(f'Create file exchange {file_instance} for upload.')

    # Transfer *.MER list chunk by chunk
    file_list = files.upload_list(cip, file_instance)
    device.log.append(f'Uploaded *.MER list using file exchange {file_instance}.')
    device.files = file_list

    # Delete file exchange on the terminal
    files.delete_exchange(cip, file_instance)
    device.log.append(f'Deleted file exchange {file_instance}.')

    # Delete *.MER list on the terminal
    helper.delete_file_list(cip)
    device.log.append(f'Delete *.MER list on terminal.')

    return file_list

def reboot(cip: pycomm3.CIPDriver, device: types.MEDeviceInfo):
    cip1 = pycomm3.CIPDriver(cip._cip_path)
    cip1._cfg['socket_timeout'] = 0.25
    cip1.open()
    try:
        # Execute reboot
        device.log.append(f'Rebooting terminal.')
        helper.reboot(cip1)

        # If we made it here... the reboot function didn't throw
        # an exception, which means it didn't reboot.
        #
        # Further investigation needed.
        device.log.append(f'Initial reboot unsuccessful.')

        # Currently tailoring additional action to terminals where:
        #
        # Firmware version is 12.108+
        # Application is set to load at startup
        # ME Station is set to run application at startup
        # Current App is defined
        if ((device.version_major < 12) or ((device.version_major == 12) and (device.version_minor < 108))):
            device.log.append(f'Did not attempt additional reboot because terminal is below minimum applicable version.')
            return
        if (registry.get_startup_options(cip) != 1):
            device.log.append(f'Did not attempt additional reboot because terminal Startup Options are not set to Run Current Application.')
            return
        startup_file = os.path.basename(registry.get_startup_mer(cip).replace('\\','/'))
        if not(startup_file.lower().endswith('.mer')):
            device.log.append(f'Did not attempt additional reboot because terminal does not have valid startup *.MER defined.')
            return

        # Rebuild existing ME Startup Shortcut on terminal
        delete_logs = registry.get_startup_delete_logs(cip)
        replace_comms = registry.get_startup_replace_comms(cip)
        device.log.append(f'Setting file: {startup_file} to run at startup with Replace Comms: {replace_comms}, Delete Logs: {delete_logs}.')
        helper.create_me_shortcut(cip, startup_file, replace_comms, delete_logs)

        # Execute reboot
        device.log.append(f'Rebooting terminal.')
        helper.reboot(cip1)
    except pycomm3.PycommError as e:
        # Unlike most CIP messages, this one is expected to
        # create an exception.  When it is received by the terminal,
        # the device reboots and breaks the socket.
        if (str(e) != 'failed to receive reply'): raise e
    
    cip1.close()