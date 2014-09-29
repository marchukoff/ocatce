#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Ngeniy
# 
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
import functools
import logging
import os
import re
import subprocess
import threading
import xml.dom.minidom
import xml.etree.ElementTree

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
fh = logging.FileHandler(''.join(__file__.rsplit('.', 1)[:-1]) + "_log.txt")
fh.setLevel(logging.ERROR)
fh.setFormatter(formatter)
logger.addHandler(fh)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)


def log(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        params = ", ".join(["{0!r}".format(a) for a in args] +
                 ["{0!s}={1!r}".format(k, v) for k, v in kwargs.items()])
        message = "called: {}({})".format(function.__name__, params)
        logger.debug(message)
    return wrapper

writer = functools.partial(open, mode="wt", encoding="cp1251")

BAT_UPDATE = """
@echo off
set SVN="c:\Program Files\TortoiseSVN\\bin\\"
set DST={dst}
start /d%SVN% TortoiseProc.exe /command:update /path:%DST%
exit
"""

BAT_CHECKOUT = """
@echo off
set SVN="c:\Program Files\TortoiseSVN\\bin\\"
set SRC={src}
set DST={dst}
start /d%SVN% TortoiseProc.exe /command:checkout /url:%URL% /path:%DST%
exit
"""

BAT_SD = """
@echo off
set TEMP=c:\Temp
set SRC={src}
set SD=E:
set DST=%SD%\sdfuse
set KEYS=/S /E /H /Y /exclude:noneed.txt
rem noneed.txt contains
rem .zip
rem .tar
set EXTRACT="c:\Program Files\\7-Zip\\7z.exe"
if not exist %SRC% goto bye
if not exist %SD% goto bye
title Formating...
echo y | format /Q /FS:FAT32 %SD%
cls
title Writing SDFUSE
md %DST%
xcopy %SRC%\*.* %DST% %KEYS%
echo
echo Insert a new SD for DATE and/or press any key to continue
pause
title Writing SDCARD
for %%I in (%SRC%\*.tar %SRC%\*.zip %SRC%\*.gz) do (
    md %TEMP%\SD
    %EXTRACT% x %%I -y -o%TEMP%\SD
    for %%J in (%TEMP%\SD\*.tar) do (
    %EXTRACT% x %%J -y -o%TEMP%\SD
    del /F /Q %%J
    )
    xcopy %TEMP%\SD\*.* %SD%\ %KEYS%
    rd /S /Q %TEMP%\SD
)
:bye
exit
"""

def bat(filename, content):
    filename = ".".join([filename, bat.__name__])
    if os.access(filename, os.F_OK):
        return
    with open(filename, 'wt') as fp:
        fp.write('REM File generated automatically - do not edit.\n')
        fp.write(content)

def update(prefix, path):
    bat("-".join([update.__name__, prefix]), BAT_UPDATE.format(dst=path))


def checkout(prefix, path):
    url = os.path.join('svn://backbsd/releases/trunk/lux2/JB/', os.path.basename(path))
    bat("-".join([checkout.__name__, prefix]), BAT_CHECKOUT.format(src=url, dst=os.getcwd()))


def write_sd(prefix, path):
    bat("-".join([write_sd.__name__, prefix]), BAT_SD.format(src=path))

def create_bat(arg):
    for a in arg:
        for f in [write_sd, update, checkout]:
            threading.Thread(target=f, args=(a, arg[a])).start()


def scan_svn_dir(path=os.getcwd()):
    dir_list = {}
    for a, b, c in os.walk(path):
        d = {os.path.basename(a): a for folder in b
             if folder.endswith(".svn")}
        dir_list.update(d)
    return dir_list


def xmlinfo(records):
    root = xml.etree.ElementTree.Element("items")
    for item in records:
        element = xml.etree.ElementTree.Element("item", name=item)
        for line in records[item].split('\n'):
            s = line.replace('\r', '').strip()
            if s:
                info = xml.etree.ElementTree.SubElement(element, "info")
                info.text = s
        root.append(element)
    tree = xml.etree.ElementTree.ElementTree(root)
    filename = ".".join([str(os.path.splitext(__file__)[0]), "xml"])
    with open(filename, "wt", encoding="UTF-8") as fp:
        fp.write(xml.dom.minidom.parseString(
            xml.etree.ElementTree.tostring(root, encoding="UTF-8")).toprettyxml())


def main():
    curdir = os.getcwd()
    data = {}
    workcopyes = scan_svn_dir()
    for name in workcopyes:
        os.chdir(workcopyes[name])
        s = subprocess.Popen("svn info", stdout=subprocess.PIPE)
        data[name] = s.communicate()[0].decode("cp1251")
    os.chdir(curdir)
    create_bat(workcopyes)
    xmlinfo(data)
    return


if __name__ == '__main__':
    main()
