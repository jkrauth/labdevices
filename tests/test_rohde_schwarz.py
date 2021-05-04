""" Unittests for the Rohde & Schwarz devices """
import unittest

from labdevices import rohde_schwarz

class FPC1000Test(unittest.TestCase):
    """ For testing the Rohde & Schwarz Spectrum Analyzer class. """

    def setUp(self) -> None:
        #This method has to be overwritten by the subclass.
        addr = '10.0.0.91'
        self.device = rohde_schwarz.FPC1000(addr)
        self.device.initialize()

    def tearDown(self) -> None:
        self.device.close()

    def test_get_trace(self):
        # This test seems to fail with the device, because the first
        # intent to get the trace fails. All further intents work fine.
        result = self.device.get_trace()
        self.assertIsInstance(result, tuple)


class FPC1000DummyTest(FPC1000Test):
    """ For testing the Rohde & Schwarz Spectrum Analyzer class with a dummy. """

    def setUp(self) -> None:
        addr = '1.1.1.1'
        self.device = rohde_schwarz.FPC1000Dummy(addr)
        self.device.initialize()


class OscilloscopeTest(unittest.TestCase):
    """ For testing the Rohde & Schwarz Oscilloscope class. """

    def setUp(self) -> None:
        addr = '10.0.0.81'
        self.channel = 1

        self.device = rohde_schwarz.Oscilloscope(addr)
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
        self.assertIsInstance(result, rohde_schwarz.Preamble)

class OscilloscopeDummyTest(OscilloscopeTest):
    """ For testing the Rohde & Schwarz Oscilloscope class with a dummy. """

    def setUp(self) -> None:
        addr = '1.1.1.1'
        self.channel = 1
        self.device = rohde_schwarz.OscilloscopeDummy(addr)
        self.device.initialize()

if __name__ == "__main__":
    unittest.main()
