"""
Warning - Firmware upgrade is experimental!
If anything fails during this process, the terminal will require a factory reset.

Warning - This example is for PanelView Plus 6 and PanelView Plus 7 Series A terminals only!
PanelView Plus (v5 hardware) is not compatible and will require additional development.

First, use the ME Firmware Upgrade Wizard utility to create a
Firmware Upgrade Card for the desired terminal type + version.
Note the path to "SC.IMG" in the folder it creates as your
firmware image path.

Next, locate the Firmware Upgrade Wizard helper DLL as your
firmware helper path.  Default location:
C:\\Program Files (x86)\\Rockwell Software\\RSView Enterprise\\FUWhelper6xX.dll

Cross fingers and flash firmware.
"""

from pymeu import MEUtility

def progress_callback(description: str, total_bytes: int, current_bytes: int):
    progress = 100* current_bytes / total_bytes
    print(f"{description} progress: {progress:.2f}% complete, {current_bytes} of {total_bytes} bytes.")

meu = MEUtility('YourPanelViewIpAddress')
meu.flash_firmware_me(
    firmware_image_path='C:\\YourFirmwareUpgradeCard\\upgrade\\SC.IMG',
    firmware_helper_path='C:\\Program Files (x86)\\Rockwell Software\\RSView Enterprise\\FUWhelper6xX.dll',
    progress=progress_callback)