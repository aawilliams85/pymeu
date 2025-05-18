import unittest

from pymeu import comms
from pymeu import terminal

from config import *

# Turn off sort so that tests run in line order
unittest.TestLoader.sortTestMethodsUsing = None

class helper_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_helper_version(self):
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

    def test_helper_free_space(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                with comms.Driver(device.comms_path) as cip:
                    result = (
                          f'Device: {device.name}\n' 
                          f'Driver: {driver}\n' 
                          f'Function: {terminal.helper.HelperFunctions.GET_FREE_SPACE}\n'
                          f'Value: {terminal.helper.get_free_space(cip, device.device_paths)}\n'
                    )
                    print(result)

    def tearDown(self):
        pass

class registry_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_read_registry(self):
        print('')
        for device in DEVICES:
            for driver in DRIVERS:
                with comms.Driver(device.comms_path) as cip:
                    for key in terminal.registry.RegKeys:
                        if (device.name == PVP5) and (key == terminal.registry.RegKeys.ME_STARTUP_APP):
                            print(f'Skipping known failure for Device: {device.name}, Key: {key}.')
                            continue
                        if (device.name == PVP5) and (key == terminal.registry.RegKeys.ME_STARTUP_DELETE_LOGS):
                            print(f'Skipping known failure for Device: {device.name}, Key: {key}.')
                            continue
                        if (device.name == PVP5) and (key == terminal.registry.RegKeys.ME_STARTUP_LOAD_CURRENT):
                            print(f'Skipping known failure for Device: {device.name}, Key: {key}.')
                            continue
                        if (device.name == PVP5) and (key == terminal.registry.RegKeys.ME_STARTUP_OPTIONS):
                            print(f'Skipping known failure for Device: {device.name}, Key: {key}.')
                            continue
                        if (device.name == PVP5) and (key == terminal.registry.RegKeys.ME_STARTUP_REPLACE_COMMS):
                            print(f'Skipping known failure for Device: {device.name}, Key: {key}.')
                            continue

                        result = (
                              f'Device: {device.name}\n'
                              f'Driver: {driver}\n'
                              f'Key: {key}\n'
                              f'Value: {terminal.registry.get_value(cip, [key])}\n'
                        )
                        print(result)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()