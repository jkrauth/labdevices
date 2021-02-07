"""
Module for keysight devices, like e.g. oscilloscopes.

File name: keysight.py
Author: Andres Martinez de Velasco
Date created: 2020/11/11
Python Version: 3.7
"

"""
from random import random
import re
import pyvisa as visa
import numpy as np

rm = visa.ResourceManager()
# rm_list = rm.list_resources()


class Oscilloscope:
    """
    Class for Keysight oscilloscopes. So far tested with models:
    ...
    """
    def __init__(self, address: str):
        """
        Arguments:
        address -- str, VISA address for USB connection or IP for Ethernet.
        """
        self.device = None
        # Check if address has IP pattern:
        if bool(re.match(r'\d+\.\d+\.\d+\.\d+', address)):
            self.device_address = (f'TCPIP::{address}::INSTR')
        # E
        elif bool(re.match('^USB.+::INSTR$', address)):
            self.device_address = address

    def initialize(self):
        """Establish connection to device."""
        self.device = rm.open_resource(self.device_address)

        print(f"Connected to:\n{self.idn}")

    def query(self, cmd):
        response = self.device.query(cmd)
        return response

    def write(self, cmd):
        self.device.write(cmd)

    def ieee_query(self, cmd):
        self.device.timeout = 20000
        self.write(cmd)
        response = self.device.query_binary_values(f'{cmd}', datatype='s')
        return response[0]


    @property
    def idn(self):
        idn = self.query("*IDN?")
        return idn

    def set_t_scale(self,cmd):
        self.write(f":TIMebase:SCALe {cmd}")

    def V_avg(self, channel):
        self.write(f":MEASure:SOURce CHANnel{channel}")
        result = self.query(":MEASure:VAVerage?")
        return float(result)

    def V_max(self, channel):
        self.write(f":MEASure:SOURce CHANnel{channel}")
        result = self.query(":MEASure:VMAX?")
        return float(result)


    def VPP(self, channel):
        self.write(f":MEASure:SOURce {channel}")
        result = self.query(":MEASure:VPP?")
        return float(result)

    def screen_shot(self):
        """
        For some unknown reason, this function only works reliably
        when using ethernet connection to the oscilloscope
        """
        self.write(":HARDcopy:INKSaver OFF")
        image_bytes = self.ieee_query(":DISPlay:DATA? PNG, COLor")
        return image_bytes

    def close(self):
        if self.device is not None:
            self.device.before_close()
            self.device.close()

    def Trace(self, channel):

        self.device.timeout = 10000
        self.write(':ACQuire:TYPE NORMal')
        self.write(f':WAVeform:SOURce {channel}')
        self.write(':WAVeform:POINts:MODE NORMal')
        self.write(':WAVeform:FORMat BYTE') #WORD or ASCii are other options

        time_scale = self.query(':TIMebase:SCALe?')

        (
        wav_form,
        acq_type,
        wfmpts,
        avgcnt,
        x_increment,
        x_origin,
        x_reference,
        y_increment,
        y_origin,
        y_reference
        ) = self.query(":WAVeform:PREamble?").split(',')

        # print(f'wave form is: {wav_form}')
        # print(f'acquire type is: {acq_type}')
        # print(f'wave form points are: {wfmpts}')
        # print(f'average count is: {avgcnt}')
        # print(f'x increment is {x_increment}')
        # print(f'x origin is {x_origin}')
        # print(f'y increment is {y_increment}')
        # print(f'y origin is {y_origin}')
        # print(f'y reference is {y_reference}')

        data_bytes = self.ieee_query(":WAVeform:DATA?")

        n_length = len(data_bytes)

        voltage_conversion = lambda x: (float(x) - float(y_reference)) * float(y_increment) + float(y_origin)
        voltage = [voltage_conversion(i) for i in data_bytes]

        x_min = eval(x_origin)
        step_size = eval(x_increment)
        x_max = (x_min+(n_length*step_size))
        time_val = np.arange(x_min, x_max, step_size)
        self.write(f':TIMebase:SCALe {time_scale}') #set time scale back to normal
        return time_val, voltage


class OscilloscopeDummy:
    """Class for testing purpose only. No device needed."""
    def __init__(self, port):
        self.port = port
        self.result = 0

    def initialize(self):
        print("Connected to dummy device")

    def finalize(self):
        print("Closing dummy device")

    def V_avg(self, channel):
        self.result = self.result + random()*10
        return self.result

    def V_max(self, channel):
        self.result = self.result + 1
        return self.result

    def VPP(self, channel):
        self.VPP_result = random()* 10
        return self.VPP_result

    def set_t_scale(self, time):
        pass

    def nothing(self, channel):
        return 0

    def close(self):
        pass

    def Trace(self, trace_channel, trace_write_file):
        x = self.result + random()*10
        y = self.result + random()*10
        print('dummy trace acquired')
        return x, y


    def __str__(self):
        return "Dummy Driver"
