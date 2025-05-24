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

    def __init__(self, cip_path=None, driver=None):
        self._cip_path = cip_path

        if not AVAILABLE_DRIVERS:
            raise ImportError("You need to install pycomm3 or pylogix")

        # select the driver the user requested
        if driver:
            if driver in AVAILABLE_DRIVERS:
                self.plc_driver = driver
            else:
                raise ImportError(f"{driver} is not installed on the system")
        else:
            # no driver requested, pick the first one
            self.plc_driver = AVAILABLE_DRIVERS[0]

        if self.plc_driver == "pylogix":
            self.cip = pylogix.PLC(self._cip_path)
        elif self.plc_driver == "pycomm3":
            self.cip = pycomm3.CIPDriver(self._cip_path)
            self.cip.open()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.plc_driver == "pylogix":
            self.cip.Close()
        if self.plc_driver == "pycomm3":
            self.cip.close()

    def generic_message(self, service, class_code, instance, request_data=b'', connected=False, unconnected_send=False, route_path=None):
        if self.plc_driver == "pylogix":
            ret = self.cip.Message(service, class_code, instance, None, request_data)
            if ret.Status == "Success":
                status = None
            else:
                status = ret.Status
            return Response(ret.Value[44:], None, status)
        elif self.plc_driver == "pycomm3":
            return self.cip.generic_message(service=service,
                                            class_code=class_code,
                                            instance=instance,
                                            request_data=request_data
                                            )

    @property
    def timeout(self):
        if self.plc_driver == "pycomm3":
            return self.cip._cfg['socket_timeout']
        if self.plc_driver == "pylogix":
            return self.cip.SocketTimeout

    @timeout.setter
    def timeout(self, new_value):
        if self.plc_driver == "pycomm3":
            self.cip._cfg['socket_timeout'] = new_value

        if self.plc_driver == "pylogix":
            self.cip.SocketTimeout = new_value

    def open(self):
        if self.plc_driver== "pycomm3":
            self.cip.open()

    def close(self):
        if self.plc_driver == "pycomm3":
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
            return 450

    def is_routed_path(self):
        if (',' in self._cip_path) or ('/' in self._cip_path):
            return True
        else:
            return False


class Response(object):

    def __init__(self, value, type, error):
        self.tag = 'generic'
        self.value = value
        self.type = type
        self.error = error