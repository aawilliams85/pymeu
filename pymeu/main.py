import os
import pycomm3

from warnings import warn
from . import terminal
from . import types


class MEUtility(object):
    def __init__(self, comms_path: str, **kwargs):
        """
        Initializes an instance of the MEUtility class.

        Args:
            comms_path (str): The path to the communications resource (ex: 192.168.1.20).
            **kwargs: Additional keyword arguments. 

                - ignore_terminal_valid (bool): Optional; if set to True, 
                the instance will ignore terminal validation checks when
                performing uploads, downloads, etc.
                Defaults to False.
        """
        self.comms_path = comms_path
        self.ignore_terminal_valid = kwargs.get('ignore_terminal_valid', False)

    def download(self, file_path: str, **kwargs) -> types.MEResponse:
        """
        Downloads a *.MER file from the local device to the remote terminal.

        Args:
            file_path (str): The local path to the *.MER file (ex: C:\\YourFolder\\YourProgram.MER)
            **kwargs: Additional keyword arguments. 
                - delete_logs (bool): Optional; if set to True, will configure
                the terminal to delete logs at startup.  Defaults to false.
                - overwrite (bool): Optional; if set to True, will allow the
                download to overwrite an existing *.MER file on the terminal
                with the same file name.  Defaults to false.
                - replace_comms (bool): Optional; if set to True, will replace
                the terminal's communications setup with the one from the *.MER
                file being downloaded.  Defaults to false.
                - remote_file_name (str): Optional; if provided, is used to
                specify a different remote filename on the terminal than the local
                filename specified as part of file_path.
                - run_at_startup (bool): Optional; if set to True, will also set
                this *.MER file to be run at terminal startup and reboot the terminal
                now.  Defaults to True.  Note that this is a departure from the ME
                Transfer Utility, where it is not checked by default.
        """
        self.delete_logs = kwargs.get('delete_logs', False)
        self.overwrite = kwargs.get('overwrite', False)
        self.replace_comms = kwargs.get('replace_comms', False)
        self.remote_file_name = kwargs.get('remote_file_name', os.path.basename(file_path))
        self.run_at_startup = kwargs.get('run_at_startup', True)

        with pycomm3.CIPDriver(self.comms_path) as cip:
            file = types.MEFile(self.remote_file_name, self.overwrite, False, file_path)

            # Validate device at this communications path is a terminal of known version.
            self.device = terminal.validation.get_terminal_info(cip)
            if not(terminal.validation.is_terminal_valid(self.device)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True when initializing MEUtility object to proceed at your own risk.')
                
            # Validate that all starting conditions for downnload to terminal are as expected
            if not(terminal.validation.is_download_valid(cip, self.device, file)): raise Exception('Download to terminal is invalid.')

            # Perform *.MER download to terminal
            if not(terminal.actions.download_mer_file(cip, self.device, file, self.run_at_startup, self.replace_comms, self.delete_logs)): raise Exception('Download to terminal failed.')

        return types.MEResponse(self.device, 'Success')

    def get_terminal_info(self) -> types.MEResponse:
        """
        If no upload or download are desired, where terminal info would typically be checked
        as a prerequisite, this function can be called to generate similar log entries to
        get information about the remote terminal.
        """
        with pycomm3.CIPDriver(self.comms_path) as cip:
            self.device = terminal.validation.get_terminal_info(cip)
            if not(terminal.validation.is_terminal_valid(self.device)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True when initializing MEUtility object to proceed at your own risk.')

            terminal.actions.create_log(cip, self.device)

        return types.MEResponse(self.device, 'Success')

    def reboot(self) -> types.MEResponse:
        """
        Reboots the remote terminal now.
        """
        with pycomm3.CIPDriver(self.comms_path) as cip:
            self.device = terminal.validation.get_terminal_info(cip)

            if not(terminal.validation.is_terminal_valid(self.device)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True when initializing MEUtility object to proceed at your own risk.')

            terminal.actions.reboot(cip, self.device)

        return types.MEResponse(self.device, 'Success')

    def upload(self, file_path: str, **kwargs) -> types.MEResponse:
        """
        Uploads a *.MER file from the remote terminal to the local device.

        Args:
            file_path (str): The local path to the *.MER file (ex: C:\\YourFolder\\YourProgram.MER)
            **kwargs: Additional keyword arguments. 
                - overwrite (bool): Optional; if set to True, will replace the
                file on the local device with the uploaded copy from the remote terminal.
                Defaults to False.
                - remote_file_name (str): Optional; if provided, is used to
                specify a different remote filename on the terminal than the local
                filename specified as part of file_path where it will end up.
        """
        file = types.MEFile(os.path.basename(file_path), False, False, file_path)
        self.remote_file_name = kwargs.get('remote_file_name', file.name)
        self.overwrite = kwargs.get('overwrite', False)
        rem_file = types.MEFile(self.remote_file_name,False,False,file_path)

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
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True when initializing MEUtility object to proceed at your own risk.')

            # Perform *.MER upload from terminal
            if not(terminal.actions.upload_mer_file(cip, self.device, file, rem_file)): raise Exception('Upload from terminal failed.')
        
        return types.MEResponse(self.device, 'Success')

    def upload_all(self, file_path: str, **kwargs):
        """
        Uploads all *.MER files from the remote terminal to the local device.

        Args:
            file_path (str): The local path to the target directory (ex: C:\\YourFolder)
            **kwargs: Additional keyword arguments. 
                - overwrite (bool): Optional; if set to True, will replace the
                file on the local device with the uploaded copy from the remote terminal.
                Defaults to False.
        """
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
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True when initializing MEUtility object to proceed at your own risk.')

            mer_list = terminal.actions.upload_mer_list(cip, self.device)
            
            for mer in mer_list:
                if len(mer) > 0:
                    mer_path = os.path.join(file_path, mer)
                    file = types.MEFile(os.path.basename(mer_path), self.overwrite, False, mer_path)

                    # Check for existing *.MER
                    if not(self.overwrite) and (os.path.exists(mer_path)): raise Exception(f'File {mer_path} already exists.  Use kwarg overwrite=True to overwrite existing local file from the remote terminal.')

                    # Perform *.MER upload from terminal
                    if not(terminal.actions.upload_mer_file(cip, self.device, file, file)): raise Exception('Upload from terminal failed.')

        return types.MEResponse(self.device, 'Success')