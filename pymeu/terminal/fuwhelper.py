from enum import StrEnum

from . import helper
from .. import comms
from .. import types

# Known static value for successful creation of a folder.
# Further investigation needed.
CREATE_DIR_SUCCESS = 0

# Known functions available from FuwHelper.
class FuwHelperFunctions(StrEnum):
    CREATE_FOLDER = 'CreateRemDirectory' # Args: {Folder Path}, Returns: Static value if successful [Further investigation needed]
    DELETE_FILE = 'DeleteRemFile' # Args: {File Path}, Returns: ???
    GET_FILE_EXISTS = 'FileExists' # Args: {File Path}, Returns: {File Size} if {File Path} exists, 0 otherwise
    GET_FOLDER_EXISTS = 'StorageExists' # Args: {Folder Path}, Returns: 1 if {Folder Path} exists
    GET_PROCESS_RUNNING = 'IsExeRunning' # Args: {Process Name}, Resp Code: 0 successful, Resp Data: 1 if process is running, 0 otherwise
    STOP_PROCESS_ME = 'SafeTerminateME' # Args: Null, Resp Code: 0 successful, 2 failed/wasn't running, Resp Data: Null

def create_folder(cip: comms.Driver, paths: types.MEPaths, dir: str) -> bool:
    req_args = [paths.fuwhelper_file, FuwHelperFunctions.CREATE_FOLDER, dir]
    resp_code, resp_data = helper.run_function(cip, req_args)
    if (resp_code != CREATE_DIR_SUCCESS): raise Exception(f'Failed to execute function: {req_args}, response code: {resp_code}, response data: {resp_data}.')
    return True

def delete_file(cip: comms.Driver, paths: types.MEPaths, file_path: str) -> bool:
    req_args = [paths.fuwhelper_file, FuwHelperFunctions.DELETE_FILE, file_path]
    resp_code, resp_data = helper.run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Failed to delete file on terminal: {file_path}, response code: {resp_code}, response data: {resp_data}.')
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

def stop_process_me(cip: comms.Driver, paths: types.MEPaths) -> bool:
    if get_process_running(cip, paths, 'MERuntime.exe'):
        req_args = [paths.fuwhelper_file, FuwHelperFunctions.STOP_PROCESS_ME, '']
        resp_code, resp_data = helper.run_function(cip, req_args)
        if (resp_code != 0): return False
    return True
