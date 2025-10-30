from enum import IntEnum, auto

class MERecipePlusStatus(IntEnum):
    DownloadStart=1
    DownloadSuccessful=2
    DownloadError=4
    UploadStart=17
    UploadSuccessful=18
    UploadError=20
    CreateStart=33
    CreateSuccessful=34
    CreateError=36
    DeleteStart=65
    DeleteSuccessful=66
    DeleteError=68
    RenameStart=129
    RenameSuccessful=130
    RenameError=132
    RestoreStart=257
    RestoreSuccessful=258
    RestoreError=260
    SaveStart=513
    SaveSuccessful=514
    SaveError=516