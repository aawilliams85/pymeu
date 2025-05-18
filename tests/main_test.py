import time
import unittest

from pymeu import MEUtility

from config import *

# Turn off sort so that tests run in line order
unittest.TestLoader.sortTestMethodsUsing = None

class download_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_download_overwrite(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                meu = MEUtility(device.comms_path, driver=driver)
                result = (
                        f'Device: {device.name}\n'
                        f'Driver: {driver}\n'
                        f'Function: download({device.download_paths[0]}, overwrite=True)\n'
                )
                print(result)
                resp = meu.download(device.download_paths[0], overwrite=True)
                for s in resp.device.log: print(s)
                print('')
                self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)
                time.sleep(device.boot_time_sec)

    def test_download_as_overwrite(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                meu = MEUtility(device.comms_path, driver=driver)
                result = (
                        f'Device: {device.name}\n'
                        f'Driver: {driver}\n'
                        f'Function: download({device.download_paths[0]}, overwrite=True, remote_file_name={device.mer_files[1]})\n'
                )
                print(result)
                resp = meu.download(device.download_paths[0], overwrite=True, remote_file_name=device.mer_files[1])
                for s in resp.device.log: print(s)
                print('')
                self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)
                time.sleep(device.boot_time_sec)

    def tearDown(self):
        pass

class info_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_terminal_info_vanilla(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                meu = MEUtility(device.comms_path, driver=driver)
                result = (
                        f'Device: {device.name}\n'
                        f'Driver: {driver}\n'
                        f'Function: get_terminal_info\n'
                )
                print(result)
                meu.get_terminal_info()

    def test_get_terminal_info_print(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                meu = MEUtility(device.comms_path, driver=driver)
                result = (
                        f'Device: {device.name}\n'
                        f'Driver: {driver}\n'
                        f'Function: get_terminal_info(print_log=True)\n'
                )
                print(result)
                meu.get_terminal_info(print_log=True)
                print('')

    def test_get_terminal_info_redacted(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                meu = MEUtility(device.comms_path, driver=driver)
                result = (
                        f'Device: {device.name}\n'
                        f'Driver: {driver}\n'
                        f'Function: get_terminal_info(print_log=True, redact_log=True)\n'
                )
                print(result)
                meu.get_terminal_info(print_log=True, redact_log=True)
                print('')

    def test_get_terminal_info_silent(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                meu = MEUtility(device.comms_path, driver=driver)
                result = (
                        f'Device: {device.name}\n'
                        f'Driver: {driver}\n'
                        f'Function: get_terminal_info(print_log=True, silent_mode=True)\n'
                )
                print(result)
                meu.get_terminal_info(print_log=True, silent_mode=True)
                print('')

    def tearDown(self):
        pass

class reboot_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_reboot(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                meu = MEUtility(device.comms_path, driver=driver)
                result = (
                        f'Device: {device.name}\n'
                        f'Driver: {driver}\n'
                        f'Function: reboot()\n'
                )
                print(result)
                resp = meu.reboot()
                for s in resp.device.log: print(s)
                print('')
                self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)
                time.sleep(device.boot_time_sec)

    def tearDown(self):
        pass    

class upload_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_upload_all(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                meu = MEUtility(device.comms_path, driver=driver)
                result = (
                        f'Device: {device.name}\n'
                        f'Driver: {driver}\n'
                        f'Function: upload_all({UPLOAD_FOLDER_PATH}, overwrite=True)\n'
                )
                print(result)
                resp = meu.upload_all(UPLOAD_FOLDER_PATH, overwrite=True)
                for s in resp.device.log: print(s)
                print('')
                self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()