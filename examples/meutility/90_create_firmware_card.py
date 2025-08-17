"""
Warning - Firmware upgrade is experimental!
If the firmware card is created incorrectly, the terminal will require a factory reset.

*** For v5 and earlier terminals, before attempting, create a backup image of the internal CF card. ***
*** See docs/me/firmware.md ***

Firmware Upgrade Packs (FUP) are stored by default in:
C:\\Program Files (x86)\\Rockwell Software\\RSView Enterprise\\FUPs

KepDrivers are an optional list

Example:
PanelView Plus 1000 v11 uses the *6xX files.
USB drive in F:\\

meu = MEUtility()
meu.flash_firmware(
    fup_path_local='ME_PVP6xX_11.00-20190915.fup',
    fwc_path_local='F:\\',
    kep_drivers=['A-B Bulletin 1609'],
    progress=progress_callback
)
"""

from pymeu import MEUtility

def progress_callback(description: str, units: str, total_bytes: int, current_bytes: int):
    progress = 100* current_bytes / total_bytes
    print(f"{description}: {progress:.2f}%, {current_bytes} of {total_bytes} {units}.")

meu = MEUtility()
meu.create_firmware_card(
    fup_path_local='YourFirmwareUpgradePack.fup',
    fwc_path_local='YourFirmwareCardPath',
    kep_drivers=None,
    progress=progress_callback
)