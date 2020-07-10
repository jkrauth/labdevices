"""
Driver for vacuum gauges connected to the 
Granville-Phillips 350 UHV Gauge Controller.                               
Commands and settings for serial communication
are found in the Instruction Manual for the Series 350
in the docs folder.


File name: granville_phillips.py
Author: Julian Krauth
Date created: 2019/07/10
Python Version: 3.7                
"""
import pyvisa
from time import sleep

class GP350:

    DEFAULTS = {
        'write_termination': '\r\n',
        'read_termination': '\r\n',
        'encoding': 'ascii',
        'baudrate': 300,
        'timeout': 100,
        'parity': visa.constants.Parity.none,
        'data_bits': 7,
        'stop_bits': visa.constants.StopBits.two,
        'flow_control': visa.constants.VI_ASRL_FLOW_NONE,
        'query_termination': '?',
    }

    device = None

    def __init__(self, port):
        self.port = port # e.g.: '/dev/ttyUSB0'

    def initialize(self):
        port = 'ASRL'+self.port+'::INSTR'
        rm = pyvisa.ResourceManager()
        self.device = rm.open_resource(
            port,
            timeout=self.DEFAULTS['timeout'],
            encoding=self.DEFAULTS['encoding'],
            parity=self.DEFAULTS['parity'],
            baud_rate=self.DEFAULTS['baudrate'],
            data_bits=self.DEFAULTS['data_bits'],
            stop_bits=self.DEFAULTS['stop_bits'],
            flow_control=self.DEFAULTS['flow_control'],
            write_termination=self.DEFAULTS['write_termination'],
            read_termination=self.DEFAULTS['read_termination']
        )
        
        # make sure connection is established before doing anything else
        sleep(0.5)
        print(f"Connected to:\n {self.idn}")

    def write(self, cmd):
        self.device.write(cmd)

    def query(self, cmd):
        respons = self.device.query(cmd)
        return respons

    def get_pressure(self):
        cmd = 'DS IG'
        respons = self.query(cmd)
        return respons

    def degas_status(self):
        cmd = 'DGS'
        respons = self.query(cmd)
        return respons

    def degas(self, on_off: str):
        """
        Arguments:
        on_off -- 'ON' or 'OFF'
        """
        cmd = f'DG {on_off}'
        respons = self.query(cmd)
        print(respons)

    def filament(self, which: int, on_off: str):
        """
        Arguments:
        which -- 1, 2; selection of filament
        on_off -- 'ON' or 'OFF'
        Returns:
        str -- 'OK' or 'INVALID'
        """
        cmd = f'IG{which} {on_off}'
        respons = self.query(cmd)
        return respons
