"""
Module for Rohde & Schwarz devices.

File name: rohde_schwarz.py
Author: Andres Martinez de Velasco
Date created: 2020/11/11
Python Version: 3.7

"""
from time import sleep
import re
from typing import NamedTuple
import numpy as np
import pyvisa

PREAMBLE_TYPES = (float, float, int, int)

class Preamble(NamedTuple):
    """ The data structure containing the axis information of the waveform """
    x_start: PREAMBLE_TYPES[0]              # in sec
    x_stop: PREAMBLE_TYPES[1]               # in sec
    points: PREAMBLE_TYPES[2]               # waveform length in samples
    values_per_sample: PREAMBLE_TYPES[3]    # usually 1


class FPC1000:
    """Simple spectrum analyzer.
    Works for now with an Ethernet connection.
    USB is not implemented.
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
    Tested with models: RTB2000
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
        self._device = pyvisa.ResourceManager().open_resource(
            self.device_address
            )
        print(f"Connected to:\n{self.idn}")


    def query(self, cmd: str) -> str:
        response = self._device.query(cmd).strip('\n\x00\x00\x00')
        return response

    def write(self, cmd: str):
        self._device.write(cmd)

    def ieee_query(self, cmd: str) -> bytes:
        self._device.timeout = 20000
        response = self._device.query_binary_values(cmd, datatype='s')
        return response[0]

    @property
    def idn(self):
        """ Get device identity """
        idn = self.query("*IDN?")
        return idn

    def get_volt_avg(self,channel: int) -> float:
        """ Installs a screen measurement and starts an
        average value measurement.
        Returns:
        average value -- float
        """
        self.write(f"MEASurement:SOURce CH{channel}; MEASurement:MAIN MEAN")
        result = self.query("MEASurement:RESult?")
        return float(result)

    def get_volt_max(self,channel: int) -> float:
        """ Installs a screen measurement and starts a
        maximum value measurement.
        Returns:
        maximum value -- float
        """
        self.write(f"MEASurement:SOURce CH{channel}; MEASurement:MAIN UPEakvalue")
        result = self.query("MEASurement:RESult?")
        return float(result)

    def get_volt_peakpeak(self, channel: int) -> float:
        """ Installs a screen measurement and starts a vertical
        peak-to-peak measurement.
        Returns:
        peak-to-peak value -- float
        """
        self.write(f"MEASurement:SOURce CH{channel}; MEASurement:MAIN PEAK")
        result = self.query("MEASurement:RESult?")
        return float(result)

    def get_trace(self, channel: int):
        """ Get the trace of a given channel from the oscilloscope.
        Returns:
        time, voltage -- as numpy arrays
        """
        # Set channel for single trigger
        self.write(f'CHANnel{channel}:SINGle')
        # Get trace data
        voltage = self.query(f'FORMat ASC; CHANnel{channel}:DATA?').split(',')
        voltage = np.asarray(voltage).astype(np.float)
        # Get time data
        # this query returns (xstart, xstop, length,Number of values per sample interval) as string
        preamble = self.get_preamble(channel)
        time = np.linspace(preamble.x_start, preamble.x_stop, preamble.points)
        return time, voltage

    def get_preamble(self, channel: int) -> Preamble:
        """Requests information about he selected waveform source.
        Returns:
        preamble -- Preamble"""
        respons = self.query(f'CHANnel{channel}:DATA:HEADer?').split(',')
        parameters = map(lambda x, y: x(y), PREAMBLE_TYPES, respons)
        return Preamble(*parameters)

    def get_screen_shot(self) -> bytes:
        """Get an image of the oscilloscope display. The return can be
        simply written to a file. Don't forget the binary mode then.
        Returns:
        png image -- bytes
        """
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
        """ Close the device. """
        if self._device is None:
            print('Device already closed.')
        self._device.before_close()
        self._device.close()
        self._device = None
