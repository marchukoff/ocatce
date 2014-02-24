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


DELIMITER_1 = ","
DELIMITER_2 = ">"


def getboolean(value):
    #['yes', 'on', '1', 'no', 'off', '0']
    if value is None:
        return False
    elif value.lower() in ['yes', 'on', '1']:
        return True
    else:
        return False

class Config(object):
    '''
    classdocs
    '''


    def __init__(self, *ignored, append, bad_dirs, bad_files, file_list,
                 order, replacements, source, source_prefix, target,
                 target_prefix, msg=None):
        '''
        Constructor
        '''
        self.append = append
        self.bad_dirs = bad_dirs
        self.bad_files = bad_files
        self.file_list = file_list
        self.order = order
        self.replacements = replacements
        self.source = source
        self.source_prefix = source_prefix
        self.target = target
        self.target_prefix = target_prefix
        self.msg = msg


    def __str__(self):
        options = ('append', 'bad_dirs', 'bad_files', 'file_list', 'order',
                   'replacements', 'source', 'source_prefix', 'target',
                   'target_prefix')
        values = (self.append, self.bad_dirs, self.bad_files, self.file_list,
                  self.order, self.replacements, self.source,
                  self.source_prefix, self.target, self.target_prefix)
        return '\n'.join(sorted(['{0}: {1}'.format(k, v)
                                 for (k, v) in zip(options, values)]))


    @property
    def msg(self):
        return self.__msg
    
    @msg.setter
    def msg(self, value):
        self.__msg = value


    @property
    def copy(self):
        return self.__copy
    
    @copy.setter
    def copy(self, value):
        self.__copy = value


    @property
    def append(self):
        return self.__append
    
    @append.setter
    def append(self, value):
        self.__append = getboolean(value)


    @property
    def bad_dirs(self):
        return self.__bad_dirs
    
    @bad_dirs.setter
    def bad_dirs(self, value):
        self.__bad_dirs = value.split(DELIMITER_1) or []


    @property
    def bad_files(self):
        return self.__bad_files
    
    @bad_files.setter
    def bad_files(self, value):
        self.__bad_files = value.split(DELIMITER_1) or []


    @property
    def order(self):
        return self.__order
    
    @order.setter
    def order(self, value):
        self.__order = value


    @property
    def replacements(self):
        return self.__replacements
    
    @replacements.setter
    def replacements(self, value):
        if DELIMITER_2 not in value:
            self.__replacements = []
        else:
            self.__replacements = [tuple(i.split(DELIMITER_2))
                               for i in value.split(DELIMITER_1)]


    @property
    def source(self):
        return self.__source
    
    @source.setter
    def source(self, value):
        self.__source = os.path.normpath(value)


    @property
    def source_prefix(self):
        return self.__source_prefix
    
    @source_prefix.setter
    def source_prefix(self, value):
        self.__source_prefix = value


    @property
    def target(self):
        return self.__target
    
    @target.setter
    def target(self, value):
        self.__target = os.path.normpath(value)


    @property
    def target_prefix(self):
        return self.__target_prefix
    
    @target_prefix.setter
    def target_prefix(self, value):
        self.__target_prefix = value


    @property
    def file_list(self):
        return self.__file_list
    
    @file_list.setter
    def file_list(self, value):
        if value is not None:
            self.__file_list = os.path.normpath(value)
        else:
            self.__file_list = None
