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
                
            # Validate that all starting conditions for downnload to terminal are good
            try:
                resp = terminal.validation.is_download_valid(cip, self.device, file)
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
                resp = terminal.actions.download_mer_file(cip, self.device, file, self.run_at_startup, self.replace_comms, self.delete_logs)
                if not(resp):
                    self.device.log.append(f'Failed to download to terminal.')
                    return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)
            except Exception as e:
                self.device.log.append(f'Exception: {str(e)}')
                self.device.log.append(f'Failed to download to terminal.')
                return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)

        return types.MEResponse(self.device, types.MEResponseStatus.SUCCESS)

    def get_terminal_info(self, **kwargs) -> types.MEResponse:
        """
        If no upload or download are desired, where terminal info would typically be checked
        as a prerequisite, this function can be called to generate similar log entries to
        get information about the remote terminal.

        Args:
            **kwargs: Additional keyword arguments.
                - print_log (bool): Optional; if set to True, will print values.  Please include
                a copy with any bug reports!
                - redact_log (bool): Optional; if set to True, will exclude potentially
                sensitive values such as the *.MER file names on the remote terminal.
                Defaults to False.
                - silent_mode (bool): Optional; if set to True, will exclude values that
                require invocations or transfers so that Diagnostics window doesn't
                pop up on the remote terminal.  Defaults to False.
        """
        self.print_log = kwargs.get('print_log', False)
        self.redact_log = kwargs.get('redact_log', False)
        self.silent_mode = kwargs.get('silent_mode', False)
        with pycomm3.CIPDriver(self.comms_path) as cip:
            self.device = terminal.validation.get_terminal_info(cip)
            if not(terminal.validation.is_terminal_valid(self.device)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True when initializing MEUtility object to proceed at your own risk.')

            try:
                terminal.actions.create_log(cip, self.device, self.print_log, self.redact_log, self.silent_mode)
            except Exception as e:
                self.device.log.append(f'Exception: {str(e)}')
                self.device.log.append(f'Failed to get terminal info.')
                return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)

        return types.MEResponse(self.device, types.MEResponseStatus.SUCCESS)

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

            try:
                terminal.actions.reboot(cip, self.device)
            except Exception as e:
                self.device.log.append(f'Failed to reboot terminal.')
                return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)

        return types.MEResponse(self.device, types.MEResponseStatus.SUCCESS)

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

        with pycomm3.CIPDriver(self.comms_path) as cip:
            # Validate device at this communications path is a terminal of known version.
            self.device = terminal.validation.get_terminal_info(cip)
            if not(terminal.validation.is_terminal_valid(self.device)):
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
                resp = terminal.actions.upload_mer_file(cip, self.device, file, rem_file)
                if not(resp):
                    self.device.log.append(f'Failed to upload from terminal.')
                    return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)
            except Exception as e:
                self.device.log.append(f'Exception: {str(e)}')
                self.device.log.append(f'Failed to upload from terminal.')
                return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)

        return types.MEResponse(self.device, types.MEResponseStatus.SUCCESS)

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

            try:
                mer_list = terminal.actions.upload_mer_list(cip, self.device)
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
                        resp = terminal.actions.upload_mer_file(cip, self.device, file, file)
                        if not(resp):
                            self.device.log.append(f'Failed to upload from terminal.')
                            return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)
                    except Exception as e:
                        self.device.log.append(f'Exception: {str(e)}')
                        self.device.log.append(f'Failed to upload from terminal.')
                        return types.MEResponse(self.device, types.MEResponseStatus.FAILURE)

        return types.MEResponse(self.device, types.MEResponseStatus.SUCCESS)