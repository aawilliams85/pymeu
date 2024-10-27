import os
import pycomm3

from . import terminal
from .types import *
from warnings import warn

class MEUtility(object):
    def __init__(self, comms_path: str, **kwargs):
        self.comms_path = comms_path
        self.ignore_terminal_valid = kwargs.get('ignore_terminal_valid', False)

    def download(self, file_path: str, **kwargs) -> MEResponse:
        #
        # Used to download a *.MER file from this system to the remote Panelview terminal.
        #
        # File path: *.MER path on local system (ex: C:\MyFolder\MyHMI.MER)
        # 
        # Optional Keyword Arguments:
        # Delete Logs: Configures terminal to delete logs at startup
        # Ignore Terminal Valid: Attempt to proceed with download, even if target
        #       product ID or version does not match tested whitelist.
        #       Proceed with caution...
        # Overwrite: If file exists already on remote terminal, replace it.
        # Replace Comms: Configures terminal to replace communications
        #       from *.MER at startup.
        # Run At Startup: Configures terminal to run downloaded *.MER at startup.
        #       Note that this option must be selected to use Delete Logs or Replace Comms.
        #
        self.delete_logs = kwargs.get('delete_logs', False)
        self.overwrite = kwargs.get('overwrite', False)
        self.replace_comms = kwargs.get('replace_comms', False)
        self.run_at_startup = kwargs.get('run_at_startup', True)

        with pycomm3.CIPDriver(self.comms_path) as cip:
            file = MEFile(os.path.basename(file_path), self.overwrite, False, file_path)

            # Validate device at this communications path is a terminal of known version.
            self.device = terminal.validation.get_terminal_info(cip)
            if not(terminal.validation.is_terminal_valid(self.device)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True to proceed at your own risk.')
                
            # Validate that all starting conditions for downnload to terminal are as expected
            if not(terminal.validation.is_download_valid(cip, self.device, file)): raise Exception('Download to terminal is invalid.')

            # Perform *.MER download to terminal
            if not(terminal.actions.download_mer_file(cip, self.device, file, self.run_at_startup, self.replace_comms, self.delete_logs)): raise Exception('Download to terminal failed.')

        return MEResponse(self.device, 'Success')

    def get_terminal_info(self) -> MEResponse:
        # 
        # Used to print some info about the remote PanelView terminal.
        #
        with pycomm3.CIPDriver(self.comms_path) as cip:
            self.device = terminal.validation.get_terminal_info(cip)
            if not(terminal.validation.is_terminal_valid(self.device)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True to proceed at your own risk.')

            terminal.actions.create_log(cip, self.device)

        return MEResponse(self.device, 'Success')

    def reboot(self) -> MEResponse:
        #
        # Used to reboot the remote PanelView terminal.
        #
        with pycomm3.CIPDriver(self.comms_path) as cip:
            self.device = terminal.validation.get_terminal_info(cip)

            if not(terminal.validation.is_terminal_valid(self.device)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True to proceed at your own risk.')

            terminal.actions.reboot(cip)

        return MEResponse(self.device, 'Success')

    def upload(self, file_path: str, **kwargs) -> MEResponse:
        #
        # Used to upload a *.MER file from the remote PanelView terminal to this system.
        #
        # File Path: Path to upload to on the local system (ex: C:\MyFolder\MyHMI.MER)
        # 
        # Optional Keyword Arguments:
        # Overwrite: If the file already exists on the local system, replace it.
        # Remote File Name: Use this to specify a different remote filename on the
        #       terminal than where the local file will end up.
        #
        file = MEFile(os.path.basename(file_path), False, False, file_path)
        self.remote_file_name = kwargs.get('remote_file_name', file.name)
        self.overwrite = kwargs.get('overwrite', False)
        rem_file = MEFile(self.remote_file_name,False,False,file_path)

        # Create upload folder if it doesn't exist yet
        if not(os.path.exists(os.path.dirname(file.path))): os.makedirs(os.path.dirname(file.path))

        # Check for existing *.MER
        if not(self.overwrite) and (os.path.exists(file.path)): raise Exception(f'File {file.name} already exists.  Use kwarg overwrite=True to overwrite existing local file from the remote terminal.')

        with pycomm3.CIPDriver(self.comms_path) as cip:
            # Validate device at this communications path is a terminal of known version.
            self.device = terminal.validation.get_terminal_info(cip)
            if not(terminal.validation.is_terminal_valid(self.device)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True to proceed at your own risk.')

            # Perform *.MER upload from terminal
            if not(terminal.actions.upload_mer_file(cip, self.device, file, rem_file)): raise Exception('Upload from terminal failed.')
        
        return MEResponse(self.device, 'Success')

    def upload_all(self, file_path: str, **kwargs):
        #
        # Used to upload all *.MER files from the remote PanelView terminal to this system.
        #
        # File Path: Path to upload to on the local system (ex: C:\MyFolder)
        # 
        # Optional Keyword Arguments:
        # Overwrite: If the file already exists on the local system, replace it.
        #
        self.overwrite = kwargs.get('overwrite', False)

        # Create upload folder if it doesn't exist yet
        if not(os.path.exists(file_path)): os.makedirs(os.path.dirname(file_path))

        with pycomm3.CIPDriver(self.comms_path) as cip:
            # Validate device at this communications path is a terminal of known version.
            self.device = terminal.validation.get_terminal_info(cip)
            if not(terminal.validation.is_terminal_valid(self.device)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True to proceed at your own risk.')

            mer_list = terminal.actions.upload_mer_list(cip, self.device)
            
            for mer in mer_list:
                if len(mer) > 0:
                    mer_path = os.path.join(file_path, mer)
                    file = MEFile(os.path.basename(mer_path), self.overwrite, False, mer_path)

                    # Check for existing *.MER
                    if not(self.overwrite) and (os.path.exists(mer_path)): raise Exception(f'File {mer_path} already exists.  Use kwarg overwrite=True to overwrite existing local file from the remote terminal.')

                    # Perform *.MER upload from terminal
                    if not(terminal.actions.upload_mer_file(cip, self.device, file, file)): raise Exception('Upload from terminal failed.')

        return MEResponse(self.device, 'Success')