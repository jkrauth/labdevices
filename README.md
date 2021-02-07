# labdevices

This python package provides simple software drivers for the easy use of typical devices found in atomic physics research labs.

## Included Devices are from

- **Allied Vision**: Manta
- **Applied Motion Products**: STF03D
- **ANDO**: SpectrumAnalyzer
- **Keysight**: ?
- **Newport**: SMC100
- **Pfeiffer Vacuum**: TPG362
- **Rohde & Schwarz**: FPC1000, ?
- **Stanford Research Systems**: DG645
- **Thorlabs**: TSP01

## Installation

It is recommended to work in a new virtual environment when installing this package.

Create a conda environment as

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
python setup.py develop
```

 Changes in the code of the labdevices package will automatically be available when loading the package in a restarted python console.

### B) For general use

With the activated conda environment run

```console
pip install git+https://gitlab.com/vu_rcs/lab_devices.git
```

If there have been updates in the repo you then have to upgrade the installation with:

```console
pip install --upgrade git+https://gitlab.com/vu_rcs/lab_devices.git
```

## Usage

Once the labdevices package is installed into a conda environment you can simply do e.g.

```python
from labdevices.thorlabs import TSP01
```

For each device there should be a dummy device available in order to test software, when there is actually no device connected. For the switching to a dummy device simply import

```python
from labdevices.thorlabs import TSP01DUMMY
```

with DUMMY added to the device's class name.

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

- stick to the [naming convention](https://visualgit.readthedocs.io/en/latest/pages/naming_convention.html).
- use docstrings whenever useful, according to [PEP257](https://www.python.org/dev/peps/pep-0257/).
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

where `<user>` is your ubuntu username, which is also shown in the terminal at the beginning of each line.

Create a file in /etc/udev/rules.d/ with the name `50-myusb.rules` (if it does not exist yet) and add the following line

```console
SUBSYSTEM=="usb", MODE="0666", GROUP="usb"
```

After restarting the PC check that you are part of the usb group by typing `groups` into the terminal.

The communication with the usb device should now work.

### Ethernet devices

If an ethernet device is not recognized, check its settings. Usually a fixed IP address can be given, which should be part of the local subnet.
