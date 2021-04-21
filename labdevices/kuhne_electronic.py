"""
Module to control the MKU LO 8-13 PLL Oscillator from Kuhne-Electronics.
Connection is done via a USB-serial cable.
Set to 7.02GHz, the main output yields the second harmonic at 14.04GHz.

An example of how to run the code is found at the end of this file.

File name: oscillator.py
Author: Julian Krauth
Date created: 2019/05/22
Python Version: 3.7

"""
from time import sleep
import pyvisa

def get_available_devices():
    """ Print visa addresses of available devices """
    dev_list = pyvisa.ResourceManager().list_resources()
    return dev_list

DEFAULTS = {'write_termination': None,
            'read_termination': '\r\n',
            'baud_rate': 115200,
            'parity': pyvisa.constants.Parity.none,
            'data_bits': 8,
            'stop_bits': pyvisa.constants.StopBits.one,
            'flow_control': pyvisa.constants.VI_ASRL_FLOW_NONE,
}

class LocalOscillator:
    """ This class is written for the MKU LO 8-13 PLL local oscillator from Kuhne Electronic.
    It might also work for other oscillators from Kuhne Electronic.
    """
    def __init__(self, address: str):
        self.address = address
        self.device = None

    def initialize(self):
        """ Connect to the device. """
        self.device = pyvisa.ResourceManager('@py').open_resource(
            self.address, **DEFAULTS
        )
        sleep(0.1)
        print(f'Connected to: {self.address}')

    def close(self):
        """ Close connection to device. """
        if self.device is None:
            return
        self.device.before_close()
        self.device.close()

    # def write(self, command: str):
    #     """ Send a command to the device. """
    #     self.device.write(command)

    def query(self, command: str):
        """ Query the device. """
        return self.device.query(command)

    def set_frequency(self, value: float):
        """Set frequency of oscillator in units of GHz"""
        ghz = int(value)
        mhz = (value - int(value)) * 10**3
        khz = (mhz - int(mhz)) * 10**3
        command1 = '%03dGF1' % ghz
        command2 = '%03dMF1' % mhz
        command3 = '%03dkF1' % khz
        _ = self.query(command1)
        sleep(0.1)
        _ = self.query(command2)
        sleep(0.1)
        _ = self.query(command3)
        print(f'Frequency set to {ghz:02d} GHz, {int(mhz):03d} MHz, and {int(khz):03d} kHz.')


if __name__ == "__main__":
    dev = LocalOscillator(get_available_devices()[0])
    dev.initialize()
    dev.set_frequency(7.02)
    dev.close()
