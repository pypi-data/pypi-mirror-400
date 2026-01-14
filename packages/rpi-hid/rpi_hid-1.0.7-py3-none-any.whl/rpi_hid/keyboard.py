from .device import HIDDevice
from .keycodes import KEY, MOD, SHIFTED
from .utils import pause
import time

class Keyboard:
    def __init__(self, delay=0.02):
        self.dev = HIDDevice(delay)

    def type(self, text, pause_after=0.05):
        for ch in text:
            if ch not in KEY:
                continue

            val = KEY[ch]

            # Symbol requiring SHIFT
            if isinstance(val, tuple):
                modifier, key = val
                self.dev.send(modifier, key)

            # Uppercase letter
            elif ch.isupper():
                self.dev.send(MOD["SHIFT"], KEY[ch.lower()])

            # Normal key
            else:
                self.dev.send(0, val)

        time.sleep(pause_after)

    def press(self, *keys):
        modifier = 0
        main_key = None

        for k in keys:
            if k.upper() in MOD:
                modifier |= MOD[k.upper()]
            elif len(k) == 1 and k.lower() in KEY:
                main_key = KEY[k.lower()]
            elif k.upper() in KEY:
                main_key = KEY[k.upper()]

        if main_key is None:
            return

        self.dev.send(modifier, main_key)

    def spamText(self, text, n=10):
        for _ in range(n):
            self.type(text)

    def enter(self):
        self.dev.send(0, KEY["ENTER"])

    def winRun(self, command, open_delay=0.4, type_delay=0.2):
        self.press("GUI", "r")
        self.pause(open_delay)

        self.type(command, pause_after=type_delay)

        self.enter()
        self.pause(type_delay)

    def pause(self, seconds=0.5):
        time.sleep(seconds)

    def close(self):
        self.dev.close()
    
    def hold(self, *keys):
        modifier = 0
        main_key = None

        for k in keys:
            k = k.strip()
            if k.upper() in MOD:
                modifier |= MOD[k.upper()]
            elif len(k) == 1 and k.lower() in KEY:
                main_key = KEY[k.lower()]
            elif k.upper() in KEY:
                main_key = KEY[k.upper()]

        if main_key is None:
            raise ValueError("No valid key to hold")

        self.dev.fd.write(bytes([modifier, 0, main_key, 0, 0, 0, 0, 0]))

    def release(self):
        self.dev.fd.write(bytes([0] * 8))
