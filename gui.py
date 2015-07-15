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
		self.values = {}
		self.pre = {}
		self.decowin = DecoClass(file)
	def update(self, valuelist):
		print('update valuelist')
		print(valuelist)
		for (i, v) in valuelist:
			try:
				prevalue = self.pre[i]
			except:
				prevalue = None
			self.decowin.insertLine(i, v, prevalue)
			self.pre[i] = v
	def refresh(self, events):
		try:
			regstr = gdb.execute(self.cmd, False, True)
		except:
			regstr = 'Exception occurred'
		vlist = self.parse(regstr)
		self.update(vlist)
		self.decowin.refresh()
	def parse(self, regstr):
		vlist = []
		for line in regstr.split('\n'):
			if len(line.strip()) == 0:
				continue
			vlist.append((line.split()[0], line))
		return vlist

class DecoWindow:
	def __init__(self, filename):
		self.filename = filename
		self.file = None
	def insertLine(self, i, v, prev):
		print("call insert line:%s"%i)
		if self.file == None:
			self.file = open(self.filename, 'w')
		if v == prev:
			print(v , file=self.file)
		else:
			print('@@' + v, file=self.file)
		self.file.flush()
	def refresh(self):
		print("call refresh")
		if self.file == None:
			self.file = open(self.filename, 'w')
		self.file.close()
		self.file = None

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
			vlist = self.parse(index, regstr)
			print('call update')
			self.update(vlist)
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
		gdb.Command.__init__(self, "lx-gui", gdb.COMMAND_DATA, gdb.COMPLETE_SYMBOL, True)
	def invoke (self, arg, from_tty):
		if (arg != "Stop" and arg != "stop" ):
			#regw = CmdWindow('/tmp/regw', 'info reg', RegDecoWindow)
			#btw = CmdWindow('/tmp/btw', 'bt', RegDecoWindow)
			watchw = WatchWindow('/tmp/watchw', '', RegDecoWindow)
			#gdb.events.stop.connect(regw.refresh)
			#gdb.events.stop.connect(btw.refresh)
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

class CurrentThread(gdb.Command):
	"""Enables handlers to send program data to specially named fifo pipes on program break"""

	def __init__ (self):
		gdb.Command.__init__(self, "current", gdb.COMMAND_DATA, gdb.COMPLETE_SYMBOL, True)
	def invoke (self, arg, from_tty):
		rsp = getVar('$rsp')
		# print("rsp is 0x%x" % rsp)
		stack = rsp & ~ 0x1fff
		# print("stack is 0x%x" % stack)
		stacktop = stack - 0x2000
		# gdb.execute('p * (struct thread_info * ) 0x%x' % stack)
		current=getVar('((struct thread_info * ) 0x%x)->task' % stacktop)
		# print("task is 0x%x" % current)
		print("set $current to 0x%x (struct task_struct *)" % current)
		gdb.execute('set $current = (struct task_struct *) 0x%x' % current, False, True)
		if current != 0:
			print('The task name is:')
			gdb.execute('p $current->comm')

CurrentThread()
