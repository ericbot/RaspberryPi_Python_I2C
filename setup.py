from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(name              = 'Python_I2C',
      version           = '1.0.0',
      description       = 'Python library for accessing I2C',
      license           = 'Public Domain',
      url               = 'https://github.com/ericbot/RaspberryPi_Python_I2C/',
      packages          = find_packages())
