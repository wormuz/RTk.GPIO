# RTk.GPIO — USB GPIO for PC/Mac/Linux

A Python GPIO module that works on any platform. Plug in an RTk.GPIO board (or Arduino Pro Micro) via USB and control 17 GPIO pins from Python — same API as `RPi.GPIO`.

Based on [anyio](https://github.com/whaleygeek/anyio) by David Whale (@whaleygeek), adapted for RTk.GPIO by Ryan Walmsley (@Ryanteck).

**Updated 2026-04-07:** Full Python 3 rewrite — all drivers fixed, auto-detect, 10 bugs resolved.

## Hardware

| Board | MCU | USB Chip | Baud | Pins |
|-------|-----|----------|------|------|
| **RTk.GPIO** | STM32 NUCLEO-F030R8 | CH340 | **230400** | 0–16 (17 GPIO) |
| Arduino Pro Micro | ATmega32U4 | CDC | 115200 | 0–16 |

## Quick Start

```bash
pip install pyserial
```

```python
import sys; sys.path.insert(0, 'RTk.GPIO')
import anyio.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

# Output
GPIO.setup(4, GPIO.OUT)
GPIO.output(4, True)

# Input
GPIO.setup(5, GPIO.IN)
print(GPIO.input(5))

GPIO.cleanup()
```

The board is auto-detected when a single USB serial device is present. If multiple devices exist, you'll be prompted to select one. The selected port is cached in `portscan.cache`.

## Drivers

| Driver | Import | Status |
|--------|--------|--------|
| **RTk.GPIO** (default) | `import anyio.GPIO as GPIO` | Working (hardware tested) |
| **Arduino** | `import anyio.arduino.GPIO as GPIO` | Working (untested, no HW) |
| **Console simulator** | `import anyio.console.GPIO as GPIO` | Working |
| **GUI simulator** | `import anyio.gui.GPIO as GPIO` | Placeholder (imports OK) |
| **Network remote** | `import anyio.net.GPIO as GPIO` | Placeholder (imports OK) |
| **Raspberry Pi** | change `DRIVER = "RPi"` in `anyio/GPIO.py` | Passthrough to RPi.GPIO |

To switch the default driver, edit `DRIVER` in `anyio/GPIO.py`.

## API

Mirrors `RPi.GPIO`:

```python
GPIO.setmode(GPIO.BCM)          # required (no-op, for compatibility)
GPIO.setup(pin, GPIO.OUT)       # configure pin as output
GPIO.setup(pin, GPIO.IN)        # configure pin as input
GPIO.output(pin, True)          # write HIGH
GPIO.output(pin, False)         # write LOW
val = GPIO.input(pin)           # read pin (returns True/False)
GPIO.cleanup()                  # release resources, close port
```

## Serial Protocol

2-byte ASCII commands at 230400 baud (RTk.GPIO) or 115200 (Arduino):

```
Byte 1: pin character = chr(pin_number + ord('a'))    # pin 0='a', pin 16='q'
Byte 2: command
  'I' — set input mode
  'O' — set output mode
  '?' — read (response: <pin_char><0|1>\r\n)
  '1' — write HIGH
  '0' — write LOW
```

## Pin Notes

- **Pins 2, 3:** Have hardware pull-ups on RTk.GPIO board (buttons/I2C). Always read HIGH regardless of output state.
- **Pin range:** 0–16 for RTk.GPIO/console/GUI/net, 0–16 for Arduino driver.

## Performance

| Metric | Value |
|--------|-------|
| Toggle speed (output) | ~9,200 Hz |
| Read latency | ~0.1 ms per pin |
| Bottleneck | Serial USB (230400 baud) |

## Project Structure

```
RTk.GPIO/
├── anyio/
│   ├── GPIO.py              # Main entry — selects driver
│   ├── protocol.py          # Wire protocol (pin commands)
│   ├── adaptors.py          # Serial/network adaptor layer
│   ├── rtk/                 # RTk.GPIO board driver (default)
│   │   ├── GPIO.py
│   │   ├── portscan.py      # Auto-detect + cache + interactive scan
│   │   ├── ports_unix.py
│   │   └── ports_win32.py
│   ├── arduino/             # Arduino Pro Micro driver
│   │   ├── GPIO.py
│   │   ├── portscan.py
│   │   ├── ports_unix.py
│   │   └── ports_win32.py
│   ├── console/             # Text-mode simulator
│   │   ├── GPIO.py
│   │   └── GPIOClient.py
│   ├── gui/                 # Tkinter simulator (placeholder)
│   │   ├── GPIO.py
│   │   └── GPIOClient.py
│   ├── net/                 # Network GPIO (placeholder)
│   │   ├── GPIO.py
│   │   ├── GPIOClient.py
│   │   └── network.py
│   ├── seg7.py              # 7-segment display driver
│   └── testSerial.py        # Serial port test utility
├── findPort.py              # Port scanner CLI
├── testHardware.py          # LED + button test
├── testLED.py               # Traffic light LED demo
├── Pibrella.py              # Pibrella board demo
├── zeropoint.py             # Stepper motor driver
├── RTkGPIOV1_NUCLEO_F030R8.bin  # Board firmware
└── LICENSE
```

## Firmware

The firmware binary `RTkGPIOV1_NUCLEO_F030R8.bin` is for the STM32 NUCLEO-F030R8 board. Flash via ST-Link or drag-and-drop to the NUCLEO mass storage device.

For Arduino Pro Micro: flash `anyio/arduino/firmware/gpio/gpio.ino` via Arduino IDE.

## Changelog (2026-04-07)

**Python 3 rewrite — 10 bugs fixed:**

- `adaptors.py`: Added missing `import time`; fixed bytes/str termset comparison
- `protocol.py`: `cleanup()` now closes serial port; read has retry limit; `_parse_valuech` handles int (Python 3 bytes indexing)
- `rtk/GPIO.py`: `s.databits` → `s.bytesize` (was silently ignored)
- `console/GPIO.py`, `gui/GPIO.py`, `net/GPIO.py`: Fixed to relative imports for Python 3
- `gui/GPIOClient.py`, `net/GPIOClient.py`: `INPUT`/`OUTPUT` → `IN`/`OUT`; added missing `self` and `channel` to `setup()`
- `net/GPIO.py`: `setup()` and `setmode()` had swapped signatures
- `ports_unix.py`: Narrowed scan from `/dev/tty*` (hundreds of matches) to `/dev/ttyUSB*` + `/dev/ttyACM*`
- `portscan.py`: Auto-detect single device without interactive prompt; cache validates device existence
- `testSerial.py`: `raw_input` → `input()`

## License

See [LICENSE](LICENSE) file.
