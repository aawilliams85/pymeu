from .. import comms
from ..common.types import CIPMessagePreset

MECreateTransfer = CIPMessagePreset(
    service=int.from_bytes(b'\x08', byteorder='big'),
    class_code=int.from_bytes(b'\x04\xFF', byteorder='big'),
    instance=0x00,
    attribute=None
)

MEDeleteTransfer = CIPMessagePreset(
    service=int.from_bytes(b'\x09', byteorder='big'),
    class_code=int.from_bytes(b'\x04\xFF', byteorder='big'),
    instance=None,
    attribute=None
)

MEReadFileChunk = CIPMessagePreset(
    service=int.from_bytes(b'\x53', byteorder='big'),
    class_code=int.from_bytes(b'\x04\xFF', byteorder='big'),
    instance=None,
    attribute=None
)

MEReadFileReady = CIPMessagePreset(
    service=int.from_bytes(b'\x0e', byteorder='big'),
    class_code=int.from_bytes(b'\x04\xFF', byteorder='big'),
    instance=0x00,
    attribute=None
)

MEReadRegistry = CIPMessagePreset(
    service=int.from_bytes(b'\x51', byteorder='big'),
    class_code=int.from_bytes(b'\x04\xFE', byteorder='big'),
    instance=0x00,
    attribute=None
)

MERunFunction = CIPMessagePreset(
    service=int.from_bytes(b'\x50', byteorder='big'),
    class_code=int.from_bytes(b'\x04\xFD', byteorder='big'),
    instance=0x00,
    attribute=None
)

MEWriteFileChunk = CIPMessagePreset(
    service=int.from_bytes(b'\x52', byteorder='big'),
    class_code=int.from_bytes(b'\x04\xFF', byteorder='big'),
    instance=None,
    attribute=None
)

MEWriteFileReady = CIPMessagePreset(
    service=int.from_bytes(b'\x10', byteorder='big'),
    class_code=int.from_bytes(b'\x04\xFF', byteorder='big'),
    instance=0x01,
    attribute=None
)

def create_transfer(cip: comms.Driver, data):
    return cip.generic_message(
        service=MECreateTransfer.service,
        class_code=MECreateTransfer.class_code,
        instance=MECreateTransfer.instance,
        attribute=MECreateTransfer.attribute,
        request_data=data
    )

def delete_transfer(cip: comms.Driver, instance: int):
    return cip.generic_message(
        service=MEDeleteTransfer.service,
        class_code=MEDeleteTransfer.class_code,
        instance=instance,
        attribute=MEDeleteTransfer.attribute
    )

def read_file_chunk(cip: comms.Driver, instance: int, data):
    return cip.generic_message(
        service=MEReadFileChunk.service,
        class_code=MEReadFileChunk.class_code,
        instance=instance,
        attribute=MEReadFileChunk.attribute,
        request_data=data
    )

def read_registry(cip: comms.Driver, data):
    return cip.generic_message(
        service=MEReadRegistry.service,
        class_code=MEReadRegistry.class_code,
        instance=MEReadRegistry.instance,
        attribute=MEReadRegistry.attribute,
        request_data=data
    )

def run_function(cip: comms.Driver, data):
    return cip.generic_message(
        service=MERunFunction.service,
        class_code=MERunFunction.class_code,
        instance=MERunFunction.instance,
        attribute=MERunFunction.attribute,
        request_data=data
    )

def write_file_chunk(cip: comms.Driver, instance: int, data):
    return cip.generic_message(
        service=MEWriteFileChunk.service,
        class_code=MEWriteFileChunk.class_code,
        instance=instance,
        attribute=MEWriteFileChunk.instance,
        request_data=data
    )

def read_file_ready(cip: comms.Driver, data):
    return cip.generic_message(
        service=MEReadFileReady.service,
        class_code=MEReadFileReady.class_code,
        instance=MEReadFileReady.instance,
        attribute=MEReadFileReady.attribute,
        request_data=data
    )

def write_file_ready(cip: comms.Driver, data):
    return cip.generic_message(
        service=MEWriteFileReady.service,
        class_code=MEWriteFileReady.class_code,
        instance=MEWriteFileReady.instance,
        attribute=MEWriteFileReady.attribute,
        request_data=data
    )