# anyio/protocol.py  20/04/2014  D.J.Whale
# Updated 2026-04-07: Full RTk.GPIO v2 protocol, dual v1/v2 firmware support
#   - pull up/down/none (U/D/N)
#   - hardware SPI (~XX → YY)
#   - version query (V)
#   - board reset (R → OK for v2)
#   - 28 pins (GP0-GP27)
#   - auto-detect enhanced mode (v2) via R probe

import time


def trace(msg):
  print(msg)

def error(msg):
  trace("error:" + str(msg))

IN  = 0
OUT = 1

PULL_UP   =  1
PULL_DOWN =  0
PULL_NONE = -1

PIN_COUNT = 28

GPIO_MODE_INPUT  = "I"
GPIO_MODE_OUTPUT = "O"

GPIO_READ       = "?"
GPIO_VALUE_HIGH = "1"
GPIO_VALUE_LOW  = "0"

GPIO_PULL_UP    = "U"
GPIO_PULL_DOWN  = "D"
GPIO_PULL_NONE  = "N"

def _pinch(channel):
  return chr(channel + ord('a'))

def _valuech(value):
  if value is None or value == 0 or value is False:
    return GPIO_VALUE_LOW
  return GPIO_VALUE_HIGH

def _modech(mode):
  if mode is None or mode == IN:
    return GPIO_MODE_INPUT
  return GPIO_MODE_OUTPUT

def _pullch(pull):
  if pull == PULL_UP or pull == 1:
    return GPIO_PULL_UP
  elif pull == PULL_DOWN or pull == 0:
    return GPIO_PULL_DOWN
  return GPIO_PULL_NONE

def _parse_valuech(ch):
  if isinstance(ch, int):
    ch = chr(ch)
  if ch == GPIO_VALUE_LOW:
    return False
  if ch == GPIO_VALUE_HIGH:
    return True
  error("Unknown value ch:" + repr(ch))
  return False

def _nibble_to_hex(n):
  return "0123456789ABCDEF"[n & 0xF]

def _hex_to_nibble(ch):
  if isinstance(ch, int):
    ch = chr(ch)
  if '0' <= ch <= '9':
    return ord(ch) - ord('0')
  if 'A' <= ch <= 'F':
    return ord(ch) - ord('A') + 10
  if 'a' <= ch <= 'f':
    return ord(ch) - ord('a') + 10
  return 0


# CLIENT ===============================================================

