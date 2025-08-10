import struct

from .. import comms
from . import messages
from . import types

def get_cip_identity(cip: comms.Driver) -> types.CIPIdentity:
    resp1 = messages.get_identity(cip)
    vendor_id, product_type, product_code, major_rev, minor_rev, status, serial_number, product_name_length = struct.unpack('<HHHBBHLB', resp1.value[:15])
    product_name = resp1.value[15:15 + product_name_length].decode('utf-8', errors='ignore')
    serial_number_str = f'{serial_number:08x}'

    try:
        resp2 = messages.get_hardware_rev(cip)
        hardware_rev = struct.unpack('<H', resp2.value)[0]
    except:
        hardware_rev = None

    return types.CIPIdentity(
        hardware_rev=hardware_rev,
        major_rev=major_rev,
        minor_rev=minor_rev,
        product_code=product_code,
        product_name=product_name,
        product_type=product_type,
        serial_number=serial_number_str,
        status=status,
        vendor_id=vendor_id
    )