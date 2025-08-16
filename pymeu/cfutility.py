from collections.abc import Callable
import os
from typing import Optional
from warnings import warn

from . import comms
from .cf import dmk
from .cf import types
from .cf import validation

LOCAL_DMK_PATH = "C:\\Users\\Public\\Documents\\Rockwell Automation\\Firmware Kits"

class CFUtility(object):
    def __init__(
        self,
        comms_path: str, 
        driver: str = None, 
        ignore_terminal_valid: bool = False, 
        ignore_driver_valid: bool = False,
        local_dmk_path: str = None,
    ):
        """
        Initializes an instance of the MEUtility class.

        Args:
            comms_path (str): The path to the communications resource (ex: 192.168.1.20).
            driver (str): The driver name to use (ex: pycomm3 or pylogix).  If not specified, will default
                the first one installed that can be found.
            ignore_terminal_valid (bool): If True, ignore terminal validation checks.
            ignore_driver_valid (bool): If True, ignore driver validation checks.
            local_dmk_path (str): The default directory to assume *.DMK files are found.
        """
        self.comms_path = comms_path
        self.driver = driver
        self.ignore_terminal_valid = ignore_terminal_valid
        self.ignore_driver_valid = ignore_driver_valid
        self.local_dmk_path = LOCAL_DMK_PATH if local_dmk_path is None else local_dmk_path

    def flash_firmware(
        self, 
        dmk_path_local: str, 
        progress: Optional[Callable[[str, str, int, int], None]] = None
    ) -> types.CFResponse:
        """
        Flashes a firmware image to the remote terminal.

        Args:
            dmk_path_local (str): The local path to the firmware image file (ex: C:\\YourFolder\\\\FirmwareImage.DMK)
            progress: Optional callback for progress indication.
        """

        # Use default DMK directory if one is not specified
        if not os.path.isfile(dmk_path_local):
            if os.path.sep not in dmk_path_local:
                dmk_path_local = os.path.join(self.local_dmk_path, dmk_path_local)

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

            # Perform firmware flash to terminal
            try:
                resp = dmk.process_dmk(
                    cip=cip,
                    device=self.device,
                    dmk_path_local=dmk_path_local,
                    dry_run=False,
                    progress=progress)                    
                if not(resp):
                    self.device.log.append(f'Failed to flash terminal.')
                    return types.CFResponse(self.device, types.ResponseStatus.FAILURE)
            except Exception as e:
                self.device.log.append(f'Exception: {str(e)}')
                self.device.log.append(f'Failed to flash terminal.')
                return types.CFResponse(self.device, types.ResponseStatus.FAILURE)

        return types.CFResponse(self.device, types.ResponseStatus.SUCCESS)