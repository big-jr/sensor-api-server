import time

from fastapi import FastAPI

from src.sensors.amg8833 import Amg8833

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/sensor/1/data")
async def temperatures():

    try:

        sensor = Amg8833(0x69, 1)

        result = {
            "ambient_temperature": sensor.read_thermistor(),
            "temperature": sensor.read_temp(64),
            "time": time.time(),
        }

        return result
    finally:
        sensor.close()
