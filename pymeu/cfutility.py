from collections.abc import Callable
import os
from typing import Optional
from warnings import warn

from . import comms
from .cf import dmk
from .cf import types
from .cf import validation

class CFUtility(object):
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

    def flash_firmware(
        self, 
        firmware_image_path: str, 
        dry_run: bool = False,
        progress: Optional[Callable[[str, str, int, int], None]] = None
    ) -> types.CFResponse:
        """
        Flashes a firmware image to the remote terminal.

        Args:
            firmware_image_path (str) : The local path to the firmware image file (ex: C:\\YourFolder\\\\FirmwareImage.DMK)
            dry_run (bool) : If True, run through pre-processing but don't actually flash the device.
            progress: Optional callback for progress indication.
        """

        with comms.Driver(self.comms_path, self.driver) as cip:
            if (self.driver == comms.DRIVER_NAME_PYLOGIX):
                if self.ignore_driver_valid:
                    warn('Drive pylogix specified but driver validation is set to IGNORE.')
                else:
                    resp = f"""
                        Cannot flash firmware with pylogix yet, work still required on forward open/forward close.
                        Please use pycomm3 instead for now.
                    """
                    raise NotImplementedError(resp)


            # Set socket timeout first.
            # The terminal will pause at certain points and delay acknowledging messages.
            # Without this, the process will fail and the terminal will require a factory reset.
            cip.timeout = 255.0

            # Validate device at this communications path is a terminal of known version.
            self.device = validation.get_device_info(cip)
            if not(validation.is_valid_dmk_terminal(self.device)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True when initializing MEUtility object to proceed at your own risk.')

            # Perform firmware flash to terminal
            try:
                resp = dmk.process_dmk(
                    cip=cip,
                    device=self.device,
                    dmk_file_path=firmware_image_path,
                    dry_run=dry_run,
                    progress=progress)                    
                if not(resp):
                    self.device.log.append(f'Failed to flash terminal.')
                    return types.CFResponse(self.device, types.ResponseStatus.FAILURE)
            except Exception as e:
                self.device.log.append(f'Exception: {str(e)}')
                self.device.log.append(f'Failed to flash terminal.')
                return types.CFResponse(self.device, types.ResponseStatus.FAILURE)

        return types.CFResponse(self.device, types.ResponseStatus.SUCCESS)