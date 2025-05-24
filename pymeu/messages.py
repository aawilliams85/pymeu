
from enum import IntEnum
from . import comms

class CipClasses(IntEnum):
    FUNCTION = int.from_bytes(b'\x04\xFD', byteorder='big')
    REGISTRY = int.from_bytes(b'\x04\xFE', byteorder='big')
    FILE = int.from_bytes(b'\x04\xFF', byteorder='big')

class CipServices(IntEnum):
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
        service=CipServices.CREATE,
        class_code=CipClasses.FILE,
        instance=0x00,
        request_data=data
    )

def delete_transfer_instance(cip: comms.Driver, transfer_instance: int):
    return cip.generic_message(
        service=CipServices.DELETE,
        class_code=CipClasses.FILE,
        instance=transfer_instance
    )

def read_file_chunk(cip: comms.Driver, transfer_instance: int, data):
    return cip.generic_message(
        service=CipServices.READ_FILE,
        class_code=CipClasses.FILE,
        instance=transfer_instance,
        request_data=data
    )

def read_registry(cip: comms.Driver, data):
    return cip.generic_message(
        service=CipServices.READ_REGISTRY,
        class_code=CipClasses.REGISTRY,
        instance=0x00,
        request_data=data
    )

def run_function(cip: comms.Driver, data):
    return cip.generic_message(
        service=CipServices.EXECUTE,
        class_code=CipClasses.FUNCTION,
        instance=0x00,
        request_data=data
    )

def write_file_chunk(cip: comms.Driver, transfer_instance: int, data):
    return cip.generic_message(
        service=CipServices.WRITE_FILE,
        class_code=CipClasses.FILE,
        instance=transfer_instance,
        request_data=data
    )

def get_attr_unk(cip: comms.Driver, data):
    return cip.generic_message(
        service=CipServices.GET_ATTRIBUTE_SINGLE,
        class_code=CipClasses.FILE,
        instance=0x00,
        request_data=data
    )

def set_attr_unk(cip: comms.Driver, data):
    return cip.generic_message(
        service=CipServices.SET_ATTRIBUTE_SINGLE,
        class_code=CipClasses.FILE,
        instance=0x01,
        request_data=data
    )