# modify your .gdbinit into:
# add-auto-load-safe-path ~/source/linux/
cd ~/source/linux/
#/opt/gdb/bin/
gdb  ~/source/linux/vmlinux -ex " target remote localhost:8864" \
  -ex "lx-dw"




