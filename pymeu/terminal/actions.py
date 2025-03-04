import os
import pycomm3

from . import files
from . import helper
from . import registry
from .. import types

def create_log(cip: pycomm3.CIPDriver, device: types.MEDeviceInfo, print_log: bool, redact_log: bool, silent_mode: bool):
    if print_log: print(f'Terminal product type: {device.product_type}.')
    if print_log: print(f'Terminal product code: {device.product_code}.')
    if print_log: print(f'Terminal product name: {device.product_name}.')
    if print_log: print(f'Terminal helper version: {device.helper_version}.')
    if print_log: print(f'Terminal ME version: {device.me_version}.')
    if print_log: print(f'Terminal major version: {device.version_major}.')
    if print_log: print(f'Terminal minor version: {device.version_minor}.')
    if print_log: print(f'Terminal helper path: {device.paths.helper_file}.')
    if print_log: print(f'Terminal storage path: {device.paths.storage}.')
    if print_log: print(f'Terminal upload list path: {device.paths.upload_list}.')

    try:
        line = f'Terminal has {helper.get_free_space(cip, device.paths)} free bytes.'
    except:
        line = f'Failed to get free space on terminal.'
    device.log.append(line)
    if print_log: print(f'{line}')

    if not silent_mode:
        try:
            files = upload_med_list(cip, device)
            if redact_log: files = ['Redacted' for _ in files]
            line = f'Terminal has MED files: {files}.'
            if len(files) > 0: device.running_med_file = files[0]
        except:
            line = f'Failed to list MED files on terminal.'
        device.log.append(line)
        if print_log: print(f'{line}')

        try:
            files = upload_mer_list(cip, device)
            if redact_log: files = ['Redacted' for _ in files]
            line = f'Terminal has MER files: {files}.'
        except:
            line = f'Failed to list MER files on terminal.'
        device.log.append(line)
        if print_log: print(f'{line}')

    try:
        file = registry.get_startup_mer(cip)
        if redact_log: file = 'Redacted'
        line = f'Terminal startup file: {file}.'
        if file.lower().endswith('.mer'): device.startup_mer_file = file.split('\\')[-1]
    except:
        major_rev = int(device.me_version.split(".")[0])
        if major_rev <= 5:
            # For PanelView Plus 5.10 and earlier this registry key appears to be unavailable.
            line = f'Terminal startup file: could not be determined due to hardware version.'
        else:
            # If no startup app has been defined, it will also fail. 
            line = f'Terminal startup file: not configured.'
    device.log.append(line)
    if print_log: print(f'{line}')

def download_mer_file(cip: pycomm3.CIPDriver, device: types.MEDeviceInfo, file:types.MEFile, run_at_startup: bool, replace_comms: bool, delete_logs: bool) -> bool:
    # Create runtime folder
    try:
        helper.create_runtime_directory(cip, device.paths, file)
        device.log.append(f'Create runtime directory on terminal.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to create runtime directory on terminal.')
        return False

    # Get attributes
    #
    # Still no clue on what these are, or when/how they would change.
    # If they aren't changed by creating paths, could be moved ahead
    # to is_download_valid().
    try:
        get_unk1 = files.is_get_unk_valid(cip)
        if get_unk1:
            device.log.append(f'Got UNK1 attributes from terminal.')
        else:
            device.log.append(f'Got invalid UNK1 attributes from terminal.  Please file a bug report with all available information.')
            return False
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to get UNK1 attributes from terminal.')
        return False

    # Create a transfer instance on the terminal
    try:
        transfer_instance = files.create_transfer_instance_download(cip, file, f'{device.paths.storage}\\Rockwell Software\\RSViewME\\Runtime')
        device.log.append(f'Create transfer instance {transfer_instance} for download.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to create transfer instance for download')
        return False

    # Set attributes
    #
    # Still no clue what this is.  Might be setting file up for write?
    continue_download = True
    try:
        set_unk1 = files.is_set_unk_valid(cip)
        if set_unk1:
            device.log.append(f'Set UNK1 attributes on terminal.')
        else:
            device.log.append(f'Failed to set UNK1 attributes on terminal.  Please file a bug report with all available information.')
            continue_download = False
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to set UNK1 attributes on terminal.')
        continue_download = False

    # Transfer *.MER chunk by chunk
    try:
        if continue_download:
            files.download_mer(cip, transfer_instance, file.path)
            device.log.append(f'Downloaded {file.name} using transfer instance {transfer_instance}.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to download {file.name} using transfer instance {transfer_instance}.')

    # Delete transfer instance on the terminal
    try:
        files.delete_transfer_instance(cip, transfer_instance)
        device.log.append(f'Deleted transfer instance {transfer_instance}.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to delete transfer instance {transfer_instance}.')

    # Set *.MER to run at startup and then reboot
    try:
        if continue_download:
            if run_at_startup:
                helper.create_me_shortcut(cip, device.paths, file.name, replace_comms, delete_logs)
                device.log.append(f'Set file: {file.name} to run at startup with Replace Comms: {replace_comms}, Delete Logs: {delete_logs}.')
                reboot(cip, device)
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to set file to run at startup.')
        
    return continue_download

