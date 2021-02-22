"""
Driver for devices from Stanford Research Systems
contains:
- DG645

File name: stanford_research_systems.py
Python version: 3.7
"""
import socket
import time


class DG645:
    """ Driver for delay generators """

    DEFAULTS = {
        'outputBNC': {
            "T0":0,
            "AB":1,
            "CD":2,
            "EF":3,
            "GH":4
        },
        'channel': {
            "T0":0,
            "T1":1,
            "A":2,
            "B":3,
            "C":4,
            "D":5,
            "E":6,
            "F":7 ,
            "G":8,
            "H":9
        },
        'write_termination': '\n',
        'read_termination': '\r\n',
    }


    def __init__(self, tcp: str, port: int, timeout: float = 0.010):
        """
        Arguments:
        tcp - IP address of device
        port - port of device
        timeout - time in seconds before recv() gives a timeout error
        """
        self.tcp = tcp
        self.port = port
        self._device = None
        self.timeout = timeout

    def initialize(self):
        """Connect to the device."""
        self._device = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._device.settimeout(self.timeout)
        self._device.connect((self.tcp, self.port))
        time.sleep(0.2)
        print('bla')
        print(f'Connected to:\n    {self.idn}')

    def close(self):
        """Closing connection with the device"""
        print(f'Close connection with:\n    {self.idn}')
        self._device.close()


    def write(self, cmd: str) -> None:
        """Send command to device"""
        # Add write termination character and encode
        termination_char = self.DEFAULTS['write_termination']
        cmd += termination_char
        cmd = cmd.encode()
        # Send command
        self._device.send(cmd)

    def query(self, cmd: str) -> str:
        """Send a request to the device and return its respons."""
        self.write(cmd)
        respons = self._device.recv(256)
        respons = respons.decode()
        # Strip off read termination character
        return respons.rstrip()

    @property
    def idn(self) -> str:
        idn = self.query('*IDN?')
        return idn

    def set_delay(self, channel, delay: float, reference = "T0"):
        """Set the delay of a certain channel with respect to a reference.
        Arguments:
        channel -- str/int corresponding to a channel (see self.DEFAULTS)
        delay -- float, with time in seconds
        reference -- defaults to 'T0'
        """
        if isinstance(channel, str):
            channel = self.DEFAULTS['channel'][channel]

        if isinstance(reference, str):
            reference = self.DEFAULTS['channel'][reference]

        cmd = f'DLAY {channel}, {reference}, {delay}'
        self.write(cmd)
        #wait for 100 ms, this is the time it will take to write the command
        time.sleep(0.1)

    def get_delay(self, channel) -> float:
        """Request the delay of a certain channel
        Arguments:
        channel -- str/int corresponding to a channel (see self.DEFAULTS)

        Returns -- float, the delay in seconds.
        Optionally also the reference channel.
        """
        if isinstance(channel, str):
            channel = self.DEFAULTS['channel'][channel]
        cmd = f'DLAY? {channel}'
        respons = self.query(cmd)
        #reference = respons[0]
        delay = float(respons[2:])
        return delay

    def get_output_level(self, channel) -> float:
        """Request output amplitude of a channel
        Arguments:
        channel -- str/int corresponding to a channel (see self.DEFAULTS)

        Returns --float, the amplitude in Volts
        """
        if isinstance(channel, str):
            channel = self.DEFAULTS['outputBNC'][channel]
        cmd = f'LAMP? {channel}'
        respons = self.query(cmd)
        return respons


class DG645Dummy(DG645):
    """For testing purpose only. No device needed."""
    def __init__(self, tcp: str, port: int, timeout: float = 0.010):
        super().__init__(tcp, port)
        self.idn = 'Dummy DG645'

    def initialize(self):
        pass

    def close(self):
        pass

    def write(self, cmd):
        pass

    def query(self, cmd):
        return 'answer'

    def set_delay(self, channel, delay: float, reference = 'T0'):
        pass

    def get_delay(self, channel) -> float:
        return float(1)

    def get_output_level(self, channel):
        return float(1)


if __name__ == "__main__":
    dg = DG645('10.0.0.34', 5025)
    dg.initialize()
    delay1 = dg.get_delay(2)
    print(delay1)
    dg.set_delay(2, 0.007061726)
    delay2 = dg.get_delay(2)
    print(delay2)
    dg.close()
