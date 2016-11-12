# RaspberryPi Python I2C

# Introduction
This python library provides an smbus I2C access at a higher level.
Instead of using a bus object, this library using a device object to access individual I2C devices.

# Installation
  
  ```
  sudo apt-get update
  sudo apt-get install build-essential python-pip python3-pip python-dev python3-dev python-smbus python3-smbus git
  git clone https://github.com/ericbot/RaspberryPi_Python_I2C.git
  cd RaspberryPi_Python_I2C
  sudo python setup.py install
  sudo python3 setup.py install
  ```

# Quick Start
Using this software is easy.

This example accesses the device 0xF4 on bus 1 and writes 0x5B to register 0xA1.

    import Python_I2C as I2C # import library

    dev = I2C.Device(0xF4, 1) # access device
    
    dev.write8(0xA1, 0x5B) # write 8 bits
