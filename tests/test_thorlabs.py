""" Unittests for the Thorlabs devices """
import unittest

from labdevices import thorlabs


class TSP01Test(unittest.TestCase):
    """ For testing the Thorlabs TSP01 class. """

    def setUp(self) -> None:
        addr = 'USB0::4883::33016::M00416749::0::INSTR'
        self.device = thorlabs.TSP01(addr)
        self.device.initialize()

    def tearDown(self) -> None:
        self.device.close()

    def test_idn(self):
        result = self.device.idn
        self.assertIsInstance(result, str)

    def test_temperature_usb(self):
        result = self.device.temperature_usb()
        self.assertIsInstance(result, float)

    def test_humidity_usb(self):
        result = self.device.humidity_usb()
        self.assertIsInstance(result, float)

    def test_temperature_probe1(self):
        result = self.device.temperature_probe1()
        self.assertIsInstance(result, float)

    def test_temperature_probe2(self):
        result = self.device.temperature_probe2()
        self.assertIsInstance(result, float)

class TSP01DummyTest(TSP01Test):
    """ For testing the Thorlabs TSP01 class with a dummy. """
    def setUp(self) -> None:
        addr = '/dev/ttyUSB0'
        self.device = thorlabs.TSP01Dummy(addr)
        self.device.initialize()
