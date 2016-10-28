from __future__ import nested_scopes, generators, division, absolute_import, with_statement, print_function, unicode_literals
import sys as _sys
from . import smbus as _smbus

def _comp(val, bits):
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

def _flip16(value):
    return ((value << 8) & 0xFF00) + (value >> 8)

class Device():
    def __init__(self, address, busnum, i2c_interface=None):
        self._address = address

        if i2c_interface == None:
            i2c_interface = _smbus.SMBus

        self._bus = i2c_interface(busnum)

    def writeRaw8(self, value):
        value &= 0xFF

        self._bus.write_byte(self._address, value)

    def write8(self, register, value):
        value &= 0xFF

        self._bus.write_byte_data(self._address, register, value)

    def write16(self, register, value):
        value &= 0xFFFF

        self._bus.write_word_data(self._address, register, value)

    def writeList(self, register, data):
        self._bus.write_i2c_block_data(self._address, register, data)

    def readList(self, register, length):
        results = self._bus.read_i2c_block_data(self._address, register, length)

        return results

    def readRaw8(self):
        result = self._bus.read_byte(self._address)

        result &= 0xFF

        return result

    def readU8(self, register):
        result = self._bus.read_byte_data(self._address, register)

        result &= 0xFF

        return result

    def readS8(self, register):
        result = self.readU8(register)

        result = _comp(result, 8)

        return result

    def readU16(self, register, little_endian=True):
        result = self._bus.read_word_data(self._address, register)

        result &= 0xFFFF

        if not little_endian:
            result = _flip16(result)

        return result

    def readS16(self, register, little_endian=True):
        result = self.readU16(register, little_endian)

        result = _comp(result, 16)

        return result

    def readU16LE(self, register):
        return self.readU16(register, little_endian=True)

    def readU16BE(self, register):
        return self.readU16(register, little_endian=False)

    def readS16LE(self, register):
        return self.readS16(register, little_endian=True)

    def readS16BE(self, register):
        return self.readS16(register, little_endian=False)

    


    
