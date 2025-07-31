from collections.abc import Callable
import os
from typing import Optional
from warnings import warn

from . import actions
from . import comms
from .me import types
from .me import validation

class MEUtility(object):
    def __init__(
        self,
        comms_path: str, 
        driver: str = None, 
        ignore_terminal_valid: bool = False, 
        ignore_driver_valid: bool = False
    ):
        """
        Initializes an instance of the MEUtility class.

        Args:
            comms_path (str) : The path to the communications resource (ex: 192.168.1.20).
            driver (str) : The driver name to use (ex: pycomm3 or pylogix).  If not specified, will default
                the first one installed that can be found.
            ignore_terminal_valid (bool) : If True, ignore terminal validation checks.
            ignore_driver_valid (bool) : If True, ignore driver validation checks.
        """
        self.comms_path = comms_path
        self.driver = driver
        self.ignore_terminal_valid = ignore_terminal_valid
        self.ignore_driver_valid = ignore_driver_valid

    def download(
        self, 
        file_path: str, 
        delete_logs: bool = False,
        overwrite: bool = False,
        replace_comms: bool = False,
        remote_file_name: str = None,
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
        self.delete_logs = delete_logs
        self.overwrite = overwrite
        self.replace_comms = replace_comms
        if remote_file_name is None:
            self.remote_file_name = os.path.basename(file_path)
        else:
            self.remote_file_name = remote_file_name
        self.run_at_startup = run_at_startup

        # Use default MER directory if one is not specified
        if not os.path.isfile(file_path):
            if os.path.sep not in file_path:
                base_path = "C:\\Users\\Public\\Documents\\RSView Enterprise\\ME\\Runtime"
                file_path = os.path.join(base_path, file_path)

        with comms.Driver(self.comms_path, self.driver) as cip:
            file = types.MEFile(self.remote_file_name, self.overwrite, False, file_path)

            # Validate device at this communications path is a terminal of known version.
            self.device = validation.get_terminal_info(cip)
            if not(validation.is_valid_me_terminal(self.device)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True when initializing MEUtility object to proceed at your own risk.')
                
            # Validate that all starting conditions for downnload to terminal are good
            try:
                resp = validation.is_valid_download(cip, self.device, file)
                if resp:
                    self.device.log.append(f'Validated download for {file.name}.')
                else:
                    self.device.log.append(f'Failed to validate download.')
                    return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)
            except Exception as e:
                self.device.log.append(f'Exception: {str(e)}')
                self.device.log.append(f'Failed to validate download.')
                return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)

            # Perform *.MER download to terminal
            try:
                resp = actions.download_mer_file(cip, self.device, file, self.run_at_startup, self.replace_comms, self.delete_logs, progress)
                if not(resp):
                    self.device.log.append(f'Failed to download to terminal.')
                    return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)
            except Exception as e:
                self.device.log.append(f'Exception: {str(e)}')
                self.device.log.append(f'Failed to download to terminal.')
                return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)

        return types.MEResponse(self.device, types.MEResponseStatus.SUCCESS)
    
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
                resp = actions.flash_firmware(
                    cip=cip,
                    device=self.device,
                    firmware_image_path=firmware_image_path,
                    firmware_helper_path=firmware_helper_path,
                    firmware_cover_path=firmware_cover_path,
                    dry_run=dry_run,
                    progress=progress)

                if not(resp):
                    self.device.log.append(f'Failed to flash terminal.')
                    return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)
            except Exception as e:
                self.device.log.append(f'Exception: {str(e)}')
                self.device.log.append(f'Failed to flash terminal.')
                return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)

        return types.MEResponse(self.device, types.MEResponseStatus.SUCCESS)

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
        self.print_log = print_log
        self.redact_log = redact_log
        self.silent_mode = silent_mode
        with comms.Driver(self.comms_path, self.driver) as cip:
            self.device = validation.get_terminal_info(cip)
            if not((validation.is_valid_me_terminal(self.device) or validation.is_valid_dmk_terminal(self.device))):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True when initializing MEUtility object to proceed at your own risk.')

            try:
                actions.create_log(cip, self.device, self.print_log, self.redact_log, self.silent_mode)
            except Exception as e:
                self.device.log.append(f'Exception: {str(e)}')
                self.device.log.append(f'Failed to get terminal info.')
                return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)

        return types.MEResponse(self.device, types.MEResponseStatus.SUCCESS)

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
                actions.reboot(cip, self.device)
            except Exception as e:
                self.device.log.append(f'Failed to reboot terminal.')
                return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)

        return types.MEResponse(self.device, types.MEResponseStatus.SUCCESS)

    def upload(
        self, 
        file_path: str, 
        overwrite: bool = False,
        remote_file_name: str = None,
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
        file = types.MEFile(os.path.basename(file_path), False, False, file_path)
        if (remote_file_name is None):
            self.remote_file_name = file.name
        else:
            self.remote_file_name = remote_file_name
        self.overwrite = overwrite
        rem_file = types.MEFile(self.remote_file_name,False,False,file_path)

        # Create upload folder if it doesn't exist yet
        if not(os.path.exists(os.path.dirname(file.path))): os.makedirs(os.path.dirname(file.path), exist_ok=True)

        with comms.Driver(self.comms_path, self.driver) as cip:
            # Validate device at this communications path is a terminal of known version.
            self.device = validation.get_terminal_info(cip)
            if not(validation.is_valid_me_terminal(self.device)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True when initializing MEUtility object to proceed at your own risk.')

            # Check for existing *.MER
            if not(self.overwrite) and (os.path.exists(file.path)):
                self.device.log.append(f'File {file.path} already exists.  Use kwarg overwrite=True to overwrite existing local file from the remote terminal.')
                return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)

            # Perform *.MER upload from terminal
            try:
                resp = actions.upload_mer_file(cip, self.device, file, rem_file, progress)
                if not(resp):
                    self.device.log.append(f'Failed to upload from terminal.')
                    return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)
            except Exception as e:
                self.device.log.append(f'Exception: {str(e)}')
                self.device.log.append(f'Failed to upload from terminal.')
                return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)

        return types.MEResponse(self.device, types.MEResponseStatus.SUCCESS)

    def upload_all(
        self, 
        file_path: str, 
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
        self.overwrite = overwrite

        # Create upload folder if it doesn't exist yet
        if not(os.path.exists(file_path)): os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with comms.Driver(self.comms_path, self.driver) as cip:
            # Validate device at this communications path is a terminal of known version.
            self.device = validation.get_terminal_info(cip)
            if not(validation.is_valid_me_terminal(self.device)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True when initializing MEUtility object to proceed at your own risk.')

            try:
                mer_list = actions.upload_mer_list(cip, self.device)
            except Exception as e:
                self.device.log.append(f'Exception: {str(e)}')
                self.device.log.append(f'Failed to upload *.MER list from terminal.')
                return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)
            
            for mer in mer_list:
                if len(mer) > 0:
                    mer_path = os.path.join(file_path, mer)
                    file = types.MEFile(os.path.basename(mer_path), self.overwrite, False, mer_path)

                    # Check for existing *.MER
                    if not(self.overwrite) and (os.path.exists(mer_path)):
                        self.device.log.append(f'File {mer_path} already exists.  Use kwarg overwrite=True to overwrite existing local file from the remote terminal.')
                        return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)
                    
                    # Perform *.MER upload from terminal
                    try:
                        resp = actions.upload_mer_file(cip, self.device, file, file, progress)
                        if not(resp):
                            self.device.log.append(f'Failed to upload from terminal.')
                            return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)
                    except Exception as e:
                        self.device.log.append(f'Exception: {str(e)}')
                        self.device.log.append(f'Failed to upload from terminal.')
                        return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)

        return types.MEResponse(self.device, types.MEResponseStatus.SUCCESS)