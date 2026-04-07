# RTk.GPIO — USB GPIO for PC/Mac/Linux

A Python GPIO module that works on any platform. Plug in an RTk.GPIO board via USB and control **28 GPIO pins** from Python — same API as `RPi.GPIO`. Supports **PWM**, **pull-up/down**, **hardware SPI**, and **APA102 LEDs**.

Based on [anyio](https://github.com/whaleygeek/anyio) by David Whale (@whaleygeek), adapted for RTk.GPIO by Ryan Walmsley (@Ryanteck).

**Firmware v2.2** — custom compiled, PWM via raw TIM3 registers, dual v1/v2 auto-detect.

## Hardware

| Parameter | Value |
|-----------|-------|
| **MCU** | STM32F030C8T6 (Cortex-M0, 48MHz, 64KB flash) |
| **USB** | CH340G serial converter |
| **GPIO** | 28 pins (GP0–GP27) |
| **Baud** | 230400 |
| **PWM** | 6 pins via TIM3 (GP8, GP9, GP10, GP18, GP25, GP26) |
| **SPI** | Hardware SPI (GP9=MISO, GP10=MOSI, GP11=SCK) |
| **Crystal** | 12 MHz HSE (firmware uses HSI fallback) |

## Quick Start

```bash
pip install pyserial
```

```python
import sys; sys.path.insert(0, 'RTk.GPIO')
import anyio.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

# Digital I/O
GPIO.setup(4, GPIO.OUT)
GPIO.output(4, True)
GPIO.setup(5, GPIO.IN)
print(GPIO.input(5))

# Pull-up/down
GPIO.pull(8, GPIO.PULL_UP)

# PWM — tone generation, LED dimming
GPIO.pwm_start(9, 1000)    # 1 kHz on GP9
GPIO.pwm_duty(9, 128)      # 50% duty
GPIO.tone(9, 440, 1.0)     # A4 note, 1 second
GPIO.pwm_stop(9)

# Hardware SPI
GPIO.spi_transfer(0xA5)    # send byte, get response

# Info
print(GPIO.version())      # 'RTk.GPIO v2.2 2026-04-07'
print(GPIO.is_enhanced())  # True

GPIO.cleanup()
```

Auto-detect: single USB serial device found automatically. Multiple devices → interactive prompt. Port cached in `portscan.cache`.

## API Reference

### GPIO (RPi.GPIO compatible)

```python
GPIO.setmode(GPIO.BCM)          # required (no-op, for compatibility)
GPIO.setup(pin, GPIO.OUT)       # output mode
GPIO.setup(pin, GPIO.IN)        # input mode
GPIO.output(pin, True/False)    # write HIGH/LOW
val = GPIO.input(pin)           # read (True/False)
GPIO.pull(pin, GPIO.PULL_UP)    # pull-up (also PULL_DOWN, PULL_NONE)
GPIO.cleanup()                  # release all, close port
```

### PWM

```python
GPIO.pwm_start(pin, freq_hz)   # start PWM, 50% duty (20–65535 Hz)
GPIO.pwm_duty(pin, duty)       # set duty: 0–255 (int) or 0.0–1.0 (float)
GPIO.pwm_stop(pin)             # stop PWM, return to GPIO mode
GPIO.tone(pin, freq, duration) # play tone, auto-stop after duration (sec)
```

**PWM pins (TIM3):** GP8, GP9, GP10, GP18, GP25, GP26

### SPI / Info

```python
GPIO.spi_transfer(byte)        # HW SPI transfer, returns received byte
GPIO.version()                 # firmware version string
GPIO.reset()                   # soft reset all pins → True
GPIO.is_enhanced()             # True if v2+ firmware detected
```

## Serial Protocol

Pin char = `chr(pin + ord('a'))`: GP0=`a`, GP27=`|`. Commands:

| Command | Format | Response | Description |
|---------|--------|----------|-------------|
| Input | `eI` | — | GP4 input mode |
| Output | `eO` | — | GP4 output mode |
| Write | `e1` / `e0` | — | GP4 HIGH / LOW |
| Read | `e?` | `e1\r\n` | read GP4 |
| Pull | `eU`/`eD`/`eN` | — | pull up/down/none |
| PWM | `jW01F4` | `K` or `E` | GP9 PWM at 500Hz |
| PWM duty | `jP80` | — | GP9 duty 50% (0x80) |
| PWM stop | `jX` | — | stop PWM on GP9 |
| SPI | `~A5` | `XX` | transfer 0xA5 |
| Version | `V` | `RTk.GPIO v2.2...\r\n` | firmware version |
| Reset | `R` | `OK` | soft reset all |

## Pin Map

```
GP0 =PA1   GP7 =PF1   GP14=PA2   GP21=PB10
GP1 =PB12  GP8 =PB5*  GP15=PA3   GP22=PA11
GP2 =PB7   GP9 =PA6*  GP16=PB8   GP23=PB2
GP3 =PB6   GP10=PA7*  GP17=PB15  GP24=PB3
GP4 =PA8   GP11=PA5   GP18=PB1*  GP25=PB4*
GP5 =PA12  GP12=PF0   GP19=PA15  GP26=PB0*
GP6 =PA13  GP13=PA14  GP20=PB9   GP27=PB14

* = PWM capable (TIM3)
SPI: GP11=SCK, GP10=MOSI, GP9=MISO
SWD: GP6=SWDIO, GP13=SWCLK
I2C: GP2=SDA, GP3=SCL (hardware pull-ups)
```

## Drivers

| Driver | Import | Status |
|--------|--------|--------|
| **RTk.GPIO** (default) | `import anyio.GPIO as GPIO` | Full (28 pins, PWM, SPI) |
| **Arduino** | `import anyio.arduino.GPIO as GPIO` | GPIO only, 115200 baud |
| **Console** | `import anyio.console.GPIO as GPIO` | Simulator |
| **GUI** | `import anyio.gui.GPIO as GPIO` | Placeholder |
| **Network** | `import anyio.net.GPIO as GPIO` | Placeholder |

Dual firmware auto-detect: v2.2 (enhanced, PWM/SPI/Reset) vs v1 (legacy, GPIO only).

## Firmware

| Version | File | Features |
|---------|------|----------|
| **v2.2** (current) | [RTk.GPIO-FW](https://github.com/wormuz/RTk.GPIO-FW) | GPIO + PWM + SPI + Pull + Reset + Version |
| v1 (original) | `RTkGPIOV1_NUCLEO_F030R8.bin` | GPIO + Pull only |

### Flashing

Requires: ST-LINK V2 (with NRST), `openocd`, `arm-none-eabi-gcc` (for recompilation).

```bash
openocd -f interface/stlink.cfg -f target/stm32f0x.cfg \
  -c "reset_config srst_only connect_assert_srst" \
  -c "init" -c "reset halt" \
  -c "flash write_image erase firmware.bin 0x08000000" \
  -c "verify_image firmware.bin 0x08000000" \
  -c "reset run" -c "shutdown"
```

SWD header: 1=SWDIO, 2=SWCLK, 3=RST, 4=GND.

## Changelog

### v2.2 (2026-04-07)
- **PWM** via raw TIM3 registers (no mbed PwmOut — avoids TIM1/us_ticker conflict)
- 6 PWM pins: GP8, GP9, GP10, GP18, GP25, GP26
- Protocol: `W` (freq), `P` (duty), `X` (stop)
- Python: `pwm_start()`, `pwm_duty()`, `pwm_stop()`, `tone()`

### v2.1 (2026-04-07)
- Full v2 protocol: SPI (`~`), Reset (`R`→OK), Version (`V`), Pull (U/D/N)
- 28 GPIO pins (GP0–GP27)
- Dual v1/v2 firmware auto-detect via `R` probe
- Compiled from v1 mbed-dev base (HSI clock fallback for 12MHz board)

### v2.0-py3 (2026-04-07)
- Python 3 rewrite: 10 bugs fixed across all drivers
- Auto-detect single USB device, no interactive prompt needed

## License

See [LICENSE](LICENSE) file.
