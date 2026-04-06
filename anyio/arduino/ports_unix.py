# ports_unix.py  22/04/2014  D.J.Whale
#
# Get a list of ports on a unix system
# Note that the precise /dev/* filter depends on the platform

# SYSTEM AND VERSION VARIANCE ==========================================

# Linux: USB serial adapters and Arduino CDC devices
DEV_PATTERNS = ["/dev/ttyUSB*", "/dev/ttyACM*"]

# Mac: USB serial
MAC_PATTERNS = ["/dev/cu.usbserial*", "/dev/cu.usbmodem*", "/dev/tty.usbserial*", "/dev/tty.usbmodem*"]

import sys

# BODY =================================================================

import glob

def scan():
  """ scan devices that might be com ports """
  devices = []
  patterns = DEV_PATTERNS
  if sys.platform == 'darwin':
    patterns = patterns + MAC_PATTERNS
  for pattern in patterns:
    devices.extend(glob.glob(pattern))
  return sorted(devices)


# TEST HARNESS =========================================================
 
if __name__ == "__main__":
  d = scan()
  print(str(d)) 
    
# END
