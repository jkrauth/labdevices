"""
Driver module for CCD/CMOS cameras from Allied Vision.
It uses the python wrapper modul 'pymba' available on Github:
https://github.com/morefigs/pymba
Tested with version 0.3.6

The C/C++ libraries are provided by Allied Vision under the
name 'Vimba'.
Tested with version: Vimba 3.0

The camera's default settings are
IP Config Mode: Auto IP config mode
Gateway: 192.168.2.254
IP: 192.168.2.21
Subnet Mask: 255.255.255.0
The IP of the camera can be set by the user (persistent mode).

File name: allied_vision.py
Author: Julian Krauth
Date created: 2019/11/14
Python Version: 3.7
"""
from typing import Tuple
import numpy as np
import pymba

from ._mock.allied_vision import VimbaDummy

def get_available_cameras() -> list:
    """ Find and show the cameras connected to the network. """
    vimba = pymba.Vimba()
    vimba.startup()
    devices = vimba.camera_ids()
    return devices

class Manta:
    """
    Driver class for the GigE Allied Vision Manta Cameras.
    """
    def __init__(self, device_id: str):
        """
        Arguments:
        camera_id -- str, usually in a format like 'DEV_000F314E1E59'
        """
        # Start the camera package
        self.vimba = pymba.Vimba()

        # Find correct camera index
        self.device_id = device_id

        # This will become the camera.
        self._device = None

    def initialize(self) -> None:
        """Establish connection to camera"""

        self.vimba.startup()
        devices = self.vimba.camera_ids()
        for index, identity in enumerate(devices):
            if self.device_id == identity:
                device_index = index
                self._device = self.vimba.camera(device_index)
                self._device.open()
                print(f"Connected to camera : {self.idn}")
                return
        print('Camera not found.')
        self.vimba.shutdown()

    def close(self):
        """Close connection to camera"""
        if self._device is not None:
            self._device.close()
            self.vimba.shutdown()
            self._device = None

    @property
    def idn(self) -> str:
        """ Return the device ID """
        return self.device_id

    @property
    def model_name(self) -> str:
        """ Return the model name of the device """
        name = self._device.DeviceModelName
        return name

    @property
    def packet_size(self) -> int:
        """ Return the packet size for Ethernet communication """
        return self._device.GVSPPacketSize

    @packet_size.setter
    def packet_size(self, value:int):
        self._device.GVSPPacketSize=value

    @property
    def exposure(self) -> float:
        """
        Returns:
        exposure -- float, in seconds
        """
        expos = float(self._device.ExposureTimeAbs)
        return expos*1e-6

    @exposure.setter
    def exposure(self, expos: float):
        """Sets exposure time of the camera
        Argument:
        exposure -- int, in seconds
        """
        # Convert to microseconds and set value
        self._device.ExposureTimeAbs = int(expos*1e6)

    @property
    def gain(self) -> float:
        """ Return the gain of the camera.
        The possible range of gain values is camera dependent. """
        # Best image quality is achieved with gain = 0
        gain = self._device.Gain
        return gain

    @gain.setter
    def gain(self, gain: float):
        self._device.Gain = gain

    @property
    def roi_x(self) -> int:
        """ The starting position of the region of interest on the x axis """
        return self._device.OffsetX

    @roi_x.setter
    def roi_x(self, val: int):
        self._device.OffsetX = val

    @property
    def roi_y(self) -> int:
        """ The starting position of the region of interest on the y axis """
        return self._device.OffsetY

    @roi_y.setter
    def roi_y(self, val: int):
        self._device.OffsetY = val

    @property
    def roi_dx(self) -> int:
        """ The width of the region of interest on the x axis """
        return self._device.Width

    @roi_dx.setter
    def roi_dx(self, val: int):
        self._device.Width = val

    @property
    def roi_dy(self) -> int:
        """ The width of the region of interest on the y axis """
        return self._device.Height

    @roi_dy.setter
    def roi_dy(self, val: int):
        self._device.Height = val

    @property
    def sensor_size(self) -> Tuple[int, int]:
        """Returns number of pixels in width and height of the sensor"""
        width = self._device.SensorWidth
        height = self._device.SensorHeight
        return width, height

    @property
    def acquisition_mode(self) -> str:
        """ Typically 'Continuous' or 'SingleFrame' """
        return self._device.AcquisitionMode

    @acquisition_mode.setter
    def acquisition_mode(self, mode: str):
        options = {'SingleFrame', 'Continuous'}
        if mode in options:
            self._device.arm(mode)
        else:
            raise Exception(f"Value '{mode}' for acquisition mode is not valied")

    def take_single_img(self) -> np.ndarray:
        """
        Sets everything to create a single image, takes the image
        and returns it.
        The argument adapts the method for the pixel format set in
        the camera. See pixFormat method.
        """
        self._device.arm('SingleFrame')
        frame = self._device.acquire_frame()
        image = frame.buffer_data_numpy().copy()
        self._device.disarm()
        return image

    @property
    def trig_mode(self) -> int:
        """Toggle Trigger Mode set by 1/0, respectively.
        Returns:
            int -- 0 or 1, depending on trigger mode off or on
        """
        onoff = {'Off': 0, 'On': 1}
        mode = self._device.TriggerMode
        return onoff[mode]

    @trig_mode.setter
    def trig_mode(self, mode: int):
        """Toggle Trigger Mode set by 1/0, respectively.
        Keyword Arguments:
            mode -- possible values: 0, 1
        """
        onoff = ['Off', 'On']
        self._device.TriggerMode = onoff[mode]

    @property
    def trig_source(self) -> str:
        """Get/Select trigger source keyword arguments:
        Returns:
            str -- trigger source
        """
        return self._device.TriggerSource

    @trig_source.setter
    def trig_source(self, source: str):
        """Get/Select trigger source keyword arguments:
            source {str} -- Source can be one of the following strings:
                            'Freerun', 'Line1', 'Line2', 'FixedRate', 'Software'
        """
        self._device.TriggerSource = source

    @property
    def pix_format(self) -> str:
        """Get/Select pixel format
        Returns:
            str -- Pixelformat
        """
        return self._device.PixelFormat

    @pix_format.setter
    def pix_format(self, pix: str):
        """Get/Select pixel format
        Keyword Arguments:
            pix {str} -- possible values: 'Mono8','Mono12','Mono12Packed'
                         (default: {None})
        """
        self._device.PixelFormat = pix


class MantaDummy(Manta):
    """Manta class for testing. It doesn't need any device connected."""
    def __init__(self, device_id: str):
        """ Replace the real pymba package with a Mock version. """
        super().__init__(device_id)
        self.vimba = VimbaDummy()
