import pycomm3

from enum import StrEnum
from .. import messages

# Known registry keys on the terminal that should be whitelisted for read access through RemoteHelper.
class RegKeys(StrEnum):
    CIP_VERSION_MAJOR = 'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\MajorRevision'                 # ex: 11
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
    """
    Gets a registry key's value from the remote terminal.

    Args:
        cip (pycomm3.CIPDriver): CIPDriver to communicate with the terminal
        key (str): The registry key to read.

    Returns:
        str: The registry value.

    Raises:
        Exception: If the message response code is not zero, indicating an error.

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
    """
    req_data = b''.join(arg.encode() + b'\x00' for arg in key)

    resp = messages.read_registry(cip, req_data)
    if not resp: raise Exception(f'Failed to read registry key: {key}')
    resp_code = int.from_bytes(resp.value[:4], byteorder='little', signed=False)
    if (resp_code != 0): raise Exception(f'Failed to read registry key: {key}, response code: {resp_code}.')

    resp_unk1 = int.from_bytes(resp.value[4:8], byteorder='little', signed=False)
    resp_value = str(resp.value[8:].decode('utf-8').strip('\x00'))
    return resp_value

def get_me_version(cip: pycomm3.CIPDriver) -> str:
    """
    Gets the ME Version on the remote terminal.

    Args:
        cip (pycomm3.CIPDriver): CIPDriver to communicate with the terminal

    Returns:
        str: ME Version string
    """
    return get_value(cip, [RegKeys.ME_VERSION])

def get_product_code(cip: pycomm3.CIPDriver) -> int:
    """
    Gets the product code on the remote terminal.

    Args:
        cip (pycomm3.CIPDriver): CIPDriver to communicate with the terminal

    Returns:
        int: Product Code value
    """
    return int(get_value(cip, [RegKeys.CIP_PRODUCT_CODE]))

def get_product_type(cip: pycomm3.CIPDriver) -> int:
    """
    Gets the product type on the remote terminal.

    Args:
        cip (pycomm3.CIPDriver): CIPDriver to communicate with the terminal

    Returns:
        int: Product Type value
    """
    return int(get_value(cip, [RegKeys.CIP_PRODUCT_TYPE]))

def get_startup_delete_logs(cip: pycomm3.CIPDriver) -> bool:
    """
    Gets the startup setting for Delete Logs on the remote terminal.

    Args:
        cip (pycomm3.CIPDriver): CIPDriver to communicate with the terminal

    Returns:
        bool: Don't (FALSE) or do (TRUE) delete log files at startup.
    """
    return bool(int(get_value(cip, [RegKeys.ME_STARTUP_DELETE_LOGS])))

def get_startup_load_current(cip: pycomm3.CIPDriver) -> bool:
    """
    Gets the startup setting for Load Current Application on the remote terminal.

    Args:
        cip (pycomm3.CIPDriver): CIPDriver to communicate with the terminal

    Returns:
        bool: Don't (FALSE) or do (TRUE) load the *.MER at startup.
    """
    return bool(int(get_value(cip, [RegKeys.ME_STARTUP_LOAD_CURRENT])))

def get_startup_mer(cip: pycomm3.CIPDriver) -> str:
    """
    Gets the *.MER file to load at startup on the remote terminal.

    Args:
        cip (pycomm3.CIPDriver): CIPDriver to communicate with the terminal

    Returns:
        str: Path to *.MER file.
    """
    return get_value(cip, [RegKeys.ME_STARTUP_APP])

def get_startup_options(cip: pycomm3.CIPDriver) -> int:
    """
    Gets the setting for On Startup on the remote terminal.

    Args:
        cip (pycomm3.CIPDriver): CIPDriver to communicate with the terminal

    Returns:
        int: At startup, 0 = Go to ME Station, 1 = Run Current Application,
        2 = Don't start ME Station      
    """
    return int(get_value(cip, [RegKeys.ME_STARTUP_OPTIONS]))

def get_startup_replace_comms(cip: pycomm3.CIPDriver) -> bool:
    """
    Gets the startup setting for Replace Communications on the remote terminal.

    Args:
        cip (pycomm3.CIPDriver): CIPDriver to communicate with the terminal

    Returns:
        bool: Don't (FALSE) or do (TRUE) replace terminal communications with *.MER
        communications settings at startup.
    """
    return bool(int(get_value(cip, [RegKeys.ME_STARTUP_REPLACE_COMMS])))

def get_version_major(cip: pycomm3.CIPDriver) -> int:
    """
    Gets the CIP Major Version from the remote terminal.

    Args:
        cip (pycomm3.CIPDriver): CIPDriver to communicate with the terminal

    Returns:
        int: The major version.

    Note:
        May not always align with the ME Version / Helper Version.
        For example, a v5.10 PanelView returned version 3.x.
    """
    return int(get_value(cip, [RegKeys.CIP_VERSION_MAJOR]))

def get_version_minor(cip: pycomm3.CIPDriver) -> int:
    """
    Gets the CIP Minor Version from the remote terminal.

    Args:
        cip (pycomm3.CIPDriver): CIPDriver to communicate with the terminal

    Returns:
        int: The minor version.

    Note:
        May not always align with the ME Version / Helper Version.
        For example, a v5.10 PanelView returned version 3.x.
    """
    return int(get_value(cip, [RegKeys.CIP_VERSION_MINOR]))
