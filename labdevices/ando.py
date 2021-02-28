"""
Module that implements the commands used for the control
of the ANDO Spectrum Analyzer. The device is connected via a
prologix gpib-to-ethernet adapter.

File name: ando.py
Author: Julian Krauth
Date created: 27.11.2019
Python Version: 3.7
"""
from time import sleep
import numpy as np

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
            ip_addr='10.0.0.40',
            gpib=1):
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

        idn = self.query('*IDN?')
        idn_respons = [
            "Manufacturer: ",
            "Device name: ",
            "Serial no.: ",
            "Software version: "
        ]
        i=0
        for each in idn:
            print(idn_respons[i], each)
            i+=1

    def write(self, cmd:str):
        self._device.write(cmd)

    def query(self, query:str):
        query = self._device.query(query)
        query = query.rstrip('\r\n')
        query = query.split(',')
        return query

    def finish(self):
        """waits till a certain task is finished"""
        while int(self._device.query('SWEEP?')[0])!=0:
            sleep(.5)

    @property
    def sampling(self) -> int:
        """ Get sampling rate"""
        smpl = self.query('SMPL?')
        return int(smpl[0])

    @sampling.setter
    def sampling(self, smpl: int):
        """ Set sampling rate"""
        if smpl<11 or smpl>1001:
            print("Use a sampling number from 11 to 1001!")
        else:
            self.write(f'SMPL{smpl}')


    def close(self):
        """Close connection to device."""
        if self._device is not None:
            self._device.close()
        else:
            print('Ando is already closed!')

    def do_sweep(self):
        """
        Does a sweep with the current settings and saves the data in a buffer.
        Read out the buffer using self.getData()
        """
        self.write('SGL')

    def _get_data(self, cmd:str):
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
            axis = self.query('%s R%i-R%i' % (cmd,step*i+1,step*(i+1)))
            axis = axis[1:]
            axis = np.array(axis, dtype = float)
            if i == 0:
                x_data = axis
            else:
                x_data = np.append(x_data,axis)
        return x_data

    def get_x_axis(self):
        return self._get_data('WDATA')

    def get_y_data(self):
        return self._get_data('LDATA')

    def get_ana(self):
        """
        this method only works when ANDO is in a certain mode???
        Haven't figured that out yet...
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
        return float(wavelength[0])

    @center.setter
    def center(self, wavelength: float=None):
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
        return float(span[0])

    @span.setter
    def span(self, span: float=None):
        """
        Set the wavelength span in units of nm.
        Allowed values are 0, or between 1.00 and 1500.00 nm
        """
        self.write('SPAN%f' % (span))

    @property
    def cw_mode(self) -> int:
        """
        Get measurement mode of ANDO for cw or pulsed laser
        0 pulsed mode
        1 cw mode
        """
        continuous_wave = self.query('CWPLS?')
        return int(continuous_wave[0])

    @cw_mode.setter
    def cw_mode(self, mode: int):
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
            print(mode)
            print("ANDO mode number has to be either 0 or 1!")


    def peak_hold_mode(self, time:int):
        """
        If in pulsed mode (see cwMode method) the Ando can use three
        different ways to trigger. One is the peakHoldMode, which
        needs the rough pulse repetition time.
        Unit: ms
        """
        self.write(f'PKHLD{time}')


class SpectrumAnalyzerDummy:
    """Class for testing purpose only."""

    def __init__(
        self,
        ip_addr='10.0.0.40',
        gpib=1):

        self._device = None
        self.ip_addr = ip_addr
        self.gpib = gpib
        self.center = 390
        self.span = 20
        self.cw_mode = 0

    def initialize(self):
        self._device = 1
        print('Connected to Ando Dummy')

    def close(self):
        if self._device is not None:
            pass
        else:
            print('Ando dummy is already closed!')

    def peak_hold_mode(self, time):
        pass




if __name__ == "__main__":

    print("This is the Conroller Driver example for the Ando Spectrometer.")
    ando = SpectrumAnalyzer()
    # Connect to Ando
    ando.initialize()
    # Do what you want

    # Close connection
    ando.close()
