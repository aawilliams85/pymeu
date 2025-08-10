"""
Warning - Firmware upgrade is experimental!
If anything fails during this process, the terminal will require a factory reset.

Firmware Upgrade Packs (FUP) are stored by default in:
C:\\Program Files (x86)\\Rockwell Software\\RSView Enterprise\\FUPs

Firmware Upgrade Cover files and Firmware Upgrade Helpers are stored by default in:
C:\\Program Files (x86)\\Rockwell Software\\RSView Enterprise

Example:
PanelView Plus 1000 v11 uses the *6xX files.

meu = MEUtility(comms_path='YourPanelViewIpAddress')
meu.flash_firmware(
    fup_path_local='ME_PVP6xX_11.00-20190915.fup',
    fuwhelper_path_local='FUWhelper6xX.dll',
    fuwcover_path_local=None,
    progress=progress_callback
)

Cross fingers and flash firmware.
"""

from pymeu import MEUtility

def progress_callback(description: str, units: str, total_bytes: int, current_bytes: int):
    progress = 100* current_bytes / total_bytes
    print(f"{description} progress: {progress:.2f}% complete, {current_bytes} of {total_bytes} {units}.")

meu = MEUtility(comms_path='YourPanelViewIpAddress')
meu.flash_firmware(
    fup_path_local='YourFirmwareUpgradePack.fup',
    fuwhelper_path_local='YourFirmwareUpgradeHelper.dll',
    fuwcover_path_local=None,
    progress=progress_callback
)