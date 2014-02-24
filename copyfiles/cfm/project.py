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
from cfm.xerox import Xerox
from cfm.printer import Printer
from cfm.config import Config

class Project(Config):
    '''
    classdocs
    '''
    def __init__(self, *ignored, **kwargs):
        '''
        Constructor
        '''
        super().__init__(**kwargs)


    def __files(self):
        for root, dirs, files in os.walk(self.source):
            for d in dirs:
                if d in self.bad_dirs: dirs.remove(d) 
            for file_ in files:
                if file_ not in self.bad_files:
                    yield os.path.join(root, file_)


    def full_update(self):
        files = []
        orders = []
        for file_ in self.__files():
            t = file_.replace(self.source, self.target, 1)
            files.append((file_, os.path.normpath(t)))
            a = file_.replace(self.source, self.source_prefix, 1)
            b =  file_.replace(self.source, self.target_prefix, 1)
            for r in self.replacements:
                b = b.replace(r[0], r[1], 1)
            orders.append((os.path.normpath(a), os.path.normpath(b)))
        p = Printer()
        p.display = self.msg
        p.append = self.append
        p.paper = self.order
        p.data = orders
        p.start()
        if self.copy:
            files.append((os.path.abspath(self.order),
                          os.path.join(self.target,
                          os.path.basename(self.order))))
            x = Xerox()
            x.display = self.msg
            x.data = files
            x.start()


    def list_update(self):
        files = []
        orders = []
        if self.copy:
            files.append((os.path.abspath(self.order),
                          os.path.join(self.target, self.order)))
            x = Xerox()
            x.display = self.msg
            x.data = files
            x.start()
