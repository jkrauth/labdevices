"""
Driver for Thorlabs temperature sensor TSP01.                               

File name: thorlabs.py
Date created: 2020/07/30
Python Version: 3.7           
"""
import pyvisa
from time import sleep

"""
In case that there is any problems with the initialization
including error messages like 'Device or resource busy' the
following might help to close the device first: 
import usb.core
device = usb.core.find(idVendor=4883, idProduct=33016)
device.detach_kernel_driver(0)
"""

class TSP01:

    DEFAULTS = {
        'read_termination': '\n',
        'encoding': 'ascii',
    }

    device = None

    def __init__(self, visa_addr):
        self.addr = visa_addr # e.g.: 'USB0::4883::33016::M00416750::0::INSTR'
        self.rm = pyvisa.ResourceManager()
        
    def initialize(self):
        self.device = self.rm.open_resource(
            self.addr,
            encoding=self.DEFAULTS['encoding'],
            read_termination=self.DEFAULTS['read_termination']
        )
        
        # make sure connection is established before doing anything else
        sleep(0.5)
        print(f"Connected to {self.idn}.")

    @property
    def idn(self):
        return self.device.query('*IDN?')

    def temperature_usb(self):
        """Returns built-in temperature of the TSP01 logger"""
        return self.device.query_ascii_values(':READ?')[0]

    def humidity_usb(self):
        """Returns built-in relative humidity"""
        return self.device.query_ascii_values(':SENSe2:HUMidity:DATA?')[0]

    def temperature_probe1(self):
        """Returns temperature of external probe 1"""
        return self.device.query_ascii_values(':SENSe3:TEMPerature:DATA?')[0]

    def temperature_probe2(self):
        """Returns temperature of external probe 2"""
        return self.device.query_ascii_values(':SENSe4:TEMPerature:DATA?')[0]

    def close(self):
        if self.device is not None:
            self.device.close()
