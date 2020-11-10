"""
Module for Rohde & Schwarz devices.
"""

import pyvisa
import numpy as np
from time import sleep
import os
import sys

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
        Increasing the timeout time couldn't solve the issue."""
        raw_y = self.query('TRAC:DATA? TRACE1')
        y = [float(i) for i in raw_y.split(',')]
        sleep(0.1)
        x_start = float(self.query('FREQ:STAR?'))
        x_stop = float(self.query('FREQ:STOP?'))
        x = list(np.linspace(x_start, x_stop, len(y)))
        return x, y
    
    @property
    def idn(self) -> str:
        """Returns the identification string of the device."""
        return self.query('*IDN?')


rm = pyvisa.ResourceManager()
# rm_list = rm.list_resources()
cur_dir = os.path.abspath(os.path.dirname(__file__))
data_folder = os.path.join(cur_dir,"..", "..","Data")

usb_dict = {
    'R&S RTB2004 0':    '',
    'R&S RTB2004 1':    'USB0::0x0AAD::0x01D6::111287::0::INSTR',
    'R&S RTB2004 2':    '',}

IP_dict = {
    'R&S RTB2004 0':    '10.0.0.80',
    'R&S RTB2004 1':    '10.0.0.81',
    'R&S RTB2004 2':    '10.0.0.82',}

conn_types = ['usb', 'ethernet']

class Oscilloscope:
    """
    Arguments:
    instrument -- str, Device Name from DICT
    connection_type -- str, 'USB' or 'ethernet'
    """ 

    def __init__(self, instrument, connection_type):
        self.instrument = instrument
        self.device = None
        if connection_type == conn_types[0]:
            self.device_address = usb_dict[self.instrument]
        elif connection_type == conn_types[1]:
            device_IPaddress = IP_dict[self.instrument]
            self.device_address = (f'TCPIP::{device_IPaddress}::INSTR')
    
    def initialize(self):
        #rm_list = rm.list_resources()
        self.device = rm.open_resource(self.device_address)

        print(f"Connected to:\n{self.idn}")

    def query(self,cmd):
        response = self.device.query(cmd)
        return response

    def write(self, cmd):
        self.device.write(cmd)

    def ieee_query(self,cmd):
        self.device.timeout = 20000
        self.write(cmd)
        response = self.device.query_binary_values(f'{cmd}', datatype='s')

        return response
        
    @property
    def idn(self):
        idn = self.query("*IDN?")
        return idn

    def V_avg(self,channel):
        self.write(f"MEASurement:SOURce CH{channel}; MEASurement:MAIN MEAN")
        result = self.query("MEASurement:RESult:AVG?")
        return float(result)

        
    def V_max(self,channel):
        self.write(f"MEASurement:SOURce CH{channel}; MEASurement:UPEakvalue")
        result = self.query("MEASurement:RESult:PPEak?") 
        return float(result)

    def VPP(self, channel):
        self.device.timeout = 8000
        self.write(f"MEASurement:SOURce CH{channel}; MEASurement:PEAK" )
        result = self.query("MEASurement:RESult:PEAK?")
        return float(result)

    def Trace(self, channel):
        print(f'acquiring trace for channel {channel}')
        self.write(f'CHANnel{channel}:SINGle')
        voltage = self.query(f'FORMat ASC; CHANnel{channel}:DATA?')
        voltage = voltage.split(',')
        for a, b in enumerate(voltage):
            voltage[a] = float(b)
     

        x_header = self.query(f'CHANnel{channel}:DATA:HEADer?') # returns (xstart, xstop, length,Number of values per sample interval) as comma separated string
        x_header = x_header.split(',')
        t = np.linspace(float(x_header[0]), float(x_header[1]), int(x_header[2]))

        return t, voltage

    def screen_shot(self):
        # self.write('HCOPy:CWINdow ON') this closes all windows when taking screen shot so signal can be seen. 
        # set format 
        self.write('HCOPy:LANG PNG') 
        image_bytes = self.ieee_query('HCOPy:DATA?')
  
        return image_bytes

    def set_t_scale(self, time):
        """format example: 1.E-9"""
        self.write(cmd = f":TIMebase:SCALe {time}")

    def close(self):
        if self.device is not None:
            self.device.before_close() 
            self.device.close()
