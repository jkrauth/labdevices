"""
Module for Thorlabs devices.

File name: thorlabs.py
Author: Julian Krauth
Date created: 2020/07/30
Python Version: 3.7
"""
from time import sleep
import pyvisa

#In case that there is any problems with the initialization
#including error messages like 'Device or resource busy' the
#following might help to close the device first:
# import usb.core
# device = usb.core.find(idVendor=4883, idProduct=33016)
# device.detach_kernel_driver(0)


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

    @property
    def idn(self) -> str:
        return self._device.query('*IDN?')

    def temperature_usb(self) -> float:
        """Returns built-in temperature of the TSP01 logger"""
        return self._device.query_ascii_values(':READ?')[0]

    def humidity_usb(self) -> float:
        """Returns built-in relative humidity"""
        return self._device.query_ascii_values(':SENSe2:HUMidity:DATA?')[0]

    def temperature_probe1(self) -> float:
        """Returns temperature of external probe 1"""
        return self._device.query_ascii_values(':SENSe3:TEMPerature:DATA?')[0]

    def temperature_probe2(self) -> float:
        """Returns temperature of external probe 2"""
        return self._device.query_ascii_values(':SENSe4:TEMPerature:DATA?')[0]


class TSP01Dummy:
    """For testing purpose only. No device needed."""
    def __init__(self, _):
        self.temp = 20
        self.humidity = 50
        self.idn = 'Thorlabs sensor dummy'

    def initialize(self):
        print('Connected to Thorlabs sensor dummy.')

    def close(self):
        pass

    def temperature_usb(self):
        return self.temp

    def humidity_usb(self):
        return self.humidity

    def temperature_probe1(self):
        return self.temp

    def temperature_probe2(self):
        return self.temp + .5
