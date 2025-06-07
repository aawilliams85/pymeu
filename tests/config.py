from dataclasses import dataclass
import os

from pymeu import types

@dataclass
class METestDevice:
    name: str
    comms_path: str
    comms_paths: list[str]
    device_paths: types.MEDevicePaths
    boot_time_sec: int
    mer_files: list[str]

def generate_test_combinations(devices: list[METestDevice], drivers: list[str]) -> list[tuple[METestDevice,str,str]]:
    """
    Generate all device-driver-device_path combinations, ordered to alternate devices.
    Returns a list of (device, driver, device_path) tuples.
    Example order: (device1, driver1, path1), (device2, driver1, path1), 
                  (device1, driver2, path1), (device2, driver2, path1),
                  (device1, driver1, path2), (device2, driver1, path2), ...
    """
    combinations = []
    # Assume all devices have the same number of comms_paths
    if not devices or not devices[0].comms_paths:
        return combinations
    
    for path_idx in range(len(devices[0].comms_paths)):
        for driver in drivers:
            for device in devices:
                combinations.append((device, driver, device.comms_paths[path_idx]))
    
    # Optional: Print combinations for debugging
    #for combo in combinations:
    #    print(f"{combo[0].name}, {combo[1]}, {combo[2]}")
    
    return combinations

# Shared paths - computer
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
DOWNLOAD_FOLDER_PATH = os.path.join(BASE_PATH, 'download')
UPLOAD_FOLDER_PATH = os.path.join(BASE_PATH, 'upload')
FIRMWARE_FOLDER_PATH = os.path.join(BASE_PATH, 'firmware')

# Shared paths - terminal
HELPER_FILE_NAME = 'RemoteHelper.DLL'
RUNTIME_PATH = 'Rockwell Software\\RSViewME\\Runtime'
UPLOAD_LIST_PATH = f'{RUNTIME_PATH}\\Results.txt'
NONEXISTENT_FILE = '\\NonexistentPath\\NonexistentFile.ext'
NONEXISTENT_FOLDER = '\\NonexistentPath'

# PanelView Plus configuration
PVP5 = 'PVP5'
PVP5_Comms_Paths = ['192.168.40.124','192.168.40.104,4,192.168.1.21']
PVP5_Device_Paths = types.MEDevicePaths(
    f'\\Storage Card\\Rockwell Software\\RSViewME\\{HELPER_FILE_NAME}',
    '\\Storage Card',
    f'\\Storage Card\\{UPLOAD_LIST_PATH}',
    f'\\Storage Card\\{RUNTIME_PATH}',
    '\\Storage Card\\FUWhelper.dll'
)
PVP5_MER_Files = [
    'Test_v5_A.mer',
    'Test_v5_B.mer',
    'Test_v5_C.mer'
]

# PanelView Plus 6 configuration
PVP6 = 'PVP6'
PVP6_Comms_Paths = ['192.168.40.123','192.168.40.104,4,192.168.1.20']
PVP6_Device_Paths = types.MEDevicePaths(
    f'\\Windows\\{HELPER_FILE_NAME}',
    '\\Application Data',
    f'\\Application Data\\{UPLOAD_LIST_PATH}',
    f'\\Application Data\\{RUNTIME_PATH}',
    '\\Storage Card\\FUWhelper.dll'
)
PVP6_MER_Files = [
    'Test_v11_A.mer',
    'Test_v11_B.mer',
    'Test_v11_C.mer'
]

# PanelView Plus 7A configuration
PVP7A = 'PVP7A'
PVP7A_Comms_Paths = ['192.168.40.126','192.168.40.104,4,192.168.1.22']
PVP7A_Device_Paths = types.MEDevicePaths(
    f'\\Windows\\{HELPER_FILE_NAME}',
    '\\Application Data',
    f'\\Application Data\\{UPLOAD_LIST_PATH}',
    f'\\Application Data\\{RUNTIME_PATH}',
    '\\Storage Card\\FUWhelper.dll'
)
PVP7A_MER_Files = [
    'Test_v11_A.mer',
    'Test_v11_B.mer',
    'Test_v11_C.mer'
]

DEVICES = [
    METestDevice(
        PVP5, 
        '192.168.40.124',
        PVP5_Comms_Paths,
        PVP5_Device_Paths, 
        75, 
        PVP5_MER_Files
    ),
    METestDevice(
        PVP6, 
        '192.168.40.123',
        PVP6_Comms_Paths,
        PVP6_Device_Paths, 
        75, 
        PVP6_MER_Files
    ),
    METestDevice(
        PVP7A, 
        '192.168.40.126',
        PVP7A_Comms_Paths,
        PVP7A_Device_Paths, 
        75, 
        PVP7A_MER_Files
    ),
]

DRIVERS = [
    'pycomm3',
    'pylogix'
]

test_combinations = generate_test_combinations(DEVICES, DRIVERS)