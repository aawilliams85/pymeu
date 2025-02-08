import os
from dataclasses import dataclass

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

@dataclass
class MEResponse(object):
    device: MEDeviceInfo
    status: str