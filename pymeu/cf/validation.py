from .. import comms
from ..common.validation import get_cip_identity

from . import types 

def get_device_info(cip: comms.Driver) -> types.CFDeviceInfo:
    cip_identity = get_cip_identity(cip)        
    return types.CFDeviceInfo(
        comms_path=cip._original_path,
        cip_identity=cip_identity,
        log=[]
    )