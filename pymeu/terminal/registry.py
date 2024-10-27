import pycomm3

from ..messages import *

def get_registry_value(cip: pycomm3.CIPDriver, key: str) -> str:
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
    return get_registry_value(cip, ['HKEY_LOCAL_MACHINE\\SOFTWARE\\Rockwell Software\\RSView Enterprise\\MEVersion'])

def get_product_code(cip: pycomm3.CIPDriver) -> str:
    return get_registry_value(cip, ['HKEY_LOCAL_MACHINE\\SOFTWARE\\Rockwell Software\\RSLinxNG\\CIP Identity\\ProductCode'])

def get_product_type(cip: pycomm3.CIPDriver) -> str:
    return get_registry_value(cip, ['HKEY_LOCAL_MACHINE\\SOFTWARE\\Rockwell Software\\RSLinxNG\\CIP Identity\\ProductType'])

def get_startup_mer(cip: pycomm3.CIPDriver) -> str:
    return get_registry_value(cip, ['HKEY_LOCAL_MACHINE\\SOFTWARE\\Rockwell Software\\RSViewME\\Startup Options\\CurrentApp'])