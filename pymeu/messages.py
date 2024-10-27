from enum import Enum
import pycomm3

# Known CIP class codes that aren't previously defined by pycomm3.
# Further investigation needed.
class CipClasses(Enum):
    function = int.from_bytes(b'\x04\xFD', byteorder='big')
    registry = int.from_bytes(b'\x04\xFE', byteorder='big')
    file = int.from_bytes(b'\x04\xFF', byteorder='big')

# Known CIP service codes that aren't previously defined by pycomm3.
# Further investigation needed.
class CipServices(Enum):
    execute = int.from_bytes(b'\x50', byteorder='big')
    read_registry = int.from_bytes(b'\x51', byteorder='big')
    write_file = int.from_bytes(b'\x52', byteorder='big')
    read_file = int.from_bytes(b'\x53', byteorder='big')

def msg_create_file_exchange(cip: pycomm3.CIPDriver, data):
    return cip.generic_message(
        service=pycomm3.Services.create,
        class_code=CipClasses.file.value,
        instance=0x00,
        request_data=data,
        connected=False,
        route_path=None
    )

def msg_delete_file_exchange(cip: pycomm3.CIPDriver, instance: int):
    return cip.generic_message(
        service=pycomm3.Services.delete,
        class_code=CipClasses.file.value,
        instance=instance,
        connected=False,
        route_path=None
    )

def msg_read_file_chunk(cip: pycomm3.CIPDriver, instance: int, data):
    return cip.generic_message(
        service=CipServices.read_file.value,
        class_code=CipClasses.file.value,
        instance=instance,
        request_data=data,
        connected=False,
        route_path=None
    )

def msg_read_registry(cip: pycomm3.CIPDriver, data):
    return cip.generic_message(
        service=CipServices.read_registry.value,
        class_code=CipClasses.registry.value,
        instance=0x00,
        request_data=data,
        connected=False,
        route_path=None
    )

def msg_run_function(cip: pycomm3.CIPDriver, data):
    return cip.generic_message(
        service=CipServices.execute.value,
        class_code=CipClasses.function.value,
        instance=0x00,
        request_data=data,
        connected=False,
        route_path=None
    )

def msg_write_file_chunk(cip: pycomm3.CIPDriver, instance: int, data):
    return cip.generic_message(
        service=CipServices.write_file.value,
        class_code=CipClasses.file.value,
        instance=instance,
        request_data=data,
        connected=False,
        route_path=None
    )

def msg_get_attr_unk(cip: pycomm3.CIPDriver, data):
    return cip.generic_message(
        service=pycomm3.Services.get_attribute_single,
        class_code=CipClasses.file.value,
        instance=0x00,
        request_data=data,
        connected=False,
        route_path=None
    )

def msg_set_attr_unk(cip: pycomm3.CIPDriver, data):
    return cip.generic_message(
        service=pycomm3.Services.set_attribute_single,
        class_code=CipClasses.file.value,
        instance=0x01,
        request_data=data,
        connected=False,
        route_path=None
    )