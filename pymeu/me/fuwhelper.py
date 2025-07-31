from enum import StrEnum

from .. import comms
from . import helper
from . import types

# Known static value for successful creation of a folder.
# Further investigation needed.
CREATE_DIR_SUCCESS = 0

# Known functions available from FuwHelper.
class FuwHelperFunctions(StrEnum):
    CLEAR_FOLDER = 'ClearRemDirectory', # Args: {Folder Path}
    CREATE_FOLDER = 'CreateRemDirectory' # Args: {Folder Path}, Returns: Static value if successful [Further investigation needed]
    DELETE_FILE = 'DeleteRemFile' # Args: {File Path}, Returns: ???
    DELETE_FOLDER = 'DeleteRemDirectory' # Args: {Folder Path}
    DISABLE_ME_CORRUPT_SCREEN = 'DisableMECorruptScreen' # Args: Null
    DISABLE_SCREENSAVER = 'DisableScreenSaver' # Args: Null
    ENABLE_ME_CORRUPT_SCREEN = 'EnableMECorruptScreen' # Args: Null
    ENABLE_SCREENSAVER = 'EnableScreenSaver' # Args: Null
    GET_FILE_EXISTS = 'FileExists' # Args: {File Path}, Returns: {File Size} if {File Path} exists, 0 otherwise
    GET_FOLDER_EXISTS = 'StorageExists' # Args: {Folder Path}, Returns: 1 if {Folder Path} exists
    GET_FREE_SPACE = 'FreeSpace' # Args: {Folder Path}, Returns: Free size in bytes
    GET_PROCESS_RUNNING = 'IsExeRunning' # Args: {Process Name}, Resp Code: 0 successful, Resp Data: 1 if process is running, 0 otherwise
    GET_TERMINAL_PARTITION_SIZE = 'GetTerminalPartitionSize' # Args: Null, Retruns {Partition Size} in bytes
    GET_TERMINAL_OS_REV = 'GetTerminalOSRev' # Args: Null, Returns: Build String
    GET_TOTAL_SPACE = 'TotalSpace' # Args: {Folder Path}, Returns: Free size in bytes
    START_PROCESS = 'InvokeEXE' # Args: {Binary Path}
    STOP_PROCESS = 'TerminateEXE' # Args: {Binary Name}
    STOP_PROCESS_ME = 'SafeTerminateME' # Args: Null, Resp Code: 0 successful, 2 failed/wasn't running, Resp Data: Null

def clear_folder(cip: comms.Driver, paths: types.MEPaths, folder_path: str) -> bool:
    req_args = [paths.fuwhelper_file, FuwHelperFunctions.CLEAR_FOLDER, folder_path]
    resp_code, resp_data = helper.run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Failed to execute function: {req_args}, response code: {resp_code}, response data: {resp_data}.')
    return True

def create_folder(cip: comms.Driver, paths: types.MEPaths, folder_path: str) -> bool:
    req_args = [paths.fuwhelper_file, FuwHelperFunctions.CREATE_FOLDER, folder_path]
    resp_code, resp_data = helper.run_function(cip, req_args)
    if (resp_code != CREATE_DIR_SUCCESS): raise Exception(f'Failed to execute function: {req_args}, response code: {resp_code}, response data: {resp_data}.')
    return True

def delete_file(cip: comms.Driver, paths: types.MEPaths, file_path: str) -> bool:
    req_args = [paths.fuwhelper_file, FuwHelperFunctions.DELETE_FILE, file_path]
    resp_code, resp_data = helper.run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Failed to delete file on terminal: {file_path}, response code: {resp_code}, response data: {resp_data}.')
    return True

def delete_folder(cip: comms.Driver, paths: types.MEPaths, folder_path: str) -> bool:
    req_args = [paths.fuwhelper_file, FuwHelperFunctions.DELETE_FOLDER, folder_path]
    resp_code, resp_data = helper.run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Failed to delete folder on terminal: {folder_path}, response code: {resp_code}, response data: {resp_data}.')
    return True

def get_process_running(cip: comms.Driver, paths: types.MEPaths, process_name: str) -> bool:
    req_args = [paths.fuwhelper_file, FuwHelperFunctions.GET_PROCESS_RUNNING, process_name]
    resp_code, resp_data = helper.run_function(cip, req_args)
    if (resp_code != 0): return False    
    return bool(int(resp_data))

