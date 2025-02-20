from enum import Enum, IntEnum
from typing import List

from .i2cdriver import I2cDriver

# Copyright 2025 Jason Ross

# Hardware settings

DEFAULT_AMG8833_ADDRESS = 0x69
RASPBERRY_PI_I2C_BUS = 0x01

# AMGxxxx Registers


class AmgRegister(IntEnum):
    __str__ = Enum.__str__  # Print name despite this being an int

    REG_PCLT = 0x00  # Set Power Control (Normal = , Sleep = )
    REG_RST = 0x01  # Reset
    REG_FPSC = 0x02  # Set frame rate
    REG_INTC = 0x03  # Set interrupt control
    REG_STAT = 0x04  # Status
    REG_SCLR = 0x05  # Status clear

    REG_AVE = 0x07  # Set moving average output mode
    REG_INTHL = 0x08  # Set interrupt upper value (Lower level)
    REG_INTHH = 0x09  # Set interrupt upper value (Upper level)
    REG_INTLL = 0x0A  # Set interrupt lower value (Lower level)
    REG_INTLH = 0x0B  # Set interrupt lower value (Upper level)
    REG_INTSL = 0x0C  # Set interrupt hysteresis lower value (Lower level)
    REG_INTSH = 0x0D  # Set interrupt hysteresis upper value (Upper level)
    REG_TTHL = 0x0E  # Thermistor output value (Lower level)
    REG_TTHH = 0x0F  # Thermistor output value (Upper level)
    REG_INT0 = 0x10  # Pixel 1-8 interrupt result
    REG_INT1 = 0x11  # Pixel 9-16 interrupt result
    REG_INT2 = 0x12  # Pixel 17-24 interrupt result
    REG_INT3 = 0x13  # Pixel 25-32 interrupt result
    REG_INT4 = 0x14  # Pixel 33-40 interrupt result
    REG_INT5 = 0x15  # Pixel 41-48 interrupt result
    REG_INT6 = 0x16  # Pixel 49-56 interrupt result
    REG_INT7 = 0x17  # Pixel 57-64 interrupt result

    REG_PIXEL_BASE = 0x80  # Pixel 1 output value (Lower level)


class PowerControlMode(IntEnum):
    """
    Power modes
    """

    MODE_NORMAL = 0x00
    MODE_SLEEP = 0x10


class ResetMode(IntEnum):
    """
    Types of reset
    """

    FLAG_RESET = 0x30
    INITIAL_RESET = 0x3F


class FrameRate(IntEnum):
    """
    Sensor reading rate
    """

    FPS_1 = 0x01
    FPS_10 = 0x00


class InterruptSettings(IntEnum):
    ABSOLUTE_VALUE = 0b00000001
    DIFFERENCE = 0b00000011
    DISABLED = 0b00000000


def twos_compliment(value: int) -> float:
    """
    Pixel value conversion
    :param value:
    :return: Two's compliment of value
    """
    if 0x7FF & value == value:
        return float(value)
    else:
        return float(value - 4096)


def signed_conversion(value) -> float:
    """
    Conversion for thermistor

    :param value:
    :return:
    """

    if 0x7FF & value == value:
        return float(value)
    else:
        return -float(0x7FF & value)


class Amg8833:
    """
    An AMG8833 device, attached to the I2C bus
    """

    def __init__(
        self,
        address: int = DEFAULT_AMG8833_ADDRESS,
        bus_number: int = RASPBERRY_PI_I2C_BUS,
    ):
        self._device = I2cDriver(address=address, bus_number=bus_number)

        self.set_sensor_mode(PowerControlMode.MODE_NORMAL)
        self.reset_flags(ResetMode.INITIAL_RESET)
        self.set_interrupt_mode(InterruptSettings.DISABLED)
        self.set_sample_rate(FrameRate.FPS_10)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(device={self._device})"

    def set_sensor_mode(self, mode: PowerControlMode) -> None:
        """
        Set the power mode for the sensor
        :param mode:
        :return:
        """

        self._device.write8(AmgRegister.REG_PCLT, mode)

    def reset_flags(self, value: ResetMode) -> None:
        """
        Reset the sensor flags
        :param value:
        :return:
        """

        self._device.write8(AmgRegister.REG_RST, value)

    def set_sample_rate(self, value: FrameRate) -> None:
        """
        Set the sensor sample rate
        :param value:
        :return:
        """
        self._device.write8(AmgRegister.REG_FPSC, value)

    def set_interrupt_mode(self, value: InterruptSettings) -> None:
        """
        Set the interrupt mode
        :param value:
        :return:
        """

        self._device.write8(AmgRegister.REG_INTC, value)

    def clear_status(self):
        """
        Clear the interrupt and overflow statuses
        :return:
        """
        self._device.write8(AmgRegister.REG_SCLR, 0b00000110)

    def read_temp(self, pixel_number: int) -> tuple[bool, List[int | float]]:
        temperatures = []  # temp array
        status = False  # status boolean for errors
        for i in range(0, pixel_number):
            raw = self._device.read16(AmgRegister.REG_PIXEL_BASE + (i << 1))
            converted = twos_compliment(raw) * 0.25
            if converted < -20 or converted > 100:
                return True, temperatures  # return error if outside temp window
            temperatures.append(converted)
        return status, temperatures

    def read_thermistor(self) -> float:
        """

        :return: The ambient temperature detected by the thermistor
        """
        raw = self._device.read16(AmgRegister.REG_TTHL)

        # Raw value requires scaling
        return signed_conversion(raw) * 0.0625
