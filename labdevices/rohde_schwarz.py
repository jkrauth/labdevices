"""
Module for Rohde & Schwarz devices.
"""

import pyvisa
import numpy as np
from time import sleep

class FPC1000:
    """Simple spectrum analyzer."""
    
    def __init__(self, ip: str):
        self.addr = 'TCPIP::'+ip
        self.device = None
        #self.timeout = 10000 # in ms, default is 2000
        self.rm = pyvisa.ResourceManager()

    def initialize(self):
        self.device = self.rm.open_resource(self.addr)
        print(f'Connected to {self.idn}')

    def close(self):
        if self.device is not None:
            self.device.close()
            print('Connection to FPC1000 closed!')
        else:
            print('FPC1000 is already closed.')
        
    def query(self, cmd: str):
        respons = self.device.query(cmd).rstrip()
        return respons

    def get_trace(self):
        raw_y = self.query('TRAC:DATA? TRACE1')
        y = [float(i) for i in raw_y.split(',')]
        sleep(0.1)
        x_start = float(self.query('FREQ:STAR?'))
        x_stop = float(self.query('FREQ:STOP?'))
        x = list(np.linspace(x_start, x_stop, len(y)))
        return x, y
    
    @property
    def idn(self):
        return self.query('*IDN?')
