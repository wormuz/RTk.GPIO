# anyio/net/GPIO.py  21/04/2014  D.J.Whale
# Updated 2026-04-07: Python 3 import, fixed swapped setup/setmode
#
# A network (remote) based GPIO connector

from .GPIOClient import *


# CONFIGURATION ========================================================


# STATIC REDIRECTORS ===================================================

instance = GPIOClient()

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
