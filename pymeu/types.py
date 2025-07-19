import os
from dataclasses import dataclass, field
from enum import StrEnum

@dataclass
class CIPIdentity:
    hardware_rev: int
    major_rev: int
    minor_rev: int
    product_code: int
    product_name: str
    product_type: int
    serial_number: str = field(repr=False)
    status: int
    vendor_id: int

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
class MEv5FileListHeader:
    me: str
    size_on_disk: int

@dataclass
class MEv5FileListFiles:
    files: list[str]

@dataclass
class MEv5FileList:
    info: MEv5FileListHeader
    mefiles: MEv5FileListFiles

@dataclass
class MEv5FileManifest:
    local_file: str
    local_path: str
    remote_file: str
    remote_folder: str
    required: bool

@dataclass
class MEFile:
    name: str
    overwrite_requested: bool
    overwrite_required: bool
    path: str

    def get_ext(self) -> str:
        filename, extension = os.path.splitext(self.path)
        return extension.lower()

    def get_size(self) -> int:
        return os.path.getsize(self.path)
    
@dataclass
class MEIdentity:
    helper_version: str
    me_version: str
    major_rev: int
    minor_rev: int
    product_code: int
    product_name: str
    product_type: int
    serial_number: str = field(repr=False)
    vendor_id: int

@dataclass
class MEPaths:
    helper_file: str
    storage: str
    upload_list: str
    runtime: str
    fuwhelper_file: str

@dataclass
class MEDeviceInfo:
    comms_path: str
    cip_identity: CIPIdentity
    me_identity: MEIdentity
    log: list[str]
    files: list[str]
    running_med_file: str
    startup_mer_file: str
    me_paths: MEPaths

@dataclass
class MEResponse(object):
    device: MEDeviceInfo
    status: str

class MEResponseStatus(StrEnum):
    SUCCESS = 'Success'
    FAILURE = 'Failure'