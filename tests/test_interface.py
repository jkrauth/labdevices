"""
Test whether all devices contain the minimum required test methods
"""
from typing import Any
import unittest

from labdevices import keysight, kuhne_electronic, newport

class DeviceMeta(type):
    """ A device meta class """

    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        return cls.__subclasscheck__(type(instance))

    @classmethod
    def __subclasscheck__(cls, subclass: type) -> bool:
        return (
            # hasattr(subclass, '_device') and
            hasattr(subclass, 'initialize') and
            callable(subclass.initialize) and
            hasattr(subclass, 'close') and
            callable(subclass.close) and
            hasattr(subclass, 'write') and
            callable(subclass.write) and
            hasattr(subclass, 'query') and
            callable(subclass.query) and
            hasattr(subclass, 'idn')
        )


class Device(metaclass=DeviceMeta):
    """ Device interface built from DeviceMeta metaclass. """


class KeysightInterfaceTest(unittest.TestCase):
    """ For testing the interface of Keysight devices. """
    def setUp(self):
        addr = "1.1.1.1"
        self.oscilloscope = keysight.Oscilloscope(addr)
        self.counter = keysight.Counter(addr)

    def test_oscilloscope_interface(self):
        # self.assertTrue(issubclass(keysight.Oscilloscope, Device))
        self.assertIsInstance(self.oscilloscope, Device)
        self.assertTrue(hasattr(self.oscilloscope, '_device'))

    def test_counter_interface(self):
        self.assertIsInstance(self.counter, Device)

class KuhneElectronicInterfaceTest(unittest.TestCase):
    """ For testing the interface of Kuhne Electronic devices. """
    def setUp(self) -> None:
        self.local_oscillator = kuhne_electronic.LocalOscillator('')

    def test_local_oscillator_interface(self):
        self.assertIsInstance(self.local_oscillator, Device)
        self.assertTrue(hasattr(self.local_oscillator, '_device'))

class NewportInterfaceTest(unittest.TestCase):
    """ For testing the interface of Newport devices. """
    def setUp(self):
        self.smc100 = newport.SMC100('')

    def test_smc100_interface(self):
        self.assertIsInstance(self.smc100, Device)
        self.assertTrue(hasattr(self.smc100, '_device'))

if __name__ == "__main__":
    unittest.main()
