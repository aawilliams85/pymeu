import pycomm3

from enum import IntEnum

# Known CIP class codes that aren't previously defined by pycomm3.
# Further investigation needed.
class CipClasses(IntEnum):
    FUNCTION = int.from_bytes(b'\x04\xFD', byteorder='big')
    REGISTRY = int.from_bytes(b'\x04\xFE', byteorder='big')
    FILE = int.from_bytes(b'\x04\xFF', byteorder='big')

# Known CIP service codes that aren't previously defined by pycomm3.
# Further investigation needed.
class CipServices(IntEnum):
    EXECUTE = int.from_bytes(b'\x50', byteorder='big')
    READ_REGISTRY = int.from_bytes(b'\x51', byteorder='big')
    WRITE_FILE = int.from_bytes(b'\x52', byteorder='big')
    READ_FILE = int.from_bytes(b'\x53', byteorder='big')

def create_transfer_instance(cip: pycomm3.CIPDriver, data):
    return cip.generic_message(
        service=pycomm3.Services.create,
        class_code=CipClasses.FILE,
        instance=0x00,
        request_data=data,
        connected=False,
        route_path=None
    )

def delete_transfer_instance(cip: pycomm3.CIPDriver, transfer_instance: int):
    return cip.generic_message(
        service=pycomm3.Services.delete,
        class_code=CipClasses.FILE,
        instance=transfer_instance,
        connected=False,
        route_path=None
    )

def read_file_chunk(cip: pycomm3.CIPDriver, transfer_instance: int, data):
    return cip.generic_message(
        service=CipServices.READ_FILE,
        class_code=CipClasses.FILE,
        instance=transfer_instance,
        request_data=data,
        connected=False,
        route_path=None
    )

def read_registry(cip: pycomm3.CIPDriver, data):
    return cip.generic_message(
        service=CipServices.READ_REGISTRY,
        class_code=CipClasses.REGISTRY,
        instance=0x00,
        request_data=data,
        connected=False,
        route_path=None
    )

def run_function(cip: pycomm3.CIPDriver, data):
    return cip.generic_message(
        service=CipServices.EXECUTE,
        class_code=CipClasses.FUNCTION,
        instance=0x00,
        request_data=data,
        connected=False,
        route_path=None
    )

def write_file_chunk(cip: pycomm3.CIPDriver, transfer_instance: int, data):
    return cip.generic_message(
        service=CipServices.WRITE_FILE,
        class_code=CipClasses.FILE,
        instance=transfer_instance,
        request_data=data,
        connected=False,
        route_path=None
    )

def get_attr_unk(cip: pycomm3.CIPDriver, data):
    return cip.generic_message(
        service=pycomm3.Services.get_attribute_single,
        class_code=CipClasses.FILE,
        instance=0x00,
        request_data=data,
        connected=False,
        route_path=None
    )

def set_attr_unk(cip: pycomm3.CIPDriver, data):
    return cip.generic_message(
        service=pycomm3.Services.set_attribute_single,
        class_code=CipClasses.FILE,
        instance=0x01,
        request_data=data,
        connected=False,
        route_path=None
    )