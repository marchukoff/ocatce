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
import os
import errno
import shutil
from .mfd import MultifunctionDevice

class Xerox(MultifunctionDevice):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()


    def run(self):
        while self.data:
            src, dst = self.data.pop()
            self.display.put(src)
            # Copy File [BEGIN]
            try:
                shutil.copy2(src, dst)
            except IOError as e:
                if e.errno == errno.ENOENT:
                    path = os.path.dirname(dst)
                    os.makedirs(path, exist_ok=True)
                    shutil.copy2(src, dst)
            # Copy File [END]            
        self.display.put('*** All files has been copied ***')
