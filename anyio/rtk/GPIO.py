# anyio/rtk/GPIO.py  2014  D.J.Whale / Ryan Walmsley
# Updated 2026-04-07: Python 3 fixes, correct baud, bytesize fix
#
# RTk.GPIO board serial-based GPIO link

# CONFIGURATION ========================================================

DEBUG = False

MIN_PIN = 0
MAX_PIN = 16

IN      = 0
OUT     = 1
BCM     = 0
BOARD   = 1
HIGH    = 1
LOW     = 0


# OS INTERFACE =========================================================

from .. import protocol
from .. import adaptors
from . import portscan

import serial


# STATIC REDIRECTORS ===================================================

# Find out if there is a pre-cached port name.
# If not, try and find a port by using the portscanner

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

s.close()
s.port = PORT
s.open()


instance = protocol.GPIOClient(adaptors.SerialAdaptor(s), DEBUG)

def setmode(mode):
  instance.setmode(mode)

def setup(channel, mode):
  instance.setup(channel, mode)

def input(channel):
  return instance.input(channel)

def output(channel, value):
  instance.output(channel, value)

def cleanup():
  instance.cleanup()

# END
