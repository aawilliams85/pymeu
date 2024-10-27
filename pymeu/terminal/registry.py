from enum import Enum
import pycomm3

from ..messages import *

# Known registry keys on the terminal that should be whitelisted for read access through RemoteHelper.
class RegKeys(Enum):
    CIP_VERSION_MAJOR = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\MajorRevision,'                # ex: 11
    CIP_VERSION_MINOR = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\MinorRevision'                 # ex: 1
    CIP_PRODUCT_CODE = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\ProductCode'                    # ex: 51
    CIP_PRODUCT_NAME = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\ProductName'                    # ex: PanelView Plus_6 1500
    CIP_PRODUCT_TYPE = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\ProductType'                    # ex: 24
    CIP_SERIAL_NUMBER = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\SerialNumber'                  # ex: 1234567
    CIP_VENDOR = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\Vendor'                               # ex: 1
    ME_VERSION = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSView Enterprise\MEVersion'                                # ex: 11.00.25.230
    ME_STARTUP_APP = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSViewME\Startup Options\CurrentApp'                    # ex: \Application Data\Rockwell Software\RSViewME\Runtime\{FileName}.mer
    ME_STARTUP_DELETE_LOGS = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSViewME\Startup Options\DeleteLogFiles'        # ex: 0
    ME_STARTUP_LOAD_CURRENT = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSViewME\Startup Options\LoadCurrentApp'       # ex: 1
    ME_STARTUP_REPLACE_COMMS = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSViewME\Startup Options\ReplaceCommSettings' # ex: 0
    ME_STARTUP_OPTIONS = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSViewME\Startup Options\StartupOptionsConfig'      # ex: 1

def get_value(cip: pycomm3.CIPDriver, key: str) -> str:
    req_data = b''.join(arg.encode() + b'\x00' for arg in key)

    # Response format
    #
    # Byte 0 to 3 response code (0 = function ran, otherwise failed)
    # Byte 4 to 7 unknown purpose
    # Byte 8 to N-1 product type string
    # Byte N null footer
    resp = msg_read_registry(cip, req_data)
    if not resp: raise Exception(f'Failed to read registry key: {key}')
    resp_code = int.from_bytes(resp.value[:4], byteorder='little', signed=False)
    if (resp_code != 0): raise Exception(f'Read registry response code was not zero.  Examine packets.')

    resp_unk1 = int.from_bytes(resp.value[4:8], byteorder='little', signed=False)
    resp_value = str(resp.value[8:].decode('utf-8').strip('\x00'))
    return resp_value

def get_me_version(cip: pycomm3.CIPDriver) -> str:
    return get_value(cip, [RegKeys.ME_VERSION.value])

def get_product_code(cip: pycomm3.CIPDriver) -> str:
    return get_value(cip, [RegKeys.CIP_PRODUCT_CODE.value])

def get_product_type(cip: pycomm3.CIPDriver) -> str:
    return get_value(cip, [RegKeys.CIP_PRODUCT_TYPE.value])

def get_startup_mer(cip: pycomm3.CIPDriver) -> str:
    return get_value(cip, [RegKeys.ME_STARTUP_APP.value])