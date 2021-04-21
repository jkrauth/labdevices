"""
Test whether all devices contain the minimum required test methods
"""
from typing import Any
import unittest

from labdevices import keysight, kuhne_electronic, newport

class DeviceMeta(type):
    """ A device meta class """
    def __instancecheck__(cls, instance: Any) -> bool:
        return cls.__subclasscheck__(type(instance))

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
    pass

class KeysightTest(unittest.TestCase):

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

class KuhneElectronicTest(unittest.TestCase):

    def setUp(self) -> None:
        self.local_oscillator = kuhne_electronic.LocalOscillator('')

    def test_local_oscillator_interface(self):
        self.assertIsInstance(self.local_oscillator, Device)

class NewportTest(unittest.TestCase):

    def setUp(self):
        self.smc100 = newport.SMC100('')

    def test_smc100_interface(self):
        self.assertIsInstance(self.smc100, Device)

if __name__ == "__main__":
    unittest.main()