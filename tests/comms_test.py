import unittest

from pymeu import comms
from pymeu import MEUtility

from config import *

# Turn off sort so that tests run in line order
unittest.TestLoader.sortTestMethodsUsing = None

ROUTE_PATHS = [
    '192.168.40.104,4,192.168.1.20',
    '192.168.1.11/bp/5/enet/192.168.1.13/bp/7/enet/192.168.1.20'
]

class routing_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_route_01_segments(self):
        resp = comms.convert_path_pycomm3_to_pylogix(ROUTE_PATHS[0])
        print(resp)
        assert (resp[0] == '192.168.40.104')
        assert (resp[1][0] == (4, '192.168.1.20'))

    def test_route_01_size(self):
        resp = comms.get_me_chunk_size(ROUTE_PATHS[0])
        print(resp)
        assert (resp == 450)

    def test_route_02_segments(self):
        resp = comms.convert_path_pycomm3_to_pylogix(ROUTE_PATHS[1])
        print(resp)
        assert (resp[0] == '192.168.1.11')
        assert (resp[1][0] == (1, 5))
        assert (resp[1][1] == (2, '192.168.1.13'))
        assert (resp[1][2] == (1, 7))
        assert (resp[1][3] == (2, '192.168.1.20'))

    def test_route_02_size(self):
        resp = comms.get_me_chunk_size(ROUTE_PATHS[1])
        print(resp)
        assert (resp == 434)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()