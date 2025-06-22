import os
import time
import unittest

from pymeu import actions
from pymeu import comms
from pymeu import dmk
from pymeu import MEUtility
from pymeu import terminal
from pymeu import types
from pymeu import validation

from config import *

# Turn off sort so that tests run in line order
unittest.TestLoader.sortTestMethodsUsing = None

class dmk_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_dmk_unpack(self):
        print('')

#        firmware_image_path = os.path.join(FIRMWARE_FOLDER_PATH, 'DMK', 'PVP7B', '2711P-PanelView_Plus_7_Performance_15.100.dmk')
        firmware_image_path = os.path.join(FIRMWARE_FOLDER_PATH, 'DMK', 'PVP7B', '2711P-PVP7_Performance_12.104.dmk')
        meu = MEUtility('192.168.40.23')
        meu.flash_firmware_me(firmware_image_path, '', progress_callback)
        #with comms.Driver('192.168.40.23', driver='pycomm3') as cip:
        #    print(messages.get_identity(cip))
        #    dmk.process_dmk(cip, firmware_image_path, progress_callback)
        print('')

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
            resp = meu.flash_firmware_me(firmware_image_path,'')
            for s in resp.device.log: print(s)
            print('')
            self.assertEqual(resp.status, types.MEResponseStatus.FAILURE)

    def tearDown(self):
        pass

class fuw_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_flash_pvp6(self):
        print('')
        for (device, driver, comms_path) in test_combinations:
            if (device.name != PVP6): continue #Only flash PVP6 in this test

            meu = MEUtility(comms_path, driver=driver)
            firmware_image_path = device.local_firmware_image_paths[0]   
            firmware_helper_path = device.local_firmware_helper_path         
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: flash_firmware({firmware_image_path})\n'
            )
            print(result)
            resp = meu.flash_firmware_me(
                firmware_image_path=firmware_image_path,
                firmware_helper_path=firmware_helper_path,
                dry_run=False,
                progress=progress_callback)
            for s in resp.device.log: print(s)
            print('')
            self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)
            time.sleep(device.boot_time_sec)

    def test_flash_pvp6_direct_pycomm3(self):
        print('')
        driver = DRIVER_PYCOMM3
        device = DEVICE_PVP6
        comms_path = device.comms_paths[0]

        meu = MEUtility(comms_path, driver=driver)
        firmware_image_path = device.local_firmware_image_paths[0]   
        firmware_helper_path = device.local_firmware_helper_path         
        result = (
                f'Device: {device.name}\n'
                f'Driver: {driver}\n'
                f'Path: {comms_path}\n'
                f'Function: flash_firmware({firmware_image_path})\n'
        )
        print(result)
        resp = meu.flash_firmware_me(
            firmware_image_path=firmware_image_path,
            firmware_helper_path=firmware_helper_path,
            dry_run=False,
            progress=progress_callback)
        for s in resp.device.log: print(s)
        print('')
        self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)
        time.sleep(device.boot_time_sec)

    def test_flash_pvp6_direct_pylogix(self):
        print('')
        driver = DRIVER_PYLOGIX
        device = DEVICE_PVP6
        comms_path = device.comms_paths[0]

        meu = MEUtility(comms_path, driver=driver)
        firmware_image_path = device.local_firmware_image_paths[0]   
        firmware_helper_path = device.local_firmware_helper_path         
        result = (
                f'Device: {device.name}\n'
                f'Driver: {driver}\n'
                f'Path: {comms_path}\n'
                f'Function: flash_firmware({firmware_image_path})\n'
        )
        print(result)
        resp = meu.flash_firmware_me(
            firmware_image_path=firmware_image_path,
            firmware_helper_path=firmware_helper_path,
            dry_run=False,
            progress=progress_callback)
        for s in resp.device.log: print(s)
        print('')
        self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)
        time.sleep(device.boot_time_sec)

    def test_flash_pvp6_routed_pycomm3(self):
        print('')
        driver = DRIVER_PYCOMM3
        device = DEVICE_PVP6
        comms_path = device.comms_paths[1]

        meu = MEUtility(comms_path, driver=driver)
        firmware_image_path = device.local_firmware_image_paths[0]   
        firmware_helper_path = device.local_firmware_helper_path         
        result = (
                f'Device: {device.name}\n'
                f'Driver: {driver}\n'
                f'Path: {comms_path}\n'
                f'Function: flash_firmware({firmware_image_path})\n'
        )
        print(result)
        resp = meu.flash_firmware_me(
            firmware_image_path=firmware_image_path,
            firmware_helper_path=firmware_helper_path,
            dry_run=False,
            progress=progress_callback)
        for s in resp.device.log: print(s)
        print('')
        self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)
        time.sleep(device.boot_time_sec)

    def test_flash_pvp6_routed_pylogix(self):
        print('')
        driver = DRIVER_PYLOGIX
        device = DEVICE_PVP6
        comms_path = device.comms_paths[1]

        meu = MEUtility(comms_path, driver=driver)
        firmware_image_path = device.local_firmware_image_paths[0]   
        firmware_helper_path = device.local_firmware_helper_path         
        result = (
                f'Device: {device.name}\n'
                f'Driver: {driver}\n'
                f'Path: {comms_path}\n'
                f'Function: flash_firmware({firmware_image_path})\n'
        )
        print(result)
        resp = meu.flash_firmware_me(
            firmware_image_path=firmware_image_path,
            firmware_helper_path=firmware_helper_path,
            dry_run=False,
            progress=progress_callback)
        for s in resp.device.log: print(s)
        print('')
        self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)
        time.sleep(device.boot_time_sec)

    def tearDown(self):
        pass

class fuwhelper_tests(unittest.TestCase):
    def setUp(self):
        print('')
        for (device, driver, comms_path) in test_combinations:
            with comms.Driver(comms_path, driver=driver) as cip:
                device2 = validation.get_terminal_info(cip)
                if device.local_firmware_helper_path:
                    fuw_helper_file = types.MEFile('FUWhelper.dll',
                                                True,
                                                True,
                                                device.local_firmware_helper_path)
                    resp = actions.download_file(cip, device2, fuw_helper_file, '\\Storage Card')

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