#!/usr/bin/env bash
ssh -t rmpp << 'EOF'

echo 'Remounting...'
mount -o remount,rw /

echo 'Removing...'
# On older firmware, this was the only image used for the sleeping screen.
# mv /usr/share/remarkable/suspended.png /usr/share/remarkable/suspended.png.bak

# On newer firmware, there are three images used for the sleeping screen, and they are in a different location.
rm /usr/share/remarkable/carousel/sleep_Illustration_01.png
rm /usr/share/remarkable/carousel/sleep_Illustration_02.png
rm /usr/share/remarkable/carousel/sleep_Illustration_03.png

echo 'Replacing...'
# On older firmware, this was the only image used for the sleeping screen.
# cp /home/root/suspended.png /usr/share/remarkable/suspended.png

# On newer firmware, there are three images used for the sleeping screen, and they are in a different location.
cp /home/root/suspended.png /usr/share/remarkable/carousel/sleep_Illustration_01.png
cp /home/root/suspended.png /usr/share/remarkable/carousel/sleep_Illustration_02.png
cp /home/root/suspended.png /usr/share/remarkable/carousel/sleep_Illustration_03.png

echo 'Rebooting...'
reboot

EOF