def upload_mer_file(cip: pycomm3.CIPDriver, device: types.MEDeviceInfo, file: types.MEFile, rem_file: types.MEFile) -> bool:
    # Verify file exists on terminal
    try:
        if helper.get_file_exists(cip, device.paths, rem_file):
            device.log.append(f'File {rem_file.name} exists on terminal.')
        else:
            device.log.append(f'File {rem_file.name} does not exist on terminal.')
            return False
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to check if file {rem_file.name} exists on terminal.')
        return False

    # Create a transfer instance on the terminal
    try:
        transfer_instance = files.create_transfer_instance_upload(cip, f'{device.paths.storage}\\Rockwell Software\\RSViewME\\Runtime\\{rem_file.name}')
        device.log.append(f'Create transfer instance {transfer_instance} for upload.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to create transfer instance for upload')
        return False

    # Transfer *.MER chunk by chunk
    try:
        files.upload_mer(cip, transfer_instance, file)
        device.log.append(f'Uploaded {rem_file.name} to {file.path} using transfer instance {transfer_instance}.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to upload {rem_file.name} to {file.path} using transfer instance {transfer_instance}.')

    # Delete transfer instance on the terminal
    try:
        files.delete_transfer_instance(cip, transfer_instance)
        device.log.append(f'Deleted transfer instance {transfer_instance}.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to delete transfer instance {transfer_instance}.')

    return True

def upload_med_list(cip: pycomm3.CIPDriver, device: types.MEDeviceInfo) -> list[str]:
    # Create list on the terminal
    try:
        helper.create_med_list(cip, device.paths)
        device.log.append(f'Created *.MED list on terminal.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to create *.MED list on terminal.')
        return None

    # Create transfer instance on the terminal
    try:
        transfer_instance = files.create_transfer_instance_upload(cip, device.paths.upload_list)
        device.log.append(f'Create transfer instance {transfer_instance} for upload.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to create transfer instance for upload')
        return None

    # Transfer list chunk by chunk
    file_list = None
    try:
        file_list = files.upload_list(cip, transfer_instance)
        device.log.append(f'Uploaded *.MED list using transfer instance {transfer_instance}.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to upload *.MED list using transfer instance {transfer_instance}.')

    # Delete transfer instance on the terminal
    try:
        files.delete_transfer_instance(cip, transfer_instance)
        device.log.append(f'Deleted transfer instance {transfer_instance}.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to delete transfer instance {transfer_instance}.')

    # Delete list on the terminal
    try:
        helper.delete_file_list(cip, device.paths)
        device.log.append(f'Deleted *.MED list on terminal.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to delete *.MED list on terminal.')

    return file_list

def upload_mer_list(cip: pycomm3.CIPDriver, device: types.MEDeviceInfo) -> list[str]:
    # Create *.MER list
    try:
        helper.create_mer_list(cip, device.paths)
        device.log.append(f'Created *.MER list on terminal.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to create *.MER list on terminal.')
        return None

    # Create transfer instance on the terminal
    try:
        transfer_instance = files.create_transfer_instance_upload(cip, device.paths.upload_list)
        device.log.append(f'Create transfer instance {transfer_instance} for upload.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to create transfer instance for upload')
        return None

    # Transfer list chunk by chunk
    file_list = None
    try:
        file_list = files.upload_list(cip, transfer_instance)
        device.files = file_list
        device.log.append(f'Uploaded *.MER list using transfer instance {transfer_instance}.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to upload *.MED list using transfer instance {transfer_instance}.')

    # Delete transfer instance on the terminal
    try:
        files.delete_transfer_instance(cip, transfer_instance)
        device.log.append(f'Deleted transfer instance {transfer_instance}.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to delete transfer instance {transfer_instance}.')

    # Delete list on the terminal
    try:
        helper.delete_file_list(cip, device.paths)
        device.log.append(f'Deleted *.MED list on terminal.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to delete *.MED list on terminal.')

    return file_list

def reboot(cip: pycomm3.CIPDriver, device: types.MEDeviceInfo):
    cip1 = pycomm3.CIPDriver(cip._cip_path)
    cip1._cfg['socket_timeout'] = 0.25
    cip1.open()
    try:
        # Execute reboot
        device.log.append(f'Rebooting terminal.')
        helper.reboot(cip1, device.paths)

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
        helper.create_me_shortcut(cip, device.paths, startup_file, replace_comms, delete_logs)

        # Execute reboot
        device.log.append(f'Rebooting terminal.')
        helper.reboot(cip1, device.paths)
    except pycomm3.PycommError as e:
        # Unlike most CIP messages, this one is expected to
        # create an exception.  When it is received by the terminal,
        # the device reboots and breaks the socket.
        if (str(e) != 'failed to receive reply'): raise e
    
    cip1.close()