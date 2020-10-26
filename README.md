Python package providing the software drivers for the devices in the RCS lab.

### Included Devices are from

- Allied Vision Manta
- Applied Motion Products
- ANDO Spectrum Analyzer
- Newport
- Pfeiffer Vacuum
- Stanford Research Systems
- Thorlabs

### Installation

We use a new conda environment to work with lab devices.

Create a conda environment as

```
$ conda create -n <name> python=3.6
```

where `<name>` is your environment name. The python version should be 3.6 or higher. Then activate the environment with

```
$ conda activate <name>
```

##### A) For development

From inside the package folder run

```
$ python setup.py develop
```

 Changes in the code of the labdevices package will automatically be available when loading the package in a restarted python console.

##### B) For general use

From inside the package folder run

```
$ pip install .
```

There might also be an option to use conda for installation. I am not sure about that at this moment.

If there have been updates in the repo you then have to upgrade the installation with:

```
$ pip install --upgrade .
```

### Usage

Once the labdevices package is installed into a conda environment you can simply do e.g.

```python
from labdevices.thorlabs import TSP01
```

For each device there should be a dummy device available in order to test software, when there is actually no device connected. For the switching to a dummy device simply import

```python
from labdevices.thorlabs import TSP01DUMMY
```

with DUMMY added to the device's class name.

### Add new drivers or modify existing ones

For modifications always work in a new branch (never the master branch).

Add a new class into a file which carries the name of its company. If any non-standard packages are required, add them to the list in the setup.py file.

New drivers should be tested before the changes are merged into the master branch. Same applies for modifications to already existing modules: Test them, before you add/merge them to the master branch.

Once the modifications are ready to go, increase the version number in the setup file and merge into master. After pushing the changes, every PC can update the package as described above.

### Troubleshooting

##### Ubuntu

If you want to read a VISA address with the pyvisa package and you get the following message

> Found a device whose serial number cannot be read. The partial VISA resource name is: USB0::2733::443::???::2::INSTR

the issue is related to the permissions regarding the [udev rules](https://www.thegeekdiary.com/beginners-guide-to-udev-in-linux/). If you don't have permission to write on USB devices you will not be able to communicate properly with the device. To solve this problem  (see also [here](http://manpages.ubuntu.com/manpages/bionic/man3/Device::USB::FAQ.3pm.html)) you have to create a group with the name *usb* by

```
addgroup --system usb
```

Next, add your user to that group by

```
sudo adduser <user> usb
```

where <user> is your ubuntu username, which is also shown in the terminal at the beginning of each line.

Create a file in /etc/udev/rules.d/ with the name `50-myusb.rules` (if it does not exist yet) and add the following line

```
SUBSYSTEM=="usb", MODE="0666", GROUP="usb"
```

After restarting the PC check that you are part of the usb group by typing `groups` into the terminal.

The communication with the usb device should now work.

##### Ethernet devices

If an ethernet device is not recognized, check its settings. Usually a fixed IP address can be given, which should be part of the local subnet.