# rpi-hid

Python USB HID Keyboard library for Raspberry Pi Zero / Zero 2 W.

## Install
sudo pip3 install .

## Example
from rpi_hid import Keyboard

kbd = Keyboard()
kbd.winRun("notepad")
kbd.type("Hello World")
kbd.close()

## DuckyScript Support
from rpi_hid import DuckyInterpreter

duck = DuckyInterpreter()
duck.run_script("""
GUI r
DELAY 300
STRING notepad
ENTER
""")
duck.close()
