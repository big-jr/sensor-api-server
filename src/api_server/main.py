import asyncio
import time
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI

from src.sensors.amg8833 import Amg8833
from src.sensors.cached_amg8833 import CachedAmg8833

sensor: Amg8833 | None = None


@asynccontextmanager
async def server_lifespan(app: FastAPI):

    # Not a fan of global - tidy this later
    global sensor
    sensor = CachedAmg8833(0x69, 1)

    # Sleep to allow the sensor to settle
    await asyncio.sleep(0.2)

    yield

    sensor.close()


app = FastAPI(lifespan=server_lifespan)


@app.get("/")
async def root():
    return {"message": "AMG8833 API. See /docs for API details."}


@app.get("/sensor/0/data")
async def temperatures():
    """

    :return: All the data from the sensor
    """

    error, temperature_readings = sensor.read_temp()

    return {
        "error": error,
        "ambient_temperature": sensor.read_thermistor(),
        "temperatures": temperature_readings,
        "time": sensor.last_read_time,
    }
