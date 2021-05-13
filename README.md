# labdevices

[![Continuous integration](https://img.shields.io/travis/jkrauth/labdevices)](https://travis-ci.org/github/jkrauth/labdevices) [![MIT licensed](https://img.shields.io/github/license/jkrauth/labdevices)](https://github.com/jkrauth/labdevices/blob/main/LICENSE.md) [![MIT licensed](https://img.shields.io/pypi/v/labdevices)](https://pypi.org/project/labdevices/)

SDK for devices used in our atomic physics research lab. Since there is probably more of those devices used in other labs as well, this package might be of a more general use.

## Included devices

The given links guide you to the programmer manuals of the included devices.

| Company                   | Model                                                        |
| ------------------------- | ------------------------------------------------------------ |
| ANDO                      | [AQ-6315A/B](https://cdn.tmi.yokogawa.com/ASS-62408E-01Y_010.pd.pdf) spectrum analyzer |
| Allied Vision             | [GigE](https://cdn.alliedvision.com/fileadmin/content/documents/products/cameras/various/features/Camera_and_Driver_Attributes.pdf) cameras |
| Applied Motion Products   | [STF03D](https://appliedmotion.s3.amazonaws.com/Host-Command-Reference_920-0002V.pdf) stepper motor controller |
| Keysight                  | [3000T X-Series](http://literature.cdn.keysight.com/litweb/pdf/75037-97025.pdf) oscilloscope |
|                           | [53220A/53230A](53220A/53230A ) counter                      |
| Kuhne Electronic          | [MKU LO 8-13 PLL](https://shop.kuhne-electronic.com/kuhne/en/shop/amateur-radio/signal-sources/oscillators/MKU+LO+813+PLL++Oscillator/?card=1714#_tab_content6) local oscillator  |
| Newport                   | [SMC100](https://www.newport.com/medias/sys_master/images/images/h8d/h3a/8797263101982/SMC100CC-SMC100PP-User-Manual.pdf) positioner controller |
| Pfeiffer Vacuum           | [TPG362](https://www.ajvs.com/library/Pfeiffer_Vacuum_TPG_361_TPG_362_Manual.pdf) vacuum gauge |
| Rohde & Schwarz           | [FPC1000](https://scdn.rohde-schwarz.com/ur/pws/dl_downloads/pdm/cl_manuals/user_manual/1178_4130_01/FPC_UserManual_en_09.pdf) spectrum analyzer |
|                           | [RTB2000](https://scdn.rohde-schwarz.com/ur/pws/dl_downloads/pdm/cl_manuals/user_manual/1333_1611_01/RTB_UserManual_en_10.pdf) oscilloscope |
| Stanford Research Systems | [DG645](https://www.thinksrs.com/downloads/pdfs/manuals/DG645m.pdf) delay generator |
| Thorlabs                  | [TSP01](https://www.thorlabs.com/drawings/d3a8b683b1da6c0e-C643E761-F31E-E669-C6BC10DCC87ABBE3/TSP01-Manual.pdf) temperature sensor |

## Third party dependencies

Most dependencies are installed automatically. For some devices, however, there are exceptions that need to be installed manually:

- ANDO spectrometer: [prologix-gpib-ethernet](https://github.com/nelsond/prologix-gpib-ethernet)
- Allied Vision GigE cameras: [Vimba SDK](https://www.alliedvision.com/en/products/software.html#agb-modal-content-5496)

## Installation

It is recommended to install the package into a virtual environment.

### A) For general use

```console
pip install labdevices
```

### B) For development

Clone the repository and from inside the package folder run

```console
pip install -e .
```

 Changes in the code will then be reflected when reimporting the labdevices package. No new installation necessary.

There is also a Jupyter Notebook provided that contains some use examples and is handy for development.

## Usage

Once the labdevices package is installed, simply do e.g.

```python
from labdevices.thorlabs import TSP01
```

or similar corresponding commands. For each device there should be a dummy device available in order to test software, when there is actually no device connected. For the switching to a dummy device simply import

```python
from labdevices.thorlabs import TSP01Dummy
```

with *Dummy* added to the device's class name. All methods of these mock devices return the same type as their real equivalents. They also accept functions that change their internal parameters. However, their functionality is for now limited, i.e. functions that get a certain parameter will always return the same value, even if the parameter was set to a different value.

## Testing

There is two kinds of tests implemented:

### Interface tests

Run by 

```console
python -m unittest test.test_interface
```

This checks that all devices have the basic methods implemented that a device needs, like e.g. `initialize()`, `query()`, or `close()`

### Unit tests

Run by e.g.

```console
python -m unittest test.test_keysight.CounterTest
python -m unittest test.test_keysight.CounterDummyTest
```

As shown here, these tests should exist for each device and its dummy version. For CI only the tests of the dummy devices are run (see `.travis.yml`). The test with the actual device can only be performed with the respective device attached.

The idea of those tests is to check that all the methods work, that the return format is correct, and that the dummy devices support calling all available methods and properties.

In the future one might want to improve the tests by e.g. changing a parameter and checking whether that parameter was actually changed. But this is currently not supported by the dummy devices.

In order to run a test across all the dummy classes use:

```console
python -m unittest test -k DummyTest
```

## Troubleshooting

### Ubuntu

If you want to read a VISA address with the pyvisa package and you get a message of the following type

> Found a device whose serial number cannot be read. The partial VISA resource name is: USB0::2733::443::???::2::INSTR

the issue is related to the permissions regarding the [udev rules](https://www.thegeekdiary.com/beginners-guide-to-udev-in-linux/). If you don't have permission to write on USB devices you will not be able to communicate properly with the device. To solve this problem  (see also [here](http://manpages.ubuntu.com/manpages/bionic/man3/Device::USB::FAQ.3pm.html)) you have to create a group with the name *usb* by

```console
addgroup --system usb
```

Next, add your user to that group by

```console
sudo adduser <user> usb
```

where `<user>` is your Ubuntu user name, which is also shown in the terminal at the beginning of each line.

Create a file in `/etc/udev/rules.d/` with the name `50-myusb.rules` (if it does not exist yet) and add the following line

```console
SUBSYSTEM=="usb", MODE="0666", GROUP="usb"
```

After restarting the PC check that you are part of the usb group by typing `groups` into the terminal.

The communication with the usb device should now work.

### Ethernet devices

If an Ethernet device is not recognized, check its settings. Usually a fixed (not dynamic) IP address can be given. That address has to be part of the local subnet.

## Contact

- Repo owner:  Julian Krauth, j.krauth@vu.nl
- Institution: Vrije Universiteit Amsterdam, Faculty of Sciences, The Netherlands
