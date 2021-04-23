""" Unittests for the Keysight devices """
import unittest
from time import sleep

from labdevices import keysight


class CounterTest(unittest.TestCase):
    """ For testing the Keysight Counter class. """

    def setUp(self) -> None:

        #This method has to be overwritten by the subclass.
        addr = '10.0.0.120'
        self.device = keysight.Counter(addr)
        self.device.initialize()

    def tearDown(self) -> None:
        self.device.close()

    def test_gate_time(self):
        result = self.device.gate_time
        self.assertIsInstance(result, float)

    def test_trigger_mode(self):
        result = self.device.trigger_mode
        self.assertIsInstance(result, str)

    def test_start_and_read_frequency_measurement(self):
        self.device.gate_time = 0.5
        self.device.start_frequency_measurement()
        sleep(0.6)
        result = self.device.read_frequency_measurement()
        self.assertIsInstance(result, float)

    def test_measure_frequency(self):
        result = self.device.measure_frequency()
        self.assertIsInstance(result, float)


class CounterDummyTest(CounterTest):
    """ For testing the Keysight Counter class with a dummy. """
    def setUp(self) -> None:
        addr = '1.1.1.1'
        self.device = keysight.CounterDummy(addr)
        self.device.initialize()


class OscilloscopeTest(unittest.TestCase):
    """ For testing the Keysight Oscilloscope class. """

    def setUp(self) -> None:
        addr = '10.0.0.84'
        self.channel = 1

        self.device = keysight.Oscilloscope(addr)
        self.device.initialize()

    def tearDown(self) -> None:
        self.device.close()

    def test_get_volt_avg(self):
        result = self.device.get_volt_avg(self.channel)
        self.assertIsInstance(result, float)

    def test_get_volt_max(self):
        result = self.device.get_volt_max(self.channel)
        self.assertIsInstance(result, float)

    def test_get_volt_peakpeak(self):
        result = self.device.get_volt_peakpeak(self.channel)
        self.assertIsInstance(result, float)

    def test_get_screenshot(self):
        result = self.device.get_screenshot()
        self.assertIsInstance(result, bytes)

    def test_get_trace(self):
        result = self.device.get_trace(self.channel)
        self.assertIsInstance(result, tuple)

    def test_get_preamble(self):
        result = self.device.get_preamble(self.channel)
        self.assertIsInstance(result, keysight.Preamble)

class OscilloscopeDummyTest(OscilloscopeTest):
    """ For testing the Keysight Oscilloscope class with a dummy. """

    def setUp(self) -> None:
        addr = '1.1.1.1'
        self.channel = 1
        self.device = keysight.OscilloscopeDummy(addr)
        self.device.initialize()

if __name__ == "__main__":
    unittest.main()
