from warnings import warn

# see which drivers are installed on the system
AVAILABLE_DRIVERS = []
try:
    import pycomm3
    AVAILABLE_DRIVERS.append("pycomm3")
except: pass

try:
    import pylogix
    AVAILABLE_DRIVERS.append("pylogix")
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
        if self._driver == "pylogix":
            self.cip = pylogix.PLC(self._ip_address)
            self.cip.Route = self._route_path
        elif self._driver == "pycomm3":
            self.cip = pycomm3.CIPDriver(self._original_path)
            self.cip.open()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._driver == "pylogix":
            self.cip.Close()
        if self._driver == "pycomm3":
            self.cip.close()

    def generic_message(self, service, class_code, instance, attribute, request_data=b''):
        if self._driver == "pylogix":
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
        elif self._driver == "pycomm3":
            connected = False
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
    def timeout(self):
        if self._driver == "pycomm3":
            return self.cip._cfg['socket_timeout']
        if self._driver == "pylogix":
            return self.cip.SocketTimeout

    @timeout.setter
    def timeout(self, new_value):
        if self._driver == "pycomm3":
            self.cip._cfg['timeout'] = new_value
            self.cip._cfg['socket_timeout'] = new_value
            self.cip.close()
            self.cip.open()

        if self._driver == "pylogix":
            self.cip.SocketTimeout = new_value

    def open(self):
        if self._driver== "pycomm3":
            self.cip.open()

    def close(self):
        if self._driver == "pycomm3":
            self.cip.close()

    @property
    def me_chunk_size(self):
        return get_me_chunk_size(self._original_path)
    
    @property
    def dmk_chunk_size(self):
        return get_dmk_chunk_size(self._original_path)

def get_dmk_chunk_size(path: str) -> int:
    if is_routed_path(path):
        raise NotImplementedError()
    else:
        # Direct path
        return 1350

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

        chunk_size = working_size
        warn(f'Chunk size set to {chunk_size} but still WIP for routed paths.')
        return chunk_size
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