class GPIOClient:
  """Full RTk.GPIO protocol client.

  Supports v1 (2016) and v2 (2022+) firmware with auto-detection.
  v2 features: R(reset→OK), no \\r\\n on read, HW SPI.
  v1 features: read returns pin+value+\\r\\n, no R/SPI.

  28 pins (GP0-GP27). Pull up/down/none. Version query.
  """
  IN = 0
  OUT = 1
  PULL_UP   =  1
  PULL_DOWN =  0
  PULL_NONE = -1
  PIN_COUNT = 28
  DEBUG = False

  def trace(self, msg):
    if self.DEBUG:
      trace(msg)

  def __init__(self, wire, debug=False):
    self.wire = wire
    self.DEBUG = debug
    self.enhanced = False  # v2 firmware detected
    self._probe_firmware()

  def _probe_firmware(self):
    """Probe for v2 firmware by sending V (version query).

    V is safe on both v1 and v2:
    - v1: ignores unknown commands (no response or garbage)
    - v2: returns version string ending with \\n
    We detect v2 by looking for 'v2' in the response.
    R command is NOT safe for probing — v1 interprets 'R' as pin 17 latch.
    """
    # Drain any pending startup data
    time.sleep(0.3)
    try:
      self.wire.read(128, minsize=0, timeout=0.2)
    except Exception:
      pass

    try:
      self._write("V")
      time.sleep(0.3)
      resp = self._read(64, minsize=0, timeout=0.5)
      resp_str = resp.decode('ascii', errors='replace').strip() if resp else ""
      if 'v2' in resp_str.lower():
        self.enhanced = True
        self.trace("Firmware: v2 enhanced (%s)" % resp_str)
      else:
        self.enhanced = False
        self.trace("Firmware: v1 legacy")
    except Exception:
      self.enhanced = False
      self.trace("Firmware: v1 (probe failed, assuming legacy)")

    # Drain anything left over
    time.sleep(0.1)
    try:
      self.wire.read(128, minsize=0, timeout=0.1)
    except Exception:
      pass

  def setmode(self, mode):
    # BCM or BOARD, only for compatibility with RPi.GPIO
    pass

  def setup(self, channel, mode):
    pinch = _pinch(channel)
    modech = _modech(mode)
    self._write(pinch + modech)
    if not self.enhanced:
      # v1 firmware echoes acknowledgement — drain
      time.sleep(0.005)
      try:
        self.wire.serial.reset_input_buffer()
      except Exception:
        pass

  def input(self, channel):
    pinch = _pinch(channel)
    self._write(pinch + GPIO_READ)

    if self.enhanced:
      # v2 firmware: response is 2 bytes only: pin_char + value
      v = self._read(2, timeout=0.5)
    else:
      # v1 firmware echoes the command AND sends a response, both \n-terminated.
      # First line: echo (raw pin byte + \n)
      # Second line: response (pin_ascii + value + \r\n)
      try:
        self.wire.serial.timeout = 0.5
        _echo = self.wire.serial.readline()  # discard echo
        v = self.wire.serial.readline()      # actual response
      except Exception:
        v = b''

    self.trace("input read back:" + repr(v))

    if len(v) < 2:
      error("No response for pin %d" % channel)
      return False

    # Response: pin_char + value('0'/'1') + optional \r\n
    # Pin chars: 'a'(0) to 'a'+27 = '|'(27) — includes non-alpha {, |
    # Strategy: find '0' or '1' that is preceded by a pin-range char
    for i in range(len(v) - 1):
      val = v[i + 1] if isinstance(v[i + 1], int) else ord(v[i + 1])
      if val == ord('0') or val == ord('1'):
        return val == ord('1')

    error("No valid pin response in: %r" % v)
    return False

  def output(self, channel, value):
    ch = _pinch(channel)
    v = _valuech(value)
    self._write(ch + v)
    if not self.enhanced:
      time.sleep(0.005)
      try:
        self.wire.serial.reset_input_buffer()
      except Exception:
        pass

  def pull(self, channel, mode):
    """Set pull-up/pull-down/none on a pin.
    mode: PULL_UP (1), PULL_DOWN (0), PULL_NONE (-1)
    """
    ch = _pinch(channel)
    p = _pullch(mode)
    self._write(ch + p)
    if not self.enhanced:
      time.sleep(0.005)
      try:
        self.wire.serial.reset_input_buffer()
      except Exception:
        pass

  def spi_transfer(self, data):
    """Hardware SPI transfer (v2 only). Send one byte, receive one byte.
    Uses GP11=SCK, GP10=MOSI, GP9=MISO.
    Returns received byte, or None if not supported.
    """
    if not self.enhanced:
      error("spi_transfer requires v2 firmware")
      return None
    hi = _nibble_to_hex((data >> 4) & 0xF)
    lo = _nibble_to_hex(data & 0xF)
    self._write("~" + hi + lo)
    resp = self._read(2, timeout=0.5)
    if len(resp) >= 2:
      r_hi = _hex_to_nibble(resp[0])
      r_lo = _hex_to_nibble(resp[1])
      return (r_hi << 4) | r_lo
    return 0

  def version(self):
    """Query firmware version string."""
    self._write("V")
    time.sleep(0.1)
    resp = self._read(64, termset="\r\n", timeout=0.5)
    if resp:
      return resp.decode('ascii', errors='replace').strip()
    return ""

  def reset(self):
    """Soft reset the board. Returns True if v2 firmware acknowledged."""
    self._write("R")
    time.sleep(0.15)
    resp = self._read(2, timeout=0.3)
    if len(resp) >= 2:
      return resp[0:2] == b'OK'
    return False

  def cleanup(self):
    try:
      self._close()
    except Exception:
      pass

  # redirector to wrapped comms link
  def _open(self, *args, **kwargs):
    self.trace("open")
    self.wire.open(*args, **kwargs)

  def _write(self, *args, **kwargs):
    self.trace("write:" + repr(args))
    self.wire.write(*args, **kwargs)

  def _read(self, maxsize=1, **kwargs):
    self.trace("read(%d)" % maxsize)
    return self.wire.read(maxsize, **kwargs)

  def _close(self):
    self.trace("close")
    self.wire.close()


# END
