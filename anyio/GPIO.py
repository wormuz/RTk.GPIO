# anyio/GPIO.py  21/04/2014  D.J.Whale
# Updated 2026-04-07: Python 3 relative imports
#
# A configurable and flexible GPIO connector package
# with multiple driver implementations to choose from.

"""
This module should be imported like this:
  import anyio.GPIO as GPIO

then just use the GPIO.*() methods like any normal GPIO interface:
  GPIO.output(1, True)

Alternatively, you can import the driver module you want explicitly:
  import anyio.console.GPIO as GPIO
  GPIO.output(1, True)

By importing any of these driver modules, an instance of the
appropriate GPIOClient is automatically created with the default
configuration inside the appropriate driver GPIO.py file

If you want more than one instance of a GPIO connector, you can do it
by using the class module directly like this:

  import anyio.console.GPIOClient
  GPIO = GPIOClient.GPIOClient(params)

Then use the GPIO instance like any other module, it has all the
same methods as the static redirector modules.
  GPIO.output(1, True)
"""


# CONFIGURATION ========================================================
# 1. Select which driver you want the anyio.GPIO connected to

# Enable this if you want a console based GPIO simulator
#DRIVER = "console"

# Enable this if you want a Tkinter based GUI GPIO simulator
#DRIVER = "gui"

# Enable this if you want an arduino GPIO on a serial port
#DRIVER = "arduino"

# Enable this if you want a GPIO client the other end of a network
#DRIVER = "net"

# Enable this if using the Raspberry Pi via this redirector
#DRIVER = "RPi"

# Enable this if using the RTk.GPIO board
DRIVER = "RTk"

# 2. Inside the appropriate DRIVER.GPIO.py change the specific
# configuration for that driver, such as which port to open,
# how many pins it has, etc.


# STATIC REDIRECTOR ====================================================

if   DRIVER == "console":
  from .console.GPIO import *
elif DRIVER == "gui":
  from .gui.GPIO import *
elif DRIVER == "arduino":
  from .arduino.GPIO import *
elif DRIVER == "RTk":
  from .rtk.GPIO import *
elif DRIVER == "net":
  from .net.GPIO import *
elif DRIVER == "RPi":
  from RPi.GPIO import *
else:
  raise ValueError("Unknown driver:" + str(DRIVER))

# END
