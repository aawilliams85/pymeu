import unittest

from pymeu import MEUtility

from config import *

# Turn off sort so that tests run in line order
unittest.TestLoader.sortTestMethodsUsing = None

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

if __name__ == '__main__':
    unittest.main()