def get_file_exists(cip: comms.Driver, paths: types.MEPaths, file_path: str) -> bool:
    req_args = [paths.fuwhelper_file, FuwHelperFunctions.GET_FILE_EXISTS, file_path]
    resp_code, resp_data = helper.run_function(cip, req_args)
    if (resp_code != 0): return False    
    return bool(int(resp_data))

def get_folder_exists(cip: comms.Driver, paths: types.MEPaths, folder_path: str) -> bool:
    req_args = [paths.fuwhelper_file, FuwHelperFunctions.GET_FOLDER_EXISTS, folder_path]
    resp_code, resp_data = helper.run_function(cip, req_args)
    if (resp_code != 0): return False    
    return bool(int(resp_data))

def get_free_space(cip: comms.Driver, paths: types.MEPaths, folder_path: str) -> int:
    if not(get_folder_exists(cip, paths, folder_path)): raise FileNotFoundError(f'Folder {folder_path} does not exist on remote terminal.')
    req_args = [paths.fuwhelper_file, FuwHelperFunctions.GET_FREE_SPACE, folder_path]
    resp_code, resp_data = helper.run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Failed to execute function: {req_args}, response code: {resp_code}, response data: {resp_data}.')
    return int(resp_data)

def get_os_rev(cip: comms.Driver, paths: types.MEPaths) -> str:
    req_args = [paths.fuwhelper_file, FuwHelperFunctions.GET_TERMINAL_OS_REV, '']
    resp_code, resp_data = helper.run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Failed to execute function: {req_args}, response code: {resp_code}, response data: {resp_data}.')
    return str(resp_data)

def get_partition_size(cip: comms.Driver, paths: types.MEPaths) -> int:
    req_args = [paths.fuwhelper_file, FuwHelperFunctions.GET_TERMINAL_PARTITION_SIZE, '']
    resp_code, resp_data = helper.run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Failed to execute function: {req_args}, response code: {resp_code}, response data: {resp_data}.')
    return int(resp_data)

def get_total_space(cip: comms.Driver, paths: types.MEPaths, folder_path: str) -> int:
    if not(get_folder_exists(cip, paths, folder_path)): raise FileNotFoundError(f'Folder {folder_path} does not exist on remote terminal.')
    req_args = [paths.fuwhelper_file, FuwHelperFunctions.GET_TOTAL_SPACE, folder_path]
    resp_code, resp_data = helper.run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Failed to execute function: {req_args}, response code: {resp_code}, response data: {resp_data}.')
    return int(resp_data)

def set_me_corrupt_screen(cip: comms.Driver, paths: types.MEPaths, state: bool) -> bool:
    if state:
        req_args = [paths.fuwhelper_file, FuwHelperFunctions.ENABLE_ME_CORRUPT_SCREEN, '']
    else:
        req_args = [paths.fuwhelper_file, FuwHelperFunctions.DISABLE_ME_CORRUPT_SCREEN, '']

    resp_code, resp_data = helper.run_function(cip, req_args)
    if (resp_code != 0): return False
    return True

def set_screensaver(cip: comms.Driver, paths: types.MEPaths, state: bool) -> bool:
    if state:
        req_args = [paths.fuwhelper_file, FuwHelperFunctions.ENABLE_SCREENSAVER, '']
    else:
        req_args = [paths.fuwhelper_file, FuwHelperFunctions.DISABLE_SCREENSAVER, '']

    resp_code, resp_data = helper.run_function(cip, req_args)
    if (resp_code != 0): return False
    return True

def start_process(cip: comms.Driver, paths: types.MEPaths, process: str) -> bool:
    req_args = [paths.fuwhelper_file, FuwHelperFunctions.START_PROCESS, process]
    resp_code, resp_data = helper.run_function(cip, req_args)
    if (resp_code != 0): return False
    return True

def stop_process(cip: comms.Driver, paths: types.MEPaths, process: str) -> bool:
    req_args = [paths.fuwhelper_file, FuwHelperFunctions.STOP_PROCESS, process]
    resp_code, resp_data = helper.run_function(cip, req_args)
    if (resp_code != 0): return False
    return True

def stop_process_me(cip: comms.Driver, paths: types.MEPaths) -> bool:
    if get_process_running(cip, paths, 'MERuntime.exe'):
        req_args = [paths.fuwhelper_file, FuwHelperFunctions.STOP_PROCESS_ME, '']
        resp_code, resp_data = helper.run_function(cip, req_args)
        if (resp_code != 0): return False
    return True