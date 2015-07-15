from __future__ import with_statement
from __future__ import print_function
import gdb
import re, sys, binascii, struct, os
from array import *

def getVar(var):
    str = gdb.execute('p/x %s' % var, False, True)
    base = int(str.split('=')[1].strip().lstrip().replace('`', ''), 16)
    return base

'''
    1. redirect content to file with auto flush
    2. ordered list
    3. colored display difference
'''
class CmdWindow:
    def __init__(self, file, cmd, DecoClass):
        self.cmd = cmd
        self.file = file
        self.decowin = DecoClass(file)
    def refresh(self, events):
        try:
            regstr = gdb.execute(self.cmd, False, True)
        except:
            regstr = 'Exception occurred'
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
    if b>0:
        return regstr[b:regstr.find('>')+1]
    b = regstr.find('[')
    if b>0:
        return regstr[b:regstr.find(']')+1]


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
global LxWatch
LxWatch = {}
LxWatch[1] = "p $lx_current().comm"
LxWatch[2] = "x/32x $rsp"
LxWatch[3] = "x/8i $rip"

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
            istr = '[%d](%d)'%(index, lineno)
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
        print(LxWatch)
        for index in LxWatch:
            cmd = LxWatch[index]
            try:
                regstr = gdb.execute(cmd, False, True)
            except:
                regstr = 'Exception occurred'
            v = self.decowin.parse(index, cmd, regstr)
            self.decowin.update(v)
        self.decowin.refresh()
    def parse(self, index, regstr):
        vlist = []
        for line in regstr.split('\n'):
            if len(line.strip()) == 0:
                continue
            vlist.append(('[%d]'%index + line.split()[0], line))
        return vlist

class LxGuiFUnction(gdb.Command):
    """Enables handlers to send program data to specially named fifo pipes on program break"""
    def __init__ (self):
        gdb.Command.__init__(self, "lx-dw", gdb.COMMAND_DATA, gdb.COMPLETE_SYMBOL, True)
    def invoke (self, arg, from_tty):
        if (arg != "Stop" and arg != "stop" ):
            regw = CmdWindow('/tmp/reg-dw', 'info reg', RegDecoWindow)
            btw = CmdWindow('/tmp/bt-dw', 'bt', RegDecoWindow)
            watchw = WatchWindow('/tmp/watch-dw', '', WatchDecoWindow)
            gdb.events.stop.connect(regw.refresh)
            gdb.events.stop.connect(btw.refresh)
            gdb.events.stop.connect(watchw.refresh)
        else:
            try:
                gdb.events.stop.disconnect(FifoStopHandler)
                gdb.events.exited.disconnect(FifoRemover)
            except:
                pass
LxGuiFUnction()

def findLxWatchSlot():
    i = 1
    while True:
        if not i in LxWatch:
            return i
        i = i +1

class LxAddFunction(gdb.Command):
    def __init__ (self):
        gdb.Command.__init__(self, "lx-add", gdb.COMMAND_DATA, gdb.COMPLETE_SYMBOL, True)
    def invoke (self, arg, from_tty):
        # print(arg.split())
        index = findLxWatchSlot()
        LxWatch[index] = arg
        print(LxWatch)
LxAddFunction()

class LxDelFunction(gdb.Command):
    def __init__ (self):
        gdb.Command.__init__(self, "lx-del", gdb.COMMAND_DATA, gdb.COMPLETE_SYMBOL, True)
    def invoke (self, arg, from_tty):
        index = int(arg)
        del LxWatch[index]
        print(LxWatch)
LxDelFunction()
