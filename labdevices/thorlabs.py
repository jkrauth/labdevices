"""
Module for Thorlabs devices.

File name: thorlabs.py
Author: Julian Krauth
Date created: 2020/07/30
Python Version: 3.7
"""
from time import sleep
import pyvisa

from ._mock.thorlabs import PyvisaDummy

# In case that there is any problems with the initialization
# including error messages like 'Device or resource busy' the
# following might help to close the device first:
#
#   import usb.core
#   device = usb.core.find(idVendor=4883, idProduct=33016)
#   device.detach_kernel_driver(0)


class TSP01:
    """Driver for Thorlabs temperature sensor TSP01."""

    DEFAULTS = {
        'read_termination': '\n',
        'encoding':         'ascii',
    }

    def __init__(self, visa_addr: str):
        self.addr = visa_addr # e.g.: 'USB0::4883::33016::M00416750::0::INSTR'
        self._device = None

    def initialize(self):
        """Connect to device."""
        self._device = pyvisa.ResourceManager().open_resource(
            self.addr,
            encoding=self.DEFAULTS['encoding'],
            read_termination=self.DEFAULTS['read_termination']
        )

        # make sure connection is established before doing anything else
        sleep(0.5)
        print(f"Connected to {self.idn}.")

    def close(self):
        """Closes connection to device if open."""
        if self._device is not None:
            self._device.close()

    def write(self, cmd: str):
        """ Send command to device. """
        self._device.write(cmd)

    def query(self, cmd: str) -> str:
        """ Query device. """
        respons = self._device.query_ascii_values(cmd)
        return respons[0]

    def clear_status(self):
        """ Clear status of device. """
        self.write('*CLS')

    @property
    def idn(self) -> str:
        """ Return identity of device. """
        return self._device.query('*IDN?')

    def temperature_usb(self) -> float:
        """Returns built-in temperature of the TSP01 logger"""
        return self.query(':READ?')

    def humidity_usb(self) -> float:
        """Returns built-in relative humidity"""
        return self.query(':SENSe2:HUMidity:DATA?')

    def temperature_probe1(self) -> float:
        """Returns temperature of external probe 1"""
        return self.query(':SENSe3:TEMPerature:DATA?')

    def temperature_probe2(self) -> float:
        """Returns temperature of external probe 2"""
        return self.query(':SENSe4:TEMPerature:DATA?')


class TSP01Dummy(TSP01):
    """For testing purpose only. No device needed."""

    def initialize(self):
        """Connect to device."""
        self._device = PyvisaDummy()
        print(f"Connected to {self.idn}.")
