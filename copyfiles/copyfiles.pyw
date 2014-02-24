#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
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
#
import os
import queue

from tkinter import *
from tkinter.scrolledtext import ScrolledText 

from cfm.manager import Manager

RATE = 2000
MSG_QUEUE = queue.Queue()
 
class UserInterface(object):
    '''GUI as is'''
    def __init__(self, parent):
        cfg = "".join(__file__.rsplit(".", 1)[:-1]) + ".ini"
        self.manager = Manager(MSG_QUEUE, cfg)
        '''Create the GUI'''
        self.parent = parent
        self.parent.title("CopyFiles")
        self.frame = Frame(parent)
        self.bar = Frame(parent)
        self.frame.pack(side=TOP, fill=BOTH, expand=YES)
        self.bar.pack(side=BOTTOM, fill=X, expand=YES)        
        self.make_widgets()            


    def make_widgets(self):
        '''Create all widgets'''
        self.project = StringVar()
        self.project.set("default")
        
        self.listbox=Listbox(self.frame, width=15,
                             selectmode=SINGLE)
        for i in self.manager.projects:
            self.listbox.insert(END,i)
        self.listbox.bind('<<ListboxSelect>>', self.select_project)
        self.listbox.pack(side=LEFT, fill=Y, expand=YES)
        
        self.console = ScrolledText(self.frame)
        self.console.pack(fill=BOTH, expand=YES)
        
        self.copy_flag = IntVar()
        self.copy_flag.set(0)
        
        self.check = Checkbutton(self.bar, text="Copy", command=self.copy,
                                 variable=self.copy_flag, onvalue=1,
                                 offvalue=0, state=DISABLED)
        self.check.deselect()
        self.check.pack(side=LEFT)
        
        self.buttons = []
        self.buttons.append(Button(self.bar, text="Clear",
                                   command=self.clear))
        self.buttons.append(Button(self.bar, text="Clean",
                                   command=self.clean))
        self.buttons.append(Button(self.bar, text="Print",
                                   command=self.report))
        self.buttons.append(Button(self.bar, text="Full Update",
                                   command=self.full_update))
        self.buttons.append(Button(self.bar, text="Update on List",
                                   command=self.list_update))
        for button in self.buttons:
            button.pack(side=RIGHT)
            button.config(state=DISABLED)

        self.__msg = MSG_QUEUE
        self.__echo()


    def report(self):
        for line in self.manager.report:
            self.__print(line, end='')


    def list_update(self):
        self.manager.list_update()        


    def full_update(self):
        self.manager.full_update()


    def clear(self):
        self.console.delete("1.0", END)


    def clean(self):
        os.remove(self.manager.project.order)
        if not os.access(self.manager.project.order, os.F_OK):
            self.buttons[1].config(state=DISABLED)
            self.buttons[2].config(state = DISABLED)                


    def select_project(self, *ignored):
        item = self.listbox.get(int(self.listbox.curselection()[0]))
        self.project.set(item)
        self.manager.select_project(item)
        self.__print(self.manager.project, cls=True)
        self.check.deselect()
        self.manager.copy = False
        for button in self.buttons:
            button.config(state = ACTIVE)
        self.check.config(state = ACTIVE)


    def copy(self):
        assert self.copy_flag.get() in [0, 1], "Wrong value in copy_flag"
        if self.copy_flag.get() == 1:
            self.check.select()
            self.manager.copy = True
            self.__print('I will copy file(s).')
        else:
            self.check.deselect()
            self.manager.copy = False
            self.__print('I will not copy file(s).')


    def __echo(self, *ignored):
        if self.manager.project is not None:
            if os.access(self.manager.project.order, os.F_OK):
                self.buttons[1].config(state = ACTIVE)
                self.buttons[2].config(state = ACTIVE)
            else:
                self.buttons[1].config(state=DISABLED)
                self.buttons[2].config(state = DISABLED)                
        while not self.__msg.empty():
            self.__print(self.__msg.get())
        self.frame.after(RATE, self.__echo)


    def __print(self, *args, **kargs):
        sep = kargs.pop("sep", " ")
        end = kargs.pop("end", "\n")
        cls = kargs.pop("cls", False)
        if kargs: raise TypeError("extra keywords {0}".format(kargs))
        output, first = "", True
        for arg in args:
            output += ("" if first else sep) + str(arg)
            first = False
        if cls:
            self.clear()
        self.console.insert(END, output + end)
        self.console.see(END)


if __name__ == "__main__":
    window = Tk()
    application = UserInterface(window)
    window.resizable(0,0)    
    window.mainloop()
