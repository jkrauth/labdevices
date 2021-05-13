"""
With this file setuptools and pip can handle the installation of the package.

File name: setup.py
Author: Julian Krauth
Date created: 2020/06/25
Python Version: 3.7
"""
import pathlib
from setuptools import setup, find_packages
from labdevices import __version__

HERE = pathlib.Path(__file__).parent

README = (HERE / 'README.md').read_text()

with open(HERE / 'requirements.txt') as fh:
    requirements = [line.strip() for line in fh]

setup(
    name='labdevices',
    version=__version__,
    description='SDK for typical devices found in an atomic physics research lab.',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/jkrauth/labdevices',
    author='Julian Krauth',
    author_email='j.krauth@vu.nl',
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Physics",
        "Intended Audience :: Science/Research",
    ],
    packages=find_packages(include=['labdevices', 'labdevices._mock']),
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=requirements,
)
