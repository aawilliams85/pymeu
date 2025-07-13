from dataclasses import dataclass
import os

from pymeu import types

@dataclass
class METestDevice:
    name: str
    comms_paths: list[str]
    device_paths: types.MEPaths
    boot_time_sec: int
    mer_files: list[str]
    local_firmware_helper_path: str
    local_firmware_image_paths: list[str]

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

def progress_callback(description: str, total_bytes: int, current_bytes: int):
    progress = 100* current_bytes / total_bytes
    print(f"{description} progress: {progress:.2f}% complete, {current_bytes} of {total_bytes} bytes.")

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
MERUNTIME_PROCESS = 'MERuntime.exe'
NONEXISTENT_PROCESS = 'NonexistentProcess.exe'

# PanelView Plus configuration
PVP5 = 'PVP5'
PVP5_Comms_Paths = ['192.168.40.20','192.168.40.11,bp,3,enet,192.168.1.20']
PVP5_Device_Paths = types.MEPaths(
    f'\\Storage Card\\Rockwell Software\\RSViewME\\{HELPER_FILE_NAME}',
    '\\Storage Card',
    f'\\Storage Card\\{UPLOAD_LIST_PATH}',
    f'\\Storage Card\\{RUNTIME_PATH}',
    '\\Storage Card\\FUWhelper.dll'
)
PVP5_Local_Firmware_Helper_Path = os.path.join(FIRMWARE_FOLDER_PATH, 'Helper', 'v15', 'FUWhelper4xX.dll')
PVP5_Local_Firmware_Image_Paths = [
    os.path.join(FIRMWARE_FOLDER_PATH, 'FUC', 'PVP5', 'ME_PVP4xX_5.10.16.09')
]
PVP5_MER_Files = [
    'Test_v5_A.mer',
    'Test_v5_B.mer',
    'Test_v5_C.mer'
]

# PanelView Plus 6 configuration
PVP6 = 'PVP6'
PVP6_Comms_Paths = ['192.168.40.21','192.168.40.11,bp,3,enet,192.168.1.21']
PVP6_Device_Paths = types.MEPaths(
    f'\\Windows\\{HELPER_FILE_NAME}',
    '\\Application Data',
    f'\\Application Data\\{UPLOAD_LIST_PATH}',
    f'\\Application Data\\{RUNTIME_PATH}',
    '\\Storage Card\\FUWhelper.dll'
)
PVP6_Local_Firmware_Helper_Path = os.path.join(FIRMWARE_FOLDER_PATH, 'Helper', 'v15', 'FUWhelper6xX.dll')
PVP6_Local_Firmware_Image_Paths = [
    os.path.join(FIRMWARE_FOLDER_PATH, 'FUC', 'PVP6', 'ME_PVP6xX_11.00-20190915', 'upgrade', 'SC.IMG'),
    os.path.join(FIRMWARE_FOLDER_PATH, 'FUC', 'PVP6', 'ME_PVP6xX_12.00-20200922', 'upgrade', 'SC.IMG'),
]
PVP6_MER_Files = [
    'Test_v11_A.mer',
    'Test_v11_B.mer',
    'Test_v11_C.mer'
]

# PanelView Plus 7A configuration
PVP7A = 'PVP7A'
PVP7A_Comms_Paths = ['192.168.40.22','192.168.40.11,bp,3,enet,192.168.1.22']
PVP7A_Device_Paths = types.MEPaths(
    f'\\Windows\\{HELPER_FILE_NAME}',
    '\\Application Data',
    f'\\Application Data\\{UPLOAD_LIST_PATH}',
    f'\\Application Data\\{RUNTIME_PATH}',
    '\\Storage Card\\FUWhelper.dll'
)
PVP7A_Local_Firmware_Helper_Path = os.path.join(FIRMWARE_FOLDER_PATH, 'Helper', 'v15', 'FUWhelper6xX.dll')
PVP7A_Local_Firmware_Image_Paths = [
    os.path.join(FIRMWARE_FOLDER_PATH, 'FUC', 'PVP7A', 'ME_PVP7xX_11.00-20190916', 'upgrade', 'SC.IMG'),
    os.path.join(FIRMWARE_FOLDER_PATH, 'FUC', 'PVP7A', 'ME_PVP7xX_15.00-20240926', 'upgrade', 'SC.IMG'),
]
PVP7A_MER_Files = [
    'Test_v11_A.mer',
    'Test_v11_B.mer',
    'Test_v11_C.mer'
]

#PanelView Plus 7B configuration
PVP7B = 'PVP7B'
#PVP7B_Comms_Paths = ['192.168.40.23','192.168.40.11,bp,3,enet,192.168.1.23']
PVP7B_Comms_Paths = ['192.168.1.23', '192.168.1.23']
PVP7B_Device_Paths = types.MEPaths(
    f'\\Windows\\{HELPER_FILE_NAME}',
    '\\Application Data',
    f'\\Application Data\\{UPLOAD_LIST_PATH}',
    f'\\Application Data\\{RUNTIME_PATH}',
    '\\Storage Card\\FUWhelper.dll'
)
PVP7B_Local_Firmware_Image_Paths = [
    os.path.join(FIRMWARE_FOLDER_PATH, 'DMK', 'PVP7B', '2711P-PanelView_Plus_7_Performance_15.100.dmk')
]
PVP7B_MER_Files = [
    'Test_v11_A.mer',
    'Test_v11_B.mer',
    'Test_v11_C.mer'
]

DEVICE_PVP5 = METestDevice(
    PVP5, 
    PVP5_Comms_Paths,
    PVP5_Device_Paths, 
    75, 
    PVP5_MER_Files,
    PVP5_Local_Firmware_Helper_Path,
    PVP5_Local_Firmware_Image_Paths)

DEVICE_PVP6 = METestDevice(
    PVP6, 
    PVP6_Comms_Paths,
    PVP6_Device_Paths, 
    75, 
    PVP6_MER_Files,
    PVP6_Local_Firmware_Helper_Path,
    PVP6_Local_Firmware_Image_Paths)

DEVICE_PVP7A = METestDevice(
    PVP7A, 
    PVP7A_Comms_Paths,
    PVP7A_Device_Paths, 
    75, 
    PVP7A_MER_Files,
    PVP7A_Local_Firmware_Helper_Path,
    PVP7A_Local_Firmware_Image_Paths)

DEVICE_PVP7B = METestDevice(
    PVP7B, 
    PVP7B_Comms_Paths,
    PVP7B_Device_Paths, 
    75, 
    PVP7B_MER_Files,
    '',
    PVP7B_Local_Firmware_Image_Paths)

DEVICES = [
    DEVICE_PVP5,
    DEVICE_PVP6,
    DEVICE_PVP7A,
    #DEVICE_PVP7B    
]

DRIVER_PYCOMM3 = 'pycomm3'
DRIVER_PYLOGIX = 'pylogix'
DRIVERS = [
    DRIVER_PYCOMM3,
    DRIVER_PYLOGIX
]

test_combinations = generate_test_combinations(DEVICES, DRIVERS)