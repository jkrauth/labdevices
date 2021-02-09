"""
Defines the base class for the devices as well as a mock interface class.

File name:      allied_vision.py
Author:         Julian Krauth
Created:        2019/11/14
Python Version: 3.7
"""

class _Device:
    """Device base class"""
    def __init__(self, dev_address: str):
        self.address = dev_address
        self._dev = None


    def initialize(self):
        """Connect to device"""
        self._dev = _MockInterface()
        self._dev.connect()

    def close(self):
        """Close connection to device"""
        if self._dev is not None:
            self._dev.close()
            print(f'{self._dev.name} closed.')
            return
        print(f'{self._dev.name} already closed.')




class _MockInterface:
    """Mimics a device interface. This is useful for testing, when no devices are connected."""
    def __init__(self):
        self._name = "DummyDevice"

    def connect(self):
        print(f'Connected to {self._name}!')

    def close(self):
        print(f'Connection to {self._name} closed!')

    def get_name(self):
        return self._name

    def get_integer(self) -> int:
        return 123

    def get_float(self) -> float:
        return 1.23

    def get_string(self) -> str:
        return "123"