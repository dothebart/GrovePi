# intended to wrap I2C.py when using a tca9548a Multiplexer
# https://learn.adafruit.com/adafruit-tca9548a-1-to-8-i2c-multiplexer-breakout/overview

import logging

import I2C
import smbus

class MXedDevice(object):
    """Class for communicating with an I2C device using the smbus library.
    Allows reading and writing 8-bit, 16-bit, and byte array values to registers
    on the device."""
    def __init__(self, mxDevice, address, busnum):
        """Create an instance of the I2C device at the specified address on the
        specified I2C bus number; asume to switch an mx active before being able
        to talk to it"""
        self._mxDevice = mxDevice
        self._address = address
        self._bus = smbus.SMBus(busnum)
        self._logger = logging.getLogger('Adafruit_I2C.Device.Bus.{0}.Address.{1:#0X}' \
                                .format(busnum, address))

    def writeRaw8(self, value):
        """Write an 8-bit value on the bus (without register)."""
        self._mxDevice.activeBus()
        value = value & 0xFF
        self._bus.write_byte(self._address, value)
        self._logger.debug("Wrote 0x%02X",
                     value)

    def write8(self, register, value):
        """Write an 8-bit value to the specified register."""
        self._mxDevice.activeBus()
        value = value & 0xFF
        self._bus.write_byte_data(self._address, register, value)
        self._logger.debug("Wrote 0x%02X to register 0x%02X",
                     value, register)

    def write16(self, register, value):
        """Write a 16-bit value to the specified register."""
        self._mxDevice.activeBus()
        value = value & 0xFFFF
        self._bus.write_word_data(self._address, register, value)
        self._logger.debug("Wrote 0x%04X to register pair 0x%02X, 0x%02X",
                     value, register, register+1)

    def writeList(self, register, data):
        """Write bytes to the specified register."""
        self._mxDevice.activeBus()
        self._bus.write_i2c_block_data(self._address, register, data)
        self._logger.debug("Wrote to register 0x%02X: %s",
                     register, data)

    def readList(self, register, length):
        """Read a length number of bytes from the specified register.  Results
        will be returned as a bytearray."""
        self._mxDevice.checkActiveBus()
        results = self._bus.read_i2c_block_data(self._address, register, length)
        self._logger.debug("Read the following from register 0x%02X: %s",
                     register, results)
        return results

    def readRaw8(self):
        """Read an 8-bit value on the bus (without register)."""
        self._mxDevice.checkActiveBus()
        result = self._bus.read_byte(self._address) & 0xFF
        self._logger.debug("Read 0x%02X",
                    result)
        return result

    def readU8(self, register):
        """Read an unsigned byte from the specified register."""
        self._mxDevice.checkActiveBus()
        result = self._bus.read_byte_data(self._address, register) & 0xFF
        self._logger.debug("Read 0x%02X from register 0x%02X",
                     result, register)
        return result

    def readS8(self, register):
        """Read a signed byte from the specified register."""
        self._mxDevice.checkActiveBus()
        result = self.readU8(register)
        if result > 127:
            result -= 256
        return result

    def readU16(self, register, little_endian=True):
        """Read an unsigned 16-bit value from the specified register, with the
        specified endianness (default little endian, or least significant byte
        first)."""
        self._mxDevice.checkActiveBus()
        result = self._bus.read_word_data(self._address,register) & 0xFFFF
        self._logger.debug("Read 0x%04X from register pair 0x%02X, 0x%02X",
                           result, register, register+1)
        # Swap bytes if using big endian because read_word_data assumes little
        # endian on ARM (little endian) systems.
        if not little_endian:
            result = ((result << 8) & 0xFF00) + (result >> 8)
        return result

    def readS16(self, register, little_endian=True):
        """Read a signed 16-bit value from the specified register, with the
        specified endianness (default little endian, or least significant byte
        first)."""
        self._mxDevice.checkActiveBus()
        result = self.readU16(register, little_endian)
        if result > 32767:
            result -= 65536
        return result

    def readU16LE(self, register):
        """Read an unsigned 16-bit value from the specified register, in little
        endian byte order."""
        return self.readU16(register, little_endian=True)

    def readU16BE(self, register):
        """Read an unsigned 16-bit value from the specified register, in big
        endian byte order."""
        return self.readU16(register, little_endian=False)

    def readS16LE(self, register):
        """Read a signed 16-bit value from the specified register, in little
        endian byte order."""
        return self.readS16(register, little_endian=True)

    def readS16BE(self, register):
        """Read a signed 16-bit value from the specified register, in big
        endian byte order."""
        return self.readS16(register, little_endian=False)

class MXedI2C(object):
    def __init__(self, mxDevice, whichChannel, bus=-1, debug=False, **kwargs):
        self.busNum = bus
        self.mxDevice = mxDevice
        self.whichChannel = whichChannel

    def get_i2c_device(self, address, busnum=None, **kwargs):
        if busnum is None:
            busnum = I2C.get_default_bus()
        return MXedDevice(self, address, busnum, **kwargs)

    def activeBus(self):
        self.mxDevice.SetActiveChannel(self.whichChannel)

    def checkActiveBus(self):
        if not self.mxDevice.IsActiveChannel(self.whichChannel):
            msg = "trying to read from bus no #%d while Bus %d is active!" % (
                self.whichChannel,
                self.mxDevice.GetActiveChannel())
            raise Exception(msg)


class MXtca9548aDevice(object):

    i2c = None

    TC9548A_I2CADDR_DEFAULT = 0x70
    TC9548A_I2CADDR_MAX = 0x77

    def __init__(self, address=TC9548A_I2CADDR_DEFAULT, bus=-1, debug=False, i2c=None, **kwargs):
        self.isDebug = debug
        self.debug("Initialising TC9548A")

        # Assume we're using platform's default I2C bus if none is specified.
        if i2c is None:
            import I2C
            self.i2c = I2C
            # Require repeated start conditions for I2C register reads.  Unfortunately
            # the MPR121 is very sensitive and requires repeated starts to read all
            # the registers.
            I2C.require_repeated_start()
            # Save a reference to the I2C device instance for later communication.
        self._device = self.i2c.get_i2c_device(address, **kwargs)
        self.address = address

        self.activeChannel = None
        self.SetActiveChannel(0)

    def SetActiveChannel(self, whichChannel):
        if self.activeChannel != None and self.activeChannel == whichChannel:
            return
        if whichChannel > 7:
            raise Exception("which bus number must be 0-7, you gave %d" % whichChannel)
        print("setting active!")
        self._device.writeRaw8(whichChannel)
        self.activeChannel = whichChannel

    def IsActiveChannel(self, whichChannel):
        return whichChannel == self.activeChannel

    def GetActiveChannel(self):
        return self.activeChannel

    def GetSubDevice(self, whichChannel):
        if whichChannel > 7:
            raise Exception("which bus number must be 0-7, you gave %d" % whichChannel)
        return MXedI2C(self, whichChannel)

    def debug(self, message):
        if not self.isDebug: return
        print message
