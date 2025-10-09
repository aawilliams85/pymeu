"""
Warning - Firmware upgrade is experimental!
If anything fails during this process, the terminal will require a factory reset.

Warning - This example is for PanelView Plus 7 Series B terminals only!
"""

from pymeu import CFUtility

def progress_callback(description: str, units: str, total_bytes: int, current_bytes: int):
    progress = 100* current_bytes / total_bytes
    print(f"{description} progress: {progress:.2f}% complete, {current_bytes} of {total_bytes} {units}.")

cfu = CFUtility(comms_path='YourPanelViewIpAddress')
cfu.flash_firmware(
    dmk_path_local='C:\\YourFolder\\YourFirmwareImage.DMK',
    progress=progress_callback
)