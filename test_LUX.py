# -*- coding: utf-8 -*-

import logging
import os

from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class TestLux:
    def __init__(self):
        self.device = MonkeyRunner.waitForConnection()
        #self.device.touch(70, 70, MonkeyDevice.DOWN_AND_UP) #All apps APPS
        #self.device.touch(170, 70, MonkeyDevice.DOWN_AND_UP) #All apps WIDGETS
        self.device.wake()
        self.device.shell('logcat -c')  # Clear logs buffer


    def allApps(self):
        self.device.press("KEYCODE_BACK", MonkeyDevice.DOWN_AND_UP)
        self.device.press("KEYCODE_BACK", MonkeyDevice.DOWN_AND_UP)
        MonkeyRunner.sleep(0.5)
        self.device.press("KEYCODE_HOME", MonkeyDevice.DOWN_AND_UP)
        MonkeyRunner.sleep(1.0)
        self.device.touch(750, 240, MonkeyDevice.DOWN_AND_UP)
        MonkeyRunner.sleep(0.5)
        self.device.touch(170, 70, MonkeyDevice.DOWN_AND_UP) #All apps WIDGETS
        self.device.touch(70, 70, MonkeyDevice.DOWN_AND_UP) #All apps APPS
        self.device.touch(70, 70, MonkeyDevice.UP)
        MonkeyRunner.sleep(1.0)


    def swipeLeft(self, times=1):
        for i in range(times):
            self.device.drag((500, 240), (200, 240), 0.1)
        MonkeyRunner.sleep(0.5)


    def swipeRight(self, times=1):
        for i in range(times):
            self.device.drag((200,  240), (500 , 240), 0.1)
        MonkeyRunner.sleep(0.5)


    def smokeTestAllApps(self):
        self.allApps()
        for i in range(3):# 5 screens
            for j in range(1): #3 series
                for k in range(2): #6 itemes
                    logging.info("Smoke Test %s_%s_%s" % (i, k, j))
                    # self.device.shell("logcat -c")
                    x = 70+130*k
                    y = 200+100*j
                    logging.info("x=%s, y=%s, z=%s" % (k, j, i))
                    if(i and k==0): self.swipeLeft()
                    MonkeyRunner.sleep(2.5)
                    self.device.touch(x, y, MonkeyDevice.DOWN_AND_UP)
                    MonkeyRunner.sleep(5.0)

                    # s = self.device.shell("logcat -d")
                    # s = "None" if s is None else s.encode("utf-8")
                    # f = open("log_%s_%s_%s.txt" % (i, k, j), 'w')
                    # f.write(s)
                    # f.close()

                    image = self.device.takeSnapshot()
                    image.writeToFile("img_%s%s%s.png" % (i, k, j), "png")
                    self.allApps()
                    self.swipeLeft(i)
        return True


def main():
    a = TestLux()
    a.smokeTestAllApps()


if __name__ == '__main__':
    main()
