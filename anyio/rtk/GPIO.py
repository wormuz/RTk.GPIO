# anyio/rtk/GPIO.py  2014  D.J.Whale / Ryan Walmsley
# Updated 2026-04-07: Python 3, full v2 protocol, 28 pins, dual v1/v2 auto-detect

# CONFIGURATION ========================================================

DEBUG = False

MIN_PIN = 0
MAX_PIN = 27  # GP0-GP27, 28 pins total

IN      = 0
OUT     = 1
BCM     = 0
BOARD   = 1
HIGH    = 1
LOW     = 0

PULL_UP   =  1
PULL_DOWN =  0
PULL_NONE = -1

# SPI pins (hardware, v2 only)
SPI_SCK  = 11
SPI_MOSI = 10
SPI_MISO = 9


# OS INTERFACE =========================================================

from .. import protocol
from .. import adaptors
from . import portscan

import serial
import time


# STATIC REDIRECTORS ===================================================

name = portscan.getName()
if name is not None:
  if DEBUG:
    print("Using port:" + name)
  PORT = name
else:
  name = portscan.find()
  if name is None:
    raise ValueError("No port selected, giving in")
  PORT = name
  print("Your RTk.GPIO board has been detected")
  print("Now running your program...")

BAUD = 230400


s = serial.Serial(PORT)
s.baudrate = BAUD
s.parity   = serial.PARITY_NONE
s.bytesize = serial.EIGHTBITS
s.stopbits = serial.STOPBITS_ONE
s.timeout  = 0.5

s.close()
s.port = PORT
s.open()
time.sleep(0.5)  # let MCU settle after serial open
s.reset_input_buffer()


instance = protocol.GPIOClient(adaptors.SerialAdaptor(s), DEBUG)

def setmode(mode):
  instance.setmode(mode)

def setup(channel, mode):
  instance.setup(channel, mode)

def input(channel):
  return instance.input(channel)

def output(channel, value):
  instance.output(channel, value)

def pull(channel, mode):
  """Set pull resistor. mode: PULL_UP (1), PULL_DOWN (0), PULL_NONE (-1)"""
  instance.pull(channel, mode)

def spi_transfer(data):
  """Hardware SPI byte transfer (v2 firmware only). Returns received byte."""
  return instance.spi_transfer(data)

def version():
  """Query firmware version string."""
  return instance.version()

def reset():
  """Soft-reset the board (v2 firmware returns True)."""
  return instance.reset()

def is_enhanced():
  """Returns True if v2 firmware detected."""
  return instance.enhanced

def cleanup():
  instance.cleanup()

# END
