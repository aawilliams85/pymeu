import pycomm3

from enum import StrEnum
from warnings import warn

from . import paths
from .. import messages
from .. import types 


# Known static value for successful creation of a folder.
# Further investigation needed.
CREATE_DIR_SUCCESS = 183 # 'b\xb7'

# Known functions available from RemoteHelper.
class HelperFunctions(StrEnum):
    REBOOT = 'BootTerminal'
    # ex: 'BootTerminal',''
    #       Returns a comms error since upon successful execution, terminal is reset.

    CREATE_DIRECTORY = 'CreateRemDirectory'
    # ex: 'CreateRemDirectory','{Path}'
    #       Returns a static value if successful, further investigation needed.

    CREATE_SHORTCUT = 'CreateRemShortcut'

    CREATE_ME_SHORTCUT = 'CreateRemMEStartupShortcut'
    # ex: 'CreateRemMEStartupShortcut','{Folder Path}:{Filename.MER}: /r /delay'
    #       Can also specify /o to replace comms and /d to delete logs at startup
    #       Returns 1 if shortcut created successfully, 0 otherwise.

    DELETE_DIRECTORY = 'DeleteRemDirectory'

    DELETE_FILE = 'DeleteRemFile'

    CREATE_FILE_LIST = 'FileBrowse'
    # ex: 'FileBrowse','{Search Path}\\*.{Search Extension}::{Results File Path}
    #       Returns 1 if results file generated successfully, 0 otherwise.

    GET_FILE_EXISTS = 'FileExists'
    # ex: 'FileExists','{File Path}'
    #       Returns 1 if file exists, 0 otherwise.

    GET_FILE_SIZE = 'FileSize'
    # ex: 'FileSize','{File Path}'
    #       Returns the number of bytes.

    CREATE_FOLDER_LIST = 'FolderBrowse'

    GET_FREE_SPACE = 'FreeSpace'
    # ex: 'FreeSpace','{Path}'
    #       Returns the number of bytes.
    GET_FILE_VERSION = 'GetFileVersion'
    GET_VERSION = 'GetVersion'
    # ex: 'GetVersion','{File Path}'
    #       Returns the a version string.

    START_PROCESS = 'InvokeEXE'
    GET_EXE_RUNNING = 'IsExeRunning'
    GET_FOLDER_EXISTS = 'StorageExists'
    # ex: 'StorageExists'.'{Path}'
    #       Returns 1 if folder exists, 0 otherwise.
    STOP_PROCESS = 'TerminateEXE'

def run_function(cip: pycomm3.CIPDriver, req_args):
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

def create_directory(cip: pycomm3.CIPDriver, dir: str) -> bool:
    req_args = [paths.helper_file_path, HelperFunctions.CREATE_DIRECTORY, dir]
    resp_code, resp_data = run_function(cip, req_args)
    if (resp_code != CREATE_DIR_SUCCESS): raise Exception('Failed to create directory on terminal.')    
    return True

def create_me_shortcut(cip: pycomm3.CIPDriver, file: str, replace_comms: bool, delete_logs: bool) -> bool:
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
    shortcut = f'{paths.storage_path}:{file}: /r /delay{replace_comms_param}{delete_logs_param}'
    req_args = [paths.helper_file_path, HelperFunctions.CREATE_ME_SHORTCUT, shortcut]
    resp_code, resp_data = run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Failed to create ME Startup Shortcut on terminal: {file}, response code: {resp_code}, response data: {resp_data}.')
    return True

def create_med_list(cip:pycomm3.CIPDriver):
    req_args = [paths.helper_file_path,HelperFunctions.CREATE_FILE_LIST, '\\Temp\\~MER.00\\*.med::' + paths.upload_list_path]
    resp_code, resp_data = run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Response code was not zero.  Examine packets.')
    return True

def create_mer_list(cip: pycomm3.CIPDriver):
    req_args = [paths.helper_file_path,HelperFunctions.CREATE_FILE_LIST, paths.storage_path + '\\Rockwell Software\\RSViewME\\Runtime\\*.mer::' + paths.upload_list_path]
    resp_code, resp_data = run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Response code was not zero.  Examine packets.')
    return True

def create_runtime_directory(cip: pycomm3.CIPDriver, file: types.MEFile) -> bool:
    # Create paths
    if not(create_directory(cip, paths.storage_path)): return False
    if not(create_directory(cip, paths.storage_path + '\\Rockwell Software')): return False
    if not(create_directory(cip, paths.storage_path + '\\Rockwell Software\\RSViewME')): return False
    if not(create_directory(cip, paths.storage_path + '\\Rockwell Software\\RSViewME\\Runtime')): return False
    return True

def delete_file(cip: pycomm3.CIPDriver, file: str) -> bool:
    req_args = [paths.helper_file_path,HelperFunctions.DELETE_FILE,file]
    resp_code, resp_data = run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Failed to delete file on terminal: {file}, response code: {resp_code}, response data: {resp_data}.')
    return True

def delete_file_list(cip: pycomm3.CIPDriver) -> bool:
    return delete_file(cip, paths.upload_list_path)

def get_file_exists(cip: pycomm3.CIPDriver, file: types.MEFile) -> bool:
    req_args = [paths.helper_file_path, HelperFunctions.GET_FILE_EXISTS, paths.storage_path + f'\\Rockwell Software\\RSViewME\\Runtime\\{file.name}']
    resp_code, resp_data = run_function(cip, req_args)
    if (resp_code != 0): return False    
    return bool(int(resp_data))

def get_file_size(cip: pycomm3.CIPDriver, file: types.MEFile) -> int:
    req_args = [paths.helper_file_path, HelperFunctions.GET_FILE_SIZE, paths.storage_path + f'\\Rockwell Software\\RSViewME\\Runtime\\{file.name}']
    resp_code, resp_data = run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Response code was not zero.  Examine packets.')
    return int(resp_data)

def get_folder_exists(cip: pycomm3.CIPDriver) -> bool:
    req_args = [paths.helper_file_path, HelperFunctions.GET_FOLDER_EXISTS, paths.storage_path]
    resp_code, resp_data = run_function(cip, req_args)
    if (resp_code != 0):
        warn(f'Response code was not zero.  Examine packets.')
        return False
    return bool(int(resp_data))

def get_free_space(cip: pycomm3.CIPDriver) -> int:
    req_args = [paths.helper_file_path, HelperFunctions.GET_FREE_SPACE, paths.storage_path + '\\Rockwell Software\\RSViewME\\Runtime\\']
    resp_code, resp_data = run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Response code was not zero.  Examine packets.')
    return int(resp_data)

def get_helper_version(cip: pycomm3.CIPDriver) -> str:
    req_args = [paths.helper_file_path, HelperFunctions.GET_VERSION, paths.helper_file_path]
    resp_code, resp_data = run_function(cip, req_args)
    if (resp_code != 0): raise Exception(f'Response code was not zero.  Examine packets.')
    return str(resp_data)

def reboot(cip: pycomm3.CIPDriver):
    req_args = [paths.helper_file_path, HelperFunctions.REBOOT,'']
    req_data = b''.join(arg.encode() + b'\x00' for arg in req_args)
    resp = messages.run_function(cip, req_data)