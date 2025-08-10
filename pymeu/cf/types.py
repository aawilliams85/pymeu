from dataclasses import dataclass, field

from ..common.types import CIPIdentity, ResponseStatus

@dataclass
class DMKContentHeader:
    dmk_type: str
    family_name: str
    revision: str
    number_catalogs: int

@dataclass
class DMKContentCatalog:
    catalog: str
    revision: str
    vendor_id: int
    vendor_id_mask: int
    product_type: int
    product_type_mask: int
    product_code: int
    product_code_mask: int
    device_instance: int
    disable_sub_minor: int
    driver_name: str

@dataclass
class DMKContentFile:
    header: DMKContentHeader
    catalogs: list[DMKContentCatalog]

@dataclass
class DMKNvsHeader:
    description: str
    programming_protocol: str
    disable_sub_minor: int
    new_revision: str
    number_updates: int
    connection_type: str
    max_power_up_seconds: int
    number_identities: int
    family_name: str
    release_notes_file_name: str

@dataclass
class DMKNvsUpdate:
    nvs_instance: int
    major_revision: int
    minor_revision: int
    tftp_timeout_seconds: int
    max_timeout_seconds: int
    starting_location: int
    file_size: int
    data_file_name: str
    rename_data_file: str
    update_reset: int
    auto_reset_on_error: int
    first_transfer_delay: int
    last_transfer_delay: int
    error_instructions: str

@dataclass
class DMKNvsFile:
    header: DMKNvsHeader
    updates: list[DMKNvsUpdate]

@dataclass
class DMKFile:
    content: DMKContentFile
    nvs: DMKNvsFile

@dataclass
class CFDeviceInfo:
    comms_path: str
    cip_identity: CIPIdentity
    log: list[str]

@dataclass
class CFResponse(object):
    device: CFDeviceInfo
    status: str