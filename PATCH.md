
scripts/gdb: add data window feature

Add data window feature to show current kernel status
on separate consoles, including: 1) registers, 2) back
trace and 3) watch data windows.

The data window would help kernel developer to understand
current hardware/ kernel status, and on single-stepping, the
modified fields in the data window would be highlighted.
