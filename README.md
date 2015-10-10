Linux Data Window Feature
------------------------------

Linux Data Window is GDB scripts to display target detail information in separate GUI window during GDB debugging. The GDB target can be either normal program or kernel. There are four kinds of linux data window.

1. Source data window: show current source code.
2. Watch data window: show watch variables, current stack content, current kernel thread's name, and assembly code pointed by current PC.
3. Back trace data window: show back trace of current application/ kernel thread.
4. Register data window: show current vCPU's register values.

## Screenshot
![](https://raw.githubusercontent.com/houcheng/lx-dw/master/lx-dw.png)


## Install procedure

Check out the lx-dw source code from git hub.

```
git clone git@github.com:houcheng/lx-dw.git
cd lx-dw
sudo ./install.sh
```

Modify your ~/.gdbinit; add this line:

```
source /usr/bin/dw.py
```


## Start data window GUI

In the lx-dw directory, run lx-dw.sh script that will create 3 debug information consoles:

```
$ lx-dw
```


## debugging with data window

start gdb to debug and issue the command to enable lx-dw feature:
```
(gdb) lx-dw
```

Then, run gdb as usual you will see information is updated on debug consoles Use "lx-add <gdb print command>" or "lx-del <number>" to add/del watch variables.

```
(gdb) lx-add p * s
(gdb) lx-del 3
```


## GDB's TUI debug mode

- Use "layout src" or "layout asm" to enter GDB's TUI debugging mode that shows source or assembly on top half screen.

- then use ctrl-p ctrl-n to command history, use ctrl-b and ctrl-f to cursor left and right.

- then use ctrl-x o to change active window, ctrl-l to redraw.

