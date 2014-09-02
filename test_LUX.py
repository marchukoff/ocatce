# -*- coding: utf-8 -*-

import logging
import os
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
fh = logging.FileHandler('_'.join((os.path.splitext(__file__)[1], "log.txt")))
fh.setLevel(logging.WARNING)
fh.setFormatter(formatter)
logger.addHandler(fh)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)


class TestLux:
    def __init__(self):
        self.device = MonkeyRunner.waitForConnection()
        self.device.wake()
        self.device.shell('logcat -c')  # Clear logs buffer
        self.x = int(self.device.getProperty("display.width"))
        self.y = int(self.device.getProperty("display.height"))


    def allApps(self):
        d =50
        self.device.press("KEYCODE_HOME", MonkeyDevice.DOWN_AND_UP)
        MonkeyRunner.sleep(1.0)
        self.device.touch(self.x-d, self.y//2, "DOWN_AND_UP")
        MonkeyRunner.sleep(1.0)


    def swipeLeft(self, times=1):
        d = 100
        for i in range(times):
            self.device.drag((self.x-d, self.y//2), (d ,self.y//2), 1.0)
        MonkeyRunner.sleep(1.0)


    def swipeRight(self, times=1):
        d = 100
        for i in range(times):
            self.device.drag((d, self.y//2), (self.x-d ,self.y//2), 1.0)
        MonkeyRunner.sleep(1.0)


    def smokeTestAllApps(self):
        nx = 70
        mx = 130
        ny = 200
        my = 100
        self.allApps()
        self.swipeRight(5)
        for zz in range(5):
            for yy in range(3):
                for xx in range(6):
                    logger.info("Smoke Test %s_%s_%s" % (zz, xx, yy))
                    self.device.shell("logcat -c")
                    self.device.touch(nx+xx*mx, ny+yy*my, "DOWN_AND_UP")
                    MonkeyRunner.sleep(6.0)

                    msg = self.device.shell("logcat -d")
                    msg = "None" if msg is None else msg.encode("utf-8")
                    f = open("log_%s_%s_%s.txt" % (zz, xx, yy), 'w')
                    f.write(msg)
                    f.close()

                    image = self.device.takeSnapshot()
                    image.writeToFile("img_%s_%s_%s.png" % (zz, xx, yy), "png")
                    MonkeyRunner.sleep(1.0)
                    self.allApps()
            self.swipeLeft()
        MonkeyRunner.sleep(1.0)


def main():
    a = TestLux()
    a.smokeTestAllApps()
    a.swipeLeft() # TODO: Работает?
    #a.device.touch(50, 140, 'DOWN_AND_UP')
    #a.device.press("KEYCODE_MENU", MonkeyDevice.DOWN_AND_UP)


if __name__ == '__main__':
    main()
