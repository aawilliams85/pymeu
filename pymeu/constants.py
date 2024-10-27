# When files are transferred, this is the maximum number of bytes
# used per message.  Quick tests up to 2000 bytes did succeed, >2000 bytes failed.
CHUNK_SIZE = 1984

# Known CIP class codes that aren't previously defined by pycomm3.
# Further investigation needed.
CIP_CLASSES = {
    b'\x04\xFD',    # Function
    b'\x04\xFE',    # Registry
    b'\x04\xFF'     # File
}

# Known CIP service codes that aren't previously defined by pycomm3.
# Further investigation needed.
CIP_SERVICES = {
    b'\x50',        # Execute
    b'\x51',        # Read Registry
    b'\x52',        # Write File
    b'\x53',        # Read File
}

# Known RemoteHelper file version numbers, used to help check that device is a valid terminal.
HELPER_VERSIONS = {
    '5.10.00',
    '7.00.00',
    '8.00.00',
    '8.10.00',
    '8.20.00',
    '9.00.00',
    '10.00.00',
    '11.00.00',
    '12.00.00',
    '12.00.00.414.73',
    '13.00.00'
}

# Known terminal MEVersion numbers, used to help check that device is a valid terminal.
ME_VERSIONS = {
    '5.10.16.09',
    '7.00.20.13',
    '7.00.55.13',
    '8.00.67.12',
    '8.10.42.13',
    '8.20.30.10',
    '9.00.17.241',
    '9.00.00.241',
    '10.00.09.290',
    '11.00.00.230',
    '11.00.25.230',
    '12.00.00.414',
    '12.00.78.414',
    '13.00.11.413'
}

# Known terminal product codes, used to help check that device is a valid terminal.
PRODUCT_CODES = {
    '17',   #PanelView Plus
    '47',   #PanelView Plus 6 1000
    '48',   #PanelView Plus 6
    '51',   #PanelView Plus 6
    '94',   #PanelView Plus 7 700 Perf
    '98',   #PanelView Plus 7 1000 Perf
    '102',  #PanelView Plus 7
    '187',  #PanelView Plus 7 1000 Standard
    '189'   #PanelView Plus 7 1200 Standard
}

# Known product types, used to help check that device is a valid terminal.
PRODUCT_TYPES = {
    '24'
}

# Known registry keys on the terminal that should be whitelisted for read access through RemoteHelper.
REG_KEYS = {
    'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\MajorRevision,',           # ex: 11
    'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\MinorRevision',            # ex: 1
    'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\ProductCode',              # ex: 51
    'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\ProductName',              # ex: PanelView Plus_6 1500
    'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\ProductType',              # ex: 24
    'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\SerialNumber',             # ex: 1234567
    'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSLinxNG\CIP Identity\Vendor',                   # ex: 1
    'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSView Enterprise\MEVersion',                    # ex: 11.00.25.230
    'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSViewME\Startup Options\CurrentApp',            # ex: \Application Data\Rockwell Software\RSViewME\Runtime\{FileName}.mer
    'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSViewME\Startup Options\DeleteLogFiles',        # ex: 0
    'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSViewME\Startup Options\LoadCurrentApp',        # ex: 1
    'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSViewME\Startup Options\ReplaceCommSettings',   # ex: 0
    'HKEY_LOCAL_MACHINE\SOFTWARE\Rockwell Software\RSViewME\Startup Options\StartupOptionsConfig'   # ex: 1
}

# Known functions available from RemoteHelper.
REMOTE_HELPER_FUNCIONS = {
    'BootTerminal',                 # ex: 'BootTerminal',''
                                    #       Returns a comms error since upon successful execution, terminal is reset.
    'CreateRemDirectory',           # ex: 'CreateRemDirectory','{Path}'
                                    #       Returns a static value if successful, further investigation needed.
    'CreateRemShortcut',
    'CreateRemMEStartupShortcut',   # ex: 'CreateRemMEStartupShortcut','{Folder Path}:{Filename.MER}: /r /delay'
                                    #       Can also specify /o to replace comms and /d to delete logs at startup
                                    #       Returns 1 if shortcut created successfully, 0 otherwise.
    'DeleteRemDirectory',
    'DeleteRemFile',
    'FileBrowse',                   # ex: 'FileBrowse','{Search Path}\\*.{Search Extension}::{Results File Path}
                                    #       Returns 1 if results file generated successfully, 0 otherwise.
    'FileExists',                   # ex: 'FileExists','{File Path}'
                                    #       Returns 1 if file exists, 0 otherwise.
    'FileSize',                     # ex: 'FileSize','{File Path}'
                                    #       Returns the number of bytes.
    'FolderBrowse',
    'FreeSpace',                    # ex: 'FreeSpace','{Path}'
                                    #       Returns the number of bytes.
    'GetFileVersion',
    'GetVersion',                   # ex: 'GetVersion','{File Path}'
                                    #       Returns the a version string.
    'InvokeEXE',
    'IsExeRunning',
    'StorageExists',                # ex: 'StorageExists'.'{Path}'
                                    #       Returns 1 if folder exists, 0 otherwise.
    'TerminateEXE'
}

UPLOAD_LIST_PATH = f'\\Rockwell Software\\RSViewME\\Runtime\\Results.txt'

# Known static value for successful creation of a folder.
# Further investigation needed.
CREATE_DIR_SUCCESS = 183 # 'b\xb7'

# Known values associated with some file services, with unclear purpose or meaning.
# Further investigation needed.
GET_UNK1_VALUES = {
    b'\x02\x00'
}

# Known values associated with some file services, with unclear purpose or meaning.
# Further investigation needed.
GET_UNK2_VALUES = {
    b'\x01\x60',
    b'\x03\x41'
}

# Known values associated with some file services, with unclear purpose or meaning.
# Further investigation needed.
GET_UNK3_VALUES = {
    b'\x64\x00'
}