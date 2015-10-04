
scripts/gdb: add data window feature

Add data window feature to show current kernel status
on separate consoles, including: 1) registers, 2) back
trace and 3) watch data windows.

The data window would help kernel developer to understand
current hardware/ kernel status, and on single-stepping, the
modified fields in the data window would be highlighted.



------------------------------------------ no use -----------

[watch DW]                           [reg DW]       
+----------------------------------+ +--------------+
|p/8x $rsp                         | |RAX 0x00000000|
|0x0000 0x0000 0x0000 0x0000       | |RBX 0x00000000|
|0x0000 0x0000 0x0000 0x0000       | |RBX 0x00000000|
|                                  | |RBX 0x00000000|
|p $lx_current().comm              | |     .        |
|"sshd\0\0\0"                      | |     .        |
|                                  | |     .        |
+----------------------------------+ |              |
[bt DW]                              |              |
+----------------------------------+ |              |
|#1                                | |              |
|#1                                | |              |
|                                  | |              |
|                                  | |              |
+----------------------------------+ +--------------+
