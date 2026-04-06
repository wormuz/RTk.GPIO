# anyio/protocol.py  20/04/2014  D.J.Whale
# Updated 2026-04-07: Python 3 fixes, cleanup closes wire, read timeout

# Eventually there will be sub modules to the protocol
# to include I2C, SPI, Uart, PWM, code load, and other stuff.
# For now, it only supports the GPIO module and it is loaded
# as the default context


def trace(msg):
  print(msg)

def error(msg):
  trace("error:" + str(msg))

IN  = 0
OUT = 1

GPIO_MODE_INPUT  = "I"
GPIO_MODE_OUTPUT = "O"

GPIO_READ       = "?"
GPIO_VALUE_HIGH = "1"
GPIO_VALUE_LOW  = "0"

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

def _parse_valuech(ch):
  if isinstance(ch, int):
    ch = chr(ch)
  if ch == GPIO_VALUE_LOW:
    return False
  if ch == GPIO_VALUE_HIGH:
    return True
  error("Unknown value ch:" + repr(ch))
  return False


# CLIENT ===============================================================
# Client will be constructed like: g = GPIOClient(Serial("/dev/ttyAMC0"))
# Client will be called via an interface just like RPi.GPIO

class GPIOClient:
  """ The GPIO command set
      Assumes the wire protocol is already in the GPIO mode.
      As we only support the GPIO module at the moment,
      that's a simple assumption to make.
  """
  IN = 0
  OUT = 1
  DEBUG = False

  def trace(self, msg):
    if self.DEBUG:
      trace(msg)

  def __init__(self, wire, debug=False):
    self.wire = wire
    self.DEBUG = debug

  def setmode(self, mode):
    # BCM or BOARD, only for compatibility with RPi.GPIO
    pass

  def setup(self, channel, mode):
    pinch = _pinch(channel)
    modech = _modech(mode)
    self._write(pinch + modech)

  def input(self, channel):
    pinch = _pinch(channel)
    self._write(pinch + GPIO_READ + "\n")
    retries = 0
    while retries < 10:
      v = self._read(3, termset="\r\n")
      if len(v) >= 2:
        break
      self.trace("retrying read (%d)" % retries)
      retries += 1

    if len(v) < 2:
      error("No response for pin %d after %d retries" % (channel, retries))
      return False

    self.trace("input read back:" + repr(v) + " len:" + str(len(v)))
    # Response is bytes on Python 3: b'<pin><value>\r\n'
    valuech = v[1]
    return _parse_valuech(valuech)

  def output(self, channel, value):
    ch = _pinch(channel)
    v = _valuech(value)
    self._write(ch + v)

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

  def _read(self, *args, **kwargs):
    self.trace("read")
    return self.wire.read(*args, **kwargs)

  def _close(self):
    self.trace("close")
    self.wire.close()


# END
