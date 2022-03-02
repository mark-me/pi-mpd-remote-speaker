#! /bin/bash

COMMAND='python3 pi-mpd-touchscreen.py'
LOGFILE=restart.txt

writelog() {
  now=`date`
  echo "$now $*" >> $LOGFILE
}

case $SSH_CONNECTION in
  '')
  writelog "Starting"
  cd pi-mpd-touchscreen
  while true ; do
    "$COMMAND"
    writelog "Exited with status $?"
    writelog "Restarting"
  done
  cd .. ;;
esac

