""" Unittests for the Applied Motion Products devices """
import unittest

from labdevices import applied_motion_products


class STF03DTest(unittest.TestCase):
    """ For testing the Applied Motion Products STF03D class. """

    def setUp(self) -> None:
        addr = '10.0.0.103'
        self.device = applied_motion_products.STF03D(addr)
        # Value for calibration using degrees and the gear ratio of the worm wheel
        cal_value = 360/96
        self.device.set_calibration(cal_value)
        self.device.initialize()

    def tearDown(self) -> None:
        self.device.close()

    def test_idn(self):
        result = self.device.idn
        self.assertIsInstance(result, str)


class STF03DDummyTest(STF03DTest):
    """ For testing the Applied Motion Products STF03D class with a dummy. """
    def setUp(self) -> None:
        addr = '0.0.0.0'
        self.device = applied_motion_products.STF03DDummy(addr)
        self.device.initialize()
