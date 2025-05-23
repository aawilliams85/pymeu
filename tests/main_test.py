import time
import unittest

from pymeu import comms
from pymeu import MEUtility
from pymeu import terminal
from pymeu import types

from config import *

# Turn off sort so that tests run in line order
unittest.TestLoader.sortTestMethodsUsing = None

class download_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_download_bad_ext(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                meu = MEUtility(device.comms_path, driver=driver)
                download_file_path = os.path.join(DOWNLOAD_FOLDER_PATH, device.mer_files[0].replace('.mer','.zzz'))
                result = (
                        f'Device: {device.name}\n'
                        f'Driver: {driver}\n'
                        f'Function: download({download_file_path}, overwrite=True)\n'
                )
                print(result)
                resp = meu.download(download_file_path, overwrite=True)
                for s in resp.device.log: print(s)
                print('')
                self.assertEqual(resp.status, types.MEResponseStatus.FAILURE)

    def test_download_overwrite(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                meu = MEUtility(device.comms_path, driver=driver)
                download_file_path = os.path.join(DOWNLOAD_FOLDER_PATH, device.mer_files[0])
                result = (
                        f'Device: {device.name}\n'
                        f'Driver: {driver}\n'
                        f'Function: download({download_file_path}, overwrite=True)\n'
                )
                print(result)
                resp = meu.download(download_file_path, overwrite=True)
                for s in resp.device.log: print(s)
                print('')
                self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)
                time.sleep(device.boot_time_sec)

    def test_download_as_overwrite(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                meu = MEUtility(device.comms_path, driver=driver)
                download_file_path = os.path.join(DOWNLOAD_FOLDER_PATH, device.mer_files[0])
                result = (
                        f'Device: {device.name}\n'
                        f'Driver: {driver}\n'
                        f'Function: download({download_file_path}, overwrite=True, remote_file_name={device.mer_files[1]})\n'
                )
                print(result)
                resp = meu.download(download_file_path, overwrite=True, remote_file_name=device.mer_files[1])
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

    def test_upload_bad_nonexistent(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                meu = MEUtility(device.comms_path, driver=driver)
                upload_file_path = os.path.join(UPLOAD_FOLDER_PATH, 'Nonexistent_Project.mer')
                result = (
                        f'Device: {device.name}\n'
                        f'Driver: {driver}\n'
                        f'Function: upload({upload_file_path}, overwrite=True)\n'
                )
                print(result)
                resp = meu.upload(upload_file_path, overwrite=True)
                for s in resp.device.log: print(s)
                print('')
                self.assertEqual(resp.status, types.MEResponseStatus.FAILURE)

    def test_upload_overwrite(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                meu = MEUtility(device.comms_path, driver=driver)
                upload_file_path = os.path.join(UPLOAD_FOLDER_PATH, device.name, driver, device.mer_files[0])
                result = (
                        f'Device: {device.name}\n'
                        f'Driver: {driver}\n'
                        f'Function: upload({upload_file_path}, overwrite=True)\n'
                )
                print(result)
                resp = meu.upload(upload_file_path, overwrite=True)
                for s in resp.device.log: print(s)
                print('')
                self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)

    def test_upload_all_overwrite(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                meu = MEUtility(device.comms_path, driver=driver)
                upload_folder_path = os.path.join(UPLOAD_FOLDER_PATH, device.name, driver)
                result = (
                        f'Device: {device.name}\n'
                        f'Driver: {driver}\n'
                        f'Function: upload_all({UPLOAD_FOLDER_PATH}, overwrite=True)\n'
                )
                print(result)
                resp = meu.upload_all(upload_folder_path, overwrite=True)
                for s in resp.device.log: print(s)
                print('')
                self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)

    def test_upload_multiple_instances(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                meu = MEUtility(device.comms_path, driver=driver)
                upload_file_path = os.path.join(UPLOAD_FOLDER_PATH, device.name, driver, device.mer_files[0])
                result = (
                        f'Device: {device.name}\n'
                        f'Driver: {driver}\n'
                        f'Function: upload({upload_file_path}, overwrite=True) with multiple instances\n'
                )
                print(result)

                with comms.Driver(device.comms_path, driver=driver) as cip2:
                    # Open parallel transfer instance (normally transfer instance 1)
                    device2 = terminal.validation.get_terminal_info(cip2)
                    path2 = f'{device2.paths.runtime}\\{device.mer_files[0]}'
                    transfer_instance_2 = terminal.files.create_transfer_instance_upload(cip2, path2)

                    # Perform upload (normally transfer instance 2)
                    resp = meu.upload(upload_file_path, overwrite=True)
                    for s in resp.device.log: print(s)
                    print('')
                    self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)

                    # Close parallel transfer instance
                    terminal.files.delete_transfer_instance(cip2, transfer_instance_2)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()