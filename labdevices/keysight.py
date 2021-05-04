"""
Module for keysight devices, like e.g. oscilloscopes.

File name: keysight.py
Author: Julian Krauth, Andres Martinez de Velasco
Date created: 2020/11/11
Python Version: 3.7

"""
from typing import NamedTuple, Tuple, get_type_hints
import re
import pyvisa as visa
import numpy as np

from ._mock.keysight import PyvisaDummy

class Preamble(NamedTuple):
    """ The data structure of the preamble of a waveform.
    Contains all the trace settings. Used in Oscilloscope class. """
    # Do not change the order of these lines! (the get_preamble method relies on it.)
    data_format: int    # 0 = BYTE, 1 = WORD, 4 = ASCII
    data_type: int      # 0 = NORM, 1 = PEAK, 2 = AVER, 3 = HRES
    points: int         # number of data points transferred
    count: int          # 1 and is always 1
    x_increment: float  # time difference between data points.
    x_origin: float     # always the first data point in memory
    x_reference: int    # specifies the data point associated with x-origin
    y_increment: float  # voltage diff between data points
    y_origin: float     # value is the voltage at center screen
    y_reference: int    # specifies the data point where y-origin occurs


class KeysightDevice:
    """ Parent class for Keysight devices. """

    def __init__(self, address: str):
        """
        Arguments:
        address -- str, VISA address for USB connection or IP for Ethernet.
        """
        self._device = None
        # Check if address has IP pattern:
        if bool(re.match(r'^\d+\.\d+\.\d+\.\d+$', address)):
            self.device_address = (f'TCPIP::{address}::INSTR')
        # E
        elif bool(re.match(r'^USB.+::INSTR$', address)):
            self.device_address = address
        else:
            raise ValueError("Address needs to be an IP or a valid VISA address.")

    def initialize(self) -> None:
        """Establish connection to device."""
        self._device = visa.ResourceManager().open_resource(
            self.device_address, read_termination = '\n'
            )
        print(f"Connected to:\n{self.idn}")

    def close(self):
        """ Close the device. """
        if self._device is None:
            print('Device already closed.')
            return
        self._device.before_close()
        self._device.close()
        self._device = None

    def write(self, cmd: str) -> None:
        """ Send a command to the device """
        self._device.write(cmd)

    def query(self, cmd: str) -> str:
        """ Query  """
        response = self._device.query(cmd)
        return response

    def ieee_query(self, cmd: str) -> bytes:
        """ Query binary data. Used mostly for screenshots. """
        #self._device.timeout = 20000
        response = self._device.query_binary_values(cmd, datatype='s')
        return response[0]

    @property
    def idn(self) -> str:
        """ Get device identity """
        idn = self.query("*IDN?")
        return idn


class Counter(KeysightDevice):
    """ Class for the Keysight / Agilent Counter. Tested with the model 53230A.
    But it should also work for others.
    """

    def reset(self):
        """ Reset device to start from known state. """
        self._device.write('*RST')
        # Clear Error buffer
        self._device.write('*CLS')

    @property
    def gate_time(self) -> float:
        """get the gate time of the counter in seconds"""
        resp = self.query('FREQuency:GATE:TIME?')
        return float(resp)

    @gate_time.setter
    def gate_time(self, gatetime: float):
        """set the gate time of the counter
        to the desired value in seconds"""
        self.write(f'FREQuency:GATE:TIME {gatetime}')

    @property
    def trigger_mode(self) -> str:
        """ Get the trigger mode """
        return self.query("TRIGger:SOURce?")

    @trigger_mode.setter
    def trigger_mode(self, mode: str='IMM'):
        """Set the trigger mode.
        Argument:
        value -- str, 'IMMediate', 'EXTernal', 'BUS'
        """
        options = ('IMMediate', 'IMM', 'EXTernal', 'EXT', 'BUS')
        # clear events register and errors queue
        if mode in options:
            self.write('*CLS')
            self.write(f'TRIGger:SOURce {mode}')
        else:
            raise Exception('Provide an existing mode')

    def start_frequency_measurement(self):
        """ Initialize frequency measurement. """
        self.write(":INIT")

    def read_frequency_measurement(self) -> float:
        """ Get frequency of last measurement from buffer. """
        frequency = self.query("FETCH?")
        return float(frequency)

    def measure_frequency(
        self, expected: float = 10e6,
        resolution: float=0.1, channel: int=1
        ) -> float:
        """Measures the frequency during the time of gate_time
        and returns the result.
        Arguments:
        expected   -- the expected frequency in Hz, default 10 MHz
        resolution -- measurement resolution in Hz, default 0.1 Hz.
        channel    -- only usable if device has the option to measure
                      in channel other than 1.
        Returns:
        frequency"""
        self.reset()
        cmd = f'MEASure:FREQuency? {expected:.0E}, {resolution}, (@{channel})'
        frequency = self.query(cmd)
        return float(frequency)


