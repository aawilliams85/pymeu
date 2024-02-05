import time
import unittest

from pymetransfer import METransfer

# Turn off sort so that tests run in line order
unittest.TestLoader.sortTestMethodsUsing = None

class pymetransfer_fast_tests(unittest.TestCase):
    def setUp(self):
        self.met = METransfer('192.168.40.123')
        print('')

    def test_get_terminal_info(self):
        self.met.get_terminal_info()

    def test_download_invalid_ext(self):
        with self.assertRaises(Exception):
            self.met.download('C:\\git\\pymetransfer\\tests\\TestA.xyz')

    def test_upload(self):
        self.met.upload('C:\\git\\pymetransfer\\tests\\upload\\TestA.mer')

    def tearDown(self):
        pass

class pymetransfer_slow_tests(unittest.TestCase):
    def setUp(self):
        self.met = METransfer('192.168.40.123')
        print('')

    def test_reboot(self):
        self.met.reboot()
        
    def test_download(self):
        self.met.download('C:\\git\\pymetransfer\\tests\\TestA.mer', overwrite_requested=True)

    def tearDown(self):
        time.sleep(60)

if __name__ == '__main__':
    unittest.main()