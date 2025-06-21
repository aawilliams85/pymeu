import filecmp
import time
import unittest

from pymeu import comms
from pymeu import MEUtility
from pymeu import terminal
from pymeu import types
from pymeu import validation

from config import *

# Turn off sort so that tests run in line order
unittest.TestLoader.sortTestMethodsUsing = None

class download_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_download_bad_ext(self):
        print('')
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            download_file_path = os.path.join(DOWNLOAD_FOLDER_PATH, device.mer_files[0].replace('.mer','.zzz'))
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: download({download_file_path}, overwrite=True)\n'
            )
            print(result)
            resp = meu.download(download_file_path, overwrite=True)
            for s in resp.device.log: print(s)
            print('')
            self.assertEqual(resp.status, types.MEResponseStatus.FAILURE)

    def test_download_multiple(self):
        print('')
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            for mer_file in device.mer_files:
                download_file_path = os.path.join(DOWNLOAD_FOLDER_PATH, mer_file)
                result = (
                        f'Device: {device.name}\n'
                        f'Driver: {driver}\n'
                        f'Path: {comms_path}\n'
                        f'Function: download({download_file_path}, overwrite=True)\n'
                )
                print(result)
                resp = meu.download(download_file_path, overwrite=True, run_at_startup=False)
                for s in resp.device.log: print(s)
                print('')
                self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)

    def test_download_overwrite(self):
        print('')
        count = 0
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            download_file_path = os.path.join(DOWNLOAD_FOLDER_PATH, device.mer_files[0])
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: download({download_file_path}, overwrite=True)\n'
            )
            print(result)
            resp = meu.download(download_file_path, overwrite=True)
            for s in resp.device.log: print(s)
            print('')
            self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)
            count += 1
            if (count % len(DEVICES)) == 0: time.sleep(device.boot_time_sec)

    def test_download_overwrite_progress(self):
        print('')

        def progress_callback(description: str, total_bytes: int, current_bytes: int):
            progress = 100* current_bytes / total_bytes
            print(f"{description} progress: {progress:.2f}% complete, {current_bytes} of {total_bytes} bytes.")

        count = 0
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            download_file_path = os.path.join(DOWNLOAD_FOLDER_PATH, device.mer_files[0])
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: download({download_file_path}, overwrite=True)\n'
            )
            print(result)
            resp = meu.download(download_file_path, progress_callback, overwrite=True, run_at_startup=False)
            for s in resp.device.log: print(s)
            print('')
            self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)
            count += 1
            #if (count % len(DEVICES)) == 0: time.sleep(device.boot_time_sec)


    def test_download_as_overwrite(self):
        print('')
        count = 0
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            download_file_path = os.path.join(DOWNLOAD_FOLDER_PATH, device.mer_files[0])
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: download({download_file_path}, overwrite=True, remote_file_name={device.mer_files[1]})\n'
            )
            print(result)
            resp = meu.download(download_file_path, overwrite=True, remote_file_name=device.mer_files[1])
            for s in resp.device.log: print(s)
            print('')
            self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)
            count += 1
            if (count % len(DEVICES)) == 0: time.sleep(device.boot_time_sec)

    def tearDown(self):
        pass

class info_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_terminal_info_vanilla(self):
        print('')
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: get_terminal_info\n'
            )
            print(result)
            meu.get_terminal_info()

    def test_get_terminal_info_print(self):
        print('')
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: get_terminal_info(print_log=True)\n'
            )
            print(result)
            meu.get_terminal_info(print_log=True)
            print('')

    def test_get_terminal_info_redacted(self):
        print('')
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: get_terminal_info(print_log=True, redact_log=True)\n'
            )
            print(result)
            meu.get_terminal_info(print_log=True, redact_log=True)
            print('')

    def test_get_terminal_info_silent(self):
        print('')
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
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
        count = 0
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: reboot()\n'
            )
            print(result)
            resp = meu.reboot()
            for s in resp.device.log: print(s)
            print('')
            self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)
            count += 1
            if (count % len(DEVICES)) == 0: time.sleep(device.boot_time_sec)

    def tearDown(self):
        pass    

class upload_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_upload_bad_nonexistent(self):
        print('')
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            upload_file_path = os.path.join(UPLOAD_FOLDER_PATH, 'Nonexistent_Project.mer')
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: upload({upload_file_path}, overwrite=True)\n'
            )
            print(result)
            resp = meu.upload(upload_file_path, overwrite=True)
            for s in resp.device.log: print(s)
            print('')
            self.assertEqual(resp.status, types.MEResponseStatus.FAILURE)

    def test_upload_overwrite(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            upload_file_path = os.path.join(UPLOAD_FOLDER_PATH, device.name, driver, device.mer_files[0])
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: upload({upload_file_path}, overwrite=True)\n'
            )
            print(result)
            resp = meu.upload(upload_file_path, overwrite=True)
            for s in resp.device.log: print(s)
            print('')
            self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)
            #results.append(upload_file_path)
        #self.assertTrue(all(filecmp.cmp(results[0], x, shallow=False) for x in results))

    def test_upload_overwrite_progress(self):
        print('')

        def progress_callback(description: str, total_bytes: int, current_bytes: int):
            progress = 100* current_bytes / total_bytes
            print(f"{description} progress: {progress:.2f}% complete, {current_bytes} of {total_bytes} bytes.")

        results = []
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            upload_file_path = os.path.join(UPLOAD_FOLDER_PATH, device.name, driver, device.mer_files[0])
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: upload({upload_file_path}, overwrite=True)\n'
            )
            print(result)
            resp = meu.upload(upload_file_path, progress_callback, overwrite=True)
            for s in resp.device.log: print(s)
            print('')
            self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)
            #results.append(upload_file_path)
        #self.assertTrue(all(filecmp.cmp(results[0], x, shallow=False) for x in results))

    def test_upload_all_overwrite(self):
        print('')
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            upload_folder_path = os.path.join(UPLOAD_FOLDER_PATH, device.name, driver)
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: upload_all({UPLOAD_FOLDER_PATH}, overwrite=True)\n'
            )
            print(result)
            resp = meu.upload_all(upload_folder_path, overwrite=True)
            for s in resp.device.log: print(s)
            print('')
            self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)

    def test_upload_all_overwrite_progress(self):
        print('')

        def progress_callback(description: str, total_bytes: int, current_bytes: int):
            progress = 100* current_bytes / total_bytes
            print(f"{description} progress: {progress:.2f}% complete, {current_bytes} of {total_bytes} bytes.")

        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            upload_folder_path = os.path.join(UPLOAD_FOLDER_PATH, device.name, driver)
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: upload_all({UPLOAD_FOLDER_PATH}, overwrite=True)\n'
            )
            print(result)
            resp = meu.upload_all(upload_folder_path, progress_callback, overwrite=True)
            for s in resp.device.log: print(s)
            print('')
            self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)

    def test_upload_multiple_instances(self):
        print('')
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            upload_file_path = os.path.join(UPLOAD_FOLDER_PATH, device.name, driver, device.mer_files[0])
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: upload({upload_file_path}, overwrite=True) with multiple instances\n'
            )
            print(result)

            with comms.Driver(comms_path, driver=driver) as cip2:
                # Open parallel transfer instance (normally transfer instance 1)
                device2 = validation.get_terminal_info(cip2)
                path2 = f'{device2.me_paths.runtime}\\{device.mer_files[0]}'
                transfer_instance_2, transfer_size_2 = terminal.files.create_transfer_instance_upload(cip2, path2)

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