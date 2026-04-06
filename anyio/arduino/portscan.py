# portscan.py  22/04/2014  D.J.Whale
# Updated 2026-04-07: auto-detect single device, Python 3 compat
#
# Find a serial port for the Arduino board.
# Supports: cached name, auto-detect (single device), interactive scan.

import time
import sys
import os

# CONFIGURATION ========================================================

CACHE_NAME = "portscan.cache"
DRIVER_UNLOAD_TIME = 2
DRIVER_LOAD_TIME = 4

def message(msg):
  print(msg)

ask = input


# PLATFORM =============================================================

if os.name == 'nt':
    from . import ports_win32 as ports
elif os.name == 'posix':
    from . import ports_unix as ports
else:
    raise ImportError("No port lister available for:" + os.name)


# HELPERS ==============================================================

def getYesNo(msg):
  answer = ask(msg + " (Y/N) ")
  return answer.strip().upper() in ('YES', 'Y')

def getAdded(before, after):
  after = list(after)
  for b in before:
    try:
      after.remove(b)
    except ValueError:
      pass
  return after


# AUTO-DETECT ==========================================================

def autoDetect():
  """Try to auto-detect a single serial device without user interaction."""
  devices = ports.scan()
  if len(devices) == 1:
    dev = devices[0]
    message("Auto-detected: " + dev)
    return dev
  return None


# INTERACTIVE SCAN =====================================================

def scan():
  """Scan devices by asking user to unplug/replug."""
  message("Scanning for serial ports")
  while True:
    ask("remove device, then press ENTER")
    message("scanning...")
    time.sleep(DRIVER_UNLOAD_TIME)
    before = ports.scan()
    message("found " + str(len(before)) + " devices")

    ask("plug in device, then press ENTER")
    message("scanning...")
    time.sleep(DRIVER_LOAD_TIME)
    after = ports.scan()
    message("found " + str(len(after)) + " devices")

    added = getAdded(before, after)

    if len(added) == 0:
      message("no new devices detected")
      if getYesNo("Try again?"):
        continue
      return None
    elif len(added) > 1:
      while True:
        message("more than one new device found")
        for i in range(len(added)):
          message(str(i + 1) + ":" + added[i])
        a = ask("which device do you want to try? ")
        try:
          a = int(a)
          if 1 <= a <= len(added):
            return added[a - 1]
          message("out of range, try again")
        except ValueError:
          pass
    else:
      dev = added[0]
      message("found 1 new device: " + dev)
      return dev


# CACHE ================================================================

def remember(device):
  with open(CACHE_NAME, "w") as f:
    f.write(device + "\n")

def forget():
  try:
    os.remove(CACHE_NAME)
  except OSError:
    pass

def getName():
  try:
    with open(CACHE_NAME, "r") as f:
      name = f.readline().strip()
      if name and os.path.exists(name):
        return name
      return None
  except (IOError, OSError):
    return None


# FIND =================================================================

def find():
  dev = autoDetect()
  if dev is not None:
    remember(dev)
    return dev
  dev = scan()
  if dev is not None:
    remember(dev)
  return dev


# MAIN =================================================================

def main():
  message("*" * 60)
  message("SERIAL PORT SCANNER")
  message("*" * 60)

  n = getName()
  if n is None:
    message("No cached port")
  else:
    message("Cached: " + n)
    message("forgetting...")
    forget()

  d = find()
  if d is None:
    message("nothing found")
  else:
    message("found device: " + d)

if __name__ == "__main__":
  main()

# END
