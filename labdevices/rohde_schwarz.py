"""
Module for Rohde & Schwarz devices.

File name: rohde_schwarz.py
Author: Andres Martinez de Velasco
Date created: 2020/11/11
Python Version: 3.7

"""
from time import sleep
import re
import numpy as np
import pyvisa


class FPC1000:
    """Simple spectrum analyzer.
    Works for now with an Ethernet connection.
    Bluetooth is not implemented.
    """

    def __init__(self, ip: str):
        """Arguments:
        ip -- IP address of the device, e.g. '10.0.0.90'
        """
        self.addr = 'TCPIP::'+ip
        self._device = None
        #self.timeout = 10000 # in ms, default is 2000

    def initialize(self):
        """Connect to the device"""
        self._device = pyvisa.ResourceManager().open_resource(self.addr)
        print(f'Connected to {self.idn}')

    @property
    def idn(self) -> str:
        """Returns the identification string of the device."""
        return self.query('*IDN?')

    def close(self):
        """Close connection to the device"""
        if self._device is not None:
            self._device.close()
            print('Connection to FPC1000 closed!')
        else:
            print('FPC1000 is already closed.')

    def query(self, cmd: str) -> str:
        """Send a command and receive the answer"""
        respons = self._device.query(cmd).rstrip()
        return respons

    def get_trace(self):
        """Get the trace which is currently shown on the display.
        For some reason this function sometimes times out.
        Increasing the timeout time couldn't solve the issue.

        Return x and y as lists of floats.
        """
        raw_y = self.query('TRAC:DATA? TRACE1')
        y_data = [float(i) for i in raw_y.split(',')]
        sleep(0.1)
        x_start = float(self.query('FREQ:STAR?'))
        x_stop = float(self.query('FREQ:STOP?'))
        x_data = list(np.linspace(x_start, x_stop, len(y_data)))
        return x_data, y_data

    def get_system_alarm(self) -> str:
        """Return system alarms and clear alarm buffer."""
        respons = self._device.query('SYST:ERR:ALL?')
        return respons


class Oscilloscope:
    """
    Is tested with the following Rohde & Schwarz oscilloscope
    models:
    """
    def __init__(self, address: str):
        """
        Arguments:
        address -- str, VISA address for USB connection or IP for Ethernet.
        """
        self._device = None
        # Check if address has IP pattern:
        if bool(re.match(r'\d+\.\d+\.\d+\.\d+', address)):
            self.device_address = (f'TCPIP::{address}::INSTR')
        # E
        elif bool(re.match('^USB.+::INSTR$', address)):
            self.device_address = address
        else:
            raise ValueError("Address needs to be an IP or a valid VISA address.")

    def initialize(self):
        """Connect to device."""
        self._device = pyvisa.ResourceManager().open_resource(self.device_address)
        print(f"Connected to:\n{self.idn}")


    def query(self, cmd: str):
        response = self._device.query(cmd)
        return response

    def write(self, cmd: str):
        self._device.write(cmd)

    def ieee_query(self, cmd: str):
        self._device.timeout = 20000
        self.write(cmd)
        response = self._device.query_binary_values(f'{cmd}', datatype='s')

        return response

    @property
    def idn(self):
        idn = self.query("*IDN?")
        return idn

    def get_volt_avg(self,channel: int):
        self.write(f"MEASurement:SOURce CH{channel}; MEASurement:MAIN MEAN")
        result = self.query("MEASurement:RESult?")
        return float(result)


    def get_volt_max(self,channel: int):
        self.write(f"MEASurement:SOURce CH{channel}; MEASurement:MAIN UPEakvalue")
        result = self.query("MEASurement:RESult?")
        return float(result)

    def get_volt_peakpeak(self, channel: int):
        self.write(f"MEASurement:SOURce CH{channel}; MEASurement:MAIN PEAK")
        result = self.query("MEASurement:RESult?")
        return float(result)

    def get_trace(self, channel: int):
        print(f'acquiring trace for channel {channel+1}')
        self.write(f'CHANnel{channel}:SINGle')
        voltage = self.query(f'FORMat ASC; CHANnel{channel}:DATA?')
        voltage = [float(i) for i in voltage.split(',')]

        # this query returns (xstart, xstop, length,Number of values per sample interval) as string
        x_header = self.query(f'CHANnel{channel}:DATA:HEADer?')
        x_header = x_header.split(',')
        trace = np.linspace(float(x_header[0]), float(x_header[1]), int(x_header[2]))

        return trace, voltage

    def screen_shot(self):
        """Takes a screenshot of the scope display."""
        # self.write('HCOPy:CWINdow ON') this closes all windows
        # when taking screen shot so signal can be seen.
        # set format
        self.write('HCOPy:LANG PNG')
        image_bytes = self.ieee_query('HCOPy:DATA?')

        return image_bytes

    def set_t_scale(self, time: str):
        """format example: '1.E-9'"""
        self.write(cmd = f":TIMebase:SCALe {time}")

    def close(self):
        if self._device is not None:
            self._device.before_close()
            self._device.close()
