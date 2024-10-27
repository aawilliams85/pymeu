import pycomm3

from . import helper

def reboot(cip: pycomm3.CIPDriver, comms_path: str):
    cip = pycomm3.CIPDriver(comms_path)
    cip._cfg['socket_timeout'] = 0.25
    cip.open()
    helper.reboot(cip)
    cip.close()