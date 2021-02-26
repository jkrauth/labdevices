[![Continuous integration](https://img.shields.io/travis/jkrauth/labdevices)](https://travis-ci.org/github/jkrauth/labdevices) [![MIT licensed](https://img.shields.io/github/license/jkrauth/labdevices)](https://github.com/jkrauth/labdevices/blob/main/LICENSE.md)

# labdevices

SDK for typical devices found in an atomic physics research lab.

This package is in an early stage. Every contribution to improve and extend it is welcome.

## Included Devices

The given links guide you to the programmer manuals.

| Company                   | Model                                                        |
| ------------------------- | ------------------------------------------------------------ |
| ANDO                      | [AQ-6315A/B](https://cdn.tmi.yokogawa.com/ASS-62408E-01Y_010.pd.pdf) spectrum analyzer |
| Allied Vision             | [GigE](https://cdn.alliedvision.com/fileadmin/content/documents/products/cameras/various/features/Camera_and_Driver_Attributes.pdf) cameras |
| Applied Motion Products   | [STF03D](https://appliedmotion.s3.amazonaws.com/Host-Command-Reference_920-0002V.pdf) stepper motor controller |
| Keysight                  | [3000T X-Series](http://literature.cdn.keysight.com/litweb/pdf/75037-97025.pdf) oscilloscope |
|                           | [53220A/53230A](53220A/53230A ) counter                      |
| Newport                   | [SMC100](https://www.newport.com/medias/sys_master/images/images/h8d/h3a/8797263101982/SMC100CC-SMC100PP-User-Manual.pdf) positioner controller |
| Pfeiffer Vacuum           | [TPG362](https://www.ajvs.com/library/Pfeiffer_Vacuum_TPG_361_TPG_362_Manual.pdf) vacuum gauge |
| Rohde & Schwarz           | [FPC1000](https://scdn.rohde-schwarz.com/ur/pws/dl_downloads/pdm/cl_manuals/user_manual/1178_4130_01/FPC_UserManual_en_09.pdf) spectrum analyzer |
|                           | [RTB2000](https://scdn.rohde-schwarz.com/ur/pws/dl_downloads/pdm/cl_manuals/user_manual/1333_1611_01/RTB_UserManual_en_10.pdf) oscilloscope |
| Stanford Research Systems | [DG645](https://www.thinksrs.com/downloads/pdfs/manuals/DG645m.pdf) delay generator |
| Thorlabs                  | [TSP01](https://www.thorlabs.com/drawings/d3a8b683b1da6c0e-C643E761-F31E-E669-C6BC10DCC87ABBE3/TSP01-Manual.pdf) temperature sensor |

## Installation

Dependencies are installed automatically. The only exception is the [prologix-gpib-ethernet](https://github.com/nelsond/prologix-gpib-ethernet) package that has to be installed manually. It is only needed for the use of the ANDO Spectrum Analyzer.

It is recommended to work in a new virtual environment when installing this package.

Create e.g. a conda virtual environment as

```console
conda create -n <name> python=3.6
```

where `<name>` is your environment name. The python version should be 3.6 or higher. Then activate the environment with

```console
conda activate <name>
```

### A) For development

Clone the repository. From inside the package folder run

```console
pip install -e .
```

 Changes in the code of the labdevices package will automatically be available when loading the package in a restarted python console.

### B) For general use

With the activated conda environment run

```console
pip install https://github.com/jkrauth/labdevices.git
```

If there have been updates in the repo you then can upgrade the installation with:

```console
pip install --upgrade https://github.com/jkrauth/labdevices.git
```

## Usage

Once the labdevices package is installed into a conda environment you can simply do e.g.

```python
from labdevices.thorlabs import TSP01
```

For each device there should be a dummy device available in order to test software, when there is actually no device connected. For the switching to a dummy device simply import

```python
from labdevices.thorlabs import TSP01Dummy
```

with *Dummy* added to the device's class name.

## Contributing

Add new drivers or improve existing ones.

Quick step guideline:

1. Fork the project

2. Create your feature branch

3. Commit changes

4. Push to the branch

5. Open a pull request

Add a new class in a file that carries the name of its company. If any non-standard packages are required, add them to the list in the setup.py file.

New drivers should be tested before the changes are merged into the master branch. Same applies for modifications to already existing modules: Test them before you push.

Please keep in mind to:

- check your code with pylint
- for new modules always add a module header with name, author, date.
- not include paths for saving files, VISA addresses of specific devices, etc., that should be part of your local application.

## Troubleshooting

### Ubuntu

If you want to read a VISA address with the pyvisa package and you get the following message

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

If an Ethernet device is not recognized, check its settings. Usually a fixed IP address can be given, which should be part of the local subnet.

## Contact

- Repo owner:  Julian Krauth, j.krauth@vu.nl
- Institution: Vrije Universiteit Amsterdam, Faculty of Sciences, The Netherlands
