import unittest

from pymeu import comms
from pymeu import terminal

from config import *

# Turn off sort so that tests run in line order
unittest.TestLoader.sortTestMethodsUsing = None

class helper_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_helper_version(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                with comms.Driver(device.comms_path) as cip:
                    result = (
                          f'Device: {device.name}\n'
                          f'Driver: {driver}\n'
                          f'Function: {terminal.helper.HelperFunctions.GET_VERSION}\n'
                          f'Value: {terminal.helper.get_helper_version(cip, device.device_paths)}\n'
                    )
                    print(result)

    def test_get_file_exists(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                file_path = device.device_paths.helper_file
                with comms.Driver(device.comms_path) as cip:
                    value = terminal.helper.get_file_exists(cip, device.device_paths, file_path)
                    result = (
                          f'Device: {device.name}\n' 
                          f'Driver: {driver}\n' 
                          f'Function: {terminal.helper.HelperFunctions.GET_FILE_EXISTS} {file_path}\n'
                          f'Value: {value}\n'
                    )
                    print(result)
                    self.assertEqual(value, True)

    def test_get_file_exists_bad_nonexistent(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                file_path = NONEXISTENT_FILE
                with comms.Driver(device.comms_path) as cip:
                    value = terminal.helper.get_file_exists(cip, device.device_paths, file_path)
                    result = (
                          f'Device: {device.name}\n' 
                          f'Driver: {driver}\n' 
                          f'Function: {terminal.helper.HelperFunctions.GET_FILE_EXISTS} {file_path}\n'
                          f'Value: {value}\n'
                    )
                    print(result)
                    self.assertEqual(value, False)

    def test_get_file_size(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                file_path = device.device_paths.helper_file
                with comms.Driver(device.comms_path) as cip:
                    value = terminal.helper.get_file_size(cip, device.device_paths, file_path)
                    result = (
                          f'Device: {device.name}\n' 
                          f'Driver: {driver}\n' 
                          f'Function: {terminal.helper.HelperFunctions.GET_FILE_SIZE} {file_path}\n'
                          f'Value: {value}\n'
                    )
                    print(result)
                    self.assertGreater(value, 0)

    def test_get_file_size_bad_nonexistent(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                file_path = NONEXISTENT_FILE
                with comms.Driver(device.comms_path) as cip:
                    result = (
                          f'Device: {device.name}\n' 
                          f'Driver: {driver}\n' 
                          f'Function: {terminal.helper.HelperFunctions.GET_FILE_SIZE} {file_path}\n'
                    )
                    print(result)
                    with self.assertRaises(FileNotFoundError):
                        terminal.helper.get_file_size(cip, device.device_paths, file_path)

    def test_get_folder_exists(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                folder_path = device.device_paths.storage
                with comms.Driver(device.comms_path) as cip:
                    value = terminal.helper.get_folder_exists(cip, device.device_paths, folder_path)
                    result = (
                          f'Device: {device.name}\n' 
                          f'Driver: {driver}\n' 
                          f'Function: {terminal.helper.HelperFunctions.GET_FOLDER_EXISTS} {folder_path}\n'
                          f'Value: {value}\n'
                    )
                    print(result)
                    self.assertEqual(value, True)

    def test_get_folder_exists_bad_nonexistent(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                folder_path = NONEXISTENT_FOLDER
                with comms.Driver(device.comms_path) as cip:
                    value = terminal.helper.get_folder_exists(cip, device.device_paths, folder_path)
                    result = (
                          f'Device: {device.name}\n' 
                          f'Driver: {driver}\n' 
                          f'Function: {terminal.helper.HelperFunctions.GET_FOLDER_EXISTS} {folder_path}\n'
                          f'Value: {value}\n'
                    )
                    print(result)
                    self.assertEqual(value, False)

    def test_get_free_space(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                folder_path = f'{device.device_paths.runtime}\\'
                with comms.Driver(device.comms_path) as cip:
                    value = terminal.helper.get_free_space(cip, device.device_paths, folder_path)
                    result = (
                          f'Device: {device.name}\n' 
                          f'Driver: {driver}\n' 
                          f'Function: {terminal.helper.HelperFunctions.GET_FREE_SPACE} {folder_path}\n'
                          f'Value: {value}\n'
                    )
                    print(result)
                    self.assertGreater(value, 0)

    def test_get_free_space_bad_nonexistent(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                folder_path = f'{NONEXISTENT_FOLDER}\\'
                with comms.Driver(device.comms_path) as cip:
                    result = (
                          f'Device: {device.name}\n' 
                          f'Driver: {driver}\n' 
                          f'Function: {terminal.helper.HelperFunctions.GET_FREE_SPACE} {folder_path}\n'
                    )
                    print(result)
                    with self.assertRaises(Exception):
                        terminal.helper.get_free_space(cip, device.device_paths, folder_path)

    def tearDown(self):
        pass

class registry_tests(unittest.TestCase):
    def setUp(self):
        self.skip_pairs = {
            PVP5: {
                terminal.registry.RegKeys.ME_STARTUP_APP,
                terminal.registry.RegKeys.ME_STARTUP_DELETE_LOGS,
                terminal.registry.RegKeys.ME_STARTUP_LOAD_CURRENT,
                terminal.registry.RegKeys.ME_STARTUP_OPTIONS,
                terminal.registry.RegKeys.ME_STARTUP_REPLACE_COMMS
            },
        }

    def test_read_registry(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                with comms.Driver(device.comms_path) as cip:
                    for key in terminal.registry.RegKeys:
                        if device.name in self.skip_pairs and key in self.skip_pairs[device.name]:
                            value = 'Skipping known failure.'
                        else:
                            value = f'Value: {terminal.registry.get_value(cip, [key])}'

                        result = (
                              f'Device: {device.name}\n'
                              f'Driver: {driver}\n'
                              f'Key: {key}\n'
                              f'{value}\n'
                        )
                        print(result)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()