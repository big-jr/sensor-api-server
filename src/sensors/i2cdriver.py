import smbus2


class I2cDriver(object):
    """
    Basic I2C driver binding
    """

    def __init__(self, address: int, bus_number: int):
        """

        :param address: Address of the device on the I2C bus
        :param bus_number: 1 for RPi 2,3,4
        """

        self._address = address
        self._bus = smbus2.SMBus(bus_number)

    def close(self) -> None:
        """
        Close the connection to the device
        :return:
        """

        self._bus.close()

    def write8(self, register, value):
        """
        Write 8 bits to the specified register
        :param register:
        :param value:
        :return:
        """

        value = value & 0xFF
        self._bus.write_byte_data(self._address, register, value)

    def read16(self, register, little_endian=True):
        """
        Read 16 bits from the specified register
        :param register:
        :param little_endian:
        :return:
        """

        result = self._bus.read_word_data(self._address, register) & 0xFFFF
        if not little_endian:
            result = ((result << 8) & 0xFF00) + (result >> 8)
        return result
