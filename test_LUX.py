# -*- coding: utf-8 -*-

import logging
import os

from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def allApps(device):
    device.press("KEYCODE_BACK", MonkeyDevice.DOWN_AND_UP)
    device.press("KEYCODE_BACK", MonkeyDevice.DOWN_AND_UP)
    MonkeyRunner.sleep(0.5)
    device.press("KEYCODE_HOME", MonkeyDevice.DOWN_AND_UP)
    MonkeyRunner.sleep(1.0)
    device.touch(750, 240, MonkeyDevice.DOWN_AND_UP)
    MonkeyRunner.sleep(0.5)
    device.touch(170, 70, MonkeyDevice.DOWN_AND_UP) #All apps WIDGETS
    device.touch(70, 70, MonkeyDevice.DOWN_AND_UP) #All apps APPS
    device.touch(70, 70, MonkeyDevice.UP)
    MonkeyRunner.sleep(1.0)


def swipeLeft(device, times=1):
    for i in range(times):
        device.drag((500, 240), (200, 240), 0.1)
    MonkeyRunner.sleep(0.5)


def swipeRight(device, times=1):
    for i in range(times):
        device.drag((200,  240), (500 , 240), 0.1)
    MonkeyRunner.sleep(0.5)


def smokeTestAllApps(device):
    allApps(device)
    for i in range(5):# 5 screens
        for j in range(3): #3 series
            for k in range(6): #6 itemes
                logging.info("Smoke Test %s_%s_%s" % (i, k, j))
                # self.device.shell("logcat -c")
                x = 70+130*k
                y = 200+100*j
                if(i and k==0): swipeLeft(device)
                MonkeyRunner.sleep(2.5)
                device.touch(x, y, MonkeyDevice.DOWN_AND_UP)
                MonkeyRunner.sleep(5.0)

                # s = self.device.shell("logcat -d")
                # s = "None" if s is None else s.encode("utf-8")
                # f = open("log_%s_%s_%s.txt" % (i, k, j), 'w')
                # f.write(s)
                # f.close()

                image = device.takeSnapshot()
                image.writeToFile("img_%s%s%s.png" % (i, k, j), "png")
                allApps(device)
                swipeLeft(device, i)
    return True


def main():
    device = MonkeyRunner.waitForConnection()
    device.wake()
    device.shell('logcat -c')  # Clear logs buffer
    smokeTestAllApps(device)


if __name__ == '__main__':
    main()
