
from enum import StrEnum
from warnings import warn

from .. import comms
from .. import messages
from .. import types 


# Known static value for successful creation of a folder.
# Further investigation needed.
CREATE_DIR_SUCCESS = 183 # 'b\xb7'

# Known functions available from RemoteHelper.
class HelperFunctions(StrEnum):
    CREATE_FILE_LIST = 'FileBrowse' # Args: {Search Path}\\*.{Search Extension}::{Results File Path}, Returns: 1 if result generated
    #CREATE_FILE_SHORTCUT = 'CreateRemShortcut' # Untested
    CREATE_FOLDER = 'CreateRemDirectory' # Args: {Folder Path}, Returns: Static value if successful [Further investigation needed]
    #CREATE_FOLDER_LIST = 'FolderBrowse' # Untested
    CREATE_ME_SHORTCUT = 'CreateRemMEStartupShortcut' # Args: {Folder Path}:{Filename.MER}: /r /delay /o /d, Returns: 1 if startup shortcut is created
    DELETE_FILE = 'DeleteRemFile' # Args: {File Path}, Returns: ???
    #DELETE_FOLDER = 'DeleteRemDirectory' # Untested
    #GET_EXE_RUNNING = 'IsExeRunning' # Untested
    GET_FILE_EXISTS = 'FileExists' # Args: {File Path}, Returns: 1 if {File Path} exists
    GET_FILE_SIZE = 'FileSize' # Args: {File Path}, Returns: File size in bytes
    #GET_FILE_VERSION = 'GetFileVersion' # Untested
    GET_FOLDER_EXISTS = 'StorageExists' # Args: {Folder Path}, Returns: 1 if {Folder Path} exists
    GET_FREE_SPACE = 'FreeSpace' # Args: {Folder Path}, Returns: Free size in bytes
    GET_VERSION = 'GetVersion' # Args: {File Path}, Returns: Version string
    REBOOT = 'BootTerminal' # Args: null, Returns: Comms error since upon successful execution, terminal is reset.
    #START_PROCESS = 'InvokeEXE' # Untested
    #STOP_PROCESS = 'TerminateEXE' # Untested

def run_function(cip: comms.Driver, req_args):
    """
    Executes a function on the remote terminal.

    Args:
        cip (pycomm3.CIPDriver): CIPDriver to communicate with the terminal
        req_args: The request to execute.  Typically a list like ['DLL Path','Function Name','Function Args'] 

    Returns:
        resp_code (int): The message response code.
        resp_data (str): The function response data.

    Raises:
        Exception: If the message response code is not zero, indicating an error.

    Request Format:
        The request consists of the following byte structure:

        | Byte Range    | Description                                         |
        |---------------|-----------------------------------------------------|
        | Bytes 0->N-1  | Request Arguments                                   |
        | Byte N        | Null footer                                         |

    Response Format:
        The response consists of the following byte structure:

        | Byte Range    | Description                                         |
        |---------------|-----------------------------------------------------|
        | Bytes 0->3    | Response code (typically 0 = ran, other = error)    |
        | Bytes 4->N-1  | Function response                                   |
        | Bytes N       | Null footer                                         |

    Note:
        Only a certain subset of functions are whitelisted for access
        by this method.  They are documented in the HelperFunctions enum.
    """
    req_data = b''.join(arg.encode() + b'\x00' for arg in req_args)

    resp = messages.run_function(cip, req_data)
    if not resp: raise Exception(f'Failed to run function: {req_args}.')
    resp_code = int.from_bytes(resp.value[:4], byteorder='little', signed=False)
    resp_data = resp.value[4:].decode('utf-8').strip('\x00')
    return resp_code, resp_data

def create_file_list_med(cip: comms.Driver, paths: types.MEDevicePaths):
    req_args = [paths.helper_file,HelperFunctions.CREATE_FILE_LIST, f'\\Temp\\~MER.00\\*.med::{paths.upload_list}']
    resp_code, resp_data = run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Response code was not zero.  Examine packets.')
    return True

def create_file_list_mer(cip: comms.Driver, paths: types.MEDevicePaths):
    req_args = [paths.helper_file,HelperFunctions.CREATE_FILE_LIST, f'{paths.runtime}\\*.mer::{paths.upload_list}']
    resp_code, resp_data = run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Response code was not zero.  Examine packets.')
    return True

def create_folder(cip: comms.Driver, paths: types.MEDevicePaths, dir: str) -> bool:
    req_args = [paths.helper_file, HelperFunctions.CREATE_FOLDER, dir]
    resp_code, resp_data = run_function(cip, req_args)
    if (resp_code != CREATE_DIR_SUCCESS): raise Exception(f'Failed to execute function: {req_args}, response code: {resp_code}, response data: {resp_data}.')
    return True

def create_folder_runtime(cip: comms.Driver, paths: types.MEDevicePaths) -> bool:
    subfolders = paths.runtime.split('\\')
    current_path = subfolders[0]
    for folder in subfolders[1:]:
        current_path = f'{current_path}\\{folder}'
        if not create_folder(cip, paths, current_path): return False

    return True

