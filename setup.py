"""
With this file setuptools can handle the installation of the package.

File name: setup.py
Author: Julian Krauth
Date created: 2020/06/25
Python Version: 3.7
"""
from setuptools import setup, find_packages

setup(
    name='labdevices',
    version='0.7',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'pyyaml',                 # for ALLIED_VISION
        'numpy',                  # for ANDO, ALLIED_VISION
        'pymba',                  # for ALLIED_VISION
        #'prologix-gpib-ethernet', # for ANDO
        'pyvisa',                 # for NEWPORT
        'pyvisa-py',              # needed for pyvisa
        'pyusb',                  # needed for pyvisa
    ],
    # For modules which have no entry in pypi.org, dependency
    # links have to be provided. They exist of a link to the
    # project on github + an appendix of the shape
    # '/tarball/master#egg=<PACKAGE_NAME>-<VERSION>',
    # where <VERSION> is the git tag to use.
    #dependency_links=[
    #    'git+https://github.com/nelsond/prologix-gpib-ethernet/tarball/master#egg=prologix-gpib-ethernet-0.1.2'
    #]
)
