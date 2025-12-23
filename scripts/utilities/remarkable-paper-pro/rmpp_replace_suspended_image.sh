#!/usr/bin/env bash
ssh -t rmpp << 'EOF'

echo 'Remounting...'
mount -o remount,rw /

echo 'Renaming...'
mv /usr/share/remarkable/suspended.png /usr/share/remarkable/suspended.png.bak

echo 'Replacing...'
cp /home/root/suspended.png /usr/share/remarkable/suspended.png

echo 'Rebooting...'
reboot

EOF