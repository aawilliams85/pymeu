import os.path
import pycomm3

from .types import *
from .terminal import *

class MEUtility(object):
    def __init__(self, comms_path: str):
        self.comms_path = comms_path

    def __download_to_terminal(self, cip: pycomm3.CIPDriver, file: MEFile) -> bool:
        # Create runtime folder
        #
        # TODO: Can we check if this already exists and skip?
        if not(terminal_create_runtime_directory(cip, file)): raise Exception('Failed to create runtime path on terminal.')

        # Get attributes
        #
        # Still no clue on what these are, or when/how they would change.
        # If they aren't changed by creating paths, could be moved ahead
        # to is_download_valid().
        if not(terminal_is_get_unk_valid(cip)): raise Exception('Invalid response from an unknown attribute.  Check packets.')

        # Create a file exchange on the terminal
        file_instance = terminal_create_file_exchange_for_download(cip, file)

        # Set attributes
        #
        # Still no clue what this is.  Might be setting file up for write?
        if not(terminal_is_set_unk_valid(cip)): raise Exception('Invalid response from an unknown attribute.  Check packets.')

        # Transfer *.MER chunk by chunk
        terminal_file_download_mer(cip, file_instance, file)

        # Mark file exchange as completed on the terminal
        terminal_end_file_write(cip, file_instance)

        # Delete file exchange on the terminal
        terminal_delete_file_exchange(cip, file_instance)

        return True

    def __get_mer_list(self, cip: pycomm3.CIPDriver):
        # Create *.MER list
        terminal_create_mer_list(cip)

        file_instance = terminal_create_file_exchange_for_mer_list(cip)

        # Transfer *.MER list chunk by chunk
        file_list = terminal_file_upload_mer_list(cip, file_instance)

        # Delete file exchange on the terminal
        terminal_delete_file_exchange(cip, file_instance)

        return file_list

    def __is_download_valid(self, cip: pycomm3.CIPDriver, file:MEFile) -> bool:
        # Check that file is correct extension
        if (file.get_ext() != '.mer'):
            print(f'File {file.name} is not a *.mer file')
            return False

        # Check that storage folder exists
        resp_storage_exists = terminal_get_folder_exists(cip)
        if not(resp_storage_exists):
            print(f'Storage folder does not exist on terminal')
            return False

        # Check free space
        resp_free_space = terminal_get_free_space(cip)
        if (resp_free_space > file.get_size()):
            print(f'File {file.name} requires {file.get_size()} byes.  Free space on terminal {resp_free_space} bytes.')
        else:
            print(f'File {file.name} requires {file.get_size()} bytes.  Free space on terminal {resp_free_space} bytes is insufficient.')
            return False

        # Check if file name already exists
        resp_file_exists = terminal_get_file_exists(cip, file)
        file.overwrite_required = False
        if (resp_file_exists and file.overwrite_requested):
            print(f'File {file.name} already exists on terminal, and overwrite was requested.  Setting overwrite to required.')
            file.overwrite_required = True
        if (resp_file_exists and not(file.overwrite_requested)):
            print(f'File {file.name} already exists on terminal, and overwrite was NOT requested.  Use kwarg overwrite_requested=True to overwrite existing.')
            return False
        if not(resp_file_exists):
            print(f'File {file.name} does not exist on terminal.  Setting overwrite to not required.')

        # Check space consumed by file if it exists
        if resp_file_exists:
            resp_file_size = terminal_get_file_size(cip, file)
            print(f'File {file.name} on terminal is {resp_file_size} bytes.')

        return True

    def __reboot(self, comms_path: str):
        cip = pycomm3.CIPDriver(comms_path)
        cip._cfg['socket_timeout'] = 0.25
        cip.open()
        terminal_reboot(cip)
        cip.close()

    def __is_terminal_valid(self, cip: pycomm3.CIPDriver) -> bool:
        resp = terminal_get_helper_version(cip)
        if resp not in PYMEU_HELPER_VERSIONS:
            print(f'Invalid helper version: {resp}')
            return False
        else:
            print(f'Valid helper version: {resp}')

        resp = terminal_get_me_version(cip)
        if resp not in PYMEU_ME_VERSIONS:
            print(f'Invalid ME version: {resp}')
            return False
        else:
            print(f'Valid ME version: {resp}')

        resp = terminal_get_product_code(cip)
        if resp not in PYMEU_PRODUCT_CODES: 
            print(f'Invalid product code: {resp}')
            return False
        else:
            print(f'Valid product code: {resp}')

        resp = terminal_get_product_type(cip)
        if resp not in PYMEU_PRODUCT_TYPES:
            print(f'Invalid product type: {resp}')
            return False
        else:
            print(f'Valid product type: {resp}')

        return True
    
    def __upload_from_terminal(self, cip: pycomm3.CIPDriver, file: MEFile, rem_file: MEFile) -> bool:
        file_instance = terminal_create_file_exchange_for_upload(cip, rem_file)

        # Transfer *.MER chunk by chunk
        terminal_file_upload_mer(cip, file_instance, file)

        # Delete file exchange on the terminal
        terminal_delete_file_exchange(cip, file_instance)

        return True

    def download(self, file_path: str, **kwargs):
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
        self.ignore_terminal_valid = kwargs.get('ignore_terminal_valid', False)
        self.overwrite = kwargs.get('overwrite', False)
        self.replace_comms = kwargs.get('replace_comms', False)
        self.run_at_startup = kwargs.get('run_at_startup', True)

        with pycomm3.CIPDriver(self.comms_path) as cip:
            file = MEFile(os.path.basename(file_path), self.overwrite, False, file_path)

            # Validate device at this communications path
            # is a terminal of known version.
            #
            # TODO: Test on more hardware to expand validated list
            if not(self.__is_terminal_valid(cip)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True to proceed at your own risk.')
                
            # Validate that all starting conditions for downnload to terminal are as expected
            if not(self.__is_download_valid(cip, file)): raise Exception('Download to terminal is invalid.')

            # Perform *.MER download to terminal
            if not(self.__download_to_terminal(cip, file)): raise Exception('Download to terminal failed.')

            # Set *.MER to run at startup and then reboot
            if self.run_at_startup:
                terminal_set_startup_file(cip, file, self.replace_comms, self.delete_logs)
                terminal_reboot(cip)

    def get_terminal_info(self):
        # 
        # Used to print some info about the remote PanelView terminal.
        #
        with pycomm3.CIPDriver(self.comms_path) as cip:
            self.__is_terminal_valid(cip)
            print(f'Terminal storage exists: {terminal_get_folder_exists(cip)}.')
            print(f'Terminal has {terminal_get_free_space(cip)} free bytes')
            print(f'Terminal has files: {self.__get_mer_list(cip)}')

    def reboot(self):
        #
        # Used to reboot the remote PanelView terminal.
        #
        self.__reboot(self.comms_path)

    def upload(self, file_path: str, **kwargs):
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
            # Validate device at this communications path
            # is a terminal of known version.
            #
            # TODO: Test on more hardware to expand validated list
            if not(self.__is_terminal_valid(cip)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True to proceed at your own risk.')

            # Perform *.MER upload from terminal
            if not(self.__upload_from_terminal(cip, file, rem_file)): raise Exception('Upload from terminal failed.')

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
            # Validate device at this communications path
            # is a terminal of known version.
            #
            # TODO: Test on more hardware to expand validated list
            if not(self.__is_terminal_valid(cip)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True to proceed at your own risk.')

            mer_list = self.__get_mer_list(cip)
            for mer in mer_list:
                mer_path = os.path.join(file_path, mer)
                file = MEFile(os.path.basename(mer_path), self.overwrite, False, mer_path)

                # Check for existing *.MER
                if not(self.overwrite) and (os.path.exists(mer_path)): raise Exception(f'File {mer_path} already exists.  Use kwarg overwrite=True to overwrite existing local file from the remote terminal.')

                # Perform *.MER upload from terminal
                if not(self.__upload_from_terminal(cip, file, file)): raise Exception('Upload from terminal failed.')