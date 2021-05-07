""" Unittests for the Pfeiffer Vacuum devices """
import unittest

from labdevices import pfeiffer_vacuum

class TPG362Test(unittest.TestCase):
    """ For testing the Pfeiffer Vacuum TPG362 class. """

    def setUp(self) -> None:
        port = '/dev/ttyUSB0'
        self.device = pfeiffer_vacuum.TPG362(port)
        self.device.initialize()

    def tearDown(self) -> None:
        self.device.close()

    def test_idn(self):
        result = self.device.idn
        self.assertIsInstance(result, dict)

    def test_error_status(self):
        result = self.device.get_error_status()
        self.assertIsInstance(result, tuple)

    def test_get_gauge_pressure(self):
        gauge = 1
        result = self.device.get_gauge_pressure(gauge)
        self.assertIsInstance(result, tuple)

    def test_get_pressure_all(self):
        result = self.device.get_pressure_all()
        self.assertIsInstance(result, tuple)

    def test_get_pressure_unit(self):
        result = self.device.get_pressure_unit()
        self.assertIsInstance(result, str)

    def test_pressure_val_gauge1(self):
        result = self.device.pressure_val_gauge1
        self.assertIsInstance(result, float)

    def test_pressure_val_gauge2(self):
        result = self.device.pressure_val_gauge2
        self.assertIsInstance(result, float)

    def test_temperature(self):
        result = self.device.temperature
        self.assertIsInstance(result, int)




class TPG362DummyTest(TPG362Test):
    """ For testing the Pfeiffer Vacuum TPG362 class with a dummy. """

    def setUp(self) -> None:
        port = ''
        self.device = pfeiffer_vacuum.TPG362Dummy(port)
        self.device.initialize()

if __name__ == "__main__":
    unittest.main()
