from dataclasses import dataclass
import os

from pymeu import types

@dataclass
class METestDevice:
    name: str
    comms_path: str
    device_paths: types.MEDevicePaths
    boot_time_sec: int
    mer_files: list[str]

# Shared paths - computer
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
DOWNLOAD_FOLDER_PATH = os.path.join(BASE_PATH, 'download')
UPLOAD_FOLDER_PATH = os.path.join(BASE_PATH, 'upload')

# Shared paths - terminal
HELPER_FILE_NAME = 'RemoteHelper.DLL'
RUNTIME_PATH = 'Rockwell Software\\RSViewME\\Runtime'
UPLOAD_LIST_PATH = f'{RUNTIME_PATH}\\Results.txt'
NONEXISTENT_FILE = '\\NonexistentPath\\NonexistentFile.ext'
NONEXISTENT_FOLDER = '\\NonexistentPath'

# PanelView Plus v5 configuration
PVP5 = 'PVP5'
PVP5_Device_Paths = types.MEDevicePaths(
    f'\\Storage Card\\Rockwell Software\\RSViewME\\{HELPER_FILE_NAME}',
    '\\Storage Card',
    f'\\Storage Card\\{UPLOAD_LIST_PATH}',
    f'\\Storage Card\\{RUNTIME_PATH}'
)
PVP5_MER_Files = [
    'Test_v5_A.mer',
    'Test_v5_B.mer',
    'Test_v5_C.mer'
]

# PanelView Plus v6 configuration
PVP6 = 'PVP6'
PVP6_Device_Paths = types.MEDevicePaths(
    f'\\Windows\\{HELPER_FILE_NAME}',
    '\\Application Data',
    f'\\Application Data\\{UPLOAD_LIST_PATH}',
    f'\\Application Data\\{RUNTIME_PATH}'
)
PVP6_MER_Files = [
    'Test_v11_A.mer',
    'Test_v11_B.mer',
    'Test_v11_C.mer'
]

DEVICES = [
    METestDevice(
        PVP5, 
        '192.168.40.124',
        PVP5_Device_Paths, 
        75, 
        PVP5_MER_Files
    ),
    METestDevice(
        PVP6, 
        '192.168.40.123',
        PVP6_Device_Paths, 
        75, 
        PVP6_MER_Files
    ),
    METestDevice(
        PVP6, 
        '192.168.40.216,4,192.168.1.20',
        PVP6_Device_Paths, 
        75, 
        PVP6_MER_Files
    )
]

DRIVERS = [
    'pycomm3',
    'pylogix'
]