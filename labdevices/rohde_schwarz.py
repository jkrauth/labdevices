"""
Module for Rohde & Schwarz devices.

File name: rohde_schwarz.py
Author: Andres Martinez de Velasco
Date created: 2020/11/11
Python Version: 3.7

"""
import re
from typing import NamedTuple, Tuple, get_type_hints
import numpy as np
import pyvisa

from ._mock.rohde_schwarz import PyvisaDummy

class Preamble(NamedTuple):
    """ The data structure containing the axis information of the waveform """
    # Do not change the order of these lines! (the get_preamble method relies on it.)
    x_start: float          # in sec
    x_stop: float           # in sec
    points: int             # waveform length in samples
    values_per_sample: int  # usually 1


class RSDevice:
    """ Baseclass for Rohde & Schwarz devices according to SCPI standard. """
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

    def close(self):
        """ Close the device. """
        if self._device is None:
            print('Device already closed.')
        self._device.before_close()
        self._device.close()
        self._device = None

    def write(self, cmd: str):
        """ Write message to device """
        self._device.write(cmd)

    def query(self, cmd: str) -> str:
        """ Query the device. """
        response = self._device.query(cmd)
        return response

    def ieee_query(self, cmd: str) -> bytes:
        """ Query binary data. Used mostly for screenshots. """
        #self._device.timeout = 20000
        response = self._device.query_binary_values(cmd, datatype='s')
        return response[0]

    @property
    def idn(self):
        """ Get device identity """
        idn = self.query("*IDN?")
        return idn

    def get_system_alarm(self) -> list:
        """Query system alarms and clear alarm buffer.
        Returns:
        list of tuples with error code and description
        """
        raw = self._device.query('SYST:ERR:ALL?').strip().split(',')
        # Formatting answer into list of tuples
        respons = [(int(raw[i]), raw[i+1].strip('"')) for i in range(0, len(raw), 2)]
        return respons

class FPC1000(RSDevice):
    """Simple spectrum analyzer.
    Works for now via Ethernet.
    It can be connected via USB, but is not a normal USB device.
    When connected via USB use address = '172.16.10.10'
    This is currently not supported in Linux it seems.
    """
    def __init__(self, address: str):
        """
        Arguments:
        address -- str, IP address.
        """
        # Must be IP address:
        if not bool(re.match(r'\d+\.\d+\.\d+\.\d+', address)):
            raise ValueError("Address needs to be an IP address.")
        super().__init__(address)

    def get_trace(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get the trace which is currently shown on the display.
        Returns:
        x, y -- as numpy arrays.
        """
        # Get y data
        raw_y = self.query('TRACe:DATA? TRACE1').split(',')
        y_data = np.asarray(raw_y).astype(np.float)
        points = len(y_data)
        # Get x data
        x_start = float(self.query('FREQ:STAR?'))
        x_stop = float(self.query('FREQ:STOP?'))
        x_data = np.linspace(x_start, x_stop, points)
        return x_data, y_data


class FPC1000Dummy(FPC1000):
    """
    Mock Rohde & Schwarz Spectrum Analyzer FPC1000
    """

    def initialize(self):
        """ Establish connection to mock device. """
        self._device = PyvisaDummy()
        print(f"Connected to:\n{self.idn}")


class Oscilloscope(RSDevice):
    """
    Is tested with the following Rohde & Schwarz oscilloscope
    Tested with models: RTB2000
    """

    def query(self, cmd: str) -> str:
        """Query the device."""
        # Strip off a few characters that happen to be there
        # via USB connection... not sure why.
        return super().query(cmd).strip('\n\x00\x00\x00')


    def get_volt_avg(self, channel: int) -> float:
        """ Installs a screen measurement and starts an
        average value measurement.
        Returns:
        average value -- float
        """
        self.write(f"MEASurement:SOURce CH{channel}; MEASurement:MAIN MEAN")
        result = self.query("MEASurement:RESult?")
        return float(result)

    def get_volt_max(self, channel: int) -> float:
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

    def get_screenshot(self) -> bytes:
        """Get an image of the oscilloscope display. The return can be
        simply written to a file. Don't forget the binary mode then.
        Returns:
        png image -- bytes
        """
        # Close all windows when taking screenshot so signal can be seen.
        # self.write('HCOPy:CWINdow ON')
        # Set format
        self.write('HCOPy:LANG PNG')
        image_bytes = self.ieee_query('HCOPy:DATA?')
        return image_bytes

    def get_trace(self, channel: int) -> Tuple[np.ndarray, np.ndarray]:
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
        preamble_types = list(get_type_hints(Preamble).values())
        parameters = map(lambda x, y: x(y), preamble_types, respons)
        return Preamble(*parameters)

    def set_t_scale(self, time: str):
        """format example: '1.E-9'"""
        self.write(cmd = f":TIMebase:SCALe {time}")


class OscilloscopeDummy(Oscilloscope):
    """ Dummy class for R&S Oscilloscope """

    def initialize(self):
        """ Establish connection to mock device. """
        self._device = PyvisaDummy()
        print(f"Connected to:\n{self.idn}")
