import time
import unittest

from pymeu import MEUtility

# Turn off sort so that tests run in line order
unittest.TestLoader.sortTestMethodsUsing = None

class pymeu_fast_tests(unittest.TestCase):
    def setUp(self):
        self.meu = MEUtility('192.168.40.123')
        print('')

    def test_get_terminal_info(self):
        print(self.meu.get_terminal_info())

    def test_download_invalid_ext(self):
        with self.assertRaises(Exception):
            self.meu.download('C:\\git\\pymeu\\tests\\TestA.xyz')

    def test_upload(self):
        print(self.meu.upload('C:\\git\\pymeu\\tests\\upload\\TestA.mer', overwrite=True))

    def test_upload_all(self):
        print(self.meu.upload_all('C:\\git\\pymeu\\tests\\upload', overwrite=True))

    def tearDown(self):
        pass

class pymeu_slow_tests(unittest.TestCase):
    def setUp(self):
        self.meu = MEUtility('192.168.40.123')
        print('')

    def test_reboot(self):
        print(self.meu.reboot())
        
    def test_download(self):
        print(self.meu.download('C:\\git\\pymeu\\tests\\TestB.mer', overwrite=True))
        
    def tearDown(self):
        pass
        #time.sleep(60)

if __name__ == '__main__':
    unittest.main()