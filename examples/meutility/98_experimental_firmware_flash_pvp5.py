"""
Warning - Firmware upgrade is experimental!
If anything fails during this process, the terminal will require a factory reset.

Warning - This example is for PanelView Plus 5 only!

First, use the ME Firmware Upgrade Wizard utility to create a
Firmware Upgrade Card for the desired terminal type + version.
The firmware image path is the Firmware Upgrade Card path.  It should
contain 'autorun.exe', 'MFCCE400.DLL', and the 'upgrade' folder.

Next, locate the Firmware Upgrade Wizard helper DLL as your
firmware helper path.  Default location:
C:\\Program Files (x86)\\Rockwell Software\\RSView Enterprise\\FUWhelper4xX.dll

Also locate the Firmware Upgrade Wizard cover *.exe as your
firmware cover path.  Default location:
C:\\Program Files (x86)\\Rockwell Software\\RSView Enterprise\\FUWCover4xX.exe


Cross fingers and flash firmware.
"""

from pymeu import MEUtility

def progress_callback(description: str, total_bytes: int, current_bytes: int):
    progress = 100* current_bytes / total_bytes
    print(f"{description} progress: {progress:.2f}% complete, {current_bytes} of {total_bytes} bytes.")

meu = MEUtility('YourPanelViewIpAddress')
meu.flash_firmware(
    firmware_image_path='C:\\YourFirmwareUpgradeCard',
    firmware_helper_path='C:\\Program Files (x86)\\Rockwell Software\\RSView Enterprise\\FUWhelper4xX.dll',
    firmware_cover_path='C:\\Program Files (x86)\\Rockwell Software\\RSView Enterprise\\FUWCover4xX.exe',
    progress=progress_callback)