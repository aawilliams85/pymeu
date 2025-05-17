import json
import os
import time
import unittest

from pymeu import comms
from pymeu import MEUtility
from pymeu import terminal
from pymeu import types

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
        self.meu.get_terminal_info()

    def test_get_terminal_info_print(self):
        self.meu.get_terminal_info(print_log=True)

    def test_get_terminal_info_print_redacted(self):
        self.meu.get_terminal_info(print_log=True, redact_log=True)

    def test_get_terminal_info_print_silent(self):
        self.meu.get_terminal_info(print_log=True, silent_mode=True)

    def test_download_invalid_ext(self):
        self.download_file_path = os.path.join(self.download_folder_path, self.config_data['download']['bad_extension'])
        resp = self.meu.download(self.download_file_path)
        self.assertEqual(resp.status, types.MEResponseStatus.FAILURE)

    def test_upload(self):
        self.upload_file_path = os.path.join(self.upload_folder_path, self.config_data['upload']['good'][0])
        resp = self.meu.upload(self.upload_file_path, overwrite=True)
        for s in resp.device.log: print(s)
        print(resp.status)

    def test_upload_all(self):
        resp = self.meu.upload_all(self.upload_folder_path, overwrite=True)
        for s in resp.device.log: print(s)
        print(resp.status)

    def test_upload_bad_missing(self):
        self.upload_file_path = os.path.join(self.upload_folder_path, self.config_data['upload']['bad_missing'])
        resp = self.meu.upload(self.upload_file_path, overwrite=True)
        for s in resp.device.log: print(s)
        print(resp.status)
        self.assertEqual(resp.status, types.MEResponseStatus.FAILURE)

    def test_upload_multiple_instances(self):
        meu2 = MEUtility(self.config_data['comms_path']['good'])
        with comms.Driver(meu2.comms_path) as cip2:
            # Open parallel transfer instance
            device2 = terminal.validation.get_terminal_info(cip2)
            file2 = self.config_data['upload']['good'][0]
            path2 = f'{device2.paths.storage}\\Rockwell Software\\RSViewME\\Runtime\\{file2}'
            transfer_instance_2 = terminal.files.create_transfer_instance_upload(cip2, path2)

            # Upload
            self.upload_file_path = os.path.join(self.upload_folder_path, self.config_data['upload']['good'][0])
            resp = self.meu.upload(self.upload_file_path, overwrite=True)

            # Verify upload result
            for s in resp.device.log: print(s)
            print(resp.status)
            self.assertEqual(resp.status, types.MEResponseStatus.SUCCESS)

            # Close parallel transfer instance
            terminal.files.delete_transfer_instance(cip2, transfer_instance_2)

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
        resp = self.meu.reboot()
        for s in resp.device.log: print(s)
        print(resp.status)
        
    def test_download(self):
        self.download_file_path = os.path.join(self.download_folder_path, self.config_data['download']['good'][0])
        resp = self.meu.download(self.download_file_path, overwrite=True)
        for s in resp.device.log: print(s)
        print(resp.status)
        
    def test_download_as(self):
        self.download_file_path = os.path.join(self.download_folder_path, self.config_data['download']['good'][0])
        resp = self.meu.download(self.download_file_path, overwrite=True, remote_file_name=self.config_data['download']['good_as'][0])
        for s in resp.device.log: print(s)
        print(resp.status)

    def tearDown(self):
        pass
        #time.sleep(60)

if __name__ == '__main__':
    unittest.main()