[ "$1" = "" ] && KERNEL=../kernel/
echo kernel is $KERNEL
cp dw.py $KERNEL/scripts/gdb/linux/
cp lx-dw.py $KERNEL/scripts/gdb/linux/
cp vmlinux-gdb.py $KERNEL/scripts/gdb/
cp lx-dw.sh $KERNEL/scripts/
cp gdb-kernel-debugging.txt $KERNEL/Documentation/
