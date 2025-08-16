from enum import StrEnum

from .. import comms
from . import messages

# Known registry keys on the terminal that should be whitelisted for read access through RemoteHelper.
class RegKeys(StrEnum):
    CIP_VERSION_MAJOR = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\MajorRevision'                 # ex: 11
    CIP_VERSION_MINOR = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\MinorRevision'                 # ex: 1
    CIP_PRODUCT_CODE = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\ProductCode'                    # ex: 51
    CIP_PRODUCT_NAME = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\ProductName'                    # ex: PanelView Plus_6 1500
    CIP_PRODUCT_TYPE = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\ProductType'                    # ex: 24
    CIP_SERIAL_NUMBER = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\SerialNumber'                  # ex: 1234567
    CIP_VENDOR_ID = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\Vendor'                            # ex: 1
    ME_VERSION = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSView Enterprise\MEVersion'                                # ex: 11.00.25.230
    ME_STARTUP_APP = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSViewME\Startup Options\CurrentApp'                    # ex: \Application Data\Rockwell Software\RSViewME\Runtime\{FileName}.mer
    ME_STARTUP_DELETE_LOGS = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSViewME\Startup Options\DeleteLogFiles'        # ex: 0
    ME_STARTUP_LOAD_CURRENT = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSViewME\Startup Options\LoadCurrentApp'       # ex: 1
    ME_STARTUP_REPLACE_COMMS = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSViewME\Startup Options\ReplaceCommSettings' # ex: 0
    ME_STARTUP_OPTIONS = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSViewME\Startup Options\StartupOptionsConfig'      # ex: 1

def get_value(cip: comms.Driver, key: str) -> str:
    '''
    Gets a registry key's value from the remote terminal.

    Request Format:
        The request consists of the following byte structure:

        | Byte Range    | Description                                         |
        |---------------|-----------------------------------------------------|
        | Bytes 0->N-1  | Registry key name                                   |
        | Byte N        | Null footer                                         |

    Response Format:
        The response consists of the following byte structure:

        | Byte Range    | Description                                         |
        |---------------|-----------------------------------------------------|
        | Bytes 0->3    | Response code (typically 0 = good, otherwise error) |
        | Bytes 4->7    | Unknown purpose                                     |
        | Bytes 8->N-1  | Registry key value                                  |
        | Bytes N       | Null footer                                         |

    Note:
        Only a certain subset of registry keys are whitelisted for access
        by this method.  They are documented in the RegKeys enum.
    '''
    req_data = b''.join(arg.encode() + b'\x00' for arg in key)

    resp = messages.read_registry(cip, req_data)
    if not resp: raise Exception(f'Failed to read registry key: {key}')
    resp_code = int.from_bytes(resp.value[:4], byteorder='little', signed=False)
    if (resp_code != 0): raise Exception(f'Failed to read registry key: {key}, response code: {resp_code}.')

    resp_unk1 = int.from_bytes(resp.value[4:8], byteorder='little', signed=False)
    resp_value = str(resp.value[8:].decode('utf-8').strip('\x00'))
    return resp_value

def get_me_version(cip: comms.Driver) -> str:
    return get_value(cip, [RegKeys.ME_VERSION])

def get_product_code(cip: comms.Driver) -> int:
    return int(get_value(cip, [RegKeys.CIP_PRODUCT_CODE]))

def get_product_name(cip: comms.Driver) -> str:
    return str(get_value(cip, [RegKeys.CIP_PRODUCT_NAME]))

def get_product_type(cip: comms.Driver) -> int:
    return int(get_value(cip, [RegKeys.CIP_PRODUCT_TYPE]))

def get_serial_number(cip: comms.Driver) -> str:
    serial_number = get_value(cip, [RegKeys.CIP_SERIAL_NUMBER])
    serial_number_str = f'{int(serial_number):08x}'
    return serial_number_str

def get_startup_delete_logs(cip: comms.Driver) -> bool:
    # True = Delete logs at startup, False = don't
    return bool(int(get_value(cip, [RegKeys.ME_STARTUP_DELETE_LOGS])))

def get_startup_load_current(cip: comms.Driver) -> bool:
    # True = Load the *.MER at startup, False = don't
    return bool(int(get_value(cip, [RegKeys.ME_STARTUP_LOAD_CURRENT])))

def get_startup_mer(cip: comms.Driver) -> str:
    # Gives the full file path, not just the file name
    return get_value(cip, [RegKeys.ME_STARTUP_APP])

def get_startup_options(cip: comms.Driver) -> int:
    # 0 = Go to ME Station, 1 = Run Current Application, 2 = Don't start ME Station
    return int(get_value(cip, [RegKeys.ME_STARTUP_OPTIONS]))

def get_startup_replace_comms(cip: comms.Driver) -> bool:
    # True = Replace terminal communications with *.MER settings, False = don't
    return bool(int(get_value(cip, [RegKeys.ME_STARTUP_REPLACE_COMMS])))

def get_version_major(cip: comms.Driver) -> int:
    # Doesn't always align with ME/Helper versions.
    # For example, v5.10 terminal returned version 3.x
    return int(get_value(cip, [RegKeys.CIP_VERSION_MAJOR]))

def get_version_minor(cip: comms.Driver) -> int:
    # Doesn't always align with ME/Helper versions.
    # For example, v5.10 terminal returned version 3.x
    return int(get_value(cip, [RegKeys.CIP_VERSION_MINOR]))

def get_vendor_id(cip: comms.Driver) -> int:
    return int(get_value(cip, [RegKeys.CIP_VENDOR_ID]))
