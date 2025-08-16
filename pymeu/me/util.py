from collections.abc import Callable
import os
import time
from typing import Optional

from .. import comms
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
        if get_major_rev(cip, device) <= 5:
            # For PanelView Plus 5.10 and earlier this registry key appears to be unavailable.
            line = f'Terminal startup file: could not be determined due to hardware version.'
        else:
            # If no startup app has been defined, it will also fail. 
            line = f'Terminal startup file: not configured.'
    device.log.append(line)
    if print_log: print(f'{line}')

def get_major_rev(
    cip: comms.Driver,
    device: types.MEDeviceInfo
) -> int:
    major_rev = int(device.me_identity.me_version.split(".")[0])
    return major_rev

def _get_stream_by_name(streams: list[types.MEArchive], name: str, case_insensitive=True) -> types.MEArchive:
    if case_insensitive:
        return next(x for x in streams if x.name.lower() == name.lower())
    else:
        return next(x for x in streams if x.name == name)
    
def _path_to_list(path: str) -> list[str]:
    path = path.replace('\\', '/').lower()
    components = [comp for comp in path.split('/') if comp]
    return components if components else [path]

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

def split_file_path(file_path_terminal: str) -> tuple[str, str]:
    dirname, basename = file_path_terminal.rsplit('\\', 1)
    return dirname, basename

def wait(
    time_sec: int,
    progress: Optional[Callable[[str, str, int, int], None]] = None
):
    elapsed = 0
    if time_sec < 0: time_sec = 1
    while elapsed < time_sec:
        elapsed += 1
        time.sleep(1)
        if progress:
            progress('Waiting', 'seconds', time_sec, elapsed)