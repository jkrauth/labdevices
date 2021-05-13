## v0.10.0

- implement a general device interface with a set of basic methods that has to apply for each device and that is tested among the package
- implement unittests for all devices and their dummy versions
- implement a new way of creating dummy devices that uses the actual driver class of a device.
- some changes create incompatibilities with the previous version. This was necessary to make the package more uniform, according to the newly implemented tests.
- bugfixes

# v0.9.0

- added Local Oscillator from Kuhne Electronic
- included missing dependency for the newport stage
- connection to allied vision was fully moved to initialize method, like in all other devices. 
- added more type hints and small refactoring

# v0.8.4

- start to apply semantic versioning
- first version indexed on PyPI