def create_me_shortcut(cip: comms.Driver, paths: types.MEDevicePaths, file: str, replace_comms: bool, delete_logs: bool) -> bool:
    """
    Setup a specific *.MER file to run at terminal startup.

    Args:
        cip (pycomm3.CIPDriver): CIPDriver to communicate with the terminal
        file (str): The *.MER file to use
        replace_comms (bool): If true, replaces the terminal comms setup with the configuration from the *.MER file.
        delete_logs (bool): If true, deletes logs at startup.

    Returns:
        Status (bool): True if function runs successfully.

    Request Format:
        {storage path}:{filename}: /r /delay /o /d

    Note:
        Even though the *.MER file resides in a subdirectory (ex: {storage path}\\Rockwell Software\\RSViewME\\Runtime\\{{filename}),
        it is only transmitted as {storage path}:{filename}.  The rest of the path is inserted by the RemoteHelper on the terminal.
    """ 
    replace_comms_param = ' /o' if replace_comms else ''
    delete_logs_param = ' /d' if delete_logs else ''
    shortcut = f'{paths.storage}:{file}: /r /delay{replace_comms_param}{delete_logs_param}'
    req_args = [paths.helper_file, HelperFunctions.CREATE_ME_SHORTCUT, shortcut]
    resp_code, resp_data = run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Failed to create ME Startup Shortcut on terminal: {file}, response code: {resp_code}, response data: {resp_data}.')
    return True

def delete_file(cip: comms.Driver, paths: types.MEDevicePaths, file_path: str) -> bool:
    req_args = [paths.helper_file, HelperFunctions.DELETE_FILE, file_path]
    resp_code, resp_data = run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Failed to delete file on terminal: {file_path}, response code: {resp_code}, response data: {resp_data}.')
    return True

def delete_file_list(cip: comms.Driver, paths: types.MEDevicePaths) -> bool:
    return delete_file(cip, paths, paths.upload_list)

'''
# Untested
def delete_folder(cip: comms.Driver, paths: types.MEDevicePaths, folder_path: str) -> bool:
    req_args = [paths.helper_file, HelperFunctions.DELETE_FOLDER, folder_path]
    resp_code, resp_data = run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Failed to execute function: {req_args}, response code: {resp_code}, response data: {resp_data}.')
    return True
'''

def get_file_exists(cip: comms.Driver, paths: types.MEDevicePaths, file_path: str) -> bool:
    req_args = [paths.helper_file, HelperFunctions.GET_FILE_EXISTS, file_path]
    resp_code, resp_data = run_function(cip, req_args)
    if (resp_code != 0): return False    
    return bool(int(resp_data))

def get_file_exists_mer(cip: comms.Driver, paths: types.MEDevicePaths, file_name: str) -> bool:
    file_path = f'{paths.runtime}\\{file_name}'
    return get_file_exists(cip, paths, file_path)

def get_file_size(cip: comms.Driver, paths: types.MEDevicePaths, file_path: str) -> int:
    if not(get_file_exists(cip, paths, file_path)): raise FileNotFoundError(f'File {file_path} does not exist on remote terminal.')
    req_args = [paths.helper_file, HelperFunctions.GET_FILE_SIZE, file_path]
    resp_code, resp_data = run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Failed to execute function: {req_args}, response code: {resp_code}, response data: {resp_data}.')
    return int(resp_data)

def get_file_size_mer(cip: comms.Driver, paths: types.MEDevicePaths, file_name: str) -> int:
    file_path = f'{paths.runtime}\\{file_name}'
    return get_file_size(cip, paths, file_path)

def get_folder_exists(cip: comms.Driver, paths: types.MEDevicePaths, folder_path: str) -> bool:
    req_args = [paths.helper_file, HelperFunctions.GET_FOLDER_EXISTS, folder_path]
    resp_code, resp_data = run_function(cip, req_args)
    if (resp_code != 0): return False    
    return bool(int(resp_data))

def get_free_space(cip: comms.Driver, paths: types.MEDevicePaths, folder_path: str) -> int:
    if not(get_folder_exists(cip, paths, folder_path)): raise FileNotFoundError(f'Folder {folder_path} does not exist on remote terminal.')
    req_args = [paths.helper_file, HelperFunctions.GET_FREE_SPACE, folder_path]
    resp_code, resp_data = run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Failed to execute function: {req_args}, response code: {resp_code}, response data: {resp_data}.')
    return int(resp_data)

def get_free_space_runtime(cip: comms.Driver, paths: types.MEDevicePaths) -> int:
    folder_path = f'{paths.runtime}\\'
    return get_free_space(cip, paths, folder_path)

def get_version(cip: comms.Driver, paths: types.MEDevicePaths, file_path: str) -> str:
    if not(get_file_exists(cip, paths, file_path)): raise FileNotFoundError(f'File {file_path} does not exist on remote terminal.')
    req_args = [paths.helper_file, HelperFunctions.GET_VERSION, file_path]
    resp_code, resp_data = run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Failed to execute function: {req_args}, response code: {resp_code}, response data: {resp_data}.')
    return str(resp_data)

def reboot(cip: comms.Driver, paths: types.MEDevicePaths):
    req_args = [paths.helper_file, HelperFunctions.REBOOT,'']
    req_data = b''.join(arg.encode() + b'\x00' for arg in req_args)
    resp = messages.run_function(cip, req_data)