import pycomm3

from enum import Enum

# Known CIP class codes that aren't previously defined by pycomm3.
# Further investigation needed.
class CipClasses(Enum):
    FUNCTION = int.from_bytes(b'\x04\xFD', byteorder='big')
    REGISTRY = int.from_bytes(b'\x04\xFE', byteorder='big')
    FILE = int.from_bytes(b'\x04\xFF', byteorder='big')

# Known CIP service codes that aren't previously defined by pycomm3.
# Further investigation needed.
class CipServices(Enum):
    EXECUTE = int.from_bytes(b'\x50', byteorder='big')
    READ_REGISTRY = int.from_bytes(b'\x51', byteorder='big')
    WRITE_FILE = int.from_bytes(b'\x52', byteorder='big')
    READ_FILE = int.from_bytes(b'\x53', byteorder='big')

def create_file_exchange(cip: pycomm3.CIPDriver, data):
    return cip.generic_message(
        service=pycomm3.Services.create,
        class_code=CipClasses.FILE.value,
        instance=0x00,
        request_data=data,
        connected=False,
        route_path=None
    )

def delete_file_exchange(cip: pycomm3.CIPDriver, instance: int):
    return cip.generic_message(
        service=pycomm3.Services.delete,
        class_code=CipClasses.FILE.value,
        instance=instance,
        connected=False,
        route_path=None
    )

def read_file_chunk(cip: pycomm3.CIPDriver, instance: int, data):
    return cip.generic_message(
        service=CipServices.READ_FILE.value,
        class_code=CipClasses.FILE.value,
        instance=instance,
        request_data=data,
        connected=False,
        route_path=None
    )

def read_registry(cip: pycomm3.CIPDriver, data):
    return cip.generic_message(
        service=CipServices.READ_REGISTRY.value,
        class_code=CipClasses.REGISTRY.value,
        instance=0x00,
        request_data=data,
        connected=False,
        route_path=None
    )

def run_function(cip: pycomm3.CIPDriver, data):
    return cip.generic_message(
        service=CipServices.EXECUTE.value,
        class_code=CipClasses.FUNCTION.value,
        instance=0x00,
        request_data=data,
        connected=False,
        route_path=None
    )

def write_file_chunk(cip: pycomm3.CIPDriver, instance: int, data):
    return cip.generic_message(
        service=CipServices.WRITE_FILE.value,
        class_code=CipClasses.FILE.value,
        instance=instance,
        request_data=data,
        connected=False,
        route_path=None
    )

def get_attr_unk(cip: pycomm3.CIPDriver, data):
    return cip.generic_message(
        service=pycomm3.Services.get_attribute_single,
        class_code=CipClasses.FILE.value,
        instance=0x00,
        request_data=data,
        connected=False,
        route_path=None
    )

def set_attr_unk(cip: pycomm3.CIPDriver, data):
    return cip.generic_message(
        service=pycomm3.Services.set_attribute_single,
        class_code=CipClasses.FILE.value,
        instance=0x01,
        request_data=data,
        connected=False,
        route_path=None
    )