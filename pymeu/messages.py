
from enum import IntEnum
from . import comms

class DMKClasses(IntEnum):
    FIRMWARE_FLASH = int.from_bytes(b'\xA1', byteorder='big')

class DMKServices(IntEnum):
    FIRMWARE_PREAMBLE = int.from_bytes(b'\x51', byteorder='big')
    FIRMWARE_CHUNK = int.from_bytes(b'\x52', byteorder='big')

class MEClasses(IntEnum):
    FUNCTION = int.from_bytes(b'\x04\xFD', byteorder='big')
    REGISTRY = int.from_bytes(b'\x04\xFE', byteorder='big')
    FILE = int.from_bytes(b'\x04\xFF', byteorder='big')

class MEServices(IntEnum):
    CREATE = int.from_bytes(b'\x08', byteorder='big')
    DELETE = int.from_bytes(b'\x09', byteorder='big')
    GET_ATTRIBUTE_SINGLE = int.from_bytes(b'\x0e', byteorder='big')
    SET_ATTRIBUTE_SINGLE = int.from_bytes(b'\x10', byteorder='big')
    EXECUTE = int.from_bytes(b'\x50', byteorder='big')
    READ_REGISTRY = int.from_bytes(b'\x51', byteorder='big')
    WRITE_FILE = int.from_bytes(b'\x52', byteorder='big')
    READ_FILE = int.from_bytes(b'\x53', byteorder='big')

def create_transfer_instance(cip: comms.Driver, data):
    return cip.generic_message(
        service=MEServices.CREATE,
        class_code=MEClasses.FILE,
        instance=0x00,
        attribute=None,
        request_data=data
    )

def delete_transfer_instance(cip: comms.Driver, transfer_instance: int):
    return cip.generic_message(
        service=MEServices.DELETE,
        class_code=MEClasses.FILE,
        instance=transfer_instance,
        attribute=None
    )

def dmk_preamble(cip: comms.Driver, data):
    return cip.generic_message(
        service=DMKServices.FIRMWARE_PREAMBLE,
        class_code=DMKClasses.FIRMWARE_FLASH,
        instance=0x01,
        attribute=None,
        request_data=data,
        connected=True
    )

def dmk_chunk(cip: comms.Driver, data):
    return cip.generic_message(
        service=DMKServices.FIRMWARE_CHUNK,
        class_code=DMKClasses.FIRMWARE_FLASH,
        instance=0x01,
        attribute=None,
        request_data=data,
        connected=True
    )

def get_identity(cip: comms.Driver):
    return cip.generic_message(
        service=0x01,
        class_code=0x01,
        instance=0x01,
        attribute=None
    )

def read_file_chunk(cip: comms.Driver, transfer_instance: int, data):
    return cip.generic_message(
        service=MEServices.READ_FILE,
        class_code=MEClasses.FILE,
        instance=transfer_instance,
        attribute=None,
        request_data=data
    )

def read_registry(cip: comms.Driver, data):
    return cip.generic_message(
        service=MEServices.READ_REGISTRY,
        class_code=MEClasses.REGISTRY,
        instance=0x00,
        attribute=None,
        request_data=data
    )

def run_function(cip: comms.Driver, data):
    return cip.generic_message(
        service=MEServices.EXECUTE,
        class_code=MEClasses.FUNCTION,
        instance=0x00,
        attribute=None,
        request_data=data
    )

def write_file_chunk(cip: comms.Driver, transfer_instance: int, data):
    return cip.generic_message(
        service=MEServices.WRITE_FILE,
        class_code=MEClasses.FILE,
        instance=transfer_instance,
        attribute=None,
        request_data=data
    )

def get_attr_unk(cip: comms.Driver, data):
    return cip.generic_message(
        service=MEServices.GET_ATTRIBUTE_SINGLE,
        class_code=MEClasses.FILE,
        instance=0x00,
        attribute=None,
        request_data=data
    )

def set_attr_unk(cip: comms.Driver, data):
    return cip.generic_message(
        service=MEServices.SET_ATTRIBUTE_SINGLE,
        class_code=MEClasses.FILE,
        instance=0x01,
        attribute=None,
        request_data=data
    )