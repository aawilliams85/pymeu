"""
Warning - Firmware upgrade is experimental!
If anything fails during this process, the terminal will require a factory reset.

*** Before attempting, create a backup image of the internal CF card. ***
*** See docs/me/firmware.md ***

Firmware Upgrade Packs (FUP) are stored by default in:
C:\\Program Files (x86)\\Rockwell Software\\RSView Enterprise\\FUPs

Firmware Upgrade Cover files and Firmware Upgrade Helpers are stored by default in:
C:\\Program Files (x86)\\Rockwell Software\\RSView Enterprise

Example:
PanelView Plus 1000 v5.10 uses the *4xX files.

meu = MEUtility(comms_path='YourPanelViewIpAddress')
meu.flash_firmware(
    fup_path_local='ME_PVP4xX_5.10.16.09.fup',
    fuwhelper_path_local='FUWhelper4xX.dll',
    fuwcover_path_local='FUWCover4xX.exe',
    progress=progress_callback
)

Cross fingers and flash firmware.
"""

from pymeu import MEUtility

def progress_callback(description: str, units: str, total_bytes: int, current_bytes: int):
    progress = 100* current_bytes / total_bytes
    print(f"{description}: {progress:.2f}%, {current_bytes} of {total_bytes} {units}.")

meu = MEUtility(comms_path='YourPanelViewIpAddress')
meu.flash_firmware(
    fup_path_local='YourFirmwareUpgradePack.fup',
    fuwhelper_path_local='YourFirmwareUpgradeHelper.dll',
    fuwcover_path_local='YourFirmwareUpgradeCover.exe',
    progress=progress_callback
)