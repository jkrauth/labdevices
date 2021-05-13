""" Unittests for ANDO devices """
import unittest
import numpy as np

from labdevices import ando

class SpectrumAnalyzerTest(unittest.TestCase):
    """ For testing the ANDO Spectrum Analyzer class. """

    def setUp(self) -> None:
        addr = '10.0.0.40'
        gpib = 1
        self.device = ando.SpectrumAnalyzer(addr, gpib)
        self.device.initialize()

    def tearDown(self) -> None:
        self.device.close()

    def test_sampling(self):
        result = self.device.sampling
        self.assertIsInstance(result, int)

    def test_get_x_data(self):
        result = self.device.get_x_data()
        self.assertIsInstance(result, np.ndarray)

    def test_get_y_data(self):
        result = self.device.get_y_data()
        self.assertIsInstance(result, np.ndarray)

    def test_get_ana(self):
        result = self.device.get_ana()
        self.assertIsInstance(result, tuple)

    def test_center(self):
        result = self.device.center
        self.assertIsInstance(result, float)

    def test_span(self):
        result = self.device.span
        self.assertIsInstance(result, float)

    def test_get_measurement_mode(self):
        result = self.device.get_measurement_mode()
        self.assertIsInstance(result[0], int)
        self.assertIsInstance(result[1], str)

    def test_get_trigger_mode(self):
        result = self.device.get_trigger_mode()
        self.assertIsInstance(result[0], int)
        self.assertIsInstance(result[1], str)

class SpectrumAnalyzerDummyTest(SpectrumAnalyzerTest):
    """ For testing the ANDO spectrum analyzer class with a dummy. """

    def setUp(self) -> None:
        addr = '1.1.1.1'
        gpib = 0
        self.device = ando.SpectrumAnalyzerDummy(addr, gpib)
        self.device.initialize()

if __name__ == "__main__":
    unittest.main()
