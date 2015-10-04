Linux Data Window Feature
------------------------------


## Install LX-DW

Setup the debug GUI feature enable by modify your ~/.gdbinit, add this line:

```
source /paths-to-lx-dw/lx-dw/dw.py
```


## Start GUI console

In the lx-dw directory, run lx-dw.sh script that will create 3 debug information consoles:

```
$ ./lx-dw.sh
```


## Enable lx-dw

start gdb to debug and issue the command to enable lx-dw feature:

```
(gdb) lx-dw
```

Then, run gdb as usual you will see information is updated on debug consoles The command lx-add and lx-del may add/del watch variables.

```
(gdb) lx-add p * s
(gdb) lx-del 3
```

## Some useful gdb commands

- layout source

```
(gdb) layout src
```

- then use ctrl-p ctrl-n to command history, use ctrl-b and ctrl-f to cursor left and right.

- then use ctrl-x o to change active window, ctrl-l to redraw.

