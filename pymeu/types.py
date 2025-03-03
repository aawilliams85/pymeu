import os
from dataclasses import dataclass
from enum import StrEnum

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
class MEDevicePaths:
    helper_file: str
    storage: str
    upload_list: str

@dataclass
class MEDeviceInfo:
    comms_path: str
    helper_version: str
    me_version: str
    version_major: int
    version_minor: int
    product_code: int
    product_name: str
    product_type: int
    log: list[str]
    files: list[str]
    running_med_file: str
    startup_mer_file: str
    paths: MEDevicePaths

@dataclass
class MEResponse(object):
    device: MEDeviceInfo
    status: str

class MEResponseStatus(StrEnum):
    SUCCESS = 'Success'
    FAILURE = 'Failure'