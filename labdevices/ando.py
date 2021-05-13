"""
Module that implements the commands used for the control
of the ANDO Spectrum Analyzer. The device is connected via a
prologix gpib-to-ethernet adapter.

File name: ando.py
Author: Julian Krauth
Date created: 27.11.2019
Python Version: 3.7
"""
from typing import Tuple
from time import sleep
import numpy as np

from ._mock.ando import PLXDummy

try:
    from plx_gpib_ethernet import PrologixGPIBEthernet
except ImportError as err:
    print(
        "Can't import PrologixGPIBEthernet module for ando.SpectrumAnalyzer!\n" +
        "Install plx_gpib_ethernet package from: \n" +
        "https://github.com/nelsond/prologix-gpib-ethernet"
    )



class SpectrumAnalyzer:
    """Driver for the Ando Spectrum Analyzer. The connection is done via
    a prologix gpib-to-ethernet adapter."""

    def __init__(
            self,
            ip_addr: str,
            gpib: int=1):
        """
        Arguments:
        ip_addr -- str, ip address of the GPIB Ethernet Adapter
        gpib -- int, address of the gpib device, a number between 1 and 15
        """
        self.ip_addr = ip_addr
        self.gpib = gpib
        self._device = None


    def initialize(self):
        """Open connection to device."""
        self._device = PrologixGPIBEthernet(self.ip_addr)
        self._device.connect()
        self._device.select(self.gpib)
        print('Connected to Ando')

        # idn_respons = [
        #     "Manufacturer: ",
        #     "Device name: ",
        #     "Serial no.: ",
        #     "Software version: "
        # ]
        # i=0
        # for each in self.idn:
        #     print(idn_respons[i], each)
        #     i+=1

    def close(self):
        """Close connection to device."""
        if self._device is not None:
            self._device.close()
        else:
            print('Ando is already closed!')

    def write(self, cmd: str):
        """ Send command to device """
        self._device.write(cmd)

    def query(self, query: str) -> str:
        """ Query device for information """
        query = self._device.query(query)
        query = query.rstrip('\r\n')
        return query

    @property
    def idn(self) -> list:
        """ Get device identity """
        idn = self.query('*IDN?')
        return idn.split(',')


    def finish(self):
        """waits till a certain task is finished"""
        while self.query('SWEEP?') != '0':
            sleep(.5)

    @property
    def sampling(self) -> int:
        """ Get sampling rate"""
        result = self.query('SMPL?')
        return int(result)

    @sampling.setter
    def sampling(self, smpl: int):
        """ Set sampling rate"""
        if smpl<11 or smpl>1001:
            print("Use a sampling number from 11 to 1001!")
        else:
            self.write(f'SMPL{smpl}')

    def do_sweep(self):
        """
        Does a sweep with the current settings and saves the data in a buffer.
        Read out the buffer using self.get_x_axis() and self.get_y_axis()
        """
        self.write('SGL')

    def _get_data(self, cmd: str) -> np.ndarray:
        """
        Retreives x or y data.

        Argument:
        cmd = 'LDATA' or 'WDATA', for Level- or Wavelength- data"""
        # Number of bins per step . Has to be small to fit into buffer length.
        step = 20
        #i_rep = int((self.sampling()-1)/step)
        i_rep = 50
        for i in range(i_rep):
            #get data
            result = self.query('%s R%i-R%i' % (cmd, step*i+1, step*(i+1)))
            axis_piece = result.lstrip().split(',')
            axis_piece = axis_piece[1:]
            axis_piece = np.array(axis_piece, dtype = float)
            if i == 0:
                data = axis_piece
            else:
                data = np.append(data, axis_piece)
        return data

    def get_x_data(self) -> np.ndarray:
        """ Obtain the x axis values in units of nm. """
        return self._get_data('WDATA')

    def get_y_data(self) -> np.ndarray:
        """ Obtain the y axis values in the units shown on the screen. """
        return self._get_data('LDATA')

    def get_ana(self) -> tuple:
        """
        this method only works when ANDO is in a certain mode???
        Haven't figured that out yet...

        Return:
            tuple -- center wavelength, bandwidth, modes
        """
        analysis = self.query('ANA?')
        if len(analysis) == 3:
            center_wavelength = analysis[0]
            bandwidth         = analysis[1]
            modes             = analysis[2]
            #print analysis
        else:
            print('Analysis Error: No data available!')
            center_wavelength = bandwidth = modes = 0
            #exit()
        return center_wavelength, bandwidth, modes

    @property
    def center(self) -> float:
        """
        Get the center wavelength in units of nm.
        Allowed values are between 350.00 and 1750.00 nm
        """
        wavelength = self.query('CTRWL?')
        return float(wavelength)

    @center.setter
    def center(self, wavelength: float):
        """
        Set the center wavelength in units of nm.
        Allowed values are between 350.00 and 1750.00 nm
        """
        self.write('CTRWL%f' % (wavelength))

    @property
    def span(self) -> float:
        """
        Get the wavelength span in units of nm.
        Allowed values are 0, or between 1.00 and 1500.00 nm
        """
        span = self.query('SPAN?')
        return float(span)

    @span.setter
    def span(self, span: float):
        """
        Set the wavelength span in units of nm.
        Allowed values are 0, or between 1.00 and 1500.00 nm
        """
        self.write('SPAN%f' % (span))

    def get_measurement_mode(self) -> Tuple[int, str]:
        """
        Get measurement mode of ANDO for cw or pulsed laser
        0 pulsed mode
        1 cw mode
        """
        modes = {
            0: 'pulsed',
            1: 'cw',
        }
        mode = int(self.query('CWPLS?'))
        return mode, modes[mode]

    def set_measurement_mode(self, mode: int):
        """
        Get/Set measurement mode of ANDO for cw or pulsed laser
        0 pulsed mode
        1 cw mode
        """
        if mode == 0:
            self.write('PLMES')
        elif mode == 1:
            self.write('CLMES')
        else:
            print(f"ANDO mode number has to be either 0 or 1, not {mode}!")

    def get_trigger_mode(self) -> Tuple[int, str]:
        """
        0 - measuring chop light by using a low pass filter
        1 - external trigger mode
        2 + hold time [ms] - peak hold mode
        """
        modes = {
            0: 'LPF',
            1: 'EXTRG',
            2: 'PKHLD'
        }
        mode = int(self.query('PLMOD?'))
        if mode < 2:
            result = (mode, modes[mode])
        else:
            result = (mode, modes[2])
        return result

    def set_hold_mode(self, time: int):
        """
        If in pulsed mode (see get_measurement_mode method) the Ando can use three
        different ways to trigger. One is the peak_hold_mode, which
        needs the rough pulse repetition time.
        Argument:
        time - int, in ms
        """
        self.write(f'PKHLD{time}')


class SpectrumAnalyzerDummy(SpectrumAnalyzer):
    """Class for testing purpose only."""

    def initialize(self):
        """Open connection to device."""
        self._device = PLXDummy()
        self._device.connect()
        self._device.select(self.gpib)
        print(f'Connected to {self.idn}')



if __name__ == "__main__":

    print("This is the Conroller Driver example for the Ando Spectrometer.")
    ando = SpectrumAnalyzer('10.0.0.40', 1234)
    # Connect to Ando
    ando.initialize()
    # Do what you want

    # Close connection
    ando.close()
