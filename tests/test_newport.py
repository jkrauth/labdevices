""" Unittests for the Newport devices """
import unittest

from labdevices import newport


class SMC100Test(unittest.TestCase):
    """ For testing the Newport SMC100 class. """

    def setUp(self) -> None:
        addr = '/dev/ttyUSB0'
        device_index = 1
        self.device = newport.SMC100(addr, device_index)
        self.device.initialize()

    def tearDown(self) -> None:
        self.device.close()

    def test_idn(self):
        result = self.device.idn
        self.assertIsInstance(result, str)

    def test_is_moving(self):
        result = self.device.is_moving
        self.assertIsInstance(result, bool)

    def test_error_and_controller_status(self):
        result = self.device.error_and_controller_status()
        self.assertIsInstance(result[0], str)
        self.assertIsInstance(result[1], str)

    def test_get_last_command_error(self):
        result = self.device.get_last_command_error()
        self.assertIsInstance(result, str)

    def test_position(self):
        result = self.device.position
        self.assertIsInstance(result, float)

    def test_speed(self):
        result = self.device.speed
        self.assertIsInstance(result, float)

    def test_acceleration(self):
        result = self.device.acceleration
        self.assertIsInstance(result, float)

class SMC100DummyTest(SMC100Test):
    """ For testing the Newport SMC100 class with a dummy. """
    def setUp(self) -> None:
        addr = '/dev/ttyUSB0'
        self.device = newport.SMC100Dummy(addr)
        self.device.initialize()
