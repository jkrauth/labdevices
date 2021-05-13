"""
Test whether all devices contain the minimum required test methods
"""
from typing import Any
import unittest

from labdevices import (
    # allied_vision, # needs Vimba installed, that doesn't work with CI
    ando,
    applied_motion_products,
    keysight,
    kuhne_electronic,
    newport,
    rohde_schwarz,
    pfeiffer_vacuum,
    stanford_research_systems,
    thorlabs,
    )

class DeviceMeta(type):
    """ A device meta class """

    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        return cls.__subclasscheck__(type(instance))

    @classmethod
    def __subclasscheck__(cls, subclass: type) -> bool:
        return (
            # hasattr(subclass, '_device') and
            hasattr(subclass, 'initialize') and
            callable(subclass.initialize) and
            hasattr(subclass, 'close') and
            callable(subclass.close) and
            hasattr(subclass, 'write') and
            callable(subclass.write) and
            hasattr(subclass, 'query') and
            callable(subclass.query) and
            hasattr(subclass, 'idn')
        )


class Device(metaclass=DeviceMeta):
    """ Device interface built from DeviceMeta metaclass. """


# @unittest.skip("Skip not message-based driver")
# class AlliedVisionInterfaceTest(unittest.TestCase):
#     """ For testing the interface of Allied Vision devices. """
#     def setUp(self):
#         self.manta = allied_vision.Manta('')

#     def test_manta_interface(self):
#         self.assertIsInstance(self.manta, Device)
        # self.assertTrue(hasattr(self.manta, '_device'))

class AndoInterfaceTest(unittest.TestCase):
    """ For testing the interface of Ando devices. """
    def setUp(self):
        self.device = ando.SpectrumAnalyzer('')

    def test_spectrum_analyzer_interface(self):
        self.assertIsInstance(self.device, Device)
        self.assertTrue(hasattr(self.device, '_device'))

class AppliedMotionProductsInterfaceTest(unittest.TestCase):
    """ For testing the interface of Applied Motion Products devices. """
    def setUp(self):
        self.driver = applied_motion_products.STF03D('')

    def test_stf03_interface(self):
        self.assertIsInstance(self.driver, Device)
        self.assertTrue(hasattr(self.driver, '_device'))

class KeysightInterfaceTest(unittest.TestCase):
    """ For testing the interface of Keysight devices. """
    def setUp(self):
        addr = "1.1.1.1"
        self.oscilloscope = keysight.Oscilloscope(addr)
        self.counter = keysight.Counter(addr)

    def test_oscilloscope_interface(self):
        # self.assertTrue(issubclass(keysight.Oscilloscope, Device))
        self.assertIsInstance(self.oscilloscope, Device)
        self.assertTrue(hasattr(self.oscilloscope, '_device'))

    def test_counter_interface(self):
        self.assertIsInstance(self.counter, Device)
        self.assertTrue(hasattr(self.counter, '_device'))

class KuhneElectronicInterfaceTest(unittest.TestCase):
    """ For testing the interface of Kuhne Electronic devices. """
    def setUp(self) -> None:
        self.local_oscillator = kuhne_electronic.LocalOscillator('')

    def test_local_oscillator_interface(self):
        self.assertIsInstance(self.local_oscillator, Device)
        self.assertTrue(hasattr(self.local_oscillator, '_device'))

class NewportInterfaceTest(unittest.TestCase):
    """ For testing the interface of Newport devices. """
    def setUp(self):
        self.smc100 = newport.SMC100('')

    def test_smc100_interface(self):
        self.assertIsInstance(self.smc100, Device)
        self.assertTrue(hasattr(self.smc100, '_device'))

class PfeifferVacuumInterfaceTest(unittest.TestCase):
    """ For testing the interface of Pfeiffer Vacuum devices. """
    def setUp(self):
        self.gauge = pfeiffer_vacuum.TPG362('')

    def test_tpg362_interface(self):
        self.assertIsInstance(self.gauge, Device)
        self.assertTrue(hasattr(self.gauge, '_device'))

class RohdeSchwarzInterfaceTest(unittest.TestCase):
    """ For testing the interface of Rohde & Schwarz devices. """
    def setUp(self):
        addr = "1.1.1.1"
        self.oscilloscope = rohde_schwarz.Oscilloscope(addr)
        self.fpc100 = rohde_schwarz.FPC1000(addr)

    def test_oscilloscope_interface(self):
        self.assertIsInstance(self.oscilloscope, Device)
        self.assertTrue(hasattr(self.oscilloscope, '_device'))

    def test_fpc100_interface(self):
        self.assertIsInstance(self.fpc100, Device)
        self.assertTrue(hasattr(self.fpc100, '_device'))

class StanfordResearchSystemsInterfaceTest(unittest.TestCase):
    """ For testing the interface of Stanford Research Systems devices. """
    def setUp(self):
        self.device = stanford_research_systems.DG645('', 1)

    def test_dg645_interface(self):
        self.assertIsInstance(self.device, Device)
        self.assertTrue(hasattr(self.device, '_device'))

class ThorlabsInterfaceTest(unittest.TestCase):
    """ For testing the interface of Thorlabs devices. """
    def setUp(self):
        self.sensor = thorlabs.TSP01('')

    def test_tsp01_interface(self):
        self.assertIsInstance(self.sensor, Device)
        self.assertTrue(hasattr(self.sensor, '_device'))


if __name__ == "__main__":
    unittest.main()
