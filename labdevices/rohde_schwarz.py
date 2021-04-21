"""
Module for Rohde & Schwarz devices.

File name: rohde_schwarz.py
Author: Andres Martinez de Velasco
Date created: 2020/11/11
Python Version: 3.7

"""
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

    def get_trace(self):
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



class FPC1000Dummy:
    """ For testing only """
    def __init__(self, address: str):
        self.address = address
        self.idn = 'dummy'

    def initialize(self):
        pass

    def close(self):
        pass

    def get_trace(self):
        x_data = np.arange(10)
        y_data = np.arange(10)
        return x_data, y_data


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


class OscilloscopeDummy:
    """ Dummy class for R&S Oscilloscope """
    def __init__(self, address: str):
        self.address = address
        self.value = 10.
        self.idn = 'DummyScope'

    def initialize(self):
        pass

    def close(self):
        pass

    def get_volt_avg(self, channel: int):
        return self.value

    def get_volt_max(self, channel: int):
        return self.get_volt_avg(channel)

    def get_volt_peakpeak(self, channel: int):
        return self.get_volt_avg(channel)

    def get_trace(self, channel: int):
        x_data = np.arange(int(self.value))
        return x_data, x_data
