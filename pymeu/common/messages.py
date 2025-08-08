from .. import comms
from .types import CIPMessagePreset

CIPGetHardwareRev = CIPMessagePreset(
    service=0x0e,
    class_code=0x01,
    instance=0x01,
    attribute=101
)

def get_identity(cip: comms.Driver):
    return cip.generic_message(
        service=0x01,
        class_code=0x01,
        instance=0x01,
        attribute=None
    )

def get_hardware_rev(cip: comms.Driver):
    return cip.generic_message(
        service=CIPGetHardwareRev.service,
        class_code=CIPGetHardwareRev.class_code,
        instance=CIPGetHardwareRev.instance,
        attribute=CIPGetHardwareRev.attribute,
    )

def reset(cip: comms.Driver, data):
    return cip.generic_message(
        service=0x05,
        class_code=0x01,
        instance=0x01,
        attribute=None,
        request_data=data
    )