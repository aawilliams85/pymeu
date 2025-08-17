from collections.abc import Callable
import os
from typing import Optional
from warnings import warn

from . import comms
from .me import firmware
from .me import fuwhelper
from .me import transfer
from .me import types
from .me import util
from .me import validation

LOCAL_RUNTIME_PATH = "C:\\Users\\Public\\Documents\\RSView Enterprise\\ME\\Runtime"
LOCAL_BIN_PATH = "C:\\Program Files (x86)\\Rockwell Software\\RSView Enterprise"
LOCAL_FUP_PATH = "C:\\Program Files (x86)\\Rockwell Software\\RSView Enterprise\\FUPs"

class MEUtility(object):
    def __init__(
        self,
        comms_path: str = None, 
        driver: str = None, 
        ignore_terminal_valid: bool = False, 
        ignore_driver_valid: bool = False,
        local_bin_path: str = None,
        local_fup_path: str = None,
        local_runtime_path: str = None,
    ):
        """
        Initializes an instance of the MEUtility class.

        Args:
            comms_path (str): The path to the communications resource (ex: 192.168.1.20).
            driver (str): The driver name to use (ex: pycomm3 or pylogix).  If not specified, will default
                the first one installed that can be found.
            ignore_terminal_valid (bool): If True, ignore terminal validation checks.
            ignore_driver_valid (bool): If True, ignore driver validation checks.
            local_bin_path (str): The default directory to assume Helper/Cover files are found.
            local_fup_path (str): The default directory to assume *.FUP files are found.
            local_runtime_path (str): The default directory to assume *.MER files are found.
        """
        self.comms_path = comms_path
        self.driver = driver
        self.ignore_terminal_valid = ignore_terminal_valid
        self.ignore_driver_valid = ignore_driver_valid

        self.local_bin_path = LOCAL_BIN_PATH if local_bin_path is None else local_bin_path
        self.local_fup_path = LOCAL_FUP_PATH if local_fup_path is None else local_fup_path 
        self.local_runtime_path = LOCAL_RUNTIME_PATH if local_runtime_path is None else local_runtime_path

    def create_firmware_card(
        self,
        fup_path_local: str,
        fwc_path_local: str,
        kep_drivers: list[str] = None,
        progress: Optional[Callable[[str, int, int], None]] = None
    ) -> types.MEResponse:
        """
        Creates a Firmware Card that can be used to update an ME terminal.

        Args:
            fup_path_local (str): The path to the *.FUP file to use.
            fwc_path_local (str): The path to the firmware card that will be generated (i.e. USB/CF card).
            kep_drivers (list[str]): The names of the KepDrivers to enable by default.
            progress: Optional callback for progress indication.
        """

        # Use default RSView directory if one is not specified
        if not os.path.isfile(fup_path_local):
            if os.path.sep not in fup_path_local:
                fup_path_local = os.path.join(self.local_fup_path, fup_path_local)

        # Perform firmware flash to terminal
        try:
            resp = firmware.fup_to_fwc_folder(
                input_path=fup_path_local,
                output_path=fwc_path_local,
                kep_drivers=kep_drivers,
                progress=progress
            )
        except Exception as e:
            print(e)
            return types.MEResponse(None, types.ResponseStatus.FAILURE)

        return types.MEResponse(None, types.ResponseStatus.SUCCESS)
    
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
            file_path_local (str): The local path to the *.MER file (ex: C:\\YourFolder\\YourProgram.MER)    
            file_name_terminal (str): If the *.MER name on the terminal should be different, specify it here.
            delete_logs (bool) : If True, will configure the terminal to delete logs atstartup.  Defaults to false.
            overwrite (bool): If True, will allow the download to overwrite an existing *.MER file on the terminal
                with the same file name.  Defaults to false.
            replace_comms (bool) : If True, will replace the terminal's communications setup with the one
                from the *.MER file being downloaded.  Defaults to false.
            run_at_startup (bool) : If True, will also set this *.MER file to be run at terminal startup and
                reboot the terminal now.  Defaults to True.
            progress: Optional callback for progress indication.
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
        fup_path_local: str, 
        fuwhelper_path_local: str, 
        fuwcover_path_local: str = None,
        kep_drivers: list[str] = None,
        progress: Optional[Callable[[str, int, int], None]] = None
    ) -> types.MEResponse:
        """
        Flashes a firmware image to the remote terminal.

        Args:
            fup_path_local (str): The local path to the firmware file (ex: C:\\Program Files (x86)\\Rockwell Software\\RSView Enterprise\\FUPs\\ME_PVP6xX_12.00-20200922.fup)
            fuwhelper_path_local (str): The local path to the firmware helper file (ex: C:\\Program Files (x86)\\Rockwell Software\\RSView Enterprise\\FUWhelper6xX.dll)
            fuwcover_path_local (str): The local path to the firmware cover file if applicable (ex: C:\\Program Files (x86)\\Rockwell Software\\RSView Enterprise\\FUWCover4xX.exe)
            kep_drivers (list[str]): The names of the KepDrivers to enable by default.
            progress: Optional callback for progress indication.
        """
        # Use default RSView directory if one is not specified
        if not os.path.isfile(fuwhelper_path_local):
            if os.path.sep not in fuwhelper_path_local:
                fuwhelper_path_local = os.path.join(self.local_bin_path, fuwhelper_path_local)

        # Use default RSView directory if one is not specified
        if fuwcover_path_local is not None:
            if not os.path.isfile(fuwcover_path_local):
                if os.path.sep not in fuwcover_path_local:
                    fuwcover_path_local = os.path.join(self.local_bin_path, fuwcover_path_local)

        # Use default RSView directory if one is not specified
        if not os.path.isfile(fup_path_local):
            if os.path.sep not in fup_path_local:
                fup_path_local = os.path.join(self.local_fup_path, fup_path_local)

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
            if not(validation.is_valid_me_terminal(self.device)) or not(validation.is_native_me_terminal(self.device)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use ignore_terminal_valid=True when initializing MEUtility object to proceed at your own risk.')

            # Perform firmware flash to terminal
            try:
                resp = firmware.flash_fup_to_terminal(
                    cip=cip,
                    device=self.device,
                    fup_path_local=fup_path_local,
                    fuwhelper_path_local=fuwhelper_path_local,
                    fuwcover_path_local=fuwcover_path_local,
                    kep_drivers=kep_drivers,
                    progress=progress
                )
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
            print_log (bool): If True, will print values.  Please include
                a copy with any bug reports!  Defaults to false.
            redact_log (bool): If True, will exclude potentially sensitive values
                such as the *.MER file names on the remote terminal. Defaults to False.
            silent_mode (bool): If True, will exclude values that require invocations
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

    def stop(
        self,
        fuwhelper_path_local: str,
        progress: Optional[Callable[[str, int, int], None]] = None
    ) -> types.MEResponse:
        """
        Stops ME Station on the terminal.

        Args:
            fuwhelper_path_local (str): The local path to the firmware helper file (ex: C:\\Program Files (x86)\\Rockwell Software\\RSView Enterprise\\FUWhelper6xX.dll)
        """
        with comms.Driver(self.comms_path, self.driver) as cip:
            self.device = validation.get_terminal_info(cip)
            if not(validation.is_valid_me_terminal(self.device)) or not(validation.is_native_me_terminal(self.device)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use ignore_terminal_valid=True when initializing MEUtility object to proceed at your own risk.')

            try:
                firmware.get_or_download_fuwhelper(
                    cip=cip,
                    device=self.device,
                    fuwhelper_path_local=fuwhelper_path_local,
                    progress=progress
                )

                if fuwhelper.get_process_running(
                    cip=cip,
                    paths=self.device.me_paths,
                    process_name='MERuntime.exe'
                ):
                    # Check major rev.  v5 lacks dedicated termination function
                    if util.get_major_rev(cip, self.device) <= 5:
                        fuwhelper.stop_process(
                            cip=cip,
                            paths=self.device.me_paths,
                            process='MERuntime.exe'
                        )
                    else:
                        fuwhelper.stop_process_me(
                            cip=cip,
                            paths=self.device.me_paths
                        )
            except Exception as e:
                self.device.log.append(f'Exception: {str(e)}')
                self.device.log.append(f'Failed to stop ME Station.')
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
            file_path_local (str): The local path to the *.MER file (ex: C:\\YourFolder\\YourProgram.MER)
            file_name_terminal (str): The remote name of the *.MER file if different from the name in the local path.
            overwrite (bool) : If True, will replace the file on the local device with the uploaded
                copy from the remote terminal.  Defaults to False.
            progress: Optional callback for progress indication.
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
            folder_path_local (str) : The local path to the target directory (ex: C:\\YourFolder)
            overwrite (bool) : If True, will replace the file on the local device with the 
                uploaded copy from the remote terminal.  Defaults to False.
            progress: Optional callback for progress indication.
        """

        # Create upload folder if it doesn't exist yet
        if not(os.path.exists(folder_path_local)): os.makedirs(folder_path_local, exist_ok=True)

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