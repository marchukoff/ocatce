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
import queue
import threading
from abc import abstractmethod

class MultifunctionDevice(threading.Thread):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        super().__init__() # threading.Thread.__init__(self)

    
    @property
    def data(self):
        return self.__data
    
    @data.setter
    def data(self, items):
        self.__data = [i for i in items]


    @property
    def display(self):
        return self.__display
    
    @display.setter
    def display(self, param=queue.Queue()):
        self.__display = param

    @abstractmethod
    def run(self):
        while self.data:
            self.display.put(self.data.pop())
        self.display.put('*** All done ***')

