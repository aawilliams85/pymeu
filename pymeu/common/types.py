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
class CIPMessagePreset:
    service: int
    class_code: int
    instance: int
    attribute: int

class ResponseStatus(StrEnum):
    SUCCESS = 'Success'
    FAILURE = 'Failure'