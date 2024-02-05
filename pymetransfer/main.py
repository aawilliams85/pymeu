import os.path
import pycomm3

from .actions import *
from .types import *

class METransfer(object):
    def __init__(self, comms_path: str):
        self.comms_path = comms_path

    def get_terminal_info(self):
        with pycomm3.CIPDriver(self.comms_path) as cip:
            is_terminal_valid(cip)
            print(f'Terminal storage exists: {terminal_get_folder_exists(cip)}.')
            print(f'Terminal has {terminal_get_free_space(cip)} free bytes')

        return True

    def download(self, file_path: str, **kwargs):
        self.delete_logs = kwargs.get('delete_logs', False)
        self.ignore_terminal_valid = kwargs.get('ignore_terminal_valid', False)
        self.overwrite_requested = kwargs.get('overwrite_requested', False)
        self.replace_comms = kwargs.get('replace_comms', False)
        self.run_at_startup = kwargs.get('run_at_startup', True)

        with pycomm3.CIPDriver(self.comms_path) as cip:
            file = MEFile(os.path.basename(file_path), self.overwrite_requested, False, file_path)

            # Validate device at this communications path
            # is a terminal of known version.
            #
            # TODO: Test on more hardware to expand validated list
            if not(is_terminal_valid(cip)):
                if self.ignore_terminal_valid:
                    warn('Invalid device selected, but terminal validation is set to IGNORE.')
                else:
                    raise Exception('Invalid device selected.  Use kwarg ignore_terminal_valid=True to proceed at your own risk.')
                
            # Validate that all starting conditions for downnload to terminal are as expected
            if not(is_download_valid(cip, file)): raise Exception('Download to terminal is invalid.')

            # Perform *.MER download to terminal
            if not(download_to_terminal(cip, file)): raise Exception('Download to terminal failed.')

            # Set *.MER to run at startup and then reboot
            if self.run_at_startup:
                terminal_set_startup_file(cip, file, self.replace_comms, self.delete_logs)
                terminal_reboot(cip)
        
        return True
    
    def reboot(self):
        reboot(self.comms_path)

    def upload(self, file_path: str, **kwargs):
        file = MEFile(os.path.basename(file_path), False, False, file_path)
        self.remote_file_name = kwargs.get('remote_file_name', file.name)

        fileRem = MEFile(self.remote_file_name,False,False,file_path)

        with pycomm3.CIPDriver(self.comms_path) as cip:
            file_instance = terminal_create_file_exchange_for_upload(cip, fileRem)

            # Transfer *.MER chunk by chunk
            terminal_file_upload(cip, file_instance, file)

            # Delete file exchange on the terminal
            terminal_delete_file_exchange(cip, file_instance)