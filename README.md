# sensor-api-server

## Introduction

A simple server to provide an API with details from a sensor

This repo contains the code to communicate with the AMG8833 - an 8x8 pixel infrared sensor that communicates on the I2C bus. The code assumes the sensor is connected to a Raspberry Pi at the default I2C address 0x69, on bus 1.

Although there is other Python code available that communicates with this device, this code was written in a more object-oriented and typesafe way. The control registers and values are all enumerated types, and the functions that accept them are specified as requiring these types as parameters. This means that any mistakes will be highlighted as warnings by the IDE, ruff, or any other code linting system.

In addition, the Amg8833 class allows the connection to the device to be closed, which many others do not. This stops the bus connection from being left open when the sensor is not required.

## Notes

The `sensors.Amd8833` class may be used as a context manager, so you don't need to explicitly call the `close()` function to release the connection.

## Running The Server

The server uses FastAPI, and to run it so that allows connections from any IP on the network, use `uvicorn` as follows:

```bash
uvicorn src.api_server.main:app --host 0.0.0.0
```

N.B. The path to the `app` variable is the fully-qualified path including all the modules relative to the current directory.

## Summary

This code is written and maintained by Jason Ross, and released under the MIT licence.

Visit my website at [https://www.softwarepragmatism.com](https://www.softwarepragmatism.com) for more projects and articles.
