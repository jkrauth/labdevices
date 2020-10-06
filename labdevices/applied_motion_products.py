"""
For communication with devices from Applied Motion Products.
We currently use the STF03-D Stepper Motor Controllers for our
rotary feedthroughs.

The IP can be set via a small wheel (S1) on the device itself.
We used the windows software 'STF Configurator' from Applied Motion
Products for the first configuration of the controller and to
give it its IP address in our local subnet. 
""" 
import socket

# The ports for communication. We usually use UDP
TCP_PORT = 7776
UDP_PORT = 7775

# IP address of host pc.
# If 0.0.0.0: Communication on all ethernet interfaces.
# When instantiating the class it is better to use
# the specific local IP address of that PC.
HOST_IP = '0.0.0.0'
HOST_PORT = 15005

class STF03D:
    def __init__(
            self,
            device_ip,
            host_ip=HOST_IP,
            host_port=HOST_PORT,
            timeout=5
    ):
        self.ip = device_ip
        self.host_ip = host_ip
        self.host_port = host_port
        self.timeout = timeout

    def initialize(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host_ip, self.host_port))
        self.sock.settimeout(self.timeout)

    def _write(self, cmd):
        """Send a message with the correct header and end characters"""
        header = bytes([0x00, 0x007])
        end = bytes([0xD])
        to_send = header + cmd.encode() + end
        self.sock.sendto(to_send, (self.ip, UDP_PORT))

    def _read(self):
        """Read UDP message, decode, strip off header and end characters
        and return."""
        respons_raw = self.sock.recv(1024)
        respons = respons_raw.decode()
        return respons[2:-1]

    def query(self, cmd):
        self._write(cmd)
        return self._read()

    def close(self):
        self.sock.close()


class STF03DDUMMY:
    def __init__(
            self,
            device_ip,
            host_ip=HOST_IP,
            host_port=HOST_PORT,
            timeout=5
    ):
        self.ip = device_ip
        self.host_ip = host_ip
        self.host_port = host_port
        self.timeout = timeout

    def initialize(self):
        pass

    def query(self, cmd):
        pass

    def close(self):
        pass
