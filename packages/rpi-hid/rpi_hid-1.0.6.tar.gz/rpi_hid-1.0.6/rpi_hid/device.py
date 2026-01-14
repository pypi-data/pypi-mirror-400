import time

HID_PATH = "/dev/hidg0"

class HIDDevice:
    def __init__(self, delay=0.02):
        self.delay = delay
        self.fd = open(HID_PATH, "wb", buffering=0)

    def send(self, modifier, key):
        self.fd.write(bytes([modifier,0,key,0,0,0,0,0]))
        time.sleep(self.delay)
        self.fd.write(bytes([0]*8))
        time.sleep(self.delay)

    def close(self):
        self.fd.close()
