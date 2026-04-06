# testSerial.py  22/04/2014  D.J.Whale
# Updated 2026-04-07: Python 3 compat
#
# Test that serial works.

import time

try:
  import serial  # pyserial
except ImportError:
  print("pyserial not installed")
  raise

# linux FTDI
SERIAL_PORT = "/dev/ttyUSB0"

# windows
#SERIAL_PORT = "COM4"

# linux Arduino (CDC)
#SERIAL_PORT = "/dev/ttyACM0"

# mac
#SERIAL_PORT = "/dev/cu.usbserial0"


def main():
  mode = int(input("1:send 2:receive "))

  if mode == 1:
    i = 0
    while True:
      print("sending...")
      s.write(("hello world " + str(i) + "\r\n").encode('ascii'))
      print("sent " + str(i))
      time.sleep(0.5)
      i += 1
  else:
    while True:
      print("receiving...")
      m = s.read(100)
      print("received:" + repr(m))

try:
  s = serial.Serial(SERIAL_PORT)
  main()

finally:
  print("closing...")
  s.close()
  print("closed")

# END
