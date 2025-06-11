import os
import zipfile
import unittest

from pymeu import comms
from pymeu import dmk
from pymeu import MEUtility
from pymeu import terminal
from pymeu import types

from config import *

# Turn off sort so that tests run in line order
unittest.TestLoader.sortTestMethodsUsing = None

class dmk_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_dmk_unpack(self):
        print('')
        firmware_image_path = os.path.join(FIRMWARE_FOLDER_PATH, 'DMK', 'PVP7B', '2711P-PanelView_Plus_7_Performance_15.100.dmk')
        with comms.Driver('192.168.40.124') as cip:
            dmk.process_dmk(cip, firmware_image_path)
        print('')

    def test_dmk_validate(self):
        print('')
        with comms.Driver(PVP7A_Comms_Paths[0]) as cip:
            self.device = terminal.validation.get_terminal_info(cip)

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
            resp = meu.flash_firmware(firmware_image_path,'')
            for s in resp.device.log: print(s)
            print('')
            self.assertEqual(resp.status, types.MEResponseStatus.FAILURE)

    def tearDown(self):
        pass

class fuw_tests(unittest.TestCase):
    def setUp(self):
        self.ip_address = '192.168.40.123'
        #self.ip_address = '192.168.40.104,4,192.168.1.20'
        #self.ip_address = '192.168.1.20'
        pass

    def test_pvp6_v11(self):
        print('')

        def progress_callback(description: str, total_bytes: int, current_bytes: int):
            progress = 100* current_bytes / total_bytes;
            print(f"{description} progress: {progress:.2f}% complete, {current_bytes} of {total_bytes} bytes.")

        self.fuw_helper_path = os.path.join(FIRMWARE_FOLDER_PATH, 'Helper', 'v15', 'FUWhelper6xX.dll')
        self.fuw_image_path = os.path.join(FIRMWARE_FOLDER_PATH, 'FUC', 'PVP6', 'ME_PVP6xX_11.00-20190915', 'upgrade', 'SC.IMG')
        print(self.fuw_helper_path)
        print(self.fuw_image_path)
        meu = MEUtility(self.ip_address, driver='pycomm3')
        resp = meu.flash_firmware(self.fuw_image_path, self.fuw_helper_path, progress_callback)
        for s in resp.device.log: print(s)
        print('')

    def test_pvp6_v12(self):
        print('')

        def progress_callback(description: str, total_bytes: int, current_bytes: int):
            progress = 100* current_bytes / total_bytes;
            print(f"{description} progress: {progress:.2f}% complete, {current_bytes} of {total_bytes} bytes.")

        self.fuw_helper_path = os.path.join(FIRMWARE_FOLDER_PATH, 'Helper', 'v15', 'FUWhelper6xX.dll')
        self.fuw_image_path = os.path.join(FIRMWARE_FOLDER_PATH, 'FUC', 'PVP6', 'ME_PVP6xX_12.00-20200922', 'upgrade', 'SC.IMG')
        print(self.fuw_helper_path)
        print(self.fuw_image_path)
        meu = MEUtility(self.ip_address, driver='pylogix')
        resp = meu.flash_firmware(self.fuw_image_path, self.fuw_helper_path, progress_callback)
        for s in resp.device.log: print(s)
        print('')

    def tearDown(self):
        pass

class fuwhelper_tests(unittest.TestCase):
    def setUp(self):
        print('')
        for (device, driver, comms_path) in test_combinations:
            with comms.Driver(comms_path, driver=driver) as cip:
                device2 = terminal.validation.get_terminal_info(cip)
                if device.local_firmware_helper_path:
                    fuw_helper_file = types.MEFile('FUWhelper.dll',
                                                True,
                                                True,
                                                device.local_firmware_helper_path)
                    resp = terminal.actions.download_file(cip, device2, fuw_helper_file, '\\Storage Card')

    def test_get_process_running(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            with comms.Driver(comms_path, driver=driver) as cip:
                if device.local_firmware_helper_path:
                    value = terminal.fuwhelper.get_process_running(cip, device.device_paths, MERUNTIME_PROCESS)
                    result = (
                        f'Device: {device.name}\n' 
                        f'Driver: {driver}\n' 
                        f'Path: {comms_path}\n'
                        f'Function: {terminal.fuwhelper.FuwHelperFunctions.GET_PROCESS_RUNNING}\n'
                        f'Value: {value}\n'
                    )
                    print(result)
                    self.assertEqual(value, True)
                    results.append(value)
        self.assertTrue(all(x == results[0] for x in results))

    def test_get_process_running_nonexistent(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            with comms.Driver(comms_path, driver=driver) as cip:
                if device.local_firmware_helper_path:
                    value = terminal.fuwhelper.get_process_running(cip, device.device_paths, NONEXISTENT_PROCESS)
                    result = (
                        f'Device: {device.name}\n' 
                        f'Driver: {driver}\n' 
                        f'Path: {comms_path}\n'
                        f'Function: {terminal.fuwhelper.FuwHelperFunctions.GET_PROCESS_RUNNING}\n'
                        f'Value: {value}\n'
                    )
                    print(result)
                    self.assertEqual(value, False)
                    results.append(value)
        self.assertTrue(all(x == results[0] for x in results))

    def test_stop_me(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            with comms.Driver(comms_path, driver=driver) as cip:
                if device.local_firmware_helper_path:
                    value = terminal.fuwhelper.stop_process_me(cip, device.device_paths)
                    result = (
                        f'Device: {device.name}\n' 
                        f'Driver: {driver}\n' 
                        f'Path: {comms_path}\n'
                        f'Function: {terminal.fuwhelper.FuwHelperFunctions.STOP_PROCESS_ME}\n'
                        f'Value: {value}\n'
                    )
                    print(result)
                    self.assertEqual(value, True)
                    results.append(value)
        self.assertTrue(all(x == results[0] for x in results))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()