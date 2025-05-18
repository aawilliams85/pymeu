from dataclasses import dataclass

from pymeu import types

@dataclass
class METestDevice:
    name: str
    comms_path: str
    device_paths: types.MEDevicePaths

# Shared paths
HELPER_FILE_NAME = 'RemoteHelper.DLL'
UPLOAD_LIST_PATH = 'Rockwell Software\\RSViewME\\Runtime\\Results.txt'

# PanelView Plus v5 configuration
PVP5 = 'PVP5'
PVP5_Device_Paths = types.MEDevicePaths(
    f'\\Storage Card\\Rockwell Software\\RSViewME\\{HELPER_FILE_NAME}',
    '\\Storage Card',
    f'\\Storage Card\\{UPLOAD_LIST_PATH}'
)

# PanelView Plus v6 configuration
PVP6 = 'PVP6'
PVP6_Device_Paths = types.MEDevicePaths(
    f'\\Windows\\{HELPER_FILE_NAME}',
    '\\Application Data',
    f'\\Application Data\\{UPLOAD_LIST_PATH}'
)

DEVICES = [
    METestDevice(PVP5, '192.168.40.124', PVP5_Device_Paths),
    METestDevice(PVP6, '192.168.40.123', PVP6_Device_Paths)
]

DRIVERS = [
    'pycomm3', 
    'pylogix'
]