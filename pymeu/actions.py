from collections.abc import Callable
import os
import time
import traceback
from typing import Optional

from .terminal import files
from .terminal import fuwhelper
from .terminal import helper
from .terminal import registry
from . import comms
from . import types

def create_log(cip: comms.Driver, device: types.MEDeviceInfo, print_log: bool, redact_log: bool, silent_mode: bool):
    if print_log: print(f'Terminal CIP identity: {device.cip_identity}.')
    if print_log: print(f'Terminal ME identity: {device.me_identity}.')
    if print_log: print(f'Terminal ME paths: {device.me_paths}.')

    try:
        line = f'Terminal has {helper.get_free_space_runtime(cip, device.me_paths)} free bytes.'
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
        if device.cip_identity.major_rev < 6:
            # For PanelView Plus 5.10 and earlier this registry key appears to be unavailable.
            line = f'Terminal startup file: could not be determined due to hardware version.'
        else:
            # If no startup app has been defined, it will also fail. 
            line = f'Terminal startup file: not configured.'
    device.log.append(line)
    if print_log: print(f'{line}')

def download(cip: comms.Driver, device: types.MEDeviceInfo, file: types.MEFile, rem_path: str, file_data: bytearray, progress: Optional[Callable[[str, int, int], None]] = None) -> bool:
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
        transfer_instance = files.create_transfer_instance_download(cip, file, rem_path)
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

    # Transfer file chunk by chunk
    try:
        if continue_download:
            files.execute_transfer_download(cip, transfer_instance, file_data, progress)
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

    return continue_download

def download_file(cip: comms.Driver, device: types.MEDeviceInfo, file: types.MEFile, rem_path: str, progress: Optional[Callable[[str, int, int], None]] = None) -> bool:
    with open(file.path, 'rb') as source_file:
        return download(cip, device, file, rem_path, bytearray(source_file.read()), progress)

def download_mer_file(cip: comms.Driver, device: types.MEDeviceInfo, file:types.MEFile, run_at_startup: bool, replace_comms: bool, delete_logs: bool, progress: Optional[Callable[[str, int, int], None]] = None) -> bool:
    # Create runtime folder
    try:
        helper.create_folder_runtime(cip, device.me_paths)
        device.log.append(f'Create runtime directory on terminal.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to create runtime directory on terminal.')
        return False

    # Perform download
    try:
        continue_download = download_file(cip, device, file, device.me_paths.runtime, progress)
        device.log.append(f'Downloaded {file.path} to {device.me_paths.runtime}.')
    except:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to download {file.path} to {device.me_paths.runtime}.')
        return False

    # Set *.MER to run at startup and then reboot
    try:
        if continue_download:
            if run_at_startup:
                helper.create_me_shortcut(cip, device.me_paths, file.name, replace_comms, delete_logs)
                device.log.append(f'Set file: {file.name} to run at startup with Replace Comms: {replace_comms}, Delete Logs: {delete_logs}.')
                reboot(cip, device)
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to set file to run at startup.')
        
    return continue_download

def flash_firmware_upgrade_card(cip: comms.Driver, 
                                device: types.MEDeviceInfo, 
                                firmware_image_path: str,
                                firmware_helper_path: str, 
                                progress: Optional[Callable[[str, int, int], None]] = None
                                ):

    # Determine if firmware upgrade helepr exists already
    transfer_fuwhelper = True
    if helper.get_file_exists(cip, device.me_paths, '\\Windows\\FUWhelper.dll'):
        transfer_fuwhelper = False
        device.me_paths.fuwhelper_file = '\\Windows\\FUWhelper.dll'
        device.log.append(f'Firmware upgrade helper already present on terminal.')
    else:
        if helper.get_file_exists(cip, device.me_paths, device.me_paths.fuwhelper_file):
            transfer_fuwhelper = False
            device.log.append(f'Firmware upgrade helper already present on terminal.')

    # Download firmware upgrade wizard helper to terminal
    if transfer_fuwhelper:
        try:
            fuw_helper_file = types.MEFile('FUWhelper.dll',
                                        True,
                                        True,
                                        firmware_helper_path)
            resp = download_file(cip, device, fuw_helper_file, '\\Storage Card', progress)
            if not(resp):
                device.log.append(f'Failed to upgrade terminal.')
                return False
            
            time.sleep(10)
        except Exception as e:
            device.log.append(f'Exception: {str(e)}')
            device.log.append(f'Traceback: {traceback.format_exc()}')
            device.log.append(f'Failed to upgrade terminal.')
            return False            

    # Prepare terminal for firmware upgrade card
    try:
        if not(fuwhelper.get_folder_exists(cip, device.me_paths, '\\Storage Card')):
            fuwhelper.create_folder(cip, device.me_paths, '\\Storage Card')
        if not(fuwhelper.get_folder_exists(cip, device.me_paths, '\\Storage Card\\vfs')):
            fuwhelper.create_folder(cip, device.me_paths, '\\Storage Card\\vfs')
        if not(fuwhelper.get_folder_exists(cip, device.me_paths, '\\Storage Card\\vfs\\platform firmware')):
            fuwhelper.create_folder(cip, device.me_paths, '\\Storage Card\\vfs\\platform firmware')
        if (fuwhelper.get_file_exists(cip, device.me_paths, '\\Storage Card\\Step2.dat')):
            fuwhelper.delete_file(cip, device.me_paths, '\\Storage Card\\Step2.dat')
        if fuwhelper.get_process_running(cip, device.me_paths, 'MERuntime.exe'):
            fuwhelper.stop_process_me(cip, device.me_paths)

        fuwhelper.get_file_exists(cip, device.me_paths, '\\Windows\\useroptions.txt')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Traceback: {traceback.format_exc()}')
        device.log.append(f'Failed to upgrade terminal.')
        return False

    # Download firmware upgrade card to terminal
    try:
        fuw_image_file = types.MEFile('SC.IMG',
                                    True,
                                    True,
                                    firmware_image_path)
        resp = download_file(cip, device, fuw_image_file, '\\vfs\\platform firmware', progress)
        if not(resp):
            device.log.append(f'Failed to upgrade terminal.')
            return False
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Traceback: {traceback.format_exc()}')
        device.log.append(f'Failed to upgrade terminal.')
        return False

    return True

def upload(cip: comms.Driver, device: types.MEDeviceInfo, rem_file_path: str, progress: Optional[Callable[[str, int, int], None]] = None) -> bytearray:
    # Create a transfer instance on the terminal
    try:
        transfer_instance, total_bytes = files.create_transfer_instance_upload(cip, f'{rem_file_path}')
        device.log.append(f'Create transfer instance {transfer_instance} for upload.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to create transfer instance for upload')
        return False

    # Transfer file chunk by chunk
    try:
        resp_binary = files.execute_transfer_upload(cip, transfer_instance, total_bytes, progress)
        device.log.append(f'Uploaded {rem_file_path} using transfer instance {transfer_instance}.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to upload {rem_file_path} using transfer instance {transfer_instance}.')

    # Delete transfer instance on the terminal
    try:
        files.delete_transfer_instance(cip, transfer_instance)
        device.log.append(f'Deleted transfer instance {transfer_instance}.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to delete transfer instance {transfer_instance}.')

    return resp_binary
    
def upload_file(cip: comms.Driver, device: types.MEDeviceInfo, local_file_path: str, rem_file_path: str, progress: Optional[Callable[[str, int, int], None]] = None):
    resp_binary = upload(cip, device, rem_file_path, progress)
    with open(local_file_path, 'wb') as dest_file:
        dest_file.write(resp_binary)

def upload_list(cip: comms.Driver, transfer_instance: int, rem_file_path: str) -> list[str]:
    resp_binary = upload(cip, transfer_instance, rem_file_path)
    resp_str = "".join([chr(b) for b in resp_binary if b != 0])
    resp_list = resp_str.split(':')
    return resp_list

def upload_mer_file(cip: comms.Driver, device: types.MEDeviceInfo, file: types.MEFile, rem_file: types.MEFile, progress: Optional[Callable[[str, int, int], None]] = None) -> bool:
    # Verify file exists on terminal
    try:
        if helper.get_file_exists_mer(cip, device.me_paths, rem_file.name):
            device.log.append(f'File {rem_file.name} exists on terminal.')
        else:
            device.log.append(f'File {rem_file.name} does not exist on terminal.')
            return False
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to check if file {rem_file.name} exists on terminal.')
        return False

    # Perform upload
    try:
        rem_file_path = f'{device.me_paths.runtime}\\{rem_file.name}'
        upload_file(cip, device, file.path, rem_file_path, progress)
        device.log.append(f'Uploaded {rem_file_path} to {file.path}.')
    except:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to upload {rem_file_path} to {file.path}.')
        return False

    return True

def upload_med_list(cip: comms.Driver, device: types.MEDeviceInfo) -> list[str]:
    # Create list on the terminal
    try:
        helper.create_file_list_med(cip, device.me_paths)
        device.log.append(f'Created *.MED list on terminal.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to create *.MED list on terminal.')
        return None

    # Perform upload
    file_list = None
    try:
        rem_file_path = f'{device.me_paths.upload_list}'
        file_list = upload_list(cip, device, rem_file_path)
        device.log.append(f'Uploaded {rem_file_path}.')
    except:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to upload {rem_file_path}.')
        return None

    # Delete list on the terminal
    try:
        helper.delete_file_list(cip, device.me_paths)
        device.log.append(f'Deleted *.MED list on terminal.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to delete *.MED list on terminal.')

    return file_list

def upload_mer_list(cip: comms.Driver, device: types.MEDeviceInfo) -> list[str]:
    # Create *.MER list
    try:
        helper.create_file_list_mer(cip, device.me_paths)
        device.log.append(f'Created *.MER list on terminal.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to create *.MER list on terminal.')
        return None

    # Perform upload
    file_list = None
    try:
        rem_file_path = f'{device.me_paths.upload_list}'
        file_list = upload_list(cip, device, rem_file_path)
        device.files = file_list
        device.log.append(f'Uploaded {rem_file_path}.')
    except:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to upload {rem_file_path}.')
        return None

    # Delete list on the terminal
    try:
        helper.delete_file_list(cip, device.me_paths)
        device.log.append(f'Deleted *.MER list on terminal.')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Failed to delete *.MER list on terminal.')

    return file_list

def reboot(cip: comms.Driver, device: types.MEDeviceInfo):
    cip1 = comms.Driver(cip._original_path)
    cip1.timeout = 0.25
    cip1.open()
    try:
        # Execute reboot
        device.log.append(f'Rebooting terminal.')
        helper.reboot(cip1, device.me_paths)

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
        if ((device.me_identity.major_rev < 12) or ((device.me_identity.major_rev == 12) and (device.me_identity.minor_rev < 108))):
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
        helper.create_me_shortcut(cip, device.me_paths, startup_file, replace_comms, delete_logs)

        # Execute reboot
        device.log.append(f'Rebooting terminal.')
        helper.reboot(cip1, device.me_paths)
    except Exception as e:
        # Unlike most CIP messages, this one is expected to
        # create an exception.  When it is received by the terminal,
        # the device reboots and breaks the socket.
        if (str(e) != 'failed to receive reply'): raise e
    
    cip1.close()