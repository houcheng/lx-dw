import os, time, sys
import curses, time

global stdscr
stdscr = curses.initscr()
prevlen = 0
def update(filename):
    global prevlen
    fd = open(filename, 'r')
    count = 0
    stdscr.erase()
    try:
      for line in fd.readlines():
        if line.find('@@') >= 0:
            line = line.replace('@@', '')
            for oline in line.split('///'):
                stdscr.addstr(count, 0, oline, curses.A_REVERSE)
                count = count +1
        else:
            for oline in line.split('///'):
                stdscr.addstr(count, 0, oline)
                count = count +1
        stdscr.refresh()
      while count < prevlen:
        stdscr.addstr(count, 0, "")
        stdscr.refresh()
        count = count + 1
    except:
      pass
    prevlen = count
    fd.close()

file = '/tmp/' + sys.argv[1]
pretime = None
while True:
    nowtime = os.path.getmtime(file)
    if pretime != nowtime:
        update(file)
        pretime = nowtime
    time.sleep(0.1)
