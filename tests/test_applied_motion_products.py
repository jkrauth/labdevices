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

    def test_get_future_movement_value(self):
        result = self.device._get_future_movement_value()
        self.assertIsInstance(result, float)

    def test_get_alarm(self):
        result = self.device.get_alarm()
        self.assertIsInstance(result, list)

    def test_get_status(self):
        result = self.device.get_status()
        self.assertIsInstance(result, list)

    def test_is_moving(self):
        result = self.device.is_moving
        self.assertIsInstance(result, bool)

    def test_microstep(self):
        result = self.device.microstep
        self.assertIsInstance(result, int)

    def test_max_current(self):
        result = self.device.max_current
        self.assertIsInstance(result, float)

    def test_idle_current(self):
        result = self.device.idle_current
        self.assertIsInstance(result, float)

    def test_change_current(self):
        result = self.device.change_current
        self.assertIsInstance(result, float)

    def test_get_position(self):
        result = self.device.get_position()
        self.assertIsInstance(result, float)

    def test_get_immediate_step(self):
        result = self.device.get_immediate_step()
        self.assertIsInstance(result, int)

    def test_acceleration(self):
        result = self.device.acceleration
        self.assertIsInstance(result, float)

    def test_deceleration(self):
        result = self.device.deceleration
        self.assertIsInstance(result, float)

    def test_speed(self):
        result = self.device.speed
        self.assertIsInstance(result, float)


class STF03DDummyTest(STF03DTest):
    """ For testing the Applied Motion Products STF03D class with a dummy. """
    def setUp(self) -> None:
        addr = '0.0.0.0'
        self.device = applied_motion_products.STF03DDummy(addr)
        # Value for calibration using degrees and the gear ratio of the worm wheel
        cal_value = 360/96
        self.device.set_calibration(cal_value)
        self.device.initialize()
