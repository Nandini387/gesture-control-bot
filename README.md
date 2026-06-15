# gesture-control-bot

A compact gesture-controlled robot project using an ESP/Arduino sketch and a Python motor controller. This repository contains the firmware to run on the microcontroller and a small Python controller to drive the motors from gesture input (OpenCV or other gesture sources).

---

**Table of contents**

- **Overview**
- **Features**
- **Hardware required**
- **Software required**
- **Wiring**
- **Setup**
	- Upload firmware (`espcode.ino`)
	- Run Python controller (`motor.py`)
- **Usage**
- **Files**
- **Contributing**
- **License**

---

## Overview

`gesture-control-bot` pairs an ESP/Arduino-compatible microcontroller running `espcode.ino` with a Python-based motor controller `motor.py`. The microcontroller receives simple motor commands (e.g., forward/backward/left/right/stop) and drives the motors accordingly; gesture detection (OpenCV or other) is expected to run separately and send commands to `motor.py` or directly to the ESP.

## Features

- Minimal, easy-to-read firmware for motor control.
- Simple Python controller to forward commands to the robot.
- Easy to adapt to your gesture-detection pipeline (OpenCV, ML, remote control).

## Hardware required

- An ESP8266 / ESP32 or Arduino-compatible board (ESP recommended for Wi-Fi use).
- Motor driver (L298N, TB6612, or similar).
- Two DC motors (or a differential drive pair).
- Power supply appropriate for motors and board.
- Jumper wires, chassis, and optional wheels.

## Software required

- Arduino IDE (to upload `espcode.ino`) or PlatformIO.
- Python 3.8+ (to run `motor.py`).
- Optional: `pyserial` if the Python controller communicates over serial.

If your `motor.py` needs packages, install them with pip. Example (adjust as needed):

```bash
python -m pip install pyserial opencv-python
```

## Wiring (general guidance)

- Connect the motor driver inputs to the microcontroller GPIO pins used in `espcode.ino`.
- Connect motor driver power (Vmotor) and ground; share ground with the microcontroller.
- Connect motor outputs to the motors.

Refer to your motor driver and board datasheets for correct connections and power ratings.

## Setup

1. Firmware: upload `espcode.ino` to your ESP/Arduino board using the Arduino IDE or PlatformIO. Update pin definitions in the sketch if your wiring differs.

2. Python controller: adapt `motor.py` to your communication method (serial, TCP, UDP). Typical usage:

```bash
# run the motor controller (may require editing port/host inside the script)
python motor.py
```

Notes:
- If `motor.py` uses serial, set the correct serial port (e.g., `COM3`, `/dev/ttyUSB0`) and baud rate to match the sketch.
- If using Wi‑Fi (ESP32/ESP8266), configure SSID/credentials and the communication protocol in both the sketch and Python script.

## Usage example

- Start your gesture recognition pipeline (OpenCV script or ML model) and map detected gestures to short, reliable commands (e.g., `FWD`, `BACK`, `LEFT`, `RIGHT`, `STOP`).
- Send those commands to `motor.py` (or directly to the ESP) over your chosen channel.

Example command sequence sent from the Python side to the microcontroller (pseudo):

```
FWD
STOP
LEFT
FWD
STOP
```

## Files

- [espcode.ino](espcode.ino): Arduino/ESP sketch that implements motor control and communication handling.
- [motor.py](motor.py): Simple Python motor controller to forward commands from a PC/gesture pipeline to the robot.

## Contributing

- Improve wiring notes or pin mappings as you test with hardware.
- If you add a gesture-detection example, include a small demo and dependency list.
- Open an issue or submit a pull request with improvements.

## License

This project is provided under the MIT License — see the `LICENSE` file for details.

---
Made by Nandini Karn. 

