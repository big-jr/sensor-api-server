import asyncio
import time

from fastapi import FastAPI

from src.sensors.amg8833 import Amg8833

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/sensor/1/data")
async def temperatures():
    """

    :return: All of the data from the sensor
    """

    # Declare the sensor so we can close it later
    # Maybe use a context manager on this
    sensor = None

    try:
        sensor = Amg8833(0x69, 1)

        # Sleep to allow the sensor to settle
        await asyncio.sleep(0.1)

        return {
            "ambient_temperature": sensor.read_thermistor(),
            "temperature": sensor.read_temp(64),
            "time": time.time(),
        }

    finally:
        if sensor:
            sensor.close()
