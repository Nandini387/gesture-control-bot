# gesture-control-bot

A compact gesture-controlled robot that pairs an ESP/Arduino-compatible microcontroller with a simple Python motor controller. This repository contains the microcontroller sketch (`espcode.ino`) and a Python helper (`motor.py`) to forward movement commands from a gesture-detection pipeline (e.g., OpenCV) to the robot.

---

**Table of contents**

- Overview
- Quick demo
- Hardware
- Software
- Wiring & pin mapping (example)
- Setup
- Usage
- Example OpenCV sender (quick)
- Troubleshooting
- Contributing
- License

---

## Overview

The project implements a minimal command protocol for basic robot movements (forward, back, left, right, stop). You can run a gesture detector on your PC or Raspberry Pi to translate gestures into short commands and send them to the robot via serial or network.

This repo intentionally keeps the firmware and Python controller lightweight so you can plug them into your preferred gesture system.

## Quick demo

1. Upload `espcode.ino` to your ESP/Arduino board.
2. Start `motor.py` on the PC or Pi that will send commands.
3. Use the sample OpenCV sender (below) or your own pipeline to send commands like `FWD`, `BACK`, `LEFT`, `RIGHT`, `STOP`.

## Hardware

- Microcontroller: ESP32 / ESP8266 / Arduino UNO (ESP recommended for Wi‑Fi options).
- Motor driver: L298N, TB6612, or similar.
- 2 DC motors (differential drive).
- Power supply for motors (ensure current/voltage match motors).
- Common ground between motor power and microcontroller.

## Software

- Arduino IDE or PlatformIO (to upload `espcode.ino`).
- Python 3.8+ for running `motor.py` and optional gesture scripts.
- Optional Python packages: `pyserial`, `opencv-python` (if using serial and OpenCV sender).

Suggested `requirements.txt` (if you want a quick file):

```
pyserial>=3.5
opencv-python>=4.5
```

## Wiring & pin mapping (example)

Below is an example wiring mapping for an **ESP32** driving an **L298N** motor driver. Adjust pins in `espcode.ino` if you use different pins or a different board.

- `IN1` (L298) -> GPIO 16
- `IN2` (L298) -> GPIO 17
- `IN3` (L298) -> GPIO 18
- `IN4` (L298) -> GPIO 19
- `EN_A`, `EN_B` -> Motor power enable (or tie to Vcc via jumper)

Power notes:
- Connect motor driver Vmotor to battery (not the ESP 5V regulator) and share ground with the ESP.
- Do not power motors from the microcontroller's 3.3V/5V regulator if motors draw significant current.

If you use a different driver (TB6612), map AIN1/AIN2/BIN1/BIN2 similarly and connect PWM pins as needed.

## Setup

1. Open `espcode.ino` in the Arduino IDE (or import into PlatformIO). Review and update pin definitions to match your wiring.
2. Select the correct board and upload the sketch.
3. Prepare the PC/Pi that will send commands:

```bash
# optional: create virtualenv
python -m venv .venv
./.venv/Scripts/activate  # Windows
source .venv/bin/activate # macOS / Linux
python -m pip install -r requirements.txt  # if you created requirements.txt
```

4. Run `motor.py`. Edit the script to set the correct serial port (e.g., `COM3` on Windows or `/dev/ttyUSB0` on Linux) or network host/port if configured.

```bash
python motor.py
```

## Usage

The command protocol is intentionally simple: send newline-terminated short strings, for example:

- `FWD` — move forward
- `BACK` — move backward
- `LEFT` — turn left
- `RIGHT` — turn right
- `STOP` — stop motors

Commands can be sent over serial or over the network depending on how `espcode.ino` and `motor.py` are set up. Keep commands short and canonical to avoid parsing ambiguity.

## Example OpenCV sender (quick)

This small example shows how a gesture script can send commands over serial to `motor.py` or directly to the microcontroller. This is deliberately minimal — integrate it into your existing gesture-detection code.

```python
import serial
import time

# adjust port and baud
ser = serial.Serial('COM3', 115200, timeout=1)

def send(cmd):
	ser.write((cmd + "\n").encode())
	time.sleep(0.05)

# Example usage
send('FWD')
time.sleep(1)
send('STOP')

ser.close()
```

If your gesture pipeline runs on the same machine as `motor.py`, you can instead call the `motor.py` API (if you adapt it) or use sockets to communicate.

## Troubleshooting

- No movement: verify motor power supply and common ground.
- Serial connection fails: confirm correct port and baud rate; ensure no other program holds the port.
- Motors jitter: add delays between commands or enable PWM smoothing depending on driver.

## Contributing

- Open issues for bugs or feature requests.
- If you add a gesture demo, include clear dependency instructions and a short video or GIF demonstrating it.

## License

This project is licensed under the MIT License — see the `LICENSE` file.



