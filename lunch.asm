; Copyright (c) 2014 Eugene Marchukov
; 
; This program is free software: you can redistribute it and/or modify
; it under the terms of the GNU General Public License as published by
; the Free Software Foundation, either version 3 of the License, or
; (at your option) any later version.
; 
; This program is distributed in the hope that it will be useful,
; but WITHOUT ANY WARRANTY; without even the implied warranty of
; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
; GNU General Public License for more details.
; 
; You should have received a copy of the GNU General Public License
; along with this program.  If not, see <http://www.gnu.org/licenses/>.
;
include 'win32ax.inc'

    invoke LockWorkStation,0

exit:
    invoke ExitProcess,0

data import
    library kernel32,'KERNEL32.DLL',\
        user32,'USER32.DLL'

    import kernel32,\
        ExitProcess,'ExitProcess'

    import user32,\
        LockWorkStation, 'LockWorkStation'
end data