class CounterDummy(Counter):
    """
    Mock Keysight Counter

    Provides a class that immitates a real counter and can be
    used for development.
    """

    def initialize(self):
        """Establish connection to mock device."""
        self._device = PyvisaDummy()
        print(f"Connected to:\n{self.idn}")



class Oscilloscope(KeysightDevice):
    """
    Class for Keysight oscilloscopes. So far tested with the 3000T X-Series.
    """

    def set_t_scale(self, sec_per_division: float):
        """ Set the units per division """
        self.write(f":TIMebase:SCALe {sec_per_division}")

    def get_volt_avg(self, channel: int) -> float:
        """ Installs a screen measurement and starts an
        average value measurement.
        Returns:
        average value -- float
        """
        self.write(f":MEASure:SOURce CHANnel{channel}")
        result = self.query(":MEASure:VAVerage?")
        return float(result)

    def get_volt_max(self, channel: int) -> float:
        """ Installs a screen measurement and starts a
        maximum value measurement.
        Returns:
        maximum value -- float
        """
        self.write(f":MEASure:SOURce CHANnel{channel}")
        result = self.query(":MEASure:VMAX?")
        return float(result)

    def get_volt_peakpeak(self, channel: int) -> float:
        """ Installs a screen measurement and starts a vertical
        peak-to-peak measurement.
        Returns:
        peak-to-peak value -- float
        """
        self.write(f":MEASure:SOURce {channel}")
        result = self.query(":MEASure:VPP?")
        return float(result)

    def get_screenshot(self) -> bytes:
        """
        Get an image of the oscilloscope display. The return can be
        simply written to a file. Don't forget the binary mode then.
        Returns:
        png image -- bytes
        """
        # To get a NOT inverted image
        self.write(":HARDcopy:INKSaver OFF")
        # Get data
        image_bytes = self.ieee_query(":DISPlay:DATA? PNG, COLor")
        return image_bytes

    def get_trace(self, channel: int) -> Tuple[np.ndarray]:
        """ Get the trace of a given channel from the oscilloscope.
        Returns:
        time, voltage -- as numpy arrays
        """
        # Increase timeout
        general_timeout = self._device.timeout
        self._device.timeout = 20000

        # Prepare waveform and get waveform settings
        self._prepare_trace_readout(channel)
        preamble = self.get_preamble(channel)

        # Get the voltage data
        data_bytes = self.ieee_query(":WAVeform:DATA?")
        voltage = np.asarray(self._bytes_to_voltage(data_bytes, preamble))

        # Reset timeout:
        self._device.timeout = general_timeout

        # Create time axis
        x_min = preamble.x_origin
        x_max = x_min+(preamble.points*preamble.x_increment)
        time = np.arange(x_min, x_max, preamble.x_increment)
        return time, voltage

    def _prepare_trace_readout(self, channel: int):
        """ Moste of these settings are probably already set on the scope.
        So this is to ensure that it also works when some settings are wrong.
        """
        # Set acquisition type to nomal, i.e. not average or smoothing
        self.write(':ACQuire:TYPE NORMal')
        # Set source for waveform commands
        self.write(f':WAVeform:SOURce {channel}')
        # Set for retrieving measurement record
        self.write(':WAVeform:POINts:MODE NORMal')
        # set the data transmission mode to bytes.
        self.write(':WAVeform:FORMat BYTE')

    @staticmethod
    def _bytes_to_voltage(data: bytes, preamble: Preamble) -> list:
        """ Calibrates the data_bytes and returns them as a list.
        Argument:
        data -- byte array
        preamble -- waveform settings

        Returns:
        list -- data converted to voltage"""
        func = lambda val: (val - preamble.y_reference) * preamble.y_increment + preamble.y_origin
        voltage = [func(i) for i in data]
        return voltage

    def get_preamble(self, channel: int) -> Preamble:
        """ Requests the preamble information for the selected waveform source.
        The preamble data contains information concerning the vertical and
        horizontal scaling of the data of the active channel.
        Argument:
        channel -- int
        Returns:
        preamble -- Preamble
        """
        # Set source for waveform commands
        self.write(f':WAVeform:SOURce {channel}')

        respons = self.query(":WAVeform:PREamble?").split(',')

        # Convert strings into correct types
        preamble_types = list(get_type_hints(Preamble).values())
        parameters = list(map(lambda x, y: x(y), preamble_types, respons))
        return Preamble(*parameters)

class OscilloscopeDummy(Oscilloscope):
    """
    Mock Keysight Oscilloscope

    Provides a class that immitates a real oscilloscope and can be
    used for development.
    """
    def initialize(self):
        """Establish connection to mock device."""
        self._device = PyvisaDummy()
        print(f"Connected to:\n{self.idn}")
