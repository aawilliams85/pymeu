"""
Warning - Firmware upgrade is experimental!
If anything fails during this process, the terminal will require a factory reset.

Warning - This example is for PanelView Plus 7 Series B terminals only!
"""

from pymeu import CFUtility

def progress_callback(description: str, total_bytes: int, current_bytes: int):
    progress = 100* current_bytes / total_bytes
    print(f"{description} progress: {progress:.2f}% complete, {current_bytes} of {total_bytes} bytes.")

meu = CFUtility('YourPanelViewIpAddress')
meu.flash_firmware_dmk(
    firmware_image_path='C:\\YourFolder\\YourFirmwareImage.DMK',
    dry_run=False,
    progress=progress_callback)