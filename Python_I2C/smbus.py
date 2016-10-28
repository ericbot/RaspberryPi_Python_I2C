from __future__ import nested_scopes, generators, division, absolute_import, with_statement, print_function, unicode_literals
from fcntl import ioctl
from ctypes import *
import struct

I2C_M_TEN             = 0x0010
I2C_M_RD              = 0x0001
I2C_M_STOP            = 0x8000
I2C_M_NOSTART         = 0x4000
I2C_M_REV_DIR_ADDR    = 0x2000
I2C_M_IGNORE_NAK      = 0x1000
I2C_M_NO_RD_ACK       = 0x0800
I2C_M_RECV_LEN        = 0x0400

I2C_SLAVE             = 0x0703
I2C_SLAVE_FORCE       = 0x0706

I2C_TENBIT            = 0x0704
I2C_FUNCS             = 0x0705
I2C_RDWR              = 0x0707
I2C_PEC               = 0x0708
I2C_SMBUS             = 0x0720

class i2c_msg(Structure):
    _fields_ = [
        ('addr',  c_uint16),
        ('flags', c_uint16),
        ('len',   c_uint16),
        ('buf',   POINTER(c_uint8))
    ]

class i2c_rdwr_ioctl_data(Structure):
    _fields_ = [
        ('msgs',  POINTER(i2c_msg)),
        ('nmsgs', c_uint32)
    ]

def make_i2c_rdwr_data(messages):
    msg_data_type = i2c_msg*len(messages)
    msg_data = msg_data_type()
    for i, m in enumerate(messages):
        msg_data[i].addr = m[0] & 0x7F
        msg_data[i].flags = m[1]
        msg_data[i].len = m[2]
        msg_data[i].buf = m[3]
    data = i2c_rdwr_ioctl_data()
    data.msgs = msg_data
    data.nmsgs = len(messages)
    return data


i2c_path = '/dev/i2c-%s'
get_i2c_path = lambda bus: i2c_path % (str(bus))

class I2CError(Exception):
    pass

class SMBus():
    def __init__(self, bus=None):
        self._device = None

        if bus is not None:
            self.open(bus)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self, bus):
        if self._is_open():
            self.close()

        try:
            self._device = open(get_i2c_path(bus), 'r+b', buffering=0)

        except IOError as e:
            raise I2CError('Couldn\'t open i2c bus!')

    def close(self):
        if self._is_open():
            self._device.close()
            self._device = None

    def _is_open(self):
        return self._device is not None

    def _file(self):
        return self._device.fileno()

    def _select_device(self, addr):
        ioctl(self._file(), I2C_SLAVE, addr & 0x7F)

    def _check_open_bus(self):
        assert self._is_open(), 'Bus must be opened before operations are made against it!'

    def _transaction(self, request):
        ioctl(self._file(), I2C_RDWR, request)

    def read_byte(self, addr):
        self._check_open_bus()

        self._select_device(addr)

        return ord(self._device.read(1))

    def read_byte_data(self, addr, cmd):
        self._check_open_bus()

        reg = c_uint8(cmd)
        result = c_uint8()

        request = make_i2c_rdwr_data([
            (addr, 0, 1, pointer(reg)),
            (addr, I2C_M_RD, 1, pointer(result))
        ])

        self._transaction(request)

        return result.value

    def read_word_data(self, addr, cmd):
        self._check_open_bus()

        reg = c_uint8(cmd)
        result = c_uint16()

        request = make_i2c_rdwr_data([
            (addr, 0, 1, pointer(reg)),
            (addr, I2C_M_RD, 2, cast(pointer(result), POINTER(c_uint8)))
        ])

        self._transaction(request)

        return result.value

    def read_block_data(self, addr, cmd):
        #not supported by raspberry pi i2c driver
        return NotImplementedError()

    def read_i2c_block_data(self, addr, cmd, length=32):
        self._check_open_bus()

        reg = c_uint8(cmd)
        result = create_string_buffer(length)

        request = make_i2c_rdwr_data([
            (addr, 0, 1, pointer(reg)),
            (addr, I2C_M_RD, length, cast(result, POINTER(c_uint8)))
        ])

        self._transaction(request)

        return bytearray(result.raw)

    def write_quick(self, addr):
        self._check_open_bus()

        request = make_i2c_rdwr_data([
            (addr, 0, 0, None),
        ])

        self._transaction(request)

    def write_byte(self, addr, val):
        self._check_open_bus()

        self._select_device(addr)

        data = bytearray(1)
        data[0] = val & 0xFF

        self._device.write(data)
        

    def write_byte_data(self, addr, cmd, val):
        self._check_open_bus()

        self._select_device(addr)

        data = bytearray(2)
        data[0] = cmd & 0xFF
        data[1] = val & 0xFF

        self._device.write(data)

    def write_word_data(self, addr, cmd, val):
        self._check_open_bus()

        self._select_device(addr)

        data = struct.pack('=BH', cmd & 0xFF, val & 0xFFFF)

        self._device.write(data)

    def write_block_data(self, addr, cmd, vals):
        data = bytearray(len(vals)+1)
        data[0] == len(vals) & 0xFF
        data[1:] = vals[0:]

        self.write_i2c_bloack_data(addr, cmd, data)

    def write_i2c_block_data(self, addr, cmd, vals):
        self._check_open_bus()

        self._select_device(addr)

        data = bytearray(len(vals)+1)
        data[0] = cmd & 0xFF
        data[1:] = vals[0:]

        self._device.write(data)

    def process_call(self, addr, cmd, val):
        self._check_open_bus()

        data = create_string_buffer(struct.pack('=BH', cmd, val))

        result = c_uint16()

        request = make_i2c_rdwr_data([
            (addr, 0, 3, cast(pointer(data), POINTER(c_uint8))),
            (addr, I2C_M_RD, 2, cast(pointer(result), POINTER(c_uint8)))
        ])

        self._transaction(request)

        return result.value
