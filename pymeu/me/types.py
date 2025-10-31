import os
from dataclasses import dataclass, field

from ..common.types import CIPIdentity, ResponseStatus

@dataclass
class MEArchive:
    name: str
    data: bytearray
    path: list[str]
    size: int

@dataclass
class MEBinStream:
    data: bytes
    offset: int

@dataclass
class MEFupUpgradeInfVersion:
    plat: int
    os: str
    me: str
    kep: str
    minos: str
    maxos: str
    ard: int

@dataclass
class MEFupUpgradeInfCard:
    files: list[tuple[str, str]]
    ram_size_bytes: int
    storage_size_bytes: int
    fp_size: int

@dataclass
class MEFupUpgradeInf:
    version: MEFupUpgradeInfVersion
    fwc: MEFupUpgradeInfCard
    otw: MEFupUpgradeInfCard
    drivers: list[tuple[str, int]]
    ce: list[tuple[str, str]]

@dataclass
class MEFupMEFileListInfInfo:
    me: str
    size_on_disk_bytes: int

@dataclass
class MEFupMEFileListInf:
    info: MEFupMEFileListInfInfo
    mefiles: list[str]
    
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
class MERecipePlusDataSet:
    name: str
    value: list[float | str]

@dataclass
class MERecipePlusIngredient:
    name: str
    type: str
    min: float
    max: float
    precision: int

@dataclass
class MERecipePlusTagSet:
    name: str
    value: list[str]

@dataclass
class MERecipePlusUnit:
    name: str
    data_set: str
    tag_set: str

@dataclass
class MERecipePlusFile:
    runtime_recipe_name: str
    status_tag: str
    percent_complete_tag: str
    runtime_recipe_name_tag: str
    ingredients: list[MERecipePlusIngredient]
    data_sets: list[MERecipePlusDataSet]
    tag_sets: list[MERecipePlusTagSet]
    units: list[MERecipePlusUnit]

@dataclass
class MEResponse(object):
    device: MEDeviceInfo
    status: str