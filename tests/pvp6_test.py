import json
import os
import time
import unittest

from pymeu import MEUtility

# Turn off sort so that tests run in line order
unittest.TestLoader.sortTestMethodsUsing = None

class pvp6_fast_tests(unittest.TestCase):
    def setUp(self):
        self.base_path = os.path.abspath(os.path.dirname(__file__))
        self.config_path = os.path.join(self.base_path, 'config.json')
        with open(self.config_path, 'r') as f:
            self.config_data = json.load(f)
            self.config_data = self.config_data['pvp6']

        self.download_folder_path = os.path.join(self.base_path, 'download')
        self.upload_folder_path = os.path.join(self.base_path, 'upload')
        self.meu = MEUtility(self.config_data['comms_path']['good'])
        print('')

    def test_get_terminal_info(self):
        print(self.meu.get_terminal_info())

    def test_get_terminal_info_print(self):
        self.meu.get_terminal_info(print_log=True)

    def test_get_terminal_info_print_redacted(self):
        self.meu.get_terminal_info(print_log=True, redact_log=True)

    def test_download_invalid_ext(self):
        self.download_file_path = os.path.join(self.download_folder_path, self.config_data['download']['bad_extension'])
        with self.assertRaises(Exception):
            self.meu.download(self.download_file_path)

    def test_upload(self):
        self.upload_file_path = os.path.join(self.upload_folder_path, self.config_data['upload']['good'][0])
        print(self.meu.upload(self.upload_file_path, overwrite=True))

    def test_upload_all(self):
        print(self.meu.upload_all(self.upload_folder_path, overwrite=True))

    def tearDown(self):
        pass

class pvp6_slow_tests(unittest.TestCase):
    def setUp(self):
        self.base_path = os.path.abspath(os.path.dirname(__file__))
        self.config_path = os.path.join(self.base_path, 'config.json')
        with open(self.config_path, 'r') as f:
            self.config_data = json.load(f)
            self.config_data = self.config_data['pvp6']

        self.download_folder_path = os.path.join(self.base_path, 'download')
        self.upload_folder_path = os.path.join(self.base_path, 'upload')
        self.meu = MEUtility(self.config_data['comms_path']['good'])
        print('')

    def test_reboot(self):
        print(self.meu.reboot())
        
    def test_download(self):
        self.download_file_path = os.path.join(self.download_folder_path, self.config_data['download']['good'][0])
        print(self.meu.download(self.download_file_path, overwrite=True))
        
    def test_download_as(self):
        self.download_file_path = os.path.join(self.download_folder_path, self.config_data['download']['good'][0])
        print(self.meu.download(self.download_file_path, overwrite=True, remote_file_name=self.config_data['download']['good_as'][0]))

    def tearDown(self):
        pass
        #time.sleep(60)

if __name__ == '__main__':
    unittest.main()