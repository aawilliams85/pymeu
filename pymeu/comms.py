from warnings import warn

# see which drivers are installed on the system
AVAILABLE_DRIVERS = []
DRIVER_NAME_PYCOMM3 = 'pycomm3'
DRIVER_NAME_PYLOGIX = 'pylogix'
try:
    from pycomm3 import CIPDriver, const, util
    AVAILABLE_DRIVERS.append(DRIVER_NAME_PYCOMM3)
except: pass

try:
    from pylogix import PLC
    AVAILABLE_DRIVERS.append(DRIVER_NAME_PYLOGIX)
except: pass

class Driver:

    def __init__(self, comms_path=None, driver=None):
        self._original_path = comms_path

        if not AVAILABLE_DRIVERS:
            raise ImportError("You need to install pycomm3 or pylogix")

        # select the driver the user requested
        if driver:
            if driver in AVAILABLE_DRIVERS:
                self._driver = driver
            else:
                raise ImportError(f"{driver} is not installed on the system")
        else:
            # no driver requested, pick the first one
            self._driver = AVAILABLE_DRIVERS[0]

        # Split originally supplied path into IP address and route if needed
        if is_routed_path(self._original_path):
            self._ip_address, self._route_path = convert_path_pycomm3_to_pylogix(self._original_path)
        else:
            self._ip_address = self._original_path
            self._route_path = None

        # Configure driver
        if self._driver == DRIVER_NAME_PYLOGIX:
            self.cip = PLC(self._ip_address)
            self.cip.Route = self._route_path
        elif self._driver == DRIVER_NAME_PYCOMM3:
            self.cip = CIPDriver(self._original_path)
            self._const_timeout_ticks = const.TIMEOUT_TICKS # Used to check for unconnected send firmware upgrade
            self.cip.open()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._driver == DRIVER_NAME_PYLOGIX:
            self.cip.Close()
        if self._driver == DRIVER_NAME_PYCOMM3:
            self.cip.close()

    def generic_message(self, service, class_code, instance, attribute, request_data=b'', connected=False):
        if self._driver == DRIVER_NAME_PYLOGIX:
            ret = self.cip.Message(cip_service=service,
                                   cip_class=class_code,
                                   cip_instance=instance,
                                   cip_attribute=attribute,
                                   data=request_data)
            if ret.Status == "Success":
                status = None
            else:
                status = ret.Status
            return Response(ret.Value[44:], None, status)
        elif self._driver == DRIVER_NAME_PYCOMM3:
            if is_routed_path(self._original_path):
                unconnected_send = True
                route_path = True
            else:
                unconnected_send = False
                route_path = False
            return self.cip.generic_message(service=service,
                                            class_code=class_code,
                                            instance=instance,
                                            attribute=attribute,
                                            request_data=request_data,
                                            connected=connected,
                                            unconnected_send=unconnected_send,
                                            route_path=route_path
                                            )

    @property
    def connection_size(self):
        if self._driver == DRIVER_NAME_PYCOMM3:
            raise self.cip.connection_size
        if self._driver == DRIVER_NAME_PYLOGIX:
            return self.cip.ConnectionSize

    @connection_size.setter
    def connection_size(self, new_value):
        if self._driver == DRIVER_NAME_PYCOMM3:
            self.cip._cfg['connection_size'] = new_value
            self.cip.close()
            self.cip.open()
        if self._driver == DRIVER_NAME_PYLOGIX:
            self.cip.ConnectionSize = new_value

    @property
    def timeout(self):
        if self._driver == DRIVER_NAME_PYCOMM3:
            return self.cip._cfg['socket_timeout']
        if self._driver == DRIVER_NAME_PYLOGIX:
            return self.cip.SocketTimeout

    @timeout.setter
    def timeout(self, new_value):
        if self._driver == DRIVER_NAME_PYCOMM3:
            self.cip._cfg['timeout'] = new_value
            self.cip._cfg['socket_timeout'] = new_value
            self.cip.close()
            self.cip.open()
        if self._driver == DRIVER_NAME_PYLOGIX:
            self.cip.SocketTimeout = new_value

    def open(self):
        if self._driver == DRIVER_NAME_PYCOMM3:
            self.cip.open()

    def close(self):
        if self._driver == DRIVER_NAME_PYCOMM3:
            self.cip.close()

    def sequence_reset(self):
        if self._driver == DRIVER_NAME_PYCOMM3:
            self.cip._sequence = util.cycle(65535, start=1)
        if self._driver == DRIVER_NAME_PYLOGIX:
            self.cip.conn._sequence_counter = 1
        
    def forward_open(self):
        if self._driver == DRIVER_NAME_PYCOMM3:
            self.cip._forward_open()
        if self._driver == DRIVER_NAME_PYLOGIX:
            return
            self.cip.conn._connect(True)

    def forward_close(self):
        if self._driver == DRIVER_NAME_PYCOMM3:
            self.cip._forward_close()
        if self._driver == DRIVER_NAME_PYLOGIX:
            return
            self.cip.conn._close_connection()

    @property
    def me_chunk_size(self):
        return get_me_chunk_size(self._original_path)

def get_me_chunk_size(path: str) -> int:
    # When files are transferred using ME services, this is the maximum
    # number of bytes used per one message.
    if is_routed_path(path):
        # Routed path through one or more other devices (ex: through CLX rack and then to terminal)
        ip_address, route_path = convert_path_pycomm3_to_pylogix(path)

        max_size = 466
        working_size = max_size - 2 # Remove route path size and reserved bytes
        for segment in route_path:
            port = segment[0]
            try:
                path = int(segment[1])
                path_size = 1
                segment_size = 1 # 1 control byte
            except:
                path = str(segment[1])
                path_size = len(path)
                segment_size = 2 + path_size # 1 control byte, 1 length byte, X path bytes
                if segment_size % 2: segment_size += 1 # if segment length is odd, there is a pad byte

            working_size -= segment_size
        return working_size
    else:
        # Direct path
        # Tests up to 2000 bytes did succeed, >2000 bytes failed.
        return 1984

def is_routed_path(path: str) -> bool:
    if (',' in path) or ('/' in path) or ('\\' in path):
        return True
    else:
        return False
        
def convert_path_pycomm3_to_pylogix(path: str):
    """
    Converts a pycomm3-style route string into a pylogix Route list.

    Args:
        path (str): A route string, e.g., '192.168.2.10/bp/3/enet/192.168.1.20'

    Returns:
        tuple: (starting_ip: str, pylogix_route: list of tuples)
    """
    # make sure we are only working with commas, then split
    parts = path.replace("/", ",").replace("\\", ",").split(",")
    ip_address = parts.pop(0)
    route = []

    if parts:
        # make sure even number of segments
        if len(parts) % 2:
            raise ValueError("Path must have at least one routing pair (port, destination) after the start IP.")
        
        for i in range(len(parts)):
            # try to convert each path segment to an int
            try:
                parts[i] = int(parts[i])
            except:
                if parts[i] == "backplane":
                    parts[i] = 1
                elif parts[i] == "bp":
                    parts[i] = 1
                elif parts[i] == "enet":
                    parts[i] = 2

        # convert the route to pylogix format (2 item lists)
        route = [tuple(parts[i:i+2]) for i in range(0, len(parts), 2)]
    return ip_address, route

class Response(object):
    def __init__(self, value, type, error):
        self.tag = 'generic'
        self.value = value
        self.type = type
        self.error = error