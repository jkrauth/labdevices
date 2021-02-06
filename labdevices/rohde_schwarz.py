"""
Module for Rohde & Schwarz devices.
"""
from time import sleep

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
        self.device = None
        #self.timeout = 10000 # in ms, default is 2000
        self.rm = pyvisa.ResourceManager()

    def initialize(self):
        """Connect to the device"""
        self.device = self.rm.open_resource(self.addr)
        print(f'Connected to {self.idn}')

    @property
    def idn(self) -> str:
        """Returns the identification string of the device."""
        return self.query('*IDN?')

    def close(self):
        """Close connection to the device"""
        if self.device is not None:
            self.device.close()
            print('Connection to FPC1000 closed!')
        else:
            print('FPC1000 is already closed.')

    def query(self, cmd: str) -> str:
        """Send a command and receive the answer"""
        respons = self.device.query(cmd).rstrip()
        return respons

    def get_trace(self):
        """Get the trace which is currently shown on the display.
        For some reason this function sometimes times out.
        Increasing the timeout time couldn't solve the issue.

        Return x and y as lists of floats.
        """
        raw_y = self.query('TRAC:DATA? TRACE1')
        y = [float(i) for i in raw_y.split(',')]
        sleep(0.1)
        x_start = float(self.query('FREQ:STAR?'))
        x_stop = float(self.query('FREQ:STOP?'))
        x = list(np.linspace(x_start, x_stop, len(y)))
        return x, y

    def get_system_alarm(self) -> str:
        """Return system alarms and clear alarm buffer."""
        respons = self.device.query('SYST:ERR:ALL?')
        return respons

rm = pyvisa.ResourceManager()
# rm_list = rm.list_resources()

usb_dict = {
    'R&S RTB2004 0':    'USB0::0x0AAD::0x01D6::111290::INSTR',
    'R&S RTB2004 1':    'USB0::0x0AAD::0x01D6::111287::0::INSTR',
    'R&S RTB2004 2':    'USB0::0x0AAD::0x01D6::111280::INSTR',}

IP_dict = {
    'R&S RTB2004 0':    '10.0.0.80',
    'R&S RTB2004 1':    '10.0.0.81',
    'R&S RTB2004 2':    '10.0.0.82',}

conn_types = ['usb', 'ethernet']

class Oscilloscope:
    """
    Is tested with the following Rohde & Schwarz oscilloscope
    models:

    """
    def __init__(self, instrument: str, connection_type: str):
        """
        Arguments:
        instrument -- str, Device Name from DICT
        connection_type -- str, 'USB' or 'ethernet'
        """
        self.instrument = instrument
        self.device = None
        if connection_type == conn_types[0]:
            self.device_address = usb_dict[self.instrument]
        elif connection_type == conn_types[1]:
            device_ip_address = IP_dict[self.instrument]
            self.device_address = (f'TCPIP::{device_ip_address}::INSTR')

    def initialize(self):
        """Connect to device."""
        #rm_list = rm.list_resources()

        self.device = rm.open_resource(self.device_address)
        print(f"Connected to:\n{self.idn}")


    def query(self, cmd: str):
        response = self.device.query(cmd)
        return response

    def write(self, cmd: str):
        self.device.write(cmd)

    def ieee_query(self, cmd: str):
        self.device.timeout = 20000
        self.write(cmd)
        response = self.device.query_binary_values(f'{cmd}', datatype='s')

        return response

    @property
    def idn(self):
        idn = self.query("*IDN?")
        return idn

    def V_avg(self,channel: int):
        self.write(f"MEASurement:SOURce CH{channel}; MEASurement:MAIN MEAN")
        result = self.query("MEASurement:RESult?")
        return float(result)


    def V_max(self,channel: int):

        self.write(f"MEASurement:SOURce CH{channel}; MEASurement:MAIN UPEakvalue")
        result = self.query("MEASurement:RESult?")
        return float(result)

    def VPP(self, channel: int):
        self.write(f"MEASurement:SOURce CH{channel}; MEASurement:MAIN PEAK")
        result = self.query("MEASurement:RESult?")
        return float(result)

    def Trace(self, channel: int):
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
        # self.write('HCOPy:CWINdow ON') this closes all windows when taking screen shot so signal can be seen.
        # set format
        self.write('HCOPy:LANG PNG')
        image_bytes = self.ieee_query('HCOPy:DATA?')

        return image_bytes

    def set_t_scale(self, time: str):
        """format example: '1.E-9'"""
        self.write(cmd = f":TIMebase:SCALe {time}")

    def close(self):
        if self.device is not None:
            self.device.before_close()
            self.device.close()
