import time
from .keyboard import Keyboard

class DuckyInterpreter:
    def __init__(self, delay=0.02):
        self.kbd = Keyboard(delay)
        self.default_delay = 0
        self.last_action = None

    def sleep_ms(self, ms):
        time.sleep(ms / 1000)

    def run_line(self, line):
        line = line.strip()
        if not line or line.startswith("REM"):
            return

        parts = line.split()
        cmd = parts[0].upper()
        args = parts[1:]

        # DEFAULT DELAY
        if cmd in ("DEFAULT_DELAY", "DEFAULTDELAY"):
            self.default_delay = int(args[0])

        elif cmd == "DELAY":
            self.sleep_ms(int(args[0]))

        elif cmd == "PAUSE":
            time.sleep(float(args[0]))

        elif cmd == "STRING":
            text = line[len("STRING "):]
            self.kbd.type(text)
            self.last_action = ("STRING", text)

        elif cmd == "STRING_DELAY":
            delay = int(args[0])
            text = line.split(" ", 2)[2]
            for c in text:
                self.kbd.type(c)
                self.sleep_ms(delay)
            self.last_action = ("STRING", text)

        elif cmd == "REPEAT":
            count = int(args[0])
            if self.last_action:
                for _ in range(count):
                    if self.last_action[0] == "STRING":
                        self.kbd.type(self.last_action[1])

        elif cmd == "HOLD":
            self.kbd.hold(*args)

        elif cmd == "RELEASE":
            self.kbd.release()

        elif cmd in ("ENTER", "TAB", "SPACE", "ESC"):
            self.kbd.press(cmd)
            self.last_action = ("PRESS", cmd)

        elif cmd in ("CTRL", "ALT", "SHIFT", "GUI"):
            combo = [cmd] + args
            self.kbd.press(*combo)
            self.last_action = ("PRESS", combo)

        else:
            raise ValueError(f"Unsupported Ducky command: {cmd}")

        if self.default_delay:
            self.sleep_ms(self.default_delay)

    def run_script(self, text):
        for line in text.splitlines():
            self.run_line(line)

    def run_file(self, path):
        with open(path) as f:
            for line in f:
                self.run_line(line)

    def close(self):
        self.kbd.close()
