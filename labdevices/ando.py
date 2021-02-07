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
    ando = None

    def __init__(
            self,
            ip='10.0.0.40',
            gpib=1):
        """
        Arguments:
        ip -- str, ip address of the GPIB Ethernet Adapter
        gpib -- int, address of the gpib device, a number between 1 and 15
        """
        self.ip = ip
        self.gpib = gpib

    def initialize(self):
        """Open connection to device."""
        self.ando = PrologixGPIBEthernet(self.ip)
        self.ando.connect()
        self.ando.select(self.gpib)

        idn = self.send_query('*IDN?')
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

    def send_cmd(self, cmd:str):
        self.ando.write(cmd)

    def send_query(self, query:str):
        query = self.ando.query(query)
        query = query.rstrip('\r\n')
        query = query.split(',')
        return query

    def finish(self):
        """waits till a certain task is finished"""
        while int(self.ando.query('SWEEP?')[0])!=0:
            sleep(.5)

    def sampling(self, smpl:int=None):
        """ Get/Set sampling rate"""
        if smpl is None:
            smpl = self.send_query('SMPL?')
            return int(smpl[0])
        elif smpl<11 or smpl>1001:
            print("Use a sampling number from 11 to 1001!")
        else:
            self.send_cmd(f'SMPL{smpl}')

    def close(self):
        """Close connection to device."""
        if self.ando is not None:
            self.ando.close()
        else:
            print('Ando is already closed!')

    def sweep(self):
        """
        Does a sweep with the current settings and saves the data in a buffer.
        Read out the buffer using self.getData()
        """
        self.send_cmd('SGL')

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
            axis = self.send_query('%s R%i-R%i' % (cmd,step*i+1,step*(i+1)))
            axis = axis[1:]
            axis = np.array(axis, dtype = float)
            if i == 0:
                x = axis
            else:
                x = np.append(x,axis)
        return x

    def get_x_axis(self):
        return self._get_data('WDATA')

    def get_y_data(self):
        return self._get_data('LDATA')

    def get_ana(self):
        """
        this method only works when ANDO is in a certain mode???
        Haven't figured that out yet...
        """
        analysis = self.send_query('ANA?')
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


    def ctr(self, wavelength:float=None):
        """
        Get/Set the center wavelength in units of nm.
        Allowed values are between 350.00 and 1750.00 nm
        """
        if wavelength is None:
            wavelength = self.send_query('CTRWL?')
            return float(wavelength[0])
        else:
            self.send_cmd('CTRWL%f' % (wavelength))

    def span(self, span:float=None):
        """
        Get/Set the wavelength span in units of nm.
        Allowed values are 0, or between 1.00 and 1500.00 nm
        """
        if span is None:
            span = self.send_query('SPAN?')
            return float(span[0])
        else:
            self.send_cmd('SPAN%f' % (span))

    def cw_mode(self, cw:bool=None):
        """
        Get/Set measurement mode of ANDO for cw or pulsed laser
        0 pulsed mode
        1 cw mode
        """
        if cw is None:
            cw = self.send_query('CWPLS?')
            cw = int(cw[0])
            return cw
        if not cw:
            self.send_cmd('PLMES')
        elif cw:
            self.send_cmd('CLMES')
        else:
            print(cw)
            print("ANDO mode number has to be either 0 or 1!")

    def peak_hold_mode(self, time:int):
        """
        If in pulsed mode (see cwMode method) the Ando can use three
        different ways to trigger. One is the peakHoldMode, which
        needs the rough pulse repetition time.
        Unit: ms
        """
        self.send_cmd(f'PKHLD{time}')


class SpectrumAnalyzerDummy:
    """Class for testing purpose only."""
    ando = None

    def __init__(
        self,
        ip='10.0.0.40',
        gpib=1):

        self.ip = ip
        self.gpib = gpib
        self.wavelength = 390
        self.span_par = 20
        self.cw = 0

    def initialize(self):
        self.ando = 1
        print('Connected to Ando Dummy')

    def close(self):
        if self.ando is not None:
            pass
        else:
            print('Ando dummy is already closed!')

    def ctr(self, wavelength=None):
        if wavelength is None:
            return self.wavelength
        else:
            self.wavelength = wavelength

    def span(self, span=None):
        if span is None:
            return self.span_par
        else:
            self.span_par = span

    def cw_mode(self, cw=None):
        if cw is None:
            return self.cw
        else:
            self.cw = cw

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
