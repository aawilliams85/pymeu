import os
from dataclasses import dataclass, field
from enum import StrEnum

from ..common.types import CIPIdentity

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