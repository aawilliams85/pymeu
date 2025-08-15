import glob
import time
import unittest

from pymeu import comms
from pymeu import MEUtility
from pymeu import me
from pymeu.me import util
from pymeu.me import types
from pymeu.me import validation

from config import *

# Turn off sort so that tests run in line order
unittest.TestLoader.sortTestMethodsUsing = None

class helper_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_create_folder(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            folder_path = device.device_paths.runtime
            with comms.Driver(comms_path, driver=driver) as cip:
                value = me.helper.create_folder(cip, device.device_paths, folder_path)
                result = (
                    f'Device: {device.name}\n' 
                    f'Driver: {driver}\n' 
                    f'Path: {comms_path}\n'
                    f'Function: {me.helper.HelperFunctions.CREATE_FOLDER} {folder_path}\n'
                    f'Value: {value}\n'
                )
                print(result)
                self.assertEqual(value, True)
                results.append(value)
        self.assertTrue(all(x == results[0] for x in results))

    '''
    # This is half-baked.
    #
    # The PVP5 accepts the invalid path and then seems to answer that the folder exists in other tests,
    # until reboot.
    # The PVP6 rejects the invalid path and throws an exception.

    def test_create_folder_bad_nonexistent(self):
        print('')
        for device in DEVICES:
            results = []
            for driver in DRIVERS:
                folder_path = NONEXISTENT_FOLDER
                with comms.Driver(device.comms_path, driver=driver) as cip:
                    result = (
                        f'Device: {device.name}\n' 
                        f'Driver: {driver}\n' 
                        f'Path: {device.comms_path}\n'
                        f'Function: {terminal.helper.HelperFunctions.CREATE_FOLDER} {folder_path}\n'
                    )
                    print(result)
                    with self.assertRaises(Exception):
                        terminal.helper.create_folder(cip, device.device_paths, folder_path)
    '''

    def test_get_file_exists(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            file_path = device.device_paths.helper_file
            with comms.Driver(comms_path, driver=driver) as cip:
                value = me.helper.get_file_exists(cip, device.device_paths, file_path)
                result = (
                    f'Device: {device.name}\n' 
                    f'Driver: {driver}\n' 
                    f'Path: {comms_path}\n'
                    f'Function: {me.helper.HelperFunctions.GET_FILE_EXISTS} {file_path}\n'
                    f'Value: {value}\n'
                )
                print(result)
                self.assertEqual(value, True)
                results.append(value)
        self.assertTrue(all(x == results[0] for x in results))

    def test_get_file_exists_bad_nonexistent(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            file_path = NONEXISTENT_FILE
            with comms.Driver(comms_path, driver=driver) as cip:
                value = me.helper.get_file_exists(cip, device.device_paths, file_path)
                result = (
                    f'Device: {device.name}\n' 
                    f'Driver: {driver}\n' 
                    f'Path: {comms_path}\n'
                    f'Function: {me.helper.HelperFunctions.GET_FILE_EXISTS} {file_path}\n'
                    f'Value: {value}\n'
                )
                print(result)
                self.assertEqual(value, False)
                results.append(value)
        self.assertTrue(all(x == results[0] for x in results))

    def test_get_file_size(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            file_path = device.device_paths.helper_file
            with comms.Driver(comms_path, driver=driver) as cip:
                value = me.helper.get_file_size(cip, device.device_paths, file_path)
                result = (
                    f'Device: {device.name}\n' 
                    f'Driver: {driver}\n' 
                    f'Path: {comms_path}\n'
                    f'Function: {me.helper.HelperFunctions.GET_FILE_SIZE} {file_path}\n'
                    f'Value: {value}\n'
                )
                print(result)
                self.assertGreater(value, 0)
                results.append(value)
        #self.assertTrue(all(x == results[0] for x in results))

    def test_get_file_size_bad_nonexistent(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            file_path = NONEXISTENT_FILE
            with comms.Driver(comms_path, driver=driver) as cip:
                result = (
                    f'Device: {device.name}\n' 
                    f'Driver: {driver}\n' 
                    f'Path: {comms_path}\n'
                    f'Function: {me.helper.HelperFunctions.GET_FILE_SIZE} {file_path}\n'
                )
                print(result)
                with self.assertRaises(FileNotFoundError):
                    me.helper.get_file_size(cip, device.device_paths, file_path)
        #self.assertTrue(all(x == results[0] for x in results))

    def test_get_folder_exists(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            folder_path = device.device_paths.storage
            with comms.Driver(comms_path, driver=driver) as cip:
                value = me.helper.get_folder_exists(cip, device.device_paths, folder_path)
                result = (
                    f'Device: {device.name}\n' 
                    f'Driver: {driver}\n' 
                    f'Path: {comms_path}\n'
                    f'Function: {me.helper.HelperFunctions.GET_FOLDER_EXISTS} {folder_path}\n'
                    f'Value: {value}\n'
                )
                print(result)
                self.assertEqual(value, True)
                results.append(value)
        self.assertTrue(all(x == results[0] for x in results))

    def test_get_folder_exists_bad_nonexistent(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            folder_path = NONEXISTENT_FOLDER
            with comms.Driver(comms_path, driver=driver) as cip:
                value = me.helper.get_folder_exists(cip, device.device_paths, folder_path)
                result = (
                    f'Device: {device.name}\n' 
                    f'Driver: {driver}\n' 
                    f'Path: {comms_path}\n'
                    f'Function: {me.helper.HelperFunctions.GET_FOLDER_EXISTS} {folder_path}\n'
                    f'Value: {value}\n'
                )
                print(result)
                self.assertEqual(value, False)
                results.append(value)
        self.assertTrue(all(x == results[0] for x in results))

    def test_get_free_space(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            folder_path = f'{device.device_paths.runtime}\\'
            with comms.Driver(comms_path, driver=driver) as cip:
                value = me.helper.get_free_space(cip, device.device_paths, folder_path)
                result = (
                    f'Device: {device.name}\n' 
                    f'Driver: {driver}\n' 
                    f'Path: {comms_path}\n'
                    f'Function: {me.helper.HelperFunctions.GET_FREE_SPACE} {folder_path}\n'
                    f'Value: {value}\n'
                )
                print(result)
                self.assertGreater(value, 0)
                results.append(value)
        #self.assertTrue(all(x == results[0] for x in results))

    def test_get_free_space_bad_nonexistent(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            folder_path = f'{NONEXISTENT_FOLDER}\\'
            with comms.Driver(comms_path, driver=driver) as cip:
                result = (
                    f'Device: {device.name}\n' 
                    f'Driver: {driver}\n' 
                    f'Path: {comms_path}\n'
                    f'Function: {me.helper.HelperFunctions.GET_FREE_SPACE} {folder_path}\n'
                )
                print(result)
                with self.assertRaises(FileNotFoundError):
                    me.helper.get_free_space(cip, device.device_paths, folder_path)

    def test_get_version(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            file_path = device.device_paths.helper_file
            with comms.Driver(comms_path, driver=driver) as cip:
                value = me.helper.get_version(cip, device.device_paths, file_path)
                result = (
                    f'Device: {device.name}\n' 
                    f'Driver: {driver}\n' 
                    f'Path: {comms_path}\n'
                    f'Function: {me.helper.HelperFunctions.GET_VERSION} {file_path}\n'
                    f'Value: {value}\n'
                )
                print(result)
                self.assertIsNotNone(value)
                results.append(value)
        #self.assertTrue(all(x == results[0] for x in results))

    def test_get_version_bad_nonexistent(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            file_path = NONEXISTENT_FILE
            with comms.Driver(comms_path, driver=driver) as cip:
                result = (
                    f'Device: {device.name}\n' 
                    f'Driver: {driver}\n' 
                    f'Path: {comms_path}\n'
                    f'Function: {me.helper.HelperFunctions.GET_VERSION} {file_path}\n'
                )
                print(result)
                with self.assertRaises(FileNotFoundError):
                    me.helper.get_version(cip, device.device_paths, file_path)

    def tearDown(self):
        pass

class registry_tests(unittest.TestCase):
    def setUp(self):
        self.skip_pairs = {
            PVP5: {
                me.registry.RegKeys.ME_STARTUP_APP,
                me.registry.RegKeys.ME_STARTUP_DELETE_LOGS,
                me.registry.RegKeys.ME_STARTUP_LOAD_CURRENT,
                me.registry.RegKeys.ME_STARTUP_OPTIONS,
                me.registry.RegKeys.ME_STARTUP_REPLACE_COMMS
            },
        }

    def test_read_registry(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            file_path = device.device_paths.helper_file
            with comms.Driver(comms_path, driver=driver) as cip:
                kvp = []
                for key in me.registry.RegKeys:
                    if device.name in self.skip_pairs and key in self.skip_pairs[device.name]:
                        value = 'Skipping known failure.'
                    else:
                        value = f'Value: {me.registry.get_value(cip, [key])}'

                    result = (
                        f'Device: {device.name}\n'
                        f'Driver: {driver}\n'
                        f'Path: {comms_path}\n'
                        f'Key: {key}\n'
                        f'{value}\n'
                    )
                    print(result)
                    kvp.append(f'{key},{value}')
                results.append(kvp)
        #self.assertTrue(all(x == results[0] for x in results))

    def tearDown(self):
        pass

class download_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_download_bad_ext(self):
        print('')
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            download_file_path = os.path.join(LOCAL_INPUT_MER_PATH, device.mer_files[0].replace('.mer','.zzz'))
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
            self.assertEqual(resp.status, types.ResponseStatus.FAILURE)

    def test_download_multiple(self):
        print('')
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            for mer_file in device.mer_files:
                download_file_path = os.path.join(LOCAL_INPUT_MER_PATH, mer_file)
                result = (
                        f'Device: {device.name}\n'
                        f'Driver: {driver}\n'
                        f'Path: {comms_path}\n'
                        f'Function: download({download_file_path}, overwrite=True)\n'
                )
                print(result)
                resp = meu.download(
                    file_path_local=download_file_path,
                    file_name_terminal=None,
                    delete_logs=False,
                    overwrite=True,
                    replace_comms=False,
                    run_at_startup=False,
                    progress=None
                )
                for s in resp.device.log: print(s)
                print('')
                self.assertEqual(resp.status, types.ResponseStatus.SUCCESS)

    def test_download_overwrite(self):
        print('')
        count = 0
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            download_file_path = os.path.join(LOCAL_INPUT_MER_PATH, device.mer_files[0])
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
            self.assertEqual(resp.status, types.ResponseStatus.SUCCESS)
            count += 1
            if (count % len(DEVICES)) == 0: time.sleep(device.boot_time_sec)

    def test_download_overwrite_progress(self):
        print('')
        count = 0
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            download_file_path = os.path.join(LOCAL_INPUT_MER_PATH, device.mer_files[0])
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: download({download_file_path}, overwrite=True)\n'
            )
            print(result)
            resp = meu.download(download_file_path, overwrite=True, progress=progress_callback)
            for s in resp.device.log: print(s)
            print('')
            self.assertEqual(resp.status, types.ResponseStatus.SUCCESS)
            count += 1
            if (count % len(DEVICES)) == 0: time.sleep(device.boot_time_sec)

    def test_download_overwrite_single(self):
        print('')
        count = 0
        for device in DEVICES:
            comms_path = device.comms_paths[1]
            driver = DRIVERS[1]
            meu = MEUtility(comms_path=comms_path, driver=driver)
            download_file_path = os.path.join(LOCAL_INPUT_MER_PATH, device.mer_files[0])
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: download({download_file_path}, overwrite=True)\n'
            )
            print(result)
            resp = meu.download(
                file_path_local=download_file_path,
                file_name_terminal=None,
                delete_logs=False,
                overwrite=True,
                replace_comms=False,
                run_at_startup=False,
                progress=None
            )
            for s in resp.device.log: print(s)
            print('')
            self.assertEqual(resp.status, types.ResponseStatus.SUCCESS)

    def test_download_as_overwrite(self):
        print('')
        count = 0
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            download_file_path = os.path.join(LOCAL_INPUT_MER_PATH, device.mer_files[0])
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: download({download_file_path}, overwrite=True, remote_file_name={device.mer_files[1]})\n'
            )
            print(result)
            resp = meu.download(download_file_path, overwrite=True, file_name_terminal=os.path.basename(device.mer_files[1]))
            for s in resp.device.log: print(s)
            print('')
            self.assertEqual(resp.status, types.ResponseStatus.SUCCESS)
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
            self.assertEqual(resp.status, types.ResponseStatus.SUCCESS)
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
            upload_file_path = os.path.join(LOCAL_OUTPUT_MER_PATH, 'Nonexistent_Project.mer')
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
            self.assertEqual(resp.status, types.ResponseStatus.FAILURE)

    def test_upload_overwrite(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            upload_file_path = os.path.join(LOCAL_OUTPUT_MER_PATH, device.name, driver, device.mer_files[0])
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
            self.assertEqual(resp.status, types.ResponseStatus.SUCCESS)
            #results.append(upload_file_path)
        #self.assertTrue(all(filecmp.cmp(results[0], x, shallow=False) for x in results))

    def test_upload_overwrite_progress(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            upload_file_path = os.path.join(LOCAL_OUTPUT_MER_PATH, device.name, driver, device.mer_files[0])
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: upload({upload_file_path}, overwrite=True)\n'
            )
            print(result)
            resp = meu.upload(upload_file_path, overwrite=True, progress=progress_callback)
            for s in resp.device.log: print(s)
            print('')
            self.assertEqual(resp.status, types.ResponseStatus.SUCCESS)
            #results.append(upload_file_path)
        #self.assertTrue(all(filecmp.cmp(results[0], x, shallow=False) for x in results))

    def test_upload_all_overwrite(self):
        print('')
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            upload_folder_path = os.path.join(LOCAL_OUTPUT_MER_PATH, device.name, driver)
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: upload_all({LOCAL_OUTPUT_MER_PATH}, overwrite=True)\n'
            )
            print(result)
            resp = meu.upload_all(upload_folder_path, overwrite=True)
            for s in resp.device.log: print(s)
            print('')
            self.assertEqual(resp.status, types.ResponseStatus.SUCCESS)

    def test_upload_all_overwrite_progress(self):
        print('')
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            upload_folder_path = os.path.join(LOCAL_OUTPUT_MER_PATH, device.name, driver)
            result = (
                    f'Device: {device.name}\n'
                    f'Driver: {driver}\n'
                    f'Path: {comms_path}\n'
                    f'Function: upload_all({LOCAL_OUTPUT_MER_PATH}, overwrite=True)\n'
            )
            print(result)
            resp = meu.upload_all(upload_folder_path, overwrite=True, progress=progress_callback)
            for s in resp.device.log: print(s)
            print('')
            self.assertEqual(resp.status, types.ResponseStatus.SUCCESS)

    def test_upload_multiple_instances(self):
        print('')
        for (device, driver, comms_path) in test_combinations:
            meu = MEUtility(comms_path, driver=driver)
            upload_file_path = os.path.join(LOCAL_OUTPUT_MER_PATH, device.name, driver, device.mer_files[0])
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
                transfer_instance_2, transfer_size_2 = me.transfer._create_upload(cip2, path2)

                # Perform upload (normally transfer instance 2)
                resp = meu.upload(upload_file_path, overwrite=True)
                for s in resp.device.log: print(s)
                print('')
                self.assertEqual(resp.status, types.ResponseStatus.SUCCESS)

                # Close parallel transfer instance
                me.transfer._delete(cip2, transfer_instance_2)

    def tearDown(self):
        pass

class decompress_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_fup_to_fuc_folder(self):
        print('')
        for file in glob.glob(os.path.join(LOCAL_INPUT_FUP_PATH, '*.fup')):
            print(file)
            start = time.time()
            me.firmware.fup_to_fuc_folder(
                input_path=file,
                output_path=os.path.join(LOCAL_OUTPUT_FUC_PATH, f'{os.path.basename(file)}'),
                progress=progress_callback
            )
            end = time.time()
            elapsed_time = end - start
            print(elapsed_time)

    def test_fup_to_fwc_folder(self):
        print('')
        for file in glob.glob(os.path.join(LOCAL_INPUT_FUP_PATH, '*.fup')):
            print(file)
            start = time.time()
            me.firmware.fup_to_fwc_folder(
                input_path=file,
                output_path=os.path.join(LOCAL_OUTPUT_FWC_PATH, f'{os.path.basename(file)}'),
                progress=progress_callback
            )           
            end = time.time()
            elapsed_time = end - start
            print(elapsed_time)

    def test_fup_to_otw_folder(self):
        print('')
        for file in glob.glob(os.path.join(LOCAL_INPUT_FUP_PATH, '*.fup')):
            print(file)
            start = time.time()
            me.firmware.fup_to_otw_folder(
                input_path=file,
                output_path=os.path.join(LOCAL_OUTPUT_OTW_PATH, f'{os.path.basename(file)}'),
                progress=progress_callback
            )
            end = time.time()
            elapsed_time = end - start
            print(elapsed_time)

    def test_apa_to_med_folder(self):
        print('')
        for file in STANDALONE_APA_FILES:
            print(file)
            start = time.time()
            me.application.apa_to_med_folder(
                input_path=file,
                output_path=os.path.join(LOCAL_OUTPUT_APA_PATH, f'{os.path.basename(file)}'),
                progress=progress_callback
            )
            end = time.time()
            elapsed_time = end - start
            print(elapsed_time)

    def test_mer_to_med_folder(self):
        print('')
        for file in STANDALONE_MER_FILES:
            print(file)
            start = time.time()
            me.application.mer_to_med_folder(
                input_path=file,
                output_path=os.path.join(LOCAL_OUTPUT_MER_PATH, f'{os.path.basename(file)}'),
                progress=progress_callback
            )
            end = time.time()
            elapsed_time = end - start
            print(elapsed_time)

    def tearDown(self):
        pass

class firmware_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_firmware_card(self):
        print('')
        fup_path = os.path.join(LOCAL_INPUT_FUP_PATH, 'ME_PVPCE4xX_5.10.16.09.WithAddins.WithViewPoint.fup')
        fwc_path = os.path.join(LOCAL_OUTPUT_FWC_PATH, 'ME_PVPCE4xX_5.10.16.09.WithAddins.WithViewPoint.fup')
        start = time.time()
        meu = MEUtility('localhost')
        meu.create_firmware_card(
            fup_path_local=fup_path,
            fwc_path_local=fwc_path,
            progress=progress_callback
        )
        end = time.time()
        elapsed_time = end - start
        print(elapsed_time)

    def test_flash_pvp5_direct_pycomm3(self):
        print('')
        driver = DRIVER_PYCOMM3
        device = DEVICE_PVP5
        comms_path = device.comms_paths[0]

        meu = MEUtility(comms_path, driver=driver)
        firmware_image_path = device.local_firmware_image_paths[0]   
        firmware_helper_path = device.local_firmware_helper_path
        firmware_cover_path = device.local_firmware_cover_path
        result = (
                f'Device: {device.name}\n'
                f'Driver: {driver}\n'
                f'Path: {comms_path}\n'
                f'Function: flash_firmware({firmware_image_path})\n'
        )
        print(result)
        resp = meu.flash_firmware(
            fup_path_local=firmware_image_path,
            fuwhelper_path_local=firmware_helper_path,
            fuwcover_path_local=firmware_cover_path,
            progress=progress_callback
        )
        for s in resp.device.log: print(s)
        print('')
        self.assertEqual(resp.status, types.ResponseStatus.SUCCESS)

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
        resp = meu.flash_firmware(
            fup_path_local=firmware_image_path,
            fuwhelper_path_local=firmware_helper_path,
            fuwcover_path_local=None,
            progress=progress_callback
        )
        for s in resp.device.log: print(s)
        print('')
        self.assertEqual(resp.status, types.ResponseStatus.SUCCESS)

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
        resp = meu.flash_firmware(
            fup_path_local=firmware_image_path,
            fuwhelper_path_local=firmware_helper_path,
            fuwcover_path_local=None,
            progress=progress_callback
        )
        for s in resp.device.log: print(s)
        print('')
        self.assertEqual(resp.status, types.ResponseStatus.SUCCESS)

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
        resp = meu.flash_firmware(
            fup_path_local=firmware_image_path,
            fuwhelper_path_local=firmware_helper_path,
            fuwcover_path_local=None,
            progress=progress_callback
        )
        for s in resp.device.log: print(s)
        print('')
        self.assertEqual(resp.status, types.ResponseStatus.SUCCESS)

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
        resp = meu.flash_firmware(
            fup_path_local=firmware_image_path,
            fuwhelper_path_local=firmware_helper_path,
            fuwcover_path_local=None,
            progress=progress_callback
        )
        for s in resp.device.log: print(s)
        print('')
        self.assertEqual(resp.status, types.ResponseStatus.SUCCESS)

    def test_flash_pvp7a_direct_pycomm3(self):
        print('')
        driver = DRIVER_PYCOMM3
        device = DEVICE_PVP7A
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
        resp = meu.flash_firmware(
            fup_path_local=firmware_image_path,
            fuwhelper_path_local=firmware_helper_path,
            fuwcover_path_local=None,
            progress=progress_callback
        )
        for s in resp.device.log: print(s)
        print('')
        self.assertEqual(resp.status, types.ResponseStatus.SUCCESS)

    def test_flash_pvp7a_direct_pylogix(self):
        print('')
        driver = DRIVER_PYLOGIX
        device = DEVICE_PVP7A
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
        resp = meu.flash_firmware(
            fup_path_local=firmware_image_path,
            fuwhelper_path_local=firmware_helper_path,
            fuwcover_path_local=None,
            progress=progress_callback
        )
        for s in resp.device.log: print(s)
        print('')
        self.assertEqual(resp.status, types.ResponseStatus.SUCCESS)

    def test_flash_pvp7a_routed_pycomm3(self):
        print('')
        driver = DRIVER_PYCOMM3
        device = DEVICE_PVP7A
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
        resp = meu.flash_firmware(
            fup_path_local=firmware_image_path,
            fuwhelper_path_local=firmware_helper_path,
            fuwcover_path_local=None,
            progress=progress_callback
        )
        for s in resp.device.log: print(s)
        print('')
        self.assertEqual(resp.status, types.ResponseStatus.SUCCESS)

    def test_flash_pvp7a_routed_pylogix(self):
        print('')
        driver = DRIVER_PYLOGIX
        device = DEVICE_PVP7A
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
        resp = meu.flash_firmware(
            fup_path_local=firmware_image_path,
            fuwhelper_path_local=firmware_helper_path,
            fuwcover_path_local=None,
            progress=progress_callback
        )
        for s in resp.device.log: print(s)
        print('')
        self.assertEqual(resp.status, types.ResponseStatus.SUCCESS)

    def tearDown(self):
        pass

class fuwhelper_tests(unittest.TestCase):
    def setUp(self):
        print('')
        for (device, driver, comms_path) in test_combinations:
            with comms.Driver(comms_path, driver=driver) as cip:
                if device.transfer_firmware_helper:
                    device2 = validation.get_terminal_info(cip)

                    # Determine if firmware upgrade helper already exists in one
                    # of the expected locations and use it, or else transfer the
                    # helper file specified.
                    if me.helper.get_file_exists(cip, device2.me_paths, '\\Windows\\FUWhelper.dll'):
                        device2.me_paths.fuwhelper_file = '\\Windows\\FUWhelper.dll'
                    elif me.helper.get_file_exists(cip, device2.me_paths, device2.me_paths.fuwhelper_file):
                        pass
                    else:
                        me.transfer.download_file(
                            cip=cip,
                            device=device2,
                            file_path_local=device.local_firmware_helper_path,
                            file_path_terminal=device2.me_paths.fuwhelper_file,
                            overwrite=True,
                            progress=progress_callback
                        )
                        me.util.wait(time_sec=5, progress=progress_callback)

    def test_get_process_running(self):
        print('')
        results = []
        print('1')
        for (device, driver, comms_path) in test_combinations:
            with comms.Driver(comms_path, driver=driver) as cip:
                if device.local_firmware_helper_path:
                    value = me.fuwhelper.get_process_running(cip, device.device_paths, MERUNTIME_PROCESS)
                    result = (
                        f'Device: {device.name}\n' 
                        f'Driver: {driver}\n' 
                        f'Path: {comms_path}\n'
                        f'Function: {me.fuwhelper.FuwHelperFunctions.GET_PROCESS_RUNNING}\n'
                        f'Value: {value}\n'
                    )
                    print(result)
                    self.assertEqual(value, True)
                    results.append(value)
        self.assertTrue(all(x == results[0] for x in results))

    def test_get_free_space(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            if device.name != PVP5: continue # Only used in PVP5 firmware upgrade wizard
            with comms.Driver(comms_path, driver=driver) as cip:
                value = me.fuwhelper.get_free_space(cip, device.device_paths, '\\Storage Card')
                result = (
                    f'Device: {device.name}\n' 
                    f'Driver: {driver}\n' 
                    f'Path: {comms_path}\n'
                    f'Function: {me.fuwhelper.FuwHelperFunctions.GET_FREE_SPACE}\n'
                    f'Value: {value}\n'
                )
                print(result)
                self.assertGreater(value, 0)
                results.append(value)

    def test_get_os_rev(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            if device.name != PVP5: continue # Only used in PVP5 firmware upgrade wizard
            with comms.Driver(comms_path, driver=driver) as cip:
                value = me.fuwhelper.get_os_rev(cip, device.device_paths)
                result = (
                    f'Device: {device.name}\n' 
                    f'Driver: {driver}\n' 
                    f'Path: {comms_path}\n'
                    f'Function: {me.fuwhelper.FuwHelperFunctions.GET_TERMINAL_OS_REV}\n'
                    f'Value: {value}\n'
                )
                print(result)
                self.assertNotEqual(value, None)
                results.append(value)

    def test_get_partition_size(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            if device.name != PVP5: continue # Only used in PVP5 firmware upgrade wizard
            with comms.Driver(comms_path, driver=driver) as cip:
                value = me.fuwhelper.get_partition_size(cip, device.device_paths)
                result = (
                    f'Device: {device.name}\n' 
                    f'Driver: {driver}\n' 
                    f'Path: {comms_path}\n'
                    f'Function: {me.fuwhelper.FuwHelperFunctions.GET_TERMINAL_PARTITION_SIZE}\n'
                    f'Value: {value}\n'
                )
                print(result)
                self.assertGreater(value, 0)
                results.append(value)

    def test_get_process_running_nonexistent(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            with comms.Driver(comms_path, driver=driver) as cip:
                if device.local_firmware_helper_path:
                    value = me.fuwhelper.get_process_running(cip, device.device_paths, NONEXISTENT_PROCESS)
                    result = (
                        f'Device: {device.name}\n' 
                        f'Driver: {driver}\n' 
                        f'Path: {comms_path}\n'
                        f'Function: {me.fuwhelper.FuwHelperFunctions.GET_PROCESS_RUNNING}\n'
                        f'Value: {value}\n'
                    )
                    print(result)
                    self.assertEqual(value, False)
                    results.append(value)
        self.assertTrue(all(x == results[0] for x in results))

    def test_get_total_space(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            if device.name != PVP5: continue # Only used in PVP5 firmware upgrade wizard
            with comms.Driver(comms_path, driver=driver) as cip:
                value = me.fuwhelper.get_total_space(cip, device.device_paths, '\\Storage Card')
                result = (
                    f'Device: {device.name}\n' 
                    f'Driver: {driver}\n' 
                    f'Path: {comms_path}\n'
                    f'Function: {me.fuwhelper.FuwHelperFunctions.GET_TOTAL_SPACE}\n'
                    f'Value: {value}\n'
                )
                print(result)
                self.assertGreater(value, 0)
                results.append(value)

    def test_set_me_corrupt_screen(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            if device.name != PVP5: continue # Only used in PVP5 firmware upgrade wizard
            with comms.Driver(comms_path, driver=driver) as cip:
                cip.timeout = 255.0
                value = me.fuwhelper.set_me_corrupt_screen(cip, device.device_paths, False)
                result = (
                    f'Device: {device.name}\n' 
                    f'Driver: {driver}\n' 
                    f'Path: {comms_path}\n'
                    f'Function: {me.fuwhelper.FuwHelperFunctions.DISABLE_ME_CORRUPT_SCREEN}\n'
                    f'Value: {value}\n'
                )
                print(result)
                self.assertEqual(value, True)
                results.append(value)

                value = me.fuwhelper.set_me_corrupt_screen(cip, device.device_paths, True)
                result = (
                    f'Device: {device.name}\n' 
                    f'Driver: {driver}\n' 
                    f'Path: {comms_path}\n'
                    f'Function: {me.fuwhelper.FuwHelperFunctions.ENABLE_ME_CORRUPT_SCREEN}\n'
                    f'Value: {value}\n'
                )
                print(result)
                self.assertEqual(value, True)
                results.append(value)
        self.assertTrue(all(x == results[0] for x in results))

    def test_set_screensaver(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            if device.name != PVP5: continue # Only used in PVP5 firmware upgrade wizard
            with comms.Driver(comms_path, driver=driver) as cip:
                value = me.fuwhelper.set_screensaver(cip, device.device_paths, False)
                result = (
                    f'Device: {device.name}\n' 
                    f'Driver: {driver}\n' 
                    f'Path: {comms_path}\n'
                    f'Function: {me.fuwhelper.FuwHelperFunctions.DISABLE_SCREENSAVER}\n'
                    f'Value: {value}\n'
                )
                print(result)
                self.assertEqual(value, True)
                results.append(value)

                value = me.fuwhelper.set_screensaver(cip, device.device_paths, True)
                result = (
                    f'Device: {device.name}\n' 
                    f'Driver: {driver}\n' 
                    f'Path: {comms_path}\n'
                    f'Function: {me.fuwhelper.FuwHelperFunctions.ENABLE_SCREENSAVER}\n'
                    f'Value: {value}\n'
                )
                print(result)
                self.assertEqual(value, True)
                results.append(value)
        self.assertTrue(all(x == results[0] for x in results))

    def test_stop_me(self):
        print('')
        results = []
        for (device, driver, comms_path) in test_combinations:
            with comms.Driver(comms_path, driver=driver) as cip:
                if device.local_firmware_helper_path:
                    value = me.fuwhelper.stop_process_me(cip, device.device_paths)
                    result = (
                        f'Device: {device.name}\n' 
                        f'Driver: {driver}\n' 
                        f'Path: {comms_path}\n'
                        f'Function: {me.fuwhelper.FuwHelperFunctions.STOP_PROCESS_ME}\n'
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