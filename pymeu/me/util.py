from collections.abc import Callable
import os
import time
import traceback
from typing import Optional

from .. import comms
from . import fuwhelper
from . import helper
from . import registry
from . import transfer
from . import types

def create_log(
    cip: comms.Driver, 
    device: types.MEDeviceInfo, 
    print_log: bool, 
    redact_log: bool, 
    silent_mode: bool
):
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
            files = transfer.upload_list_med(cip, device)
            if redact_log: files = ['Redacted' for _ in files]
            line = f'Terminal has MED files: {files}.'
            if len(files) > 0: device.running_med_file = files[0]
        except:
            line = f'Failed to list MED files on terminal.'
        device.log.append(line)
        if print_log: print(f'{line}')

        try:
            files = transfer.upload_list_mer(cip, device)
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

def flash_firmware(
    cip: comms.Driver, 
    device: types.MEDeviceInfo, 
    firmware_image_path: str,
    firmware_helper_path: str, 
    firmware_cover_path: str = None,
    dry_run: bool = False,
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

    # Determine which process to run
    major_rev = int(device.me_identity.me_version.split(".")[0])
    if (major_rev <= 5):
        flash_firmware_pvp5(
            cip=cip,
            device=device,
            firmware_image_path=firmware_image_path,
            firmware_cover_path=firmware_cover_path,
            progress=progress
        )
    else:
        flash_firmware_pvp6(
            cip=cip,
            device=device,
            firmware_image_path=firmware_image_path,
            progress=progress
        )
    return True

def flash_firmware_pvp5(
    cip: comms.Driver, 
    device: types.MEDeviceInfo,
    firmware_image_path: str,
    firmware_cover_path: str,
    progress: Optional[Callable[[str, int, int], None]] = None
):

    # Prepare local files
    firmware_cover_file = types.MEFile(
        name='FUWCover.exe',
        overwrite_requested=True,
        overwrite_required=True,
        path=firmware_cover_path
    )

    # Firmware image known files
    firmware_image_files = []
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='upgrade.inf',
        local_path=os.path.join(firmware_image_path, 'upgrade', 'upgrade.inf'),
        remote_file='upgrade.inf',
        remote_folder='\\Storage Card\\upgrade',
        required=True
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='autorun.exe',
        local_path=os.path.join(firmware_image_path, 'autorun.exe'),
        remote_file='autorun.exe',
        remote_folder='\\Storage Card\\upgrade',
        required=True
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='MFCCE400.DLL',
        local_path=os.path.join(firmware_image_path, 'MFCCE400.DLL'),
        remote_file='MFCCE400.DLL',
        remote_folder='\\Storage Card\\upgrade',
        required=True
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='UpgradeOptions.exe',
        local_path=os.path.join(firmware_image_path, 'upgrade', 'UpgradeOptions.exe'),
        remote_file='FUWcleanup.exe',
        remote_folder='\\Storage Card\\upgrade',
        required=False
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='InstallME.exe',
        local_path=os.path.join(firmware_image_path, 'upgrade', 'InstallME.exe'),
        remote_file='InstallME.exe',
        remote_folder='\\Storage Card\\upgrade',
        required=True
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='KepwareCEInstall.exe',
        local_path=os.path.join(firmware_image_path, 'upgrade', 'KepwareCEInstall.exe'),
        remote_file='KepwareCEInstall.exe',
        remote_folder='\\Storage Card\\upgrade',
        required=False
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='Autoapp.bat',
        local_path=os.path.join(firmware_image_path, 'upgrade', 'Autoapp.bat'),
        remote_file='Autoapp.bat',
        remote_folder='\\Storage Card\\upgrade',
        required=True
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='locOSUp.exe',
        local_path=os.path.join(firmware_image_path, 'upgrade', 'locOSUp.exe'),
        remote_file='locOSUp.exe',
        remote_folder='\\Windows\\upgrade',
        required=True
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='ebcbootrom.bin',
        local_path=os.path.join(firmware_image_path, 'upgrade', 'ebcbootrom.bin'),
        remote_file='ebcbootrom.bin',
        remote_folder='\\Windows\\upgrade',
        required=False
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='EBCMOZ.EBC',
        local_path=os.path.join(firmware_image_path, 'upgrade', 'EBCMOZ.EBC'),
        remote_file='EBCMOZ.EBC',
        remote_folder='\\Storage Card\\upgrade',
        required=False
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='PVPlus_Mozart_nkc.MCE',
        local_path=os.path.join(firmware_image_path, 'upgrade', 'PVPlus_Mozart_nkc.MCE'),
        remote_file='PVPlus_Mozart_nkc.MCE',
        remote_folder='\\Storage Card\\upgrade',
        required=False
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='system.bin',
        local_path=os.path.join(firmware_image_path, 'upgrade', 'system.bin'),
        remote_file='system.bin',
        remote_folder='\\Windows\\upgrade',
        required=False
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='UpgradeOptions.exe',
        local_path=os.path.join(firmware_image_path, 'upgrade', 'UpgradeOptions.exe'),
        remote_file='UpgradeOptions.exe',
        remote_folder='\\Windows\\upgrade',
        required=False
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='valOSPart.exe',
        local_path=os.path.join(firmware_image_path, 'upgrade', 'valOSPart.exe'),
        remote_file='valOSPart.exe',
        remote_folder='\\Windows\\upgrade',
        required=False
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='GetFreeRAM.exe',
        local_path=os.path.join(firmware_image_path, 'upgrade', 'GetFreeRAM.exe'),
        remote_file='GetFreeRAM.exe',
        remote_folder='\\Windows\\upgrade',
        required=True
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='RFOn.bat',
        local_path=os.path.join(firmware_image_path, 'upgrade', 'RFOn.bat'),
        remote_file='RFOn.bat',
        remote_folder='\\Storage Card\\upgrade',
        required=True
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='RFOn1.bat',
        local_path=os.path.join(firmware_image_path, 'upgrade', 'RFOn1.bat'),
        remote_file='RFOn1.bat',
        remote_folder='\\Storage Card\\upgrade',
        required=False
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='RFOn2.bat',
        local_path=os.path.join(firmware_image_path, 'upgrade', 'RFOn2.bat'),
        remote_file='RFOn2.bat',
        remote_folder='\\Storage Card\\upgrade',
        required=False
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='RFOn3.bat',
        local_path=os.path.join(firmware_image_path, 'upgrade', 'RFOn3.bat'),
        remote_file='RFOn3.bat',
        remote_folder='\\Storage Card\\upgrade',
        required=False
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='FUWInhibitor.exe',
        local_path=os.path.join(firmware_image_path, 'upgrade', 'FUWInhibitor.exe'),
        remote_file='FUWInhibitor.exe',
        remote_folder='\\Storage Card\\upgrade',
        required=True
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='MEFileList.inf',
        local_path=os.path.join(firmware_image_path, 'upgrade', 'MEFileList.inf'),
        remote_file='MEFileList.inf',
        remote_folder='\\Storage Card\\upgrade',
        required=True
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='FTVP.Cab',
        local_path=os.path.join(firmware_image_path, 'upgrade', 'FTVP.Cab'),
        remote_file='FTVP.Cab',
        remote_folder='\\Storage Card\\upgrade',
        required=False
    ))
    firmware_image_files.append(types.MEv5FileManifest_zzz(
        local_file='WebServer.Cab',
        local_path=os.path.join(firmware_image_path, 'upgrade', 'WebServer.Cab'),
        remote_file='WebServer.Cab',
        remote_folder='\\Storage Card\\upgrade',
        required=False
    ))

    for file in firmware_image_files:
        if not(os.path.exists(file.local_path)):
            if file.required: raise FileNotFoundError(f'Expected {file.local_path} to exist.')
        else:
            print(f'Found {file.local_path}')

    # For additional files - make a guess at whether they belong in Storage Card or Windows
    firmware_image_other_files = os.listdir(os.path.join(firmware_image_path, 'upgrade'))
    for file in firmware_image_other_files:
        if not any(file2.local_file.lower() == file.lower() for file2 in firmware_image_files):
            if (file.lower().startswith('RFOn')):
                remote_folder = '\\Storage Card\\upgrade'
            elif (file.lower().endswith('bin')):
                remote_folder = '\\Windows\\upgrade'
            elif (file.lower().endswith('ebc')):
                remote_folder = '\\Storage Card\\upgrade'
            elif (file.lower().endswith('mce')):
                remote_folder = '\\Storage Card\\upgrade'
            elif (file.lower().endswith('exe')):
                remote_folder = '\\Windows\\upgrade'
            else:
                remote_folder = '\\Storage Card\\upgrade'

            firmware_image_files.append(types.MEv5FileManifest_zzz(
                local_file=file,
                local_path=os.path.join(firmware_image_path, 'upgrade', file),
                remote_file=file,
                remote_folder=remote_folder,
                required=False
            ))

    for file in firmware_image_files:
        print(file)
        print('')

    # Read MEFileList... this is a list of files that will be checked and deleted later
    with open(os.path.join(firmware_image_path, 'upgrade', 'MEFileList.inf'), 'r') as file:
        me_file_list = deserialize_me_file_list(file.read())

    # Prepare terminal for firmware upgrade card
    try:
        fuwhelper.set_screensaver(cip, device.me_paths, False)
        fuwhelper.set_me_corrupt_screen(cip, device.me_paths, False)
        os_rev = fuwhelper.get_os_rev(cip, device.me_paths)
        print(os_rev)
        part_size = fuwhelper.get_partition_size(cip, device.me_paths)
        print(part_size)
        restore = fuwhelper.get_file_exists(cip, device.me_paths, '\\Storage Card\\_restore_reserve.cmd')
        print(restore)
        fuwhelper.start_process(cip, device.me_paths, 'GenReserve:0')

        if not(fuwhelper.get_folder_exists(cip, device.me_paths, '\\Storage_Card')):
            fuwhelper.create_folder(cip, device.me_paths, '\\Storage Card')
        if not(fuwhelper.get_folder_exists(cip, device.me_paths, '\\Storage Card\\upgrade')):
            fuwhelper.create_folder(cip, device.me_paths, '\\Storage Card\\upgrade')
        fuwhelper.clear_folder(cip, device.me_paths, '\\Storage Card\\upgrade')

        if not(fuwhelper.get_folder_exists(cip, device.me_paths, '\\Windows')):
            fuwhelper.create_folder(cip, device.me_paths, '\\Windows')
        if not(fuwhelper.get_folder_exists(cip, device.me_paths, '\\Windows\\upgrade')):
            fuwhelper.create_folder(cip, device.me_paths, '\\Windows\\upgrade')
        fuwhelper.clear_folder(cip, device.me_paths, '\\Windows\\upgrade')

        if (fuwhelper.get_file_exists(cip, device.me_paths, '\\Storage Card\\Step2.dat')):
            try:
                fuwhelper.delete_file(cip, device.me_paths, '\\Storage Card\\Step2.dat')
            except Exception as e:
                print(e)

        storage_free_space = fuwhelper.get_free_space(cip, device.me_paths, '\\Storage Card')
        print(storage_free_space)
        storage_total_space = fuwhelper.get_total_space(cip, device.me_paths, '\\Storage Card')
        print(storage_total_space)
        windows_free_space = fuwhelper.get_free_space(cip, device.me_paths, '\\Windows')
        print(windows_free_space)
        windows_total_space = fuwhelper.get_total_space(cip, device.me_paths, '\\Windows')
        print(windows_total_space)

        # Check files from MEFileInfo.inf?
        for file in me_file_list.mefiles.files:
            fuwhelper.get_file_exists(cip, device.me_paths, f'\\Storage Card{file}')

        # *** Check whether all expected files exists from MEFileInfo.inf?
        resp = download_file(cip, device, firmware_cover_file, '\\Windows', progress)
        fuwhelper.start_process(cip, device.me_paths, '\\Windows\\FUWCover.exe')
        fuwhelper.stop_process(cip, device.me_paths, 'MERuntime.exe')
        fuwhelper.clear_folder(cip, device.me_paths, '\\Storage Card\\Rockwell Software\\RSViewME')

        # Delete files from MEFileInfo.inf?
        for file in me_file_list.mefiles.files:
            if fuwhelper.get_file_exists(cip, device.me_paths, f'\\Storage Card{file}'):
                try:
                    fuwhelper.delete_file(cip, device.me_paths, f'\\Storage Card{file}')
                except Exception as e:
                    print(e)

        # Delete KEPServer
        if fuwhelper.get_folder_exists(cip, device.me_paths, '\\Storage Card\\KEPServerEnterprise'):
            fuwhelper.clear_folder(cip, device.me_paths, '\\Storage Card\\KEPServerEnterprise')
            fuwhelper.delete_folder(cip, device.me_paths, '\\Storage Card\\KEPServerEnterprise')
    except Exception as e:
        device.log.append(f'Exception: {str(e)}')
        device.log.append(f'Traceback: {traceback.format_exc()}')
        device.log.append(f'Failed to upgrade terminal.')
        return False

    # Download firmware upgrade card to terminal
    for file in firmware_image_files:
        if (os.path.exists(file.local_path)):
            this_file = types.MEFile(
                name=file.remote_file,
                overwrite_requested=True,
                overwrite_required=True,
                path=file.local_path
            )
            resp = download_file(
                cip=cip,
                device=device,
                file=this_file,
                rem_path=file.remote_folder,
                progress=progress
            )
            time.sleep(1)
        else:
            if file.required: raise FileNotFoundError(f'Expected {file.local_path} to exist.')    

    # Initiate install
    fuwhelper.set_screensaver(cip, device.me_paths, True)
    fuwhelper.set_me_corrupt_screen(cip, device.me_paths, True)
    time.sleep(5)
    fuwhelper.stop_process(cip, device.me_paths, 'FUWCover.exe')
    fuwhelper.start_process(cip, device.me_paths, '\\Storage Card\\upgrade\\autorun.exe')
    return True

def flash_firmware_pvp6(
    cip: comms.Driver, 
    device: types.MEDeviceInfo,
    firmware_image_path: str,
    progress: Optional[Callable[[str, int, int], None]] = None
):
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

def reboot(
    cip: comms.Driver, 
    device: types.MEDeviceInfo
):
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