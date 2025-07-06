import os
import time
import unittest

from pymeu import comms
from pymeu import CFUtility
from pymeu import terminal
from pymeu import types
from pymeu import validation

from config import *

# Turn off sort so that tests run in line order
unittest.TestLoader.sortTestMethodsUsing = None

class dmk_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_flash_pvp7b_direct_pycomm3(self):
        print('')
        driver = DRIVER_PYCOMM3
        device = DEVICE_PVP7B
        comms_path = device.comms_paths[0]

        cfu = CFUtility(comms_path, driver=driver)
        firmware_image_path = device.local_firmware_image_paths[0]   
        result = (
                f'Device: {device.name}\n'
                f'Driver: {driver}\n'
                f'Path: {comms_path}\n'
                f'Function: flash_firmware_dmk({firmware_image_path})\n'
        )
        print(result)
        resp = cfu.flash_firmware(
            firmware_image_path=firmware_image_path,
            dry_run=False,
            progress=progress_callback)
        for s in resp.device.log: print(s)
        print('')
        self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)

    def test_flash_pvp7b_direct_pylogix(self):
        print('')
        driver = DRIVER_PYLOGIX
        device = DEVICE_PVP7B
        comms_path = device.comms_paths[0]

        cfu = CFUtility(comms_path, driver=driver)
        firmware_image_path = device.local_firmware_image_paths[0]   
        result = (
                f'Device: {device.name}\n'
                f'Driver: {driver}\n'
                f'Path: {comms_path}\n'
                f'Function: flash_firmware_dmk({firmware_image_path})\n'
        )
        print(result)
        resp = cfu.flash_firmware(
            firmware_image_path=firmware_image_path,
            dry_run=False,
            progress=progress_callback)
        for s in resp.device.log: print(s)
        print('')
        self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)

    '''
    def test_dmk_validate(self):
        print('')
        with comms.Driver(PVP7A_Comms_Paths[0]) as cip:
            self.device = validation.get_terminal_info(cip)

            firmware_image_path = os.path.join(FIRMWARE_FOLDER_PATH, 'DMK', 'PVP7B', '2711P-PanelView_Plus_7_Performance_15.100.dmk')
            self.dmk_content = dmk.process_dmk(firmware_image_path)

            print(dmk.validate_dmk_for_terminal(self.device, self.dmk_content))
        print('')

    def test_dmk_unsupported(self):
        print('')
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            firmware_image_path = os.path.join(FIRMWARE_FOLDER_PATH, 'DMK', 'PVP7B', '2711P-PanelView_Plus_7_Performance_15.100.dmk')
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: flash_firmware({firmware_image_path})\n'
            )
            print(result)
            resp = meu.flash_firmware_dmk(firmware_image_path, False)
            for s in resp.device.log: print(s)
            print('')
            self.assertEqual(resp.status, types.MEResponseStatus.FAILURE)
    '''
            
    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()