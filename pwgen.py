#!/usr/bin/env python
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
import math
import random
import string
 
def generate_password(length=16):
    def next_char_generator():
        alpha = string.ascii_lowercase #'abcdefghijklmnopqrstuvwxyz'
        digits = string.digits #'0123456789'
        prev = None
        while True:
            if not prev:
                prev = random.choice(alpha)
            else:
                prev = random.choice(alpha+digits)
            if prev.isalpha():
                prev = prev.upper() if random.choice([False, True]) else prev
            yield prev
 
    g = next_char_generator()
    return ''.join([next(g) for i in range(length)])
 
if __name__ == '__main__':
    print(generate_password(8))