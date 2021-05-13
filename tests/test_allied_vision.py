""" Unittests for the Allied Vision devices """
import unittest
import numpy as np

from labdevices import allied_vision


class MantaTest(unittest.TestCase):
    """ For testing the Allied Vision Manta class. """

    def setUp(self) -> None:
        addr = 'DEV_000F314E6DE1'
        self.device = allied_vision.Manta(addr)
        self.device.initialize()

    def tearDown(self) -> None:
        self.device.close()

    def test_model_name(self):
        result = self.device.model_name
        self.assertIsInstance(result, str)

    def test_packet_size(self):
        result = self.device.packet_size
        self.assertIsInstance(result, int)

    def test_exposure(self):
        result = self.device.exposure
        self.assertIsInstance(result, float)

    def test_gain(self):
        result = self.device.gain
        self.assertIsInstance(result, float)

    def test_roi_x(self):
        result = self.device.roi_x
        self.assertIsInstance(result, int)

    def test_roi_y(self):
        result = self.device.roi_y
        self.assertIsInstance(result, int)

    def test_roi_dx(self):
        result = self.device.roi_dx
        self.assertIsInstance(result, int)

    def test_roi_dy(self):
        result = self.device.roi_dy
        self.assertIsInstance(result, int)

    def test_sensor_size(self):
        result = self.device.sensor_size
        self.assertIsInstance(result[0], int)
        self.assertIsInstance(result[1], int)

    def test_acquisition_mode(self):
        result = self.device.acquisition_mode
        self.assertIsInstance(result, str)

    def test_take_single_image(self):
        result = self.device.take_single_img()
        self.assertIsInstance(result, np.ndarray)

    def test_trig_mode(self):
        result = self.device.trig_mode
        self.assertIsInstance(result, int)

    def test_trig_source(self):
        result = self.device.trig_source
        self.assertIsInstance(result, str)

    def test_pix_format(self):
        result = self.device.pix_format
        self.assertIsInstance(result, str)


class MantaDummyTest(MantaTest):
    """ For testing the Allied Vision Manta class with a dummy. """
    def setUp(self) -> None:
        addr = 'DEV_000F314E6DE1'
        self.device = allied_vision.MantaDummy(addr)
        self.device.initialize()
