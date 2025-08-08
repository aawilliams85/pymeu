from .. import comms
from ..common.types import CIPMessagePreset

CFFilePreamble = CIPMessagePreset(
    service=int.from_bytes(b'\x51', byteorder='big'),
    class_code=int.from_bytes(b'\xA1', byteorder='big'),
    instance=None,
    attribute=None
)

CFFileChunk = CIPMessagePreset(
    service=int.from_bytes(b'\x52', byteorder='big'),
    class_code=int.from_bytes(b'\xA1', byteorder='big'),
    instance=None,
    attribute=None
)

def dmk_preamble(cip: comms.Driver, instance: int, data):
    return cip.generic_message(
        service=CFFilePreamble.service,
        class_code=CFFilePreamble.class_code,
        instance=instance,
        attribute=CFFilePreamble.attribute,
        request_data=data,
        connected=True
    )

def dmk_chunk(cip: comms.Driver, instance: int, data):
    return cip.generic_message(
        service=CFFileChunk.service,
        class_code=CFFileChunk.class_code,
        instance=instance,
        attribute=CFFileChunk.attribute,
        request_data=data,
        connected=True
    )