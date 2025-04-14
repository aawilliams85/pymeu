
from enum import Enum
from . import comms

# Known CIP class codes that aren't previously defined by pycomm3.
# Further investigation needed.
class CipClasses(Enum):
    FUNCTION = int.from_bytes(b'\x04\xFD', byteorder='big')
    REGISTRY = int.from_bytes(b'\x04\xFE', byteorder='big')
    FILE = int.from_bytes(b'\x04\xFF', byteorder='big')

# Known CIP service codes that aren't previously defined by pycomm3.
# Further investigation needed.
class CipServices(Enum):
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
        service=CipServices.CREATE.value,
        class_code=CipClasses.FILE,
        instance=0x00,
        request_data=data,
        connected=False,
        route_path=None
    )

def delete_transfer_instance(cip: comms.Driver, transfer_instance: int):
    return cip.generic_message(
        service=CipServices.DELETE.value,
        class_code=CipClasses.FILE,
        instance=transfer_instance,
        connected=False,
        route_path=None
    )

def read_file_chunk(cip: comms.Driver, transfer_instance: int, data):
    return cip.generic_message(
        service=CipServices.READ_FILE,
        class_code=CipClasses.FILE,
        instance=transfer_instance,
        request_data=data,
        connected=False,
        route_path=None
    )

def read_registry(cip: comms.Driver, data):
    return cip.generic_message(
        service=CipServices.READ_REGISTRY,
        class_code=CipClasses.REGISTRY,
        instance=0x00,
        request_data=data,
        connected=False,
        route_path=None
    )

def run_function(cip: comms.Driver, data):
    return cip.generic_message(
        service=CipServices.EXECUTE,
        class_code=CipClasses.FUNCTION,
        instance=0x00,
        request_data=data,
        connected=False,
        route_path=None
    )

def write_file_chunk(cip: comms.Driver, transfer_instance: int, data):
    return cip.generic_message(
        service=CipServices.WRITE_FILE,
        class_code=CipClasses.FILE,
        instance=transfer_instance,
        request_data=data,
        connected=False,
        route_path=None
    )

def get_attr_unk(cip: comms.Driver, data):
    return cip.generic_message(
        service=CipServices.GET_ATTRIBUTE_SINGLE.value,
        class_code=CipClasses.FILE,
        instance=0x00,
        request_data=data,
        connected=False,
        route_path=None
    )

def set_attr_unk(cip: comms.Driver, data):
    return cip.generic_message(
        service=CipServices.SET_ATTRIBUTE_SINGLE.value,
        class_code=CipClasses.FILE,
        instance=0x01,
        request_data=data,
        connected=False,
        route_path=None
    )