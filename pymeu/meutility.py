from collections.abc import Callable
import os
from typing import Optional
from warnings import warn

from . import comms
from .me import transfer
from .me import types
from .me import util
from .me import validation

LOCAL_RUNTIME_PATH = "C:\\Users\\Public\\Documents\\RSView Enterprise\\ME\\Runtime"

class MEUtility(object):
    def __init__(
        self,
        comms_path: str, 
        driver: str = None, 
        ignore_terminal_valid: bool = False, 
        ignore_driver_valid: bool = False,
        local_runtime_path: str = None
    ):
        """
        Initializes an instance of the MEUtility class.

        Args:
            comms_path (str): The path to the communications resource (ex: 192.168.1.20).
            driver (str): The driver name to use (ex: pycomm3 or pylogix).  If not specified, will default
                the first one installed that can be found.
            ignore_terminal_valid (bool): If True, ignore terminal validation checks.
            ignore_driver_valid (bool): If True, ignore driver validation checks.
            local_runtime_path (str): The default directory where *.MER files are found.
        """
        self.comms_path = comms_path
        self.driver = driver
        self.ignore_terminal_valid = ignore_terminal_valid
        self.ignore_driver_valid = ignore_driver_valid
        if local_runtime_path is None:
            self.local_runtime_path = LOCAL_RUNTIME_PATH
        else:
            self.local_runtime_path = local_runtime_path

    def download(
        self, 
        file_path_local: str,
        file_name_terminal: str = None,
        delete_logs: bool = False,
        overwrite: bool = False,
        replace_comms: bool = False,
        run_at_startup: bool = True,
        progress: Optional[Callable[[str, int, int], None]] = None, 
    ) -> types.MEResponse:
        """
        Downloads a *.MER file from the local device to the remote terminal.

        Args:
            file_path (str) : The local path to the *.MER file (ex: C:\\YourFolder\\YourProgram.MER)            
            delete_logs (bool) : If True, will configure the terminal to delete logs atstartup.  Defaults to false.
            overwrite (bool): If True, will allow the download to overwrite an existing *.MER file on the terminal
                with the same file name.  Defaults to false.
            replace_comms (bool) : If True, will replace the terminal's communications setup with the one
                from the *.MER file being downloaded.  Defaults to false.
            remote_file_name (str) : If provided, is used to specify a different remote filename on the
                terminal than the local filename specified as part of file_path.
            run_at_startup (bool) : If True, will also set this *.MER file to be run at terminal startup and
                reboot the terminal now.  Defaults to True.
        """
        # Use default MER directory if one is not specified
        if not os.path.isfile(file_path_local):
            if os.path.sep not in file_path_local:
                file_path_local = os.path.join(self.local_runtime_path, file_path_local)

        if file_name_terminal is None: file_name_terminal = os.path.basename(file_path_local)

        with comms.Driver(self.comms_path, self.driver) as cip:
            # Validate device at this communications path is a terminal of known version.
            self.device = validation.get_terminal_info(cip)
            if not(validation.is_valid_me_terminal(self.device)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use ignore_terminal_valid=True when initializing MEUtility object to proceed at your own risk.')
                

            # Validate that all starting conditions for downnload to terminal are good
            try:
                resp = validation.is_valid_download(
                    cip=cip,
                    device=self.device,
                    file_path_local=file_path_local,
                    file_name_terminal=file_name_terminal,
                    overwrite=overwrite
                )
                if resp:
                    self.device.log.append(f'Validated download for {file_path_local}.')
                else:
                    self.device.log.append(f'Failed to validate download.')
                    return types.MEResponse(self.device, types.ResponseStatus.FAILURE)
            except Exception as e:
                self.device.log.append(f'Exception: {str(e)}')
                self.device.log.append(f'Failed to validate download.')
                return types.MEResponse(self.device, types.ResponseStatus.FAILURE)

            # Perform *.MER download to terminal
            try:
                resp = transfer.download_file_mer(
                    cip=cip,
                    device=self.device,
                    file_path_local=file_path_local,
                    file_name_terminal=file_name_terminal,
                    overwrite=overwrite,
                    run_at_startup=run_at_startup,
                    replace_comms=replace_comms,
                    delete_logs=delete_logs,
                    progress=progress
                )
                if not(resp):
                    self.device.log.append(f'Failed to download to terminal.')
                    return types.MEResponse(self.device, types.ResponseStatus.FAILURE)
            except Exception as e:
                self.device.log.append(f'Exception: {str(e)}')
                self.device.log.append(f'Failed to download to terminal.')
                return types.MEResponse(self.device, types.ResponseStatus.FAILURE)

        return types.MEResponse(self.device, types.ResponseStatus.SUCCESS)
    
    def flash_firmware(
        self, 
        firmware_image_path: str, 
        firmware_helper_path: str, 
        firmware_cover_path: str = None,
        dry_run: bool = False,
        progress: Optional[Callable[[str, int, int], None]] = None
    ) -> types.MEResponse:
        """
        Flashes a firmware image to the remote terminal.

        Args:
            firmware_image_path (str) : The local path to the firmware image file (ex: C:\\YourFolder\\FirmwareUpgradeCard\\upgrade\\SC.IMG)
            firmware_helper_path (str) : The local path to the firmware helper file (ex: C:\\Program Files (x86)\\Rockwell Software\\RSView Enterprise\\FUWhelper6xX.dll)
            progress : Optional callback for progress indication.
        """
        # Use default RSView directory if one is not specified
        if not os.path.isfile(firmware_helper_path):
            if os.path.sep not in firmware_helper_path:
                base_path = "C:\\Program Files (x86)\\Rockwell Software\\RSView Enterprise"
                firmware_helper_path = os.path.join(base_path, firmware_helper_path)

        with comms.Driver(self.comms_path, self.driver) as cip:
            if (self.driver == comms.DRIVER_NAME_PYCOMM3) and comms.is_routed_path(self.comms_path):
                if (cip._const_timeout_ticks != b'\xFF'):
                    if self.ignore_driver_valid:
                        warn('Drive pycomm3 specified with bad TIMEOUT_TICKS value, but driver validation is set to IGNORE.')
                    else:
                        resp = f"""
                            Cannot flash firmware to routed path using pycomm3 due to TIMEOUT_TICKS default value {cip._const_timeout_ticks}.
                            This will cause failures during the firmware upgrade process and require a factory reset to recover.
                            Please change the value in pycomm3.const.TIMEOUT_TICKS to b'\\xFF' to proceed, or use pylogix instead.
                        """
                        raise NotImplementedError(resp)

            # Set socket timeout first.
            # The terminal will pause at certain points and delay acknowledging messages.
            # Without this, the process will fail and the terminal will require a factory reset.
            cip.timeout = 255.0

            # Validate device at this communications path is a terminal of known version.
            self.device = validation.get_terminal_info(cip)
            if not(validation.is_valid_me_terminal(self.device)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True when initializing MEUtility object to proceed at your own risk.')

            # Perform firmware flash to terminal
            try:
                resp = util.flash_firmware(
                    cip=cip,
                    device=self.device,
                    firmware_image_path=firmware_image_path,
                    firmware_helper_path=firmware_helper_path,
                    firmware_cover_path=firmware_cover_path,
                    dry_run=dry_run,
                    progress=progress)

                if not(resp):
                    self.device.log.append(f'Failed to flash terminal.')
                    return types.MEResponse(self.device, types.ResponseStatus.FAILURE)
            except Exception as e:
                self.device.log.append(f'Exception: {str(e)}')
                self.device.log.append(f'Failed to flash terminal.')
                return types.MEResponse(self.device, types.ResponseStatus.FAILURE)

        return types.MEResponse(self.device, types.ResponseStatus.SUCCESS)

    def get_terminal_info(
        self, 
        print_log: bool = False,
        redact_log: bool = False,
        silent_mode: bool = False,
    ) -> types.MEResponse:
        """
        If no upload or download are desired, where terminal info would typically be checked
        as a prerequisite, this function can be called to generate similar log entries to
        get information about the remote terminal.

        Args:
            print_log (bool) : If True, will print values.  Please include
                a copy with any bug reports!  Defaults to false.
            redact_log (bool) : If True, will exclude potentially sensitive values
                such as the *.MER file names on the remote terminal. Defaults to False.
            silent_mode (bool) : If True, will exclude values that require invocations
                or transfers so that Diagnostics window doesn't pop up on the remote
                terminal.  Defaults to False.
        """
        with comms.Driver(self.comms_path, self.driver) as cip:
            self.device = validation.get_terminal_info(cip)
            if not(validation.is_valid_me_terminal(self.device)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use ignore_terminal_valid=True when initializing MEUtility object to proceed at your own risk.')

            try:
                util.create_log(cip, self.device, print_log, redact_log, silent_mode)
            except Exception as e:
                self.device.log.append(f'Exception: {str(e)}')
                self.device.log.append(f'Failed to get terminal info.')
                return types.MEResponse(self.device, types.ResponseStatus.FAILURE)

        return types.MEResponse(self.device, types.ResponseStatus.SUCCESS)

    def reboot(
        self
    ) -> types.MEResponse:
        """
        Reboots the remote terminal now.
        """
        with comms.Driver(self.comms_path, self.driver) as cip:
            self.device = validation.get_terminal_info(cip)

            if not(validation.is_valid_me_terminal(self.device)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True when initializing MEUtility object to proceed at your own risk.')

            try:
                util.reboot(cip, self.device)
            except Exception as e:
                self.device.log.append(f'Failed to reboot terminal.')
                return types.MEResponse(self.device, types.ResponseStatus.FAILURE)

        return types.MEResponse(self.device, types.ResponseStatus.SUCCESS)

    def upload(
        self, 
        file_path_local: str, 
        file_name_terminal: str = None,
        overwrite: bool = False,
        progress: Optional[Callable[[str, int, int], None]] = None, 
    ) -> types.MEResponse:
        """
        Uploads a *.MER file from the remote terminal to the local device.

        Args:
            file_path (str) : The local path to the *.MER file (ex: C:\\YourFolder\\YourProgram.MER)
            overwrite (bool) : If True, will replace the file on the local device with the uploaded
                copy from the remote terminal.  Defaults to False.
            remote_file_name (str) : If provided, is used to specify a different remote filename on
                the terminal than the local filename specified as part of file_path where it will end up.
        """

        # Create local path if it doesn't exist yet
        if not(os.path.exists(os.path.dirname(file_path_local))): os.makedirs(os.path.dirname(file_path_local), exist_ok=True)

        if file_name_terminal is None: file_name_terminal = os.path.basename(file_path_local)

        with comms.Driver(self.comms_path, self.driver) as cip:
            # Validate device at this communications path is a terminal of known version.
            self.device = validation.get_terminal_info(cip)
            if not(validation.is_valid_me_terminal(self.device)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use ignore_terminal_valid=True when initializing MEUtility object to proceed at your own risk.')

            # Check for existing file
            if not(overwrite) and (os.path.exists(file_path_local)):
                self.device.log.append(f'File {file_path_local} already exists.  Use overwrite=True to overwrite existing local file from the remote terminal.')
                return types.MEResponse(self.device, types.ResponseStatus.FAILURE)

            # Perform *.MER upload from terminal
            try:
                resp = transfer.upload_file_mer(
                    cip=cip,
                    device=self.device,
                    file_path_local=file_path_local,
                    file_name_terminal=file_name_terminal,
                    progress=progress
                )                    
                if not(resp):
                    self.device.log.append(f'Failed to upload from terminal.')
                    return types.MEResponse(self.device, types.ResponseStatus.FAILURE)
            except Exception as e:
                self.device.log.append(f'Exception: {str(e)}')
                self.device.log.append(f'Failed to upload from terminal.')
                return types.MEResponse(self.device, types.ResponseStatus.FAILURE)

        return types.MEResponse(self.device, types.ResponseStatus.SUCCESS)

    def upload_all(
        self, 
        folder_path_local: str, 
        overwrite: bool = False,
        progress: Optional[Callable[[str, int, int], None]] = None, 
    ) -> types.MEResponse:
        """
        Uploads all *.MER files from the remote terminal to the local device.

        Args:
            file_path (str) : The local path to the target directory (ex: C:\\YourFolder)
            overwrite (bool) : If True, will replace the file on the local device with the 
                uploaded copy from the remote terminal.  Defaults to False.
        """

        # Create upload folder if it doesn't exist yet
        if not(os.path.exists(folder_path_local)): os.makedirs(os.path.dirname(folder_path_local), exist_ok=True)

        with comms.Driver(self.comms_path, self.driver) as cip:
            # Validate device at this communications path is a terminal of known version.
            self.device = validation.get_terminal_info(cip)
            if not(validation.is_valid_me_terminal(self.device)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use ignore_terminal_valid=True when initializing MEUtility object to proceed at your own risk.')

            try:
                mer_list = transfer.upload_list_mer(cip, self.device)
                mer_list = [mer for mer in mer_list if mer]
                for file_name_terminal in mer_list:
                    file_path_local = os.path.join(folder_path_local, file_name_terminal)

                    # Check for existing *.MER
                    if not(overwrite) and (os.path.exists(file_path_local)):
                        self.device.log.append(f'File {file_path_local} already exists.  Use overwrite=True to overwrite existing local file from the remote terminal.')
                        return types.MEResponse(self.device, types.ResponseStatus.FAILURE)
                    
                    resp = transfer.upload_file_mer(
                        cip=cip,
                        device=self.device,
                        file_path_local=file_path_local,
                        file_name_terminal=file_name_terminal,
                        progress=progress
                    )
                    if not(resp):
                        self.device.log.append(f'Failed to upload from terminal.')
                        return types.MEResponse(self.device, types.ResponseStatus.FAILURE)
            except Exception as e:
                self.device.log.append(f'Exception: {str(e)}')
                self.device.log.append(f'Failed to upload from terminal.')
                return types.MEResponse(self.device, types.ResponseStatus.FAILURE)
        return types.MEResponse(self.device, types.ResponseStatus.SUCCESS)