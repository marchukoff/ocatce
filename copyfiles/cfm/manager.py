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
import functools

from configparser import ConfigParser
from .project import Project

CODEPAGE = 'cp1251'
reader = functools.partial(open, mode="rt", encoding=CODEPAGE)
writer = functools.partial(open, mode="wt", encoding=CODEPAGE)


class ConfigError(BaseException):pass
class ConfigSectionError(ConfigError): pass
class ConfigOptionError(ConfigError): pass

def make_sample_config(file_name):
    config = ConfigParser()
    config['DEFAULT'] = {'append': 'no',
                         'bad_dirs': '.svn',
                         'order': 'CopyFiles.txt',
                         'source_prefix': 'StorageCard'}
    config['example'] = {'source': 'c:\\temp',
                         'target': 'd:\\temp',
                         'file_list': 'svn_log.txt',
                         'replacements': '\\NAND\\DATA>\\DATA,\\NAND\\NAND>\\NAND',
                         'bad_files': 'update.bin,update.cde,system.bin,NK.bin',
                         'bad_dirs': '.svn,My Books',
                         'target_prefix': 'NAND'}
    with open(file_name, 'w') as configfile:
        config.write(configfile)


class Manager(object):
    '''Main Logic'''
    def __init__(self, msg, config_file):
        '''
        msg must be an instance of queue.Queue()
        config_file must be a file
        '''
        self.__msg = msg
        self.__project = None
        assert os.access(config_file, os.F_OK), 'Cannot find the configuration file'
        self.__config_file = config_file
        self.__config = ConfigParser()
        try:
            fp = reader(self.__config_file)
        except IOError as e:
            make_sample_config(self.__config_file)
            raise e
        else:
            with fp:
                self.__config.read_file(fp)
        self.__projects = self.__config.sections()[:]


    @property
    def project(self):
        return self.__project
    
    @property
    def projects(self):
        return tuple(self.__projects)
    
    @property
    def report(self):
        try:
            fp = reader(self.project.order)
        except IOError as e:
            self.__msg.put(e)
            raise
        else:
            return fp.readlines()
        
    @property
    def copy(self):
        if self.project is not None:
            return self.project.copy
        else:
            return False

    @copy.setter
    def copy(self, value):
        if self.project is not None:
            self.project.copy = value


    def list_update(self):
        assert self.project is not None, 'Project was not selected'
        self.project.list_update()
    
    def full_update(self):
        assert self.project is not None, 'Project was not selected'
        self.project.full_update()


    def select_project(self, value):
        if value not in self.projects:
            raise ConfigSectionError
        options = ('append', 'bad_dirs', 'bad_files', 'order', 'file_list',
                   'replacements', 'source', 'source_prefix', 'target',
                   'target_prefix')
        cfg = {option: self.__config.get(value, option, fallback=None)
               for option in options}
        cfg['msg'] = self.__msg
        try:
            self.__project = Project(**cfg)
        except:
            raise ConfigOptionError()

    
#    def __load(self):
#        try:
#            fp = reader(self.__config_file)
#        except IOError as e:
#            make_sample_config(self.__config_file)
#            print(e)
#            raise
#        else:
#            with fp:
#                self.__config.read_file(fp)
#        self.__projects = self.__config.sections()[:]
    
#    def save(self):
#        try:
#            fp = writer("my_config.ini")
#        except IOError as e:
#            print(e)
#            raise
#        else:
#            with fp:
#                self.__config.write(fp)
