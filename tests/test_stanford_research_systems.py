""" Unittests for the Stanford Research Systems devices """
import unittest

from labdevices import stanford_research_systems

class DG645Test(unittest.TestCase):
    """ For testing the Stanford Research Systems DG class. """

    def setUp(self) -> None:
        addr = '10.0.0.34'
        port = 5025
        self.device = stanford_research_systems.DG645(addr, port)
        self.device.initialize()

    def tearDown(self) -> None:
        self.device.close()

    def test_get_delay(self):
        channel = 2
        result = self.device.get_delay(channel)
        self.assertIsInstance(result[0], int)
        self.assertIsInstance(result[1], float)

    def test_get_output_level(self):
        channel = 2
        result = self.device.get_output_level(channel)
        self.assertIsInstance(result, float)

class DG645DummyTest(DG645Test):
    """ For testing the Stanford Research Systems DG class with a dummy. """

    def setUp(self) -> None:
        addr = '1.1.1.1'
        port = 0
        self.device = stanford_research_systems.DG645Dummy(addr, port)
        self.device.initialize()

if __name__ == "__main__":
    unittest.main()
