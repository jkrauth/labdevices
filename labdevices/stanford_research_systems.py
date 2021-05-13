"""
Driver for devices from Stanford Research Systems
contains:
- DG645

File name: stanford_research_systems.py
Python version: 3.7
"""
from typing import Tuple, Union
import socket
import time

from ._mock.stanford_research_systems import SocketDummy


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
        """ Get identification of device. """
        idn = self.query('*IDN?')
        return idn

    def set_delay(self, channel: Union[int, str], delay: float, reference: Union[int, str] = "T0"):
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

    def get_delay(self, channel: Union[int, str]) -> Tuple[int, float]:
        """Request the delay of a certain channel

        Arguments:
            channel -- str/int corresponding to a channel (see self.DEFAULTS)

        Returns -- (int, float) | reference channel, delay in seconds.
        """

        if isinstance(channel, str):
            channel = self.DEFAULTS['channel'][channel]
        cmd = f'DLAY? {channel}'
        respons = self.query(cmd).split(',')
        reference = int(respons[0])
        delay = float(respons[1])
        return reference, delay

    def get_output_level(self, channel: Union[int, str]) -> float:
        """Request output amplitude of a channel
        Arguments:
        channel -- str/int corresponding to a channel (see self.DEFAULTS)

        Returns --float, the amplitude in Volts
        """
        if isinstance(channel, str):
            channel = self.DEFAULTS['outputBNC'][channel]
        cmd = f'LAMP? {channel}'
        respons = self.query(cmd)
        return float(respons)


class DG645Dummy(DG645):
    """For testing purpose only. No device needed."""

    def initialize(self):
        """Connect to the device."""
        self._device = SocketDummy()
        self._device.settimeout(self.timeout)
        self._device.connect((self.tcp, self.port))
        time.sleep(0.2)
        print(f'Connected to:\n    {self.idn}')


if __name__ == "__main__":
    dg = DG645('10.0.0.34', 5025)
    dg.initialize()
    delay1 = dg.get_delay(2)
    print(delay1)
    dg.set_delay(2, 0.007061726)
    delay2 = dg.get_delay(2)
    print(delay2)
    dg.close()
