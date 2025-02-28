import time
from sys import float_info
from typing import List

from src.sensors.amg8833 import (
    AMG8833_PIXEL_COUNT,
    DEFAULT_AMG8833_ADDRESS,
    RASPBERRY_PI_I2C_BUS,
    Amg8833,
    FrameRate,
)


class CachedAmg8833(Amg8833):
    """
    A derived Amg8833-handling class with built-in caching.
    Why a derived class? The sensor knows its own limits,
    including the maximum caching rate. Building it into the class
    avoids the need for callers to worry about any specifics,
    they simply drop the new class into their code.
    """

    def __init__(
        self,
        address: int = DEFAULT_AMG8833_ADDRESS,
        bus_number: int = RASPBERRY_PI_I2C_BUS,
    ):

        # Cached data - start with values that will get overwritten
        self.cached_temp_data: tuple[bool, List[int | float]] = (True, [])
        self.cached_thermistor_value = float_info.min

        self.frame_time = 1.0  # Default 1fps

        # Call super() after other setup, because base __init__ calls derived set_sample_rate()
        # Tidy this later
        super().__init__(address, bus_number)

    def update_cache_if_necessary(self):
        """
        If there's no data in the object, or if the cache was updated earlier than
        the required cache time, renew the cached data
        """
        if (
            time.time() - self.last_read_time > self.frame_time
            or not self.cached_temp_data
        ):
            self.cached_temp_data = super().read_temp(
                AMG8833_PIXEL_COUNT
            )  # Get all the data
            self.cached_thermistor_value = super().read_thermistor()
            self._last_read_time = time.time()

    def set_sample_rate(self, value: FrameRate) -> None:

        super().set_sample_rate(value)

        # Keep track of the timing
        if value == FrameRate.FPS_10:
            self.frame_time = 0.1
        else:
            self.frame_time = 1.0

    def read_temp(
        self, pixel_number: int = AMG8833_PIXEL_COUNT
    ) -> tuple[bool, List[int | float]]:

        self.update_cache_if_necessary()

        return self.cached_temp_data

    def read_thermistor(self) -> float:

        self.update_cache_if_necessary()

        return self.cached_thermistor_value
