import pycomm3

def msg_create_file_exchange(cip: pycomm3.CIPDriver, data):
    return cip.generic_message(
        service=pycomm3.Services.create,
        class_code=0x04ff,
        instance=0x00,
        request_data=data,
        connected=False,
        route_path=None
    )

def msg_delete_file_exchange(cip: pycomm3.CIPDriver, instance: int):
    return cip.generic_message(
        service=pycomm3.Services.delete,
        class_code=0x04ff,
        instance=instance,
        connected=False,
        route_path=None
    )

def msg_read_file_chunk(cip: pycomm3.CIPDriver, instance: int, data):
    return cip.generic_message(
        service=0x53,
        class_code=0x04ff,
        instance=instance,
        request_data=data,
        connected=False,
        route_path=None
    )

def msg_read_registry(cip: pycomm3.CIPDriver, data):
    return cip.generic_message(
        service=0x51,
        class_code=0x04fe,
        instance=0x00,
        request_data=data,
        connected=False,
        route_path=None
    )

def msg_run_function(cip: pycomm3.CIPDriver, data):
    return cip.generic_message(
        service=0x50,
        class_code=0x04fd,
        instance=0x00,
        request_data=data,
        connected=False,
        route_path=None
    )

def msg_write_file_chunk(cip: pycomm3.CIPDriver, instance: int, data):
    return cip.generic_message(
        service=0x52,
        class_code=0x04ff,
        instance=instance,
        request_data=data,
        connected=False,
        route_path=None
    )

def msg_get_attr_unk(cip: pycomm3.CIPDriver, data):
    return cip.generic_message(
        service=pycomm3.Services.get_attribute_single,
        class_code=0x04ff,
        instance=0x00,
        request_data=data,
        connected=False,
        route_path=None
    )

def msg_set_attr_unk(cip: pycomm3.CIPDriver, data):
    return cip.generic_message(
        service=pycomm3.Services.set_attribute_single,
        class_code=0x04ff,
        instance=0x01,
        request_data=data,
        connected=False,
        route_path=None
    )
