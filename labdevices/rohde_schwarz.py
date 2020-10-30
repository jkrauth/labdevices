import pyvisa as visa 
import time
import os
import sys
import numpy as np
import numpy
rm = visa.ResourceManager()
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
        self.device = None
        if connection_type == conn_types[0]:
            self.device_address = usb_dict[instrument]
        elif connection_type == conn_types[1]:
            device_IPaddress = IP_dict[instrument]
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

    # def ieee_query(self,cmd):
    #     self.device.timeout = 20000
    #     self.write(cmd)
    #     response = self.device.query_binary_values(f'{cmd}', datatype='s')
    #     return response[0]
        
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
        self.write(f'CHANnel{channel}:DATA:POINts DEFault')
        voltage = self.query(f'FORMat ASC; CHANnel{channel}:DATA?')
        x_header = self.query(f'CHANnel{channel}:DATA:HEADer?') # returns (xstart, xstop, length)
        x_header = x_header.split(',')
        t = np.linspace(float(x_header[0]), float(x_header[1]), int(x_header[2]))
        print(f'voltage array length: {len(voltage)}')
        print(f'header: xstart {x_header[0]}, xstop {x_header[1]}, array length {x_header[2]}')

        return t, voltage

    def set_t_scale(self, time):
        """format example: 1.E-9"""
        self.write(cmd = f":TIMebase:SCALe {time}")



    def close(self):
        if self.device is not None:
            self.device.before_close() 
            self.device.close()