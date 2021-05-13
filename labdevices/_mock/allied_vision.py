""" Provides a mock for the pymba package used for Allied Vision devices. """
from unittest.mock import Mock
from typing import List
import pathlib
import pickle

import numpy as np

DATA_DIR = pathlib.Path(__file__).parent / 'data'

CAMERA_ATTRIBUTES = {
    'DeviceModelName': 'Manta G-235B',
    'GVSPPacketSize': 1500,
    'ExposureTimeAbs': 14999.0,
    'Gain': 0.0,
    'OffsetX': 0,
    'OffsetY': 0,
    'Width': 1936,
    'Height': 1216,
    'SensorWidth': 1936,
    'SensorHeight': 1216,
    'AcquisitionMode': 'Continuous',
    'TriggerMode': 'On',
    'TriggerSource': 'Freerun',
    'PixelFormat': 'Mono8',
}



class VimbaDummy(Mock):
    """ Mock class for the pymba package when using the
    Allied Vision devices as dummy. """

    @staticmethod
    def camera_ids() -> List[str]:
        """ Return available camera identities """
        return ['camera1', 'camera2', 'DEV_000F314E6DE1']

    @staticmethod
    def camera(idn: str):
        """ Return the mock camera object """
        return CameraDummy(idn)


class CameraDummy(Mock):
    """ Mock class for the Allied Vision camera """

    def __init__(self, device_index):
        """ Create the attributes for the camera with their values. """
        _ = device_index
        super().__init__()

        for item, val in CAMERA_ATTRIBUTES.items():
            setattr(self, item, val)

    @staticmethod
    def acquire_frame():
        """ Returns a frame dummy object. """
        return FrameDummy()

    def open(self):
        pass

    def close(self):
        pass

    def arm(self, _):
        pass

    def disarm(self):
        pass


class FrameDummy:
    """ Mock class for frame object of Manta camera """

    @staticmethod
    def buffer_data_numpy() -> np.ndarray:
        """ Returns a Manta frame """
        file_dir = DATA_DIR / 'allied_vision_frame.pickle'
        with open(file_dir, "rb") as f:
            return pickle.load(f)
