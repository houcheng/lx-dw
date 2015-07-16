#
# gdb data window feature for Linux kernel debugging
#
#
# Authors:
#  Houcheng Lin <houcheng@gmail.com>
#
# This work is licensed under the terms of the GNU GPL version 2.
#

from __future__ import with_statement
from __future__ import print_function

import gdb


class CmdWindow:
    def __init__(self, file, cmd, DecoClass):
        self.cmd = cmd
        self.file = file
        self.decowin = DecoClass(file)
    def refresh(self, events):
        try:
            regstr = gdb.execute(self.cmd, False, True)
        except:
            regstr = 'Exception on instruction:%s' % cmd
        v = self.decowin.parse(regstr)
        self.decowin.update(v)
        self.decowin.refresh()

class DecoWindow:
    def __init__(self, filename):
        self.filename = filename
        self.file = None
        self.pre = {}
        self.pre2 = {}
    def insertLine(self, i, v, prev):
        if self.file == None:
            self.file = open(self.filename, 'w')
        if v == prev:
            print(v , file=self.file)
        else:
            print('@@' + v, file=self.file)
        self.file.flush()
    def update(self, valuelist):
        for (i, v) in valuelist:
            try:
                prevalue = self.pre[i]
            except:
                prevalue = None
            self.insertLine(i, v, prevalue)
            self.pre2[i] = v
    def parse(self, regstr):
        vlist = []
        for line in regstr.split('\n'):
            if len(line.strip()) == 0:
                continue
            vlist.append((line.split()[0], line))
        return vlist
    def refresh(self):
        if self.file == None:
            self.file = open(self.filename, 'w')
        self.file.close()
        self.file = None
        self.pre = self.pre2
        self.pre2 = {}


def findRegAnnotate(regstr):
    b = regstr.find('<')
    if b > 0:
        return regstr[b:regstr.find('>') + 1]
    b = regstr.find('[')
    if b > 0:
        return regstr[b:regstr.find(']') + 1]


class RegDecoWindow(DecoWindow):
    def __init__(self, filename):
        DecoWindow.__init__(self, filename)
    def insertLine(self, i, v, prev):
        if self.file == None:
            self.file = open(self.filename, 'w')
        ann = findRegAnnotate(v)
        if v == prev:
            prefix = '\r'
        else:
            prefix = '\r@@'
        if ann != None:
            output = prefix + i + '\t' + v.split()[1] + '///\t' + ann
        else:
            output = prefix + i + '\t' + v.split()[1]
        print(output, file=self.file)
        self.file.flush()

'''
  decorate bt output string
'''
class BtDecoWindow(DecoWindow):
    def __init__(self, filename):
        DecoWindow.__init__(self, filename)
    def parse(self, regstr):
        vlist = []
        lines = regstr.strip().split('\n')
        # reverse the index order
        index = len(lines)
        for line in lines:
            if len(line.strip()) == 0:
                continue
            if line.split()[0] == 'Exception':
                pass
            else:
                # remove first token
                line = line.replace(line.split()[0], '').lstrip()
                line = ('#%-3d' % index ) + line
            vlist.append((str(index), line))
            index = index -1
        return vlist


'''
  store watch variables
'''
global LxWatch
LxWatch = {}
LxWatch[1] = "p $lx_current().comm"
LxWatch[2] = "x/32x $rsp"
LxWatch[3] = "x/8i $rip"

'''
  Watch data window's decorator
'''
class WatchDecoWindow(DecoWindow):
    def __init__(self, filename):
        DecoWindow.__init__(self, filename)
    def parse(self, index, cmd, regstr):
        vlist = []
        vlist.append(('[%d]'%index, '[%d] '%index + cmd))
        cmd0 = cmd.split()[0]
        lineno = 0
        for line in regstr.split('\n'):
            if len(line.strip()) == 0:
                continue
            istr = '[%d](%d)' % (index, lineno)
            if cmd0 == 'p':
                vlist.append((istr, line.split('=')[1]))
            else:
                vlist.append((istr, line))
            lineno = lineno + 1
        return vlist

class WatchWindow(CmdWindow):
    def __init__(self, file, cmd, DecoClass):
        CmdWindow.__init__(self, file, cmd, DecoClass)
    def refresh(self, events):
        for index in LxWatch:
            cmd = LxWatch[index]
            try:
                regstr = gdb.execute(cmd, False, True)
            except:
                regstr = 'Exception on instruction:%s' % cmd
            v = self.decowin.parse(index, cmd, regstr)
            self.decowin.update(v)
        self.decowin.refresh()
    def parse(self, index, regstr):
        vlist = []
        for line in regstr.split('\n'):
            if len(line.strip()) == 0:
                continue
            vlist.append(('[%d]' % index + line.split()[0], line))
        return vlist

class LxGuiFUnction(gdb.Command):
    """Enable GDB data window feature.

lx-dw: to enable the data window feature, including reg/ bt and watch data windows.
    """
    def __init__ (self):
        gdb.Command.__init__(self, "lx-dw", gdb.COMMAND_DATA, gdb.COMPLETE_SYMBOL, True)
    def invoke (self, arg, from_tty):
        if arg == "off":
            try:
                gdb.events.stop.disconnect(self.regw.refresh)
                gdb.events.stop.disconnect(self.btw.refresh)
                gdb.events.stop.disconnect(self.watchw.refresh)
            except:
                pass
        else:
            self.regw = CmdWindow('/tmp/reg-dw', 'info reg', RegDecoWindow)
            self.btw = CmdWindow('/tmp/bt-dw', 'bt', BtDecoWindow)
            self.watchw = WatchWindow('/tmp/watch-dw', '', WatchDecoWindow)
            gdb.events.stop.connect(self.regw.refresh)
            gdb.events.stop.connect(self.btw.refresh)
            gdb.events.stop.connect(self.watchw.refresh)

LxGuiFUnction()

def findLxWatchSlot():
    i = 1
    while True:
        if not i in LxWatch:
            return i
        i = i +1

class LxAddFunction(gdb.Command):
    """Add gdb command into watch data window.

lx-add <gdb-command>: add gdb command into watch data window; the command would be
executed on every step or execution break and command results would be updated on
to watch data window."""

    def __init__ (self):
        gdb.Command.__init__(self, "lx-add", gdb.COMMAND_DATA, gdb.COMPLETE_SYMBOL, True)
    def invoke (self, arg, from_tty):
        index = findLxWatchSlot()
        LxWatch[index] = arg
        print(LxWatch)

LxAddFunction()

class LxDelFunction(gdb.Command):
    """Remove one expression into watch data window.

lx-del <id>: remove the gdb command from watch data window."""

    def __init__ (self):
        gdb.Command.__init__(self, "lx-del", gdb.COMMAND_DATA, gdb.COMPLETE_SYMBOL, True)
    def invoke (self, arg, from_tty):
        index = int(arg)
        del LxWatch[index]
        print(LxWatch)

LxDelFunction()
