# -*- coding: utf-8 -*-
# Copyright (c) 2014 Eugene Marchukov
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import functools
from .mfd import MultifunctionDevice

CODEPAGE = 'cp1251'

class Printer(MultifunctionDevice):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
        self.__append = False
        self.__paper = sys.stdout


    @property
    def append(self):
        return self.__append

    @append.setter
    def append(self, v):
        self.__append = v


    @property
    def paper(self):
        return self.__paper

    @paper.setter
    def paper(self, p):
        if self.append:
            writer = functools.partial(open, mode="at", encoding=CODEPAGE)
        else:
            writer = functools.partial(open, mode="wt", encoding=CODEPAGE)
        self.__paper = writer(p)


    def run(self):
        while self.data:
            src, dst = self.data.pop()
            print(src, dst, sep=';', file=self.paper)
        self.__paper.close()
        self.display.put('*** CopyFile creation is done ***')
