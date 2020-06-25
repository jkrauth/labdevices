Python package providing the software drivers for the devices in the RCS lab.

### Installation

We use a new conda environment to work with lab devices.

Create a conda environment as

```
$ conda create -n <name> python=3.6 
```

where `<name>` is your environment name. Then activate the environment with

```
$ conda activate <name>
```

##### A) For Development (I guess this is the better way for the general use in our lab)

From inside the package folder run

```
$ python setup.py develop
```

 Changes in the code of the labdevices package will automatically be available when loading the package in a restarted python console.

##### B) Alternatively

From inside the package folder run

```
$ pip install .
```

There might also be an option to use conda for installation. I am not sure about that at this moment.

If there have been updates in the repo you then have to upgrade the installation with

```
$ pip install --upgrade .
```

