# anyio/console/GPIOClient  22/04/2014  D.J.Whale
# Updated 2026-04-07: Python 3 fixes (thread import, input())
#
# A class based interface to the console GPIO simulator

import sys

try:
  import _thread as thread  # Python 3
except ImportError:
  import thread  # Python 2

# CONFIGURATION ========================================================

MIN_PIN = 0
MAX_PIN = 16
LABELS  = "0123456789ABCDEFGH"

IN      = 0
OUT     = 1
BCM     = 0
BOARD   = 1
HIGH    = 1
LOW     = 0

def trace(msg):
  print(str(msg))

def write(msg):
  print(str(msg))

def ask(msg=""):
  return input(msg)


# CLASS ================================================================

class GPIOClient:
  def __init__(self, server=False):
    self.pinmode = {}
    self.pinstate = {}
    self._serverRunning = False
    self._kbdThread = None
    if server:
      self.controlInputs(True)

  def setmode(self, mode):
    # BCM or BOARD
    pass  # nothing to do here for a simulation

  def setup(self, channel, mode):
    self.pinmode[channel] = mode

    if mode == IN:
      self.pinstate[channel] = HIGH
    elif mode == OUT:
      self.pinstate[channel] = LOW
      self._show()

  def input(self, channel):
    try:
      return self.pinstate[channel]
    except KeyError:
      return HIGH

  def output(self, channel, value):
    self.pinstate[channel] = self._pinValue(value)
    self._show()

  def cleanup(self):
    self.pinmode = {}
    self.pinstate = {}

  def _pinValue(self, v):
    if v is None or v is False or v == 0:
      return LOW
    return HIGH

  def _show(self):
    line = "PIN   "
    for p in range(MIN_PIN, MAX_PIN + 1):
      line += LABELS[p]
      if (p + 1) % 4 == 0:
        line += " "
    write(line)

    line = "MODE  "
    for p in range(MIN_PIN, MAX_PIN + 1):
      try:
        if self.pinmode[p] == IN:
          line += "I"
        elif self.pinmode[p] == OUT:
          line += "O"
        else:
          line += "?"
      except KeyError:
        line += "X"
      if (p + 1) % 4 == 0:
        line += " "
    write(line)

    line = "STATE "
    for p in range(MIN_PIN, MAX_PIN + 1):
      try:
        if self.pinstate[p] == 1:
          line += "1"
        elif self.pinstate[p] == 0:
          line += "0"
        else:
          trace("unknown[" + str(p) + "]:" + str(self.pinstate[p]))
          line += "?"
      except KeyError:
        line += "X"
      if (p + 1) % 4 == 0:
        line += " "
    write(line)
    write("")

  def changeInput(self, channel, value):
    if self.pinmode.get(channel) != IN:
      raise ValueError("Pin is not an input")
    self.pinstate[channel] = self._pinValue(value)


  # INPUT CONTROL ======================================================

  def controlInputs(self, flag):
    if flag and not self._serverRunning:
      self._startServer()
    elif not flag and self._serverRunning:
      self._stopServer()

  def _startServer(self):
    self._kbdThread = thread.start_new_thread(self._server, ())
    self._serverRunning = True

  def _stopServer(self):
    # thread.start_new_thread returns an ID, can't .stop() it
    self._serverRunning = False
    self._kbdThread = None

  def _parse_pinch(self, ch):
    # the index into LABELS is the channel number
    return LABELS.index(ch.upper())

  def _getcmd(self):
    while True:
      cmdstr = ask()
      cmdstr = cmdstr.strip()
      if len(cmdstr) >= 2:
        return cmdstr

  def _parsecmd(self, cmdstr):
    pinch   = cmdstr[0]
    valuech = cmdstr[1]
    channel = self._parse_pinch(pinch)
    return channel, valuech

  def _process(self, channel, valuech):
    if valuech == "I":
      self.setup(channel, IN)
    elif valuech == "O":
      self.setup(channel, OUT)
    elif valuech == "1":
      self.changeInput(channel, True)
    elif valuech == "0":
      self.changeInput(channel, False)

  def _server(self):
    while self._serverRunning:
      try:
        cmdstr = self._getcmd()
        channel, valuech = self._parsecmd(cmdstr)
        self._process(channel, valuech)
      except Exception as e:
        trace("server error: " + str(e))

# END
