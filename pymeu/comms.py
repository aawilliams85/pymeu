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
        self._comms_path = comms_path
        self._route_path = None

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

        if self.is_routed_path():
            address, self._route_path = self.pycomm3_path_to_pylogix_route(self._comms_path)

        if self._driver == "pylogix":
            if self.is_routed_path(): self._comms_path = address
            self.cip = pylogix.PLC(self._comms_path)
            self.cip.Route = self._route_path
        elif self._driver == "pycomm3":
            self.cip = pycomm3.CIPDriver(self._comms_path)
            self.cip.open()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._driver == "pylogix":
            self.cip.Close()
        if self._driver == "pycomm3":
            self.cip.close()

    def generic_message(self, service, class_code, instance, request_data=b''):
        if self._driver == "pylogix":
            ret = self.cip.Message(cip_service=service,
                                   cip_class=class_code,
                                   cip_instance=instance,
                                   cip_attribute=None,
                                   data=request_data)
            if ret.Status == "Success":
                status = None
            else:
                status = ret.Status
            return Response(ret.Value[44:], None, status)
        elif self._driver == "pycomm3":
            connected = False
            if self.is_routed_path():
                unconnected_send = True
                route_path = True
            else:
                unconnected_send = False
                route_path = False
            return self.cip.generic_message(service=service,
                                            class_code=class_code,
                                            instance=instance,
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
            self.cip._cfg['socket_timeout'] = new_value

        if self._driver == "pylogix":
            self.cip.SocketTimeout = new_value

    def open(self):
        if self._driver== "pycomm3":
            self.cip.open()

    def close(self):
        if self._driver == "pycomm3":
            self.cip.close()

    @property
    def chunk_size(self):
        # When files are transferred, this is the maximum number of bytes
        # used per message.  Quick tests up to 2000 bytes did succeed, >2000 bytes failed.
        if not(self.is_routed_path()):
            # Direct path
            return 1984
        else:
            # Routed path
            max_size = 466
            working_size = max_size - 2 # Remove route path size and reserved bytes
            for segment in self._route_path:
                segment_size = 2 + len(str(segment[1])) # 1 control byte, 1 length byte, x path bytes
                if segment_size % 2: segment_size += 1 # if segment length is odd, there is a pad byte
                working_size -= segment_size

            chunk_size = working_size
            warn(f'Chunk size set to {chunk_size} but still WIP for routed paths.')
            return chunk_size

    def is_routed_path(self):
        if (',' in self._comms_path) or ('/' in self._comms_path) or ('\\' in self._comms_path) or (self._route_path is not None):
            return True
        else:
            return False
        
    def pycomm3_path_to_pylogix_route(self, path: str):
        """
        Converts a pycomm3-style route string into a pylogix Route list.

        Args:
            path (str): A comma-separated route string, e.g., '192.168.1.20,4,192.168.2.10'

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