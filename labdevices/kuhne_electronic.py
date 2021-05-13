"""
Module to control the MKU LO 8-13 PLL Oscillator from Kuhne-Electronics.
Connection is done via a USB-serial cable.
Set to 7.02GHz, the main output yields the second harmonic at 14.04GHz.

An example of how to run the code is found at the end of this file.

File name: kuhne_electronic.py
Author: Julian Krauth
Date created: 2019/05/22
Python Version: 3.7

"""
from time import sleep
import pyvisa

from ._mock.kuhne_electronic import PyvisaDummy

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
        """
        Argument:
            address -- the VISA address of the device.
        """
        self.address = address
        self._device = None

    def initialize(self):
        """ Connect to the device. """
        self._device = pyvisa.ResourceManager('@py').open_resource(
            self.address, **DEFAULTS
        )
        print(f'Connected to: {self.idn}')

    def close(self):
        """ Close connection to device. """
        if self._device is None:
            return
        self._device.before_close()
        self._device.close()

    def write(self, command: str):
        """ Send a command to the device. """
        # If the command is send successfully "A" is returned.
        _ = self._device.query(command)

    def query(self, command: str) -> str:
        """ Query the device. """
        return self._device.query(command)

    @property
    def idn(self) -> str:
        """ Returns a string with the model name.

        This is not implemented in the device. The string is hardcoded
        into this module.
        """
        model_string = "MKU LO 8-13 PLL Oscillator"
        return model_string

    def get_status(self) -> str:
        """ Request the status of the oscillator module """
        return self.query('sa')

    def set_giga_hz(self, value: int) -> None:
        """ Set the 3 gigahertz digits of the frequency of the oscillator.
        value -- range from 0 to 999 """
        self.write('%03dGF1' % value)

    def set_mega_hz(self, value: int) -> None:
        """ Set the 3 megahertz digits of the frequency of the oscillator.
        value -- range from 0 to 999 """
        self.write('%03dMF1' % value)

    def set_kilo_hz(self, value: int) -> None:
        """ Set the 3 kilohertz digits of the frequency of the oscillator.
        value -- range from 0 to 999 """
        self.write('%03dkF1' % value)

    def set_hz(self, value: int) -> None:
        """ Set the hertz digits of the frequency of the oscillator.
        value -- range from 0 to 999 """
        self.write('%03dHF1' % value)

    def set_frequency(self, value: float) -> None:
        """Set frequency of oscillator in units of GHz. Precicion can be down to Hz level. """
        ghz = int(value)
        mhz = int( (value*1e3) % 1e3)
        khz = int( (value*1e6) % 1e3)
        hertz = int( (value*1e9) % 1e3)
        self.set_giga_hz(ghz)
        sleep(0.01)
        self.set_mega_hz(mhz)
        sleep(0.01)
        self.set_kilo_hz(khz)
        sleep(0.01)
        self.set_hz(hertz)
        print(f'Frequency set to {ghz:02d} GHz, {mhz:03d} MHz, {khz:03d} kHz, and {hertz:03d} Hz.')


class LocalOscillatorDummy(LocalOscillator):
    """ A Mock Local Oscillator class """

    def initialize(self):
        """ Connect to the device. """
        self._device = PyvisaDummy()
        print(f'Connected to: {self.idn}')


if __name__ == "__main__":
    dev = LocalOscillator(get_available_devices()[0])
    dev.initialize()
    dev.set_frequency(7.02)
    dev.close()
