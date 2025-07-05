from collections.abc import Callable
import os
from typing import Optional
from warnings import warn

from . import comms
from . import dmk
from . import types
from . import validation

class CFUtility(object):
    def __init__(self, comms_path: str, **kwargs):
        """
        Initializes an instance of the CFUtility class.

        Args:
            comms_path (str): The path to the communications resource (ex: 192.168.1.20).
            **kwargs: Additional keyword arguments. 

                - driver (str): Optional; can be set to pycomm3 or pylogix
                to request specific driver for CIP messaging.
                - ignore_terminal_valid (bool): Optional; if set to True, 
                the instance will ignore terminal validation checks when
                performing uploads, downloads, etc.
                Defaults to False.
        """
        self.comms_path = comms_path
        self.driver = kwargs.get('driver', None)
        self.ignore_terminal_valid = kwargs.get('ignore_terminal_valid', False)

    def flash_firmware_dmk(self, 
                       firmware_image_path: str, 
                       dry_run: Optional[bool] = False,
                       progress: Optional[Callable[[str, int, int], None]] = None
                       ) -> types.MEResponse:
        """
        Flashes a firmware image to the remote terminal.

        Args:
            firmware_image_path (str): The local path to the firmware image file (ex: C:\\YourFolder\\\\FirmwareImage.DMK)
            progress: Optional callback for progress indication.
        """

        with comms.Driver(self.comms_path, self.driver) as cip:
            # Set socket timeout first.
            # The terminal will pause at certain points and delay acknowledging messages.
            # Without this, the process will fail and the terminal will require a factory reset.
            cip.timeout = 255.0

            # Validate device at this communications path is a terminal of known version.
            self.device = validation.get_terminal_info(cip)
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
                    return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)
            except Exception as e:
                self.device.log.append(f'Exception: {str(e)}')
                self.device.log.append(f'Failed to flash terminal.')
                return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)

        return types.MEResponse(self.device, types.MEResponseStatus.SUCCESS)