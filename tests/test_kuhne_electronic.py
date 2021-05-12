""" Unittests for the Kuhne Electronic devices """
import unittest

from labdevices import kuhne_electronic


class LocalOscillatorTest(unittest.TestCase):
    """ For testing the Kuhne Electronic Local Oscillator class. """

    def setUp(self) -> None:
        addr = '/dev/ttyUSB0'
        self.device = kuhne_electronic.LocalOscillator(addr)
        self.device.initialize()

    def tearDown(self) -> None:
        self.device.close()

    def test_idn(self):
        result = self.device.idn
        self.assertIsInstance(result, str)


class LocalOscillatorDummyTest(LocalOscillatorTest):
    """ For testing the Kuhne Electronic Local Oscillator class with a dummy. """

    def setUp(self) -> None:
        addr = '/dev/ttyUSB0'
        self.device = kuhne_electronic.LocalOscillatorDummy(addr)
        self.device.initialize()
