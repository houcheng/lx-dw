
scripts/gdb: add data window feature

Add data window feature to show current kernel status
on separate consoles, including: 1) registers, 2) back
trace and 3) watch data windows.

The data window would updated on each step or break of 
kernel execution. The modified fields of data window 
would be highlighted.


