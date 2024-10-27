import pycomm3

from ..types import *
from . import files
from . import helper

def get_mer_list(cip: pycomm3.CIPDriver, device: MEDeviceInfo):
    # Create *.MER list
    helper.create_mer_list(cip)

    # Create file exchange on the terminal
    file_instance = files.create_exchange_upload_mer_list(cip)
    device.log.append(f'Create file exchange {file_instance} for upload.')

    # Transfer *.MER list chunk by chunk
    file_list = files.upload_mer_list(cip, file_instance)
    device.log.append(f'Uploaded *.MER list using file exchange {file_instance}.')
    device.files = file_list

    # Delete file exchange on the terminal
    files.delete_exchange(cip, file_instance)
    device.log.append(f'Deleted file exchange {file_instance}.')

    # Delete *.MER list on the terminal
    helper.delete_file_mer_list(cip)
    device.log.append(f'Delete *.MER list on terminal.')

    return file_list

def reboot(cip: pycomm3.CIPDriver, comms_path: str):
    cip = pycomm3.CIPDriver(comms_path)
    cip._cfg['socket_timeout'] = 0.25
    cip.open()
    helper.reboot(cip)
    cip